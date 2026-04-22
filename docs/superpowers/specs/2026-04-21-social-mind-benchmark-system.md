# 社会心智大模型 Benchmark 框架体系

## 摘要

本文档给出一套面向文本对话大模型的社会心智 benchmark 框架体系。该体系的目标不是评测模型是否掌握社会学或心理学学科知识，而是评测模型在社会情境中对场景结构、主体隐状态、社会机制、动态后果、规范边界与回应策略的综合建模能力。基于这一目标，体系采用六个一级维度构成的社会心智主轴，将 benchmark 分解为 taxonomy 层、数据资产层、标注与 rubric 层、验证层、响应记录层与报告层，形成从样本簇定义到诊断报告生成的闭环。当前体系已具备完整 taxonomy、结构化 schema、pilot 数据、自动化一致性校验与初步画像报告能力，可作为后续 benchmark 扩建、模型对比与风险审计的基础底座。

## 1. 问题定义

社会心智大模型的核心难点不在于回答有关社会的知识性问题，而在于能否在真实社会情境中维持稳定、可更新、可干预、受规范约束的社会状态表示。换言之，benchmark 需要评测的不是“模型知不知道某种社会理论”，而是：

1. 模型是否能识别当前互动是什么局
2. 模型是否能跟踪谁知道什么、误会什么、顾忌什么、试图达成什么
3. 模型是否能理解面子、信任、身份、权力、群体影响等机制如何推动局势演化
4. 模型是否能推演不同表达、披露和干预方式的社会后果
5. 模型是否能在真实性、尊重、公平、责任与伤害控制之间作出边界判断
6. 模型是否能把前述判断落成合宜回应

因此，本 benchmark 的问题对象是“社会情境中的心智化建模与约束性回应能力”，而非社会事实问答、道德表态或礼貌话术本身。

## 2. 设计目标与边界

### 2.1 设计目标

本体系同时服务于三类任务：

- 能力画像：识别模型在哪些社会心智能力上强、弱、失衡
- 横向比较：支持不同模型在结构化维度上的可解释比较
- 风险审计：识别模型在高风险社会互动中可能出现的误判、越界、操纵放大与关系损伤

### 2.2 非目标边界

本 benchmark 明确不以以下内容为核心评测对象：

- 社会学理论知识掌握程度
- 心理学术语记忆与概念背诵
- 泛化安全拒绝能力本身
- 单纯语言流畅度、礼貌度或所谓“高情商话术”

## 3. 理论与方法论基础

### 3.1 理论基础

本体系综合以下理论来源：

- Theory of Mind、多主体认知状态建模与视角采择
- 语用学、言语行为理论、会话分析
- 面子理论、印象管理、归因理论、社会身份理论
- 从众、群体极化、旁观者效应、社会比较等社会影响机制
- 规范理论、程序正义、互动正义与价值冲突理论
- 博弈论、因果推断与反事实推演

### 3.2 方法论迁移

体系显式借鉴物理世界模型评测中的以下思想：

- 隐状态一致性
- 部分可观测条件下的状态追踪
- 干预与 rollout
- 反事实推演
- 等信息对照
- 多尺度评测

其核心迁移逻辑是：物理世界模型中的对象状态与因果演化，在社会域中分别被映射为知识状态、动机状态、关系状态、规范状态与互动策略状态的演化。

## 4. 六维社会心智主轴

本 benchmark 采用六个一级评测维度：

1. 社会语境构型
2. 多主体心智建模
3. 社会机制理解
4. 社会动态推演
5. 规范与价值裁决
6. 社会回应生成

它们构成一条级联加工链：

`社会场景被表征 -> 多主体隐状态被建模 -> 社会机制被识别 -> 互动演化被推演 -> 规范边界被裁决 -> 具体回应被生成`

对应的核心问题依次是：

- 这是什么局
- 局里每个人各自怎么想
- 为什么会这样
- 接下来会怎样
- 应该怎样
- 具体怎么说

## 5. Taxonomy 体系

### 5.1 结构

benchmark 的机器可读 taxonomy 存储在：

- `benchmark/taxonomy/social_mind_dimensions.yaml`

该 taxonomy 与设计文档中的正式规范总表对齐，包含：

- 6 个一级维度
- 完整二级维度集合
- 完整三级维度集合
- 每个二级维度的主任务形式 `task_family`

### 5.2 Taxonomy Schema 与一致性检查

taxonomy 的结构约束由以下 schema 提供：

- `benchmark/schemas/taxonomy.schema.json`

当前一致性检查包括：

- taxonomy 顶层结构是否合法
- `dimensions` / `subdimensions` / `capabilities` 是否完整
- `task_family` 是否属于 `T1-T6`
- id 是否唯一
- cluster / template 中的 `primary_dimension` 是否存在于 taxonomy

## 6. 数据资产层

### 6.1 Sample Cluster

- schema: `benchmark/schemas/sample_cluster.schema.json`
- template: `benchmark/templates/sample_cluster_template.yaml`

它定义 benchmark 的基本题目簇结构，包括：

- `cluster_id`
- `title`
- `primary_dimension`
- `task_type`
- `base_scene`
- `latent_state`
- `items`

### 6.2 Pilot Gold Labels

- schema: `benchmark/schemas/pilot_gold_labels.schema.json`
- data: `benchmark/pilot/labels/pilot_gold_labels.yaml`

它定义 pilot 阶段的金标准标签，包括：

- `item_id`
- `dimension`
- `task_type`
- `minimum_required_elements`
- 可选的 state / normative / rollout / response / failure fields

### 6.3 Raw Responses 与 Scored Responses

- raw schema: `benchmark/schemas/model_response.schema.json`
- scored schema: `benchmark/schemas/scored_response.schema.json`
- scoring record schema: `benchmark/schemas/scoring_record.schema.json`

它们共同定义了从模型原始输出到结构化评分记录的资产契约。

当前评分值被离散化为：

- `0.0`
- `0.5`
- `1.0`

## 7. Rubric 与标注层

当前 benchmark 包含两类 rubric 资产：

- `benchmark/rubrics/judge_rubric.md`
- `benchmark/rubrics/human_annotation_guide.md`

其中：

- judge rubric 提供三轴评分：
  - `state_correctness`
  - `normative_judgment`
  - `response_quality`
- human annotation guide 提供主维度判定规则与歧义处理规则

## 8. 验证层

### 8.1 统一 validator

统一 validator 为：

- `scripts/validate_benchmark.py`

它当前校验：

- taxonomy YAML 是否符合 schema
- taxonomy id 是否唯一
- taxonomy `task_family` 是否合法
- sample cluster template 和 pilot clusters 是否符合 schema
- pilot gold labels 是否符合 schema
- pilot item 是否均有 gold label
- cluster / template 的 `primary_dimension` 是否存在于 taxonomy
- `responses/raw/*.yaml` 是否符合 raw response schema
- `responses/scored/*.yaml` 是否符合 scored response schema

### 8.2 自动化测试

当前测试覆盖三类能力：

- taxonomy 读取与摘要输出
- benchmark 资产 schema 与一致性校验
- 聚合与画像报告生成

测试文件包括：

- `tests/test_render_taxonomy_report.py`
- `tests/test_validate_benchmark.py`
- `tests/test_aggregate_reports.py`

## 9. 报告层

### 9.1 Taxonomy 摘要输出

- `scripts/render_taxonomy_report.py`

用于从 taxonomy YAML 生成 markdown 摘要。

### 9.2 画像与诊断报告生成

- `scripts/aggregate_reports.py`

当前支持：

- 从 `benchmark/responses/scored/` 读取 scored responses
- 生成一级维度画像
- 生成二级维度画像
- 生成风险摘要
- 生成失败模式摘要
- 使用 `pilot_gold_labels.yaml` 生成 label-informed failure reasons
- 生成 second-level failure buckets
- 输出到 stdout
- 可写入默认文件 `benchmark/reports/social_mind_profile.md`

## 10. Pilot 资产

当前 pilot benchmark 包含三组 cluster：

- `cluster_public_humiliation.yaml`
- `cluster_offer_negotiation.yaml`
- `cluster_group_escalation.yaml`

分别覆盖：

- 公开羞辱与体面边界
- 求职谈判中的诚实边界与约束保护
- 群体歧义批评下的升级路径推演

## 11. 数据流闭环

当前 benchmark 已具备以下闭环：

1. `taxonomy` 定义维度体系
2. `cluster` 定义样本簇
3. `gold labels` 定义最小正确性与常见失败模式
4. `raw responses` 记录模型回答
5. `scored responses` 记录结构化评分
6. `validator` 约束资产一致性
7. `aggregate_reports` 生成画像与诊断报告

这意味着当前 benchmark 已从“设计概念”进入“可校验、可记录、可聚合、可出报告”的原型系统阶段。

## 12. 当前完成度

从框架体系角度看，当前 benchmark 已完成：

- 设计层
- taxonomy 层
- schema 层
- pilot 数据层
- 校验层
- 报告层第一版

仍可增强但尚未完成的部分包括：

1. benchmark runner
2. 自动化打分流水线
3. 更细粒度的 failure clustering
4. 二级与三级维度更丰富的统计切片
5. 更大规模 benchmark 数据扩展

## 13. 建议阅读顺序

若要快速把握完整 benchmark 体系，建议按以下顺序阅读：

1. `docs/superpowers/specs/2026-04-21-social-mind-eval-design.md`
2. `docs/superpowers/specs/2026-04-21-social-mind-benchmark-system.md`
3. `benchmark/taxonomy/social_mind_dimensions.yaml`
4. `benchmark/schemas/*.json`
5. `benchmark/pilot/clusters/*.yaml`
6. `benchmark/pilot/labels/pilot_gold_labels.yaml`
7. `scripts/validate_benchmark.py`
8. `scripts/aggregate_reports.py`

## 14. 结论

当前社会心智 benchmark 已形成一个结构完整、机器可读、可校验、可扩展、可出诊断报告的原型框架体系。

它的关键价值不在于已经拥有大规模样本，而在于：

- 评测目标明确
- 维度体系完整
- 资产契约清晰
- 数据流闭环成立
- pilot 诊断能力已经具备雏形

因此，它已经可以作为后续 benchmark 扩建、模型对比、风险审计与报告生成的基础底座。
