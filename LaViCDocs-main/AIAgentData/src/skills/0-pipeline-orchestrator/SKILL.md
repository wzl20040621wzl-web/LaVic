---
name: pipeline-orchestrator
description: "当需要执行完整的 'One Prompt to Simulation Model' 流水线、
  从自然语言描述生成可导入 LaViC 系统的标准 ZIP 包、编排多个子技能协同工作、
  或通过 LangGraph 自动化批量创建仿真模型时触发。"
---

# Pipeline Orchestrator — 仿真模型生成流水线编排器

## 1. Overview

本技能是整条 **"One Prompt to Simulation Model"** 流水线的总调度器。它将用户的自然语言描述转化为一个可直接导入 LaViC 仿真系统的标准 `.zip` 资产包，通过串联调用以下 5 个子技能完成全流程：

```
用户输入 (自然语言)
    │
    ├─① agent-json          构建 agent.json + 选择动力学 + Schema 校验
    ├─② thumbnail            搜索/优选/下载缩略图
    ├─③ military-symbol      生成 NATO APP-6D 军标
    ├─④ 3d-model             获取/修正/校验 3D GLB 模型
    └─⑤ zip-packaging        目录组装 + 路径修复 + 打包 ZIP
         │
         ▼
    {ModelName}.zip  ← 可直接导入 LaViC
```

## 2. 触发条件

满足以下任一条件时使用本技能：

- 用户要求"生成一个仿真模型"或类似完整流水线请求
- 需要从零开始创建 LaViC 模型资产包
- 需要批量生成多个模型（车辆/战斗机/航母/eVTOL 等）
- 需要通过 LangGraph 工作流自动化创建模型

## 3. 标准流水线 (Standard Pipeline)

### 3.1 单模型生成流程

按以下顺序依次调用子技能，每一步的输出作为下一步的输入：

| 步骤 | 子技能 | 输入 | 输出 | 失败处理 |
|------|--------|------|------|----------|
| ① | `agent-json` | 自然语言描述 | `agent.json` | 终止并报错 |
| ② | `thumbnail` | 模型名称 + 类型 | `{ModelName}.png` | 使用 GLB 离线渲染兜底 |
| ③ | `military-symbol` | 实体类型 | `{ModelName}_mil.png` | 终止并报错 |
| ④ | `3d-model` | 模型名称 + 参考图 | `{ModelName}_AI_Rodin.glb` | 回退重生成 |
| ⑤ | `zip-packaging` | 上述全部产物 | `{ModelName}.zip` | 拒绝打包并报告原因 |

### 3.2 步骤间校验关卡

- **②→④ 之间**：缩略图与 3D 模型一致性校验（SSIM / 边缘 IoU / 颜色直方图，三项满足两项即通过）
- **④→⑤ 之前**：3D 模型质量门控（结构完整性、细节复杂度、真实性）
- **⑤ 打包前**：缩略图路径非 `*_mil.png`、所有资源路径引用一致

### 3.3 最终产物规范

```text
models/
├── {ModelName}/
│   ├── agent.json                    ← 顶层数组，仅含 1 个对象
│   └── {ModelName}/
│       ├── {ModelName}.png           ← 缩略图
│       ├── {ModelName}_mil.png       ← 军标
│       └── {ModelName}_AI_Rodin.glb  ← 3D 模型
└── {ModelName}.zip                   ← UTF-8 编码，扁平化结构
```

## 4. LangGraph 工作流

### 4.1 V1 基础工作流

```
introduce_equipment → construct_lavicagent_data → add_image_data → choose_dynamics → submit_lavic_agent → END
```

### 4.2 V2 增强工作流

```
search_equipment_info → construct_lavicagent_data → add_image_data → text_to_model → choose_dynamics
    → check_equipment_exists → [条件分支]
        ├─ 已存在 → add_actions → submit_lavic_agent → END
        └─ 不存在 → submit_lavic_agent → END
```

### 4.3 状态定义

```python
class EquipmentSubgraphState(TypedDict):
    messages: List[BaseMessage]           # 流程消息链
    current_equipment: str                # 当前处理的装备名称
    equipment_introductions: List[Dict]   # 装备介绍信息
    lavicagent_data: LavicAgentData       # LaViC Agent 数据
    auth_token: str                       # LaViC API 认证令牌
    tenant_id: str                        # 租户 ID
    agent_keys: List[AgentEntry]          # 已创建的 Agent 键列表
```

## 5. 批量生产模式

### 5.1 已有批量编排脚本

| 脚本 | 用途 |
|------|------|
| `generate_vehicle_packages.py` | 车辆模型批量生成（从 Excel 读取参数） |
| `gen_fighter_packages.py` | 战斗机模型批量生成 |
| `gen_carrier_packages.py` | 航母模型批量生成 |
| `gen_sm3_pipeline.py` | SM-3 导弹生成流水线 |
| `generate_evtol_agents.py` | eVTOL Agent 批量生成 |

### 5.2 仿真运行时数据注入

通过 `exec.py` 向仿真引擎（端口 18087）注入数据：

```python
POST /AgentData          ← 实体定义 (agentdata_*.json)
POST /RuntimeData        ← 行为模式 (patterndata_*.json)
POST /DoctrinesConfig    ← 条令配置 (doc.json)
POST /ExperimentConfig   ← 实验配置 (ExperimentConfig.json)
```

## 6. LaViC API 交互

```
# 获取动力学插件列表
GET /api/v1/lavic-core/getPluginByType?pluginType=dynamics

# 提交创建模型
POST /api/v1/lavic-core/saveAgent?isGitLab=false
```

## 7. 扩展新类型

1. **agent-json**：确保 `agentType` 和 `dynamics` 选择正确
2. **military-symbol**：添加对应 SIDC 代码映射
3. **3d-model**：获取 GLB 并执行坐标修正
4. **zip-packaging**：运行打包流程

## 8. Scripts

- `scripts/equipment_subgraph.py` — LangGraph 工作流定义
- `scripts/construct_lavicagent_data.py` — 构建仿真模型基础数据
- `scripts/introduce_equipment.py` — LLM 生成装备介绍
- `scripts/submit_lavic_agent.py` — 提交模型到 LaViC API
- `scripts/exec.py` — 仿真运行时数据注入
