# Scope 2 追溯矩阵

来源优先级：Proposal 的 Scope 2 确定业务范围；Cabot.md 是讨论记录；code.py 是原型实现参考。原型第 4 条是付款金额，第 5 条是付款状态；本体 REC-04/REC-05 按下表稳定映射，不能按代码注释序号直接映射。

|规则|结果词表|验收|
|---|---|---|
|REC-01 供应商侧发票存在性|sca:SupplierOnlyRecord|规则词表完整性；REC-03/07 有金额桥接样例，REC-06 有独立部分应用样例；均非生产算法|
|REC-02 企业侧发票存在性|sca:CabotOnlyRecord|规则词表完整性；REC-03/07 有金额桥接样例，REC-06 有独立部分应用样例；均非生产算法|
|REC-03 发票金额一致性|sca:InvoiceValueDifference|规则词表完整性；REC-03/07 有金额桥接样例，REC-06 有独立部分应用样例；均非生产算法|
|REC-04 付款状态一致性|sca:PaymentStatusDifference|规则词表完整性；REC-03/07 有金额桥接样例，REC-06 有独立部分应用样例；均非生产算法|
|REC-05 付款金额一致性|sca:PaymentDifference|规则词表完整性；REC-03/07 有金额桥接样例，REC-06 有独立部分应用样例；均非生产算法|
|REC-06 贷项应用检查|sca:CreditOffsetDifference|规则词表完整性；REC-03/07 有金额桥接样例，REC-06 有独立部分应用样例；均非生产算法|
|REC-07 净应付对账|sca:NetPayableDifference|规则词表完整性；REC-03/07 有金额桥接样例，REC-06 有独立部分应用样例；均非生产算法|

|需求|来源定位|实现|自动测试|
|---|---|---|---|
|七类检查语义|Proposal Scope 2；code.py 仅五类|AuditRule REC-01..07 + FindingType|test_16|
|两端存在性不能用金额为空替代|code.py presence 分支的风险|RecordObservation + SourceDataset 完整性声明|test_06、07、20|
|金额/状态/付款差异|code.py 对应 check_name|REC-03 金额；REC-04 状态（原型第5条）；REC-05 付款金额（原型第4条）|test_14、16|
|V100 22300/18800|Cabot.md 经典案例|BalanceSnapshot、REC-07 预设 Evaluation|test_08|
|部分贷项应用|Scope 2 + Cabot.md credit discussion；600/200/400为本轮合成|CreditAllocation + Credit_Observation|test_09、19|
|原因解释与人工确认分开|已批准实现计划|FindingInterpretation、ReviewDecision|test_15|
|术语访问|PROJECT_CONTEXT.md|OAK SqlImplementation|test_10..14、18|
|质量与开发发布门禁|已批准计划|metadata_errors、data_errors、ROBOT verify|test_01..06、21|
|不混入正式实例|已批准计划|主本体/演示本体与数据库分离|test_17；Docker模式另查核心数据库|

文件散列见 source-manifest.json。REC-01、02、04、05 本轮只有语义定义，不是已执行/验收的业务算法；REC-03、06、07 的实例也只是预设合成结果。
