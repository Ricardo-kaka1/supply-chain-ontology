# 本地外部术语桥接

metadata.owl 只声明所复用的外部术语类型，不复制完整 SKOS、PROV 或 IAO 本体，不声明具有完整外部语义。
这样正常编辑、推理与构建可以离线加载。业务限制由本项目公理和数据契约提供。

来源：https://www.w3.org/TR/skos-reference/ ，https://www.w3.org/TR/prov-o/ ，http://purl.obolibrary.org/obo/IAO_0000115
更改该模块必须更新 config/toolchain.lock.json 中散列并重新执行完整验收。
