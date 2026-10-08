# MVP 架构与治理

## 实现范围

OWL 是业务术语及公理的权威源；来源记录、业务凭证、计算结果、原因解释与人工决定分离。主本体由 Protégé 编辑，ODK 负责生命周期，ROBOT/HermiT 负责解析和逻辑，独立 Python 约束负责必填字段与证据，OAK/SemSQL 负责访问。没有完整审计引擎、真实数据接入、HTTP 服务、GraphRAG 或 Agent 部署。

## 逻辑模块

|模块|核心概念|设计理由|
|---|---|---|
|主体与账户|Organization、Supplier、BuyerLegalEntity、SupplierAccount|供应商与采购法人共同定义账户范围|
|凭证与来源|FinancialDocument、Invoice、CreditMemo、DebitNote、SupplierStatement、Payment、SourceDataset、RecordObservation|同一业务对象允许多条来源观察，金额冲突不覆盖|
|核对过程|ReconciliationScope、ReconciliationRun、MatchDecision、AuditRule、RuleEvaluation、BalanceSnapshot|把输入版本、匹配判断、执行与检查结果分开|
|异常与审核|AuditFinding、FindingInterpretation、ReviewDecision|解释不是事实，审核决定不是计算结果|
|分配|Allocation、PaymentAllocation、CreditAllocation|允许多对多付款及部分贷项应用|
|词表|CheckOutcome、FindingStatus、PaymentStatus、RiskLevel、IssueSeverity、CauseCategory 等|保持状态、严重程度、原因分类的语义差异|

完整类、属性、定义见 `glossary.tsv` 及主 OWL。词表是具类型的个体，ControlledConcept 复用 SKOS Concept。规则 `REC-01`—`REC-07` 是 AuditRule 个体。OAK 查询不执行这些规则。

金额是 decimal；所有带金额实例须有币种，观察与分配有来源关系、快照或交易日期。OWL domain/range 用于推理，不等于输入验证。最少存在限制说明业务语义；闭世界必填校验在 `validation.py`。Organization 与 FinancialDocument、观察与 Finding、Finding 与解释、审核与解释有必要互斥，不把所有供应链类一概互斥。

## 导入与 namespace

开发实体 `https://example.org/cabot-audit/ontology/`，合成实例 `urn:example:cabot-audit:`。目前使用具可读名称的 IRI；生成器附带的数字 ID ranges 文件只保留为 ODK 模板资产，当前不通过其分配新术语。正式发布前确定企业命名策略。

metadata.owl 是本地维护的最小声明依赖：SKOS、PROV 和定义注释术语的必要声明。它不是完整的 SKOS/PROV 导入，也不声称继承其全部语义；依赖已固定散列。若未来需要完整 PROV 推理，单独评估模块抽取和 license，再迁移并验收。

## 仓库布局

```text
supply-chain-ontology/
├── src/ontology/
│   ├── scaudit-edit.owl          # 编辑真源
│   ├── Makefile                  # 官方 ODK seed 生成
│   ├── scaudit.Makefile          # 项目扩展
│   ├── scaudit-odk.yaml          # ODK 配置
│   ├── imports/metadata.owl      # 固定本地术语声明
│   ├── config/                   # prefix/context
│   └── catalog-v001.xml
├── src/cabot_ontology/            # OAK adapter、CLI、数据约束
├── src/sparql/                    # ROBOT QC 查询
├── scripts/                       # Windows/Linux 构建与验收
├── tests/                         # 数据、OAK、负例测试
├── examples/                      # 合成 ABox、CSV、预设结果
├── config/                        # 工具锁定和字段映射
├── docs/                          # 中文手册、来源和追溯
├── .github/workflows/             # 待远程仓库启用的 CI
├── build/                         # 不入 Git 的派生制品
├── .tools/                        # 不入 Git 的本地工具
└── .venv/                         # 本机诊断环境
```

首轮不用多份可编辑 OWL 人为制造跨模块循环导入。规模增长后再拆 identity、finance、reconciliation、provenance 模块，确保单向依赖。

## 企业工作流

|阶段|输入 → 输出|角色与交付物|
|---|---|---|
|业务确认|Scope 2 + 案例 → 已批准能力问题与政策|业务负责人；规则追溯表|
|本体设计/Protégé|能力问题 → OWL、公理和受控词表|本体工程师；术语及定义|
|Git 评审|OWL 差异 → 受审查版本|业务 owner + 本体 owner；变更记录|
|ODK/ROBOT|固定输入 → 推理 OWL、QC、SemSQL|工程师；可重建制品与 manifest|
|OAK 验收|数据库 → 标签、定义、层级及证据查询|应用工程师；合同测试|
|未来 KG|获批映射 + 数据快照 → 具来源的业务图|数据治理；身份、质量和权限策略|
|未来 GraphRAG|受权限过滤的图和文档 → 带证据回答|检索负责人；评估集与引用|
|未来 Copilot/Agent|语义约束 + 工具权限 → 可审核建议/动作|产品及安全负责人；动作授权、人工决定与审计日志|

## 风险与实践差距

|差距/风险|当前处理|后续门槛|
|临时域名不能稳定发布|正式发布门禁失败|企业 namespace 与 owner 批准、迁移测试|
|OBO Foundry 的开放发布/许可并非企业内部默认目标|复用定义、稳定标识和质量原则，不宣称 OBO 合规|明确组织许可、发布与弃用政策|
|完整约束尚未采用 LinkML/SHACL|MVP Python 约束可运行|映射规模扩大时以 LinkML 定义结构，生成验证器；避免与 OWL 双份真源漂移|
|来源完整性是合成声明|记录 snapshot、hash 与两端观察|真实 extract 完整性、截止日、符号政策和去重必须得到业务确认|
|标识匹配风险|同义词只返回候选；MatchDecision 保留过程|法人、账户、币种、重复发票、归一化碰撞策略|
|ODK 容器未在本机执行|固定镜像 digest，提供严格验收入口|安装 WSL2/Docker，实际执行 test 后才能完成闭环|
|SemSQL 不等于完整 OWL 推理服务|HermiT 与 OAK 各司其职；fixture 明确测试用途|实际数据库对匿名公理、语言、ABox 的回归验收|
|多套本体工具维护负担|编辑源唯一、主 Makefile不改、版本锁定|季度升级演练、导入变更与查询兼容测试|
|推广和治理职责未批准|定义 owner 流程和待办|业务负责人正式确认规则、容差、贷项及风险分级|
|Agent 把解释当结论|独立 FindingInterpretation 与 ReviewDecision|访问控制在数据/查询层实施，引用可追踪、动作需明确授权|

优先瓶颈是数据身份、账户边界、快照完整性和证据质量，而不是增加更多类。未来依次扩展：真实小批量只读映射 → 确定性审计引擎 → 受权限控制的 KG → 有检索评估的 GraphRAG → 有人工动作门禁的 Agent。

ASSUMPTION: CNY、截止日、Cabot_Test_Entity、所有实例金额仅为演示选择；不代表 Cabot 已批准政策。

TODO: 明确金额容差、贷项正负号、风险等级、主数据标识、外部许可与正式域名。未经业务批准不能将预设结果称为审计结论。
