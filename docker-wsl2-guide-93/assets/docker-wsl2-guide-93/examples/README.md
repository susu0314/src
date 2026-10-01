# Docker Desktop + WSL2：配套项目

本文配套代码包含两个独立项目，避免把学习用的 Flask 启动方式与完整项目混用。

- `01-basic-web`：单容器 Flask 项目，对应文章第 8～10 节。
- `02-flask-redis`：Gunicorn + Flask + Redis 持久化计数器，对应文章第 16 节。
- `VERIFICATION.md`：已经执行的检查和当前环境无法执行的检查。

## 运行前提

Windows 端已按文章配置 WSL2 和 Docker Desktop，选择 Linux containers，并启用目标发行版的 WSL Integration。项目建议放在 WSL Linux 文件系统。以下 Docker 命令在 WSL Bash 执行；Windows HTTP 测试使用 PowerShell 的 `curl.exe`。

## 1. 单容器项目

进入目录并构建：

```bash
cd 01-basic-web
docker build -t docker-demo:v1 .
docker run -d --name basic-web -p 127.0.0.1:8000:8000 docker-demo:v1
```

`cd` 切换目录；`build` 将当前目录作为上下文并设置标签；`run` 后台启动新容器，只向本机发布 8000。

PowerShell 中验证：

```powershell
curl.exe -f http://localhost:8000/
```

它读取首页 JSON，HTTP 错误时返回失败。该项目使用 Flask 开发服务器，仅用于理解构建与运行。

进入第二个项目之前，停止并删除容器，释放 8000：

```bash
docker stop basic-web
docker rm basic-web
cd ../02-flask-redis
```

## 2. 完整项目

```bash
docker compose config -q
docker compose up -d --build
docker compose ps
docker compose logs --tail 50 app redis
```

分别验证配置、构建并启动服务、查看状态、读取两个服务最近日志。首次构建完成后等待健康状态就绪。

PowerShell 中：

```powershell
curl.exe -f http://localhost:8000/health
curl.exe -f http://localhost:8000/counter
curl.exe -f -X POST http://localhost:8000/counter
curl.exe -f http://localhost:8000/counter
```

分别检查健康、读取计数、增加一次、验证新值。新卷初值为 0；已有卷从原值继续。WSL Bash 使用 `curl` 替代 `curl.exe`。

## 3. 依赖故障恢复

```bash
docker compose stop redis
```

该命令只停止 Redis。PowerShell 检查响应状态码：

```powershell
curl.exe -i http://localhost:8000/health
curl.exe -i -X POST http://localhost:8000/counter
```

`-i` 显示响应头，预期为 503。接着在 WSL 中恢复服务：

```bash
docker compose start redis
```

等待就绪后重新检查健康和计数；应恢复 200，原值保留。

## 4. 持久化验收和清理

记下当前计数，再执行：

```bash
docker compose down
docker compose up -d
```

`down` 删除容器和默认网络，保留 named volume；`up` 从已有镜像与卷重新创建服务。恢复健康后读取计数，应与原值一致。

日常停止可用 `docker compose stop`。只有确定练习数据不再需要时执行：

```bash
docker compose down --volumes
```

它会删除本项目管理的非 external 卷，包括计数数据。

## 配置边界

镜像使用 `python:3.12-slim` 与 `redis:7.4`，标签可能更新；requirements 固定直接依赖，未完全锁定传递依赖。正式项目应进一步固定内容并维护升级策略。

服务只为本机练习设计。Redis 不向宿主发布端口，但没有配置认证；正式部署需根据实际场景增加安全配置、备份、外部入口和资源限制。所有关键字段在文章中逐项解释。
