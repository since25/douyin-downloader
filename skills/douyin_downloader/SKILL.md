---
name: douyin-downloader
description: 下载抖音无水印视频、图文和用户主页作品的批量下载工具
metadata: {"openclaw": {"emoji": "📹", "requires": {"bins": ["python"]}}}
---

# Douyin Downloader Skill

该技能用于通过命令行执行 `douyin-downloader` 下载抖音无水印视频、图文或整个用户主页的作品。

## 🎯 适用场景 (When to use)
- 当用户要求下载某个具体的抖音视频或图文链接时。
- 当用户要求批量下载某个抖音用户（作者）主页的所有作品时。
- 当用户询问某个抖音链接的信息并希望提取其无水印原视频/原图时。

## ⚙️ 环境准备 (Prerequisites)
1. **执行目录**：所有相关命令建议在 `~/.openclaw/workspace/douyin-downloader` 目录中执行以确保路径和依赖正确。
2. **虚拟环境**：依赖 `.venv`。请在运行时先 `source .venv/bin/activate`。
3. **配置与身份验证**：`config.yml` 文件中保存了下载配置（如并发数、数据库等）、Cookie 及其他身份凭证。
   - 如果下载失败提示 Cookie 过期、"Brotli error"、或因未登录被阻断，请提示用户运行脚本刷新或手动修改 `config.yml`。

## 🚀 如何使用 (How to use)

该工具提供了一个 `run.py` 命令行入口。在使用时请**务必调用 `-c config.yml`** 以读取默认配置。

### 1. 使用预设配置运行（默认链接）
如果只希望以 `config.yml` 中默认的配置加载下载链接，直接执行：
```bash
cd ~/.openclaw/workspace/douyin-downloader
source .venv/bin/activate
python run.py -c config.yml
```

### 2. 命令行临时追加参数（常用）
如果要下载特定链接，同时指定并发数和目录，请使用如下形式：
```bash
cd ~/.openclaw/workspace/douyin-downloader
source .venv/bin/activate
python run.py -c config.yml \
  -u "https://www.douyin.com/video/7604129988555574538" \
  -t 8 \
  -p ./Downloaded
```

**支持的参数说明**：
- `-u, --url`：追加下载链接（支持重叠传入）。
- `-c, --config`：指定配置文件。
- `-p, --path`：指定下载目录。
- `-t, --thread`：指定并发数。
- `--show-warnings`：显示 warning/error 日志。
- `-v, --verbose`：显示 info/warning/error 日志。

## 📂 输出结果与验证
- 媒体文件默认保存在 `Downloaded/` 目录下（例如 `Downloaded/作者名/post/`）。
- **独立下载清单**：每次下载的任务清单会追加写入到 `Downloaded/download_manifest.jsonl` 中，包含详细的 metadata (`aweme_id`, `date`, `desc`, `tags`, `file_paths` 等)。如需提取本地真实路径，应优先解析此文件。
- **SQLite 数据库**：历史记录保存在项目根目录的 `dy_downloader.db` 数据库中。
