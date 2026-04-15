# Credential Rotation
日期：2026-07-10

对象存储写入密钥已从 secret version v14 切到 v15。
新版本要求 backup agent 的 SECRET_VERSION 同步更新，否则会返回 SignatureDoesNotMatch。
