---
name: douyin_downloader
description: 下载抖音无水印视频、图文和用户主页作品的批量下载工具
---

# Douyin Downloader Skill

该技能用于通过命令行执行 `douyin-downloader` 下载抖音无水印视频、图文或整个用户主页的作品。

## 🎯 适用场景 (When to use)
- 当用户要求下载某个具体的抖音视频或图文链接时。
- 当用户要求批量下载某个抖音用户（作者）主页的所有作品时。
- 当用户询问某个抖音链接的信息并希望提取其无水印原视频/原图时。

## ⚙️ 环境准备 (Prerequisites)
1. **项目根目录**：`~/.openclaw/workspace/douyin-downloader`。所有相关命令必须在此目录中执行。
2. **虚拟环境**：建议在 Python 虚拟环境中运行。在执行具体 `run.py` 之前激活虚拟环境，例如组合命令：
   ```bash
   cd ~/.openclaw/workspace/douyin-downloader
   source .venv/bin/activate
   ```
3. **配置与身份验证**：`config.yml` 文件中保存了下载配置（如并发数、数据库等）、Cookie 及其他身份凭证。
   - 如果下载失败提示 Cookie 过期、"Brotli error"、或因未登录而被阻断，请提示用户修改 `config.yml`，或者运行 `python tools/cookie_extractor.py` 进行 cookie 更新。

## 🚀 如何使用 (How to use)

该工具提供了一个 `run.py` 命令行入口。在使用时请**务必调用 `config.yml`** 以读取默认配置。

### 使用配置文件运行（下载 `config.yml` 中定义的链接）
如果用户在 `config.yml` 中已经写好了要下载的链接，或者需要以默认配置启动，直接执行：
```bash
python run.py -c config.yml
```

### 命令行追加参数（临时下载特定链接）
如果要下载特定链接，同时指定并发数和目录，请优先使用如下形式：
```bash
python run.py -c config.yml \
  -u "https://www.douyin.com/video/7604129988555574538" \
  -t 8 \
  -p ./Downloaded
```

**参数说明**：
- `-u, --url`：追加下载链接（可重复传入）。
- `-c, --config`：指定配置文件（必须传入 `-c config.yml` 以防漏缺核心配置）。
- `-p, --path`：指定下载目录。
- `-t, --thread`：指定并发数。
- `--show-warnings`：显示 warning/error 日志。
- `-v, --verbose`：显示 info/warning/error 日志。

## 📂 输出结果与验证
- 媒体文件默认保存在 `Downloaded/` 目录下（例如 `Downloaded/作者名/post/`）。文件通常以作品发布时间（`YYYY-MM-DD`）作为前缀。
- **独立下载清单**：每次下载的任务清单会追加写入到 `Downloaded/download_manifest.jsonl` 中，这是结构化的 JSON Lines 格式，包含详细的 metadata (`aweme_id`, `date`, `desc`, `tags`, `file_paths` 等)。如需返回下载文件的具体本地路径，应优先读取并解析此文件。
- **SQLite 数据库**：默认也会将历史记录保存在项目根目录的 `dy_downloader.db` 数据库中。

## 🛠 常见错误排查
- **未找到依赖/模块**：未正确激活虚拟环境 `.venv/bin/activate`。
- **接口无返回/报错 403/Brotli压缩错误**：大概率 Cookie 已失效或被风控，提醒用户更新 Cookie。
- **部分主页由于翻页受限无法获取全部**：系统具备 Browser Fallback 机制，如遇主页抓取不全问题可查阅日志确认兜底策略是否生效。
