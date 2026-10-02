# uv FastAPI demo

第 95 篇《uv 实战指南》的配套项目。运行版本在本次验证中为 uv 0.12.19、Python 3.12.14；包版本以仓库的 `uv.lock` 为准。

## 开始

在项目根目录执行：

```bash
uv sync --locked
uv run --locked python -m pytest -q
uv run --locked uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

然后访问 `http://127.0.0.1:8000/health`。API 还支持 `POST /tasks`、`GET /tasks/{task_id}`、`DELETE /tasks/{task_id}`。任务仅保存在运行进程的内存中，重启即清空。

`.python-version` 请求 Python 3.12；如系统没有合适的解释器，uv 在允许下载时会自动获取或使用 `uv python install 3.12`。`uv.lock` 应与 `pyproject.toml` 一同提交。不要提交 `.venv`。

`Dockerfile` 和 `.github/workflows/ci.yml` 分别是与官方指南核对的部署/CI 示例；本次没有 Docker daemon 和远端 GitHub Actions 运行记录。当前 FastAPI/Starlette 的 TestClient 在测试时提示 httpx 弃用警告，不影响三项测试通过，详见上层 [验证记录](../VERIFICATION.md)。
