# 第 95 篇验证记录

核对日期：2026-10-02。执行环境：Linux x86_64；uv 0.12.19；CPython 3.12.14。依赖从 Python 包索引解析，使用本次生成的 `uv.lock`；未在 Windows、Docker daemon、GitHub Actions 的远端 runner 上执行。

## 实际完成

1. `uv init demo-project --python 3.12 --vcs none`：确认默认应用模板生成 `.python-version`、README、pyproject 和 `src/demo_project/__init__.py`，并在 `pyproject.toml` 中包含 `uv_build` 构建后端。`--vcs none` 只为隔离探针 Git 状态。
2. `uv init --no-package --python 3.12 --vcs none uv-fastapi-demo`：生成示例根目录和初始 `main.py`；将示例代码迁移为 `app/main.py`，删除初始 `main.py`。`--vcs none` 在本地 staging 避免创建嵌套仓库，正文中使用常规 `uv init --no-package`。
3. `uv add fastapi uvicorn` 与 `uv add --dev pytest httpx`：解析 24 个包并写入真实 `uv.lock`；`pyproject.toml` 中运行依赖和 `dev` 组与文章完整代码一致。
4. `uv lock --check`：通过。`uv tree --locked`：直接依赖 FastAPI、uvicorn；测试组 httpx、pytest，并显示其间接依赖。
5. `uv run --locked python -m pytest -q`：**3 passed，1 warning**。警告为 Starlette 测试客户端在当前 FastAPI/Starlette 组合中使用 `httpx` 的弃用提示，来自依赖，不是应用测试断言失败。
6. 在同一执行环境启动 uvicorn 后实际发送 HTTP：`GET /health` → 200 和 `{"status":"ok"}`；`POST /tasks` → 201 和 ID 1；`GET /tasks/1` → 200；`DELETE /tasks/1` → 204；再次 GET → 404；空标题 POST → 422。测试后服务已停止。
7. 将**不含 `.venv`** 的项目复制到临时目录，执行本地 `git init`、commit、`git clone`，在新 clone 中 `uv sync --locked`、`uv run --locked python -m pytest -q`：克隆端新建 `.venv`，`uv.lock` 与原项目逐字节相同，仍是 **3 passed，1 warning**。这是本地 Git 克隆模拟，并非 GitHub 推送或另一台计算机实测。
8. `uv export --format requirements.txt --no-dev --output-file <临时路径>`：成功导出。导出物留在临时验证目录，未作为项目必须维护的第二依赖源提交。
9. 临时旧项目含原始 `main.py` 与 `requirements.txt`（`requests==2.32.5`、`Flask==3.1.2`），运行 `uv init --no-package --python 3.12 --vcs none`、`uv add -r requirements.txt`、`uv run python main.py`：两个固定版本成功解析安装，原脚本输出 `legacy`。这验证了**直接依赖文件**的迁移路径；对 `pip freeze` 导出的混合列表仍应先甄别依赖来源。

## 未执行的环境相关步骤

- Windows PowerShell 安装、激活脚本、IDE 解释器选择：按官方文档核对，未在 Windows 主机实测。
- Dockerfile：无 Docker daemon，因此只核对官方 uv Docker 指南与文件内容，未 `docker build`。
- `.github/workflows/ci.yml`：参考官方 GitHub Actions 指南，未在 GitHub runner 执行。文件归档在示例目录，不能证明外层 CSDN 仓库已有绿色 CI。
- 上游包更新、其他 CPU 架构、非 Linux 平台的实际 wheel 安装：未实测；锁文件支持条件分支也不代表这些平台都经本文验收。

文章中绝对路径、机器名称和示例依赖版本只在核对日期与对应环境有意义；在你的机器上应重新运行 `uv --version`、`uv run python -V` 和测试。
