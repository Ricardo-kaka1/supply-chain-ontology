# 变更规范

1. 每项业务含义变化记录需求、业务 owner 和来源；ASSUMPTION 不能伪装为已批准政策。
2. 编辑主 OWL；核心术语补齐 en/zh 标签及定义，新增关系明确方向和适用场景。
3. 保留稳定 IRI；废弃用 owl:deprecated 并记录替代关系，不能复用旧标识表示新含义。
4. 同步相关例子、映射和测试；正式发布前迁移临时 namespace。
5. 保留 ODK 主 Makefile，扩展放 scaudit.Makefile；配置更新使用官方 generator 并保存版本和散列。
6. 执行 Docker test；未执行的检查保持未完成。Protégé 桌面操作另行记录。
7. 配置自己的 Git author 后本地提交；未来由业务 owner 和本体 owner 评审。当前不推送远程。
8. 不提交真实财务数据、缓存、数据库、工具包或凭证；合成数据须有标识及来源。
