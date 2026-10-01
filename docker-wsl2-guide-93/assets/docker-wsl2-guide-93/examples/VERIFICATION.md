# 验证记录

日期：2026-10-01。

## 已执行

| 检查 | 实际方式 | 结果 |
| --- | --- | --- |
| 基础 Flask 首页 | Flask test client 调用实际应用 | PASS |
| 完整 Compose 结构 | 官方 compose-spec JSON Schema 校验 YAML | PASS |
| HTTP + Redis 计数 | Linux 上启动实际 Gunicorn，2 个 worker，连接真实 Redis 服务 | PASS |
| 并发写入一致性 | 先写入 1 次，再并发提交 30 次 POST，核对连续计数及最终值 31 | PASS |
| Redis 停止后的行为 | 停止真实 Redis，检查健康与 POST 接口 | 均返回 503 |
| 依赖恢复与数据恢复 | 使用原数据目录重启 Redis，应用保持运行 | 健康恢复 200，计数保留，可继续写入 |
| 应用进程重建 | 停止并重新启动 Gunicorn | 计数继续保留 |

应用测试使用 Python 3.12.14、Flask 3.1.2、redis 客户端 6.4.0、Gunicorn 23.0.0；本地 Redis 服务端为 redislite 分发的 Redis 6.2.14。持久化测试关闭 RDB 快照并启用 AOF，以明确验证 AOF 恢复。

官方 Schema 来源：[compose-spec/compose-spec](https://github.com/compose-spec/compose-spec/blob/main/schema/compose-spec.json)。Schema 校验不是 `docker compose config` 的实际执行，也不验证镜像构建或运行行为。

## 未执行

验证环境没有 Docker CLI/daemon，也不是 Windows/WSL 主机，因此以下项目没有被实际执行：

- Windows 与 WSL2 安装、Docker Desktop 启动和 WSL Integration。
- `docker build`、`docker run`、`docker compose config/up/down`。
- `python:3.12-slim` 镜像内安装、UID 和容器进程运行。
- `redis:7.4` 镜像及 Redis 7 的多文件 AOF 行为。
- Docker 网络 DNS、Windows 端口转发、named volume 和 bind mount。
- 删除容器后重建时的卷数据恢复。

这些项目不能由 Linux 进程测试替代。README 和文章第 16 节给出实际 Docker 环境的验收步骤，发布者可在目标机器上补充记录。
