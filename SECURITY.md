# Security Policy

## 本仓库负责的范围

可以报告 Overlay 导致的 DOM 注入或内容处理风险、Installer/upgrade/restore 可能覆盖非目标文件的问题、诊断命令意外输出敏感信息，以及 GitHub Actions / 发布流程中的供应链风险。

LiteLLM Proxy 核心、Provider、数据库、认证或上游 WebUI 自身漏洞应报告给 BerriAI/litellm。

## 报告方式

如果问题涉及可利用的安全漏洞或敏感信息，请优先使用 GitHub Security Advisory 的私密报告渠道（如仓库已启用），不要在公开 Issue 中附真实凭据或生产日志。

普通翻译错误、漏翻和兼容性问题可以使用公开 Issue 模板。

## 不要提交的敏感信息

- API Key / MASTER_KEY
- 密码或 Access Token
- Cookie / Session
- 数据库 URL
- 完整 .env 或生产配置
- 未脱敏请求、响应或日志
