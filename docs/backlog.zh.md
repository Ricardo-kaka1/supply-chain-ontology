# 可执行开发待办

## Epic 1：完成工具闭环（P0）

### Task ENV-01：启用 WSL2 / Docker

#### Objective
解除官方构建阻塞。
#### Inputs
中文手册、已下载安装包、用户/企业 IT 系统权限。
#### Outputs
doctor 成功日志及实际环境版本。
#### Dependencies
用户/IT 启用 Windows 功能及必要重启；当前未完成。
#### Definition of Done
固定 digest 的 Linux 容器启动，目录挂载及 ROBOT/OAK/SemSQL 版本检查通过。

### Task BUILD-01：官方构建验收

#### Objective
生成真实 SemSQL 发布库并完成容器验收。
#### Inputs
主 OWL、演示数据、ODK Makefile、固定容器。
#### Outputs
版本化 OWL、两个 DB、manifest、acceptance.json。
#### Dependencies
ENV-01；脚本已实现但尚未运行。
#### Definition of Done
`scripts/cabot.ps1 test` 成功；真实 DB 查询、逻辑反例、干净重建语义与查询比较通过；不能用 fixture 代替。

### Task UI-01：Protégé 桌面验收

#### Objective
确认编辑与查看体验。
#### Inputs
Protégé 5.6.9、主 OWL、demo、catalog。
#### Outputs
填写完成的 desktop-acceptance.md。
#### Dependencies
用户实际操作；可先于 ENV-01。
#### Definition of Done
本地 imports、双语标签、HermiT、两端观察、贷项及解释/审核关系全部确认。

## Epic 2：固化语义与访问（P0/P1）

### Task ONT-01：核心本体与七类规则

#### Objective
区分账户、凭证、观察、计算、解释、审核与分配。
#### Inputs
Scope 2、Cabot.md、code.py、已批准计划。
#### Outputs
主 OWL、metadata、术语表、追溯矩阵；已实现。
#### Dependencies
无系统安装依赖。
#### Definition of Done
标签与定义齐全，本机 HermiT/OWL 2 DL 通过；正式容器验收由 BUILD-01 完成。

### Task ACCESS-01：OAK 接口与数据门禁

#### Objective
稳定提供 search/get/label/definition/ancestors/relationships/reference 校验。
#### Inputs
SemSQL DB、prefix、术语和数据约束。
#### Outputs
adapter、CLI、约束和自动测试；本机测试已通过。
#### Dependencies
BUILD-01 提供正式 DB。
#### Definition of Done
同一套接口在官方 DB 上通过；未知标识明确返回未找到，同义词只给候选，层级只走 subclass。

### Task GOV-01：业务评审与 Git 基线

#### Objective
明确业务批准和技术验证的边界。
#### Inputs
追溯矩阵、ASSUMPTION、业务 owner、用户 Git author。
#### Outputs
已批准/待定规则清单、首个本地 commit。
#### Dependencies
ONT-01；不能编造作者身份或业务批准。
#### Definition of Done
七类规则映射确认，容差/贷项/风险政策状态明确，原始资料散列一致，Git 可追溯。

## Epic 3：后续演进（不在本轮执行范围）

### Task DATA-01：真实数据映射与验证

#### Objective
验证身份、完整性和账户边界。
#### Inputs
获授权脱敏数据、法人/币种/截止日政策。
#### Outputs
LinkML/SHACL 方案评估、字段映射、碰撞检测、数据质量报告。
#### Dependencies
GOV-01、数据授权。
#### Definition of Done
重复发票、归一化碰撞、null 与缺行、多币种、快照不完整均有正反例；原始观察不覆盖。

### Task ENGINE-01：确定性规则执行

#### Objective
将语义规则连接到可复现的审计实现。
#### Inputs
已批准规则政策与 DATA-01 契约。
#### Outputs
七类业务引擎、RuleEvaluation、稳定 finding fingerprint、证据链。
#### Dependencies
DATA-01。
#### Definition of Done
七类业务正反例通过，金额容差、部分抵扣、净差额及回收金额分开，重复运行幂等；当前预设数据不算完成证据。

### Task RELEASE-01：正式域名与发布治理

#### Objective
建立稳定企业语义版本。
#### Inputs
企业 namespace、owner、许可和发布范围。
#### Outputs
IRI 迁移、弃用策略、企业 Git/CI。
#### Dependencies
GOV-01、BUILD-01。
#### Definition of Done
正式门禁无临时 namespace，迁移映射和升级兼容策略批准，干净环境重建通过。

### Task KG-01：KG → GraphRAG → Agent

#### Objective
在有权限、有证据的语义层上提供辅助分析。
#### Inputs
审计输出、数据权限、检索能力问题及评估集。
#### Outputs
图映射、证据检索、答案引用、人工审核和动作授权记录。
#### Dependencies
DATA-01、ENGINE-01、RELEASE-01。
#### Definition of Done
跨法人/账户权限隔离、来源引用、检索质量和拒答评估通过；解释不冒充事实，动作经过明确授权。

优先下一步：UI-01 可立即操作；ENV-01 → BUILD-01 完成工具闭环；随后 GOV-01。未来瓶颈优先关注身份匹配、数据完整性和政策批准。
