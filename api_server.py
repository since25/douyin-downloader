import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from threading import Lock, Thread
from typing import Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


APP_ROOT = Path(__file__).parent.resolve()
LOG_DIR = APP_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class DownloadRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    path: Optional[str] = None
    cookie: Optional[str] = None
    auto_cookie: Optional[bool] = None
    config: Optional[str] = None


class JobInfo(BaseModel):
    id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    exit_code: Optional[int] = None
    pid: Optional[int] = None
    log_file: str
    command: str


class JobManager:
    def __init__(self) -> None:
        self._jobs: Dict[str, JobInfo] = {}
        self._lock = Lock()

    def submit(self, command: list[str]) -> JobInfo:
        job_id = uuid4().hex
        log_file = LOG_DIR / f"{job_id}.log"
        created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        job = JobInfo(
            id=job_id,
            status="queued",
            created_at=created_at,
            log_file=str(log_file),
            command=" ".join(command),
        )
        with self._lock:
            self._jobs[job_id] = job

        thread = Thread(target=self._run_job, args=(job_id, command, log_file), daemon=True)
        thread.start()
        return job

    def get(self, job_id: str) -> JobInfo:
        with self._lock:
            job = self._jobs.get(job_id)
        if not job:
            raise KeyError(job_id)
        return job

    def list(self) -> list[JobInfo]:
        with self._lock:
            return list(self._jobs.values())

    def _run_job(self, job_id: str, command: list[str], log_file: Path) -> None:
        started_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        with self._lock:
            job = self._jobs[job_id]
            job.status = "running"
            job.started_at = started_at

        try:
            with open(log_file, "w", encoding="utf-8") as f:
                proc = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT)
                with self._lock:
                    job.pid = proc.pid
                exit_code = proc.wait()
        except OSError as exc:
            exit_code = 1
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n[api_server] spawn failed: {exc}\n")

        finished_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        with self._lock:
            job.exit_code = exit_code
            job.finished_at = finished_at
            job.status = "success" if exit_code == 0 else "failed"


def _extract_url(url: Optional[str], text: Optional[str]) -> str:
    if url and url.strip():
        return url.strip()
    if text:
        match = re.search(r"https?://\S+", text)
        if match:
            candidate = match.group(0).strip()
            return candidate.rstrip("'\"),，。！？!?]")
    raise HTTPException(status_code=400, detail="missing_url")


def _build_command(payload: DownloadRequest, url: str) -> list[str]:
    python = sys.executable
    script = APP_ROOT / "downloader.py"

    command = [python, str(script), "-u", url]
    if payload.config:
        command.extend(["-c", payload.config])
    if payload.path:
        command.extend(["-p", payload.path])
    if payload.auto_cookie:
        command.append("--auto-cookie")
    if payload.cookie:
        command.extend(["--cookie", payload.cookie])
    return command


app = FastAPI(title="Douyin Downloader API", version="0.1.0")
jobs = JobManager()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/download", response_model=JobInfo)
def download(payload: DownloadRequest) -> JobInfo:
    url = _extract_url(payload.url, payload.text)
    command = _build_command(payload, url)
    return jobs.submit(command)


@app.get("/api/jobs", response_model=list[JobInfo])
def list_jobs() -> list[JobInfo]:
    return jobs.list()


@app.get("/api/jobs/{job_id}", response_model=JobInfo)
def get_job(job_id: str) -> JobInfo:
    try:
        return jobs.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job_not_found") from exc
