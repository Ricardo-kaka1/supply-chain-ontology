# Cabot Supplier Reconciliation Ontology MVP

本地开发版本 `0.1.0-dev`：Protégé 编辑 → ODK/ROBOT/HermiT → OWL → SemSQL → OAK。

核心本体、独立合成案例、OAK Python/CLI、测试和构建入口已实现。本机诊断已通过；**Docker 官方构建和 Protégé 桌面验收待完成，尚不能称为端到端通过**。

- [中文操作手册](docs/manual.zh.md)
- [架构与治理](docs/architecture.zh.md)
- [需求追溯](docs/traceability.md) / [术语表](docs/glossary.tsv)
- [开发待办](docs/backlog.zh.md) / [桌面验收表](docs/desktop-acceptance.md)

```powershell
.\scripts\cabot.ps1 native-test
.\scripts\cabot.ps1 protege
.\scripts\cabot.ps1 doctor
.\scripts\cabot.ps1 test
```

主编辑文件为 `src/ontology/scaudit-edit.owl`，合成实例为 `examples/owl/cabot-demo.owl`。只编辑源文件，派生文件在 build 中。原 OneDrive 资料保持原样；新仓库无 remote、无公共发布。本机 Git 未配置作者身份，尚未创建提交；manifest 将如实记录。

七类 AuditRule 是语义定义，未实现完整业务引擎。预设差额不代表真实审计结论或可追回金额。
