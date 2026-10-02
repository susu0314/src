# 验证记录

核对与执行日期：2026-10-02。详见 [verification-summary.json](verification-summary.json)。

## 实际执行

- Linux Python 3.12.14、Flask 3.1.2、Node.js 24.19.0、Newman 6.2.1。
- 实际 HTTPS GET https://jsonplaceholder.typicode.com/users/1 返回 200；id=1、username=Bret。公网服务后续可用性不作保证。
- Collection JSON 通过官方 2.1.0 JSON Schema 校验。
- 从独立教学 SQLite 数据库启动真实 HTTP 服务，Newman 连续三轮执行 48 请求、90 断言，0 失败。
- 创建后读取、PATCH 保留其他字段、PUT 完整更新、删除 204、删除后 404 均通过。
- 409 / 401 / 403 / 400 / 415 / 422 的负向行为通过状态及业务码断言。
- 三轮后 users 表剩余 0 条，验证本轮数据被清理。
- 错误密码并预设旧 Token，Newman 返回非零，仅执行 Health 和 Login，没有进行用户操作。
- 指向本地未允许的 18099 端口，用受控 HTTP 接收端验证防护：非零退出，收到 0 次请求。
- 正文核心脚本与 API 源码和导入文件核对一致；JSON 和 Markdown 文件结构检查通过。

报告只保留不含 Token、登录响应、Cookie 和原始请求体的结果摘要。完整 Newman 报告可能包含凭据，不作为可分享资产。

## 未执行范围

没有把 Linux 命令行结果描述为 Postman 桌面 GUI 或 Windows 实测。以下提供复现步骤，但未在本次环境执行：

- Windows 安装、PowerShell 命令、Postman GUI 导入与 Functional Runner。
- Postman Web / Desktop Agent、浏览器 CORS、Cookie 与 Session。
- Test 8001 第二实例、证书与上传场景。
- Postman CLI、Collection 3.0 Native Git 工作流。

本文本地 API 不包含文件上传、Session、OAuth2 / JWT、签名接口；相关章节解释其协议与排查方法，没有虚构执行结果。

## 目标机器验收

1. 按 README 创建 Python 虚拟环境、安装依赖、启动 API。
2. curl 或 Postman 请求 /health，确认 200 与 status=ok。
3. 导入 Collection、Environment，选择 Development，手工 Login 后 Me 成功。
4. Functional Runner 一轮 16 请求、30 断言；再执行三轮，48 请求、90 断言。
5. 验证错误密码时不继续用户链路，按本轮 ID 清理未走完的资源。
6. 启动独立 8001 / test.sqlite3 实例，切 Test，从登录开始验证。
7. 停止后再重启服务，确认旧 Token 失效、重新登录可用。
