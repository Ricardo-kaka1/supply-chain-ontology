# Cabot MVP 操作手册

本仓库实现供应商对账的语义层。七类规则是定义和稳定标识，不是已经执行的审计引擎。全部交易、法人、币种及日期为合成案例。当前已通过本机 ROBOT/HermiT 与 OAK 测试；Docker 中的完整 ODK/SemSQL 构建及 Protégé 桌面人工确认尚未完成。

## 1. 本机准备

工作目录：`C:\Users\ricardo.tong\Documents\Codex\supply-chain-ontology`。

已准备 `.tools/Protege-5.6.9/`、`.tools/robot.jar` 和 `.tools/Docker Desktop Installer.exe`。这些大文件与 `.venv` 不进 Git。版本和下载散列见 `config/toolchain.lock.json`；Docker 安装包签名已验证为 Docker Inc。

当前未找到 Docker，先前 `wsl --status` 提示 WSL 未安装。硬件虚拟化状态的系统查询被拒绝访问，因此尚未验证。

由用户或企业 IT 完成以下需要系统权限的步骤：

1. 按 [Microsoft WSL 安装文档](https://learn.microsoft.com/en-us/windows/wsl/install)，在管理员 PowerShell 中运行 `wsl --install`，按提示重启；重新打开终端运行 `wsl --version` 和 `wsl --status`。
2. 运行已下载的 Docker Desktop 安装包，选择企业 IT 允许的安装方式和 WSL2 后端；启动 Docker Desktop，等待 Linux engine 就绪。按 [Docker 官方安装指南](https://docs.docker.com/desktop/setup/install/windows-install/)核对系统条件。
3. 回到仓库目录运行下列 doctor。首次容器下载需要网络；镜像引用已经固定到 digest。后续普通本体构建使用本地 imports，不下载外部本体。

```powershell
Set-Location 'C:\Users\ricardo.tong\Documents\Codex\supply-chain-ontology'
.\scripts\cabot.ps1 doctor
.\scripts\cabot.ps1 test
```

`doctor` 验证 Docker 服务、Linux 模式、目录挂载及容器内 ROBOT/OAK/SemSQL 版本。缺环境时返回失败，不回退为“通过”。公司策略若禁止 PowerShell 脚本，请由 IT 提供允许的执行方式，不修改全局执行策略。

## 2. Protégé 编辑与人工验收

```powershell
.\scripts\cabot.ps1 protege
```

也可运行 `.tools/Protege-5.6.9/run.bat` 后用 File → Open 打开 `src/ontology/scaudit-edit.owl`。使用发行包自带 JRE。不要打开 `build/native/inconsistent.owl` 当作正常示例。

人工检查并将真实结果记入 `docs/desktop-acceptance.md`：

1. Active Ontology 中核对 ontology IRI 和 `0.1.0-dev`；imports 中本地 metadata 依赖成功加载。
2. Entities → Classes 查看 Supplier → Organization；Annotations 查看 Supplier 的中英文 `rdfs:label`、定义和 Vendor 同义词。
3. Reasoner 选择 HermiT 并启动，确认无不一致或不可满足类。
4. 另开 `examples/owl/cabot-demo.owl`，确认 imports 使用同目录 catalog 定位主本体和 metadata。
5. Individuals 查看 `supplier_INV_017` 和 `cabot_INV_017`，金额分别为 5500 与 5000，指向同一 Invoice、不同 SourceDataset。
6. 查看 `Finding_INV017 → Evaluation_INV017 → REC-03 / Run_V100 / 两端观察`；查看 `Interpretation_INV017` 与 `Review_INV017`，人工决定为 NeedsEvidence。
7. 查看 `CreditAllocation_Test → Credit_Test / INV_017`，200 的分配及 600、400 的贷项数据，查看 `prov:wasDerivedFrom` 的合成来源。

命令行加载与推理已验证，但不代替以上桌面检查。本轮工具无法查看原生 Protégé 窗口，桌面记录保持待确认。

新增术语时，编辑主 OWL；类用 PascalCase，属性用 lowerCamelCase；保留已有 IRI，不能靠改 label 更换身份。补齐 en/zh 标签、英文规范定义、合适父类或属性 range，更新词汇表和必要测试，再运行 `test`。纯日期采用 `xsd:string` 的 `YYYY-MM-DD` 格式并由 Python 检查；时点采用 `xsd:dateTime`。这是为保持 OWL 2 DL，而非把不明时间补成午夜。

## 3. 构建入口

|命令|结果|前提|
|---|---|---|
|`scripts/cabot.ps1 doctor`|环境、挂载、工具版本检查|Docker Linux engine|
|`scripts/cabot.ps1 qc`|ODK test、HermiT、OWL 2 DL、元数据和数据约束|Docker|
|`scripts/cabot.ps1 build`|ODK 发布 OWL、官方 SemSQL 核心库与演示库、manifest|Docker|
|`scripts/cabot.ps1 test`|build、真实数据库 OAK 测试、逻辑反例、干净目录重建比较|Docker|
|`scripts/cabot.ps1 demo`|Finding 的规则、运行、观察、解释和人工审核关系|已经 build|
|`scripts/cabot.ps1 native-test`|本机诊断、OAK 命名三元组测试库、ROBOT/HermiT|本机 .venv 和 .tools|

官方流程的输出目录是 `build/releases/0.1.0-dev/`。`scaudit.owl` / `scaudit.db` 只含 schema、规则和词表；`scaudit-demo.owl` / `scaudit-demo.db` 另含合成实例。`manifest.json` 保存版本、commit（未提交时为空）、dirty 状态和散列。`acceptance.json` 只在完整自动测试成功后生成，桌面确认仍独立。

本机 `build/native/` 仅是诊断制品；`build/tests/*/TEST-ONLY-named-triples.db` 只加载命名三元组来验证真实 OAK SqlImplementation。它使用 SemSQL 官方 DDL，但不执行 rdftab/relation-graph、不保留匿名 OWL 公理，不是发布数据库，也不能证明官方 SemSQL 构建已通过。

正式发布门禁：在容器内 `make sca-formal-release` 必须因临时 namespace 失败。企业正式域名确认后需要一次统一迁移，修改 ontology IRI、prefix、catalog、构建配置、adapter 和测试并重新验收。普通开发构建不受此门禁影响；不配置远程发布。

## 4. OAK Python / CLI

容器中已通过 `PYTHONPATH=/work/src` 暴露项目包。Linux 的完整自动流程为 `sh scripts/ci.sh`；本地 Windows 使用上述 PowerShell 入口。

```python
from cabot_ontology.adapter import OntologyAdapter
a = OntologyAdapter('build/releases/0.1.0-dev/scaudit.db')
try:
    print(a.search_terms('Vendor', 'en'))
    print(a.get_term('sca:Supplier'))
    print(a.get_label('sca:Supplier', 'zh'))
    print(a.get_definition('sca:REC-03'))
    print(a.get_ancestors('sca:Supplier'))
    print(a.get_relationships('sca:Supplier'))
    print(a.validate_term_reference('sca:DoesNotExist'))  # False
finally:
    a.close()
```

```text
python -m cabot_ontology.cli build/releases/0.1.0-dev/scaudit.db search Vendor
python -m cabot_ontology.cli build/releases/0.1.0-dev/scaudit-demo.db evidence ex:Finding_INV017
```

完整 IRI 与 CURIE 都可输入。未知标识返回 `found=false`；不存在语言标签返回 None；同义词匹配返回候选，不能当作发票或供应商的身份判断。层级只遍历 `rdfs:subClassOf`。`get_relationships` 是 OAK 支持的命名关系视图，不是 OWL 全公理序列化接口；完整公理以发布 OWL 为准。

## 5. 常见问题

- `Docker is unavailable`：安装/启动 Docker 后重新打开终端，使 PATH 更新；不能用 native-test 结果替代容器验收。
- Import 找不到：检查打开文件旁边的 catalog 与相对路径，保留仓库目录结构；不要点击网络下载来掩盖缺失依赖。
- 日期触发 OWL 2 DL：纯日期使用项目定义的字符串格式，不改回 xsd:date。
- OAK 缺 prefix/version：确认使用本项目官方构建数据库，不是测试 fixture、空数据库或旧版本。
- Python cache 写权限错误：入口已把 `PYSTOW_HOME` 指向 `build/cache`。直接调用 Python 时也要设置该环境变量。
- 5500/5000 是冲突观察，不是 OWL 不一致。它们属于不同观察节点；不要在 Invoice 上用一个金额覆盖另一个。
- 3500 是净差额，5900 是四项差异绝对值合计。可追回金额未验证，不能把这两个数相加当作收益。

## 6. 版本与来源

固定 [ODK 1.6.1](https://github.com/INCATools/ontology-development-kit/releases/tag/v1.6.1) 与 [Protégé 5.6.9](https://github.com/protegeproject/protege-distribution/releases/tag/protege-5.6.9)。ODK 主 Makefile 由官方 seed 原样生成，项目扩展在 `scaudit.Makefile`；初始化实际在本机 Python 执行，不能称为容器初始化已验收。原 OneDrive 文件未修改，来源散列见 `docs/source-manifest.json`。
