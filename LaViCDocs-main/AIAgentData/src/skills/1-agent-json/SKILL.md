---
name: agent-json
description: "当需要从自然语言描述构建 LaViC AgentData JSON、校验 agent.json 合法性、
  选择动力学类型、配置动作指令、或修复 JSON 字段映射时触发。
  也适用于需要查找 Agent 模板参考、理解 AgentData Schema 结构的场景。"
---

# Agent JSON — AgentData 构建与校验

## 1. Overview

本技能负责从自然语言描述中提取装备属性，构建符合 LaViC 标准的 `agent.json` 文件，并通过 Schema 校验确保其合法性。同时负责自动选择动力学类型和配置动作指令。

## 2. 触发条件

- 需要从自然语言描述生成 `agent.json`
- 需要校验现有 `agent.json` 是否符合 Schema
- 需要为装备选择正确的动力学类型
- 需要修复 `agent.json` 中的字段映射错误
- 需要查找某类装备的 Agent 模板参考

## 3. 核心工作流程

### 3.1 JSON 构建流程

```
自然语言描述
    │
    ▼
LLM 属性提取 ─────────────────┐
    │                          │
    ▼                          ▼
选择参考模板 (assets/)     选择动力学类型
    │                      (references/dynamics_catalog.md)
    ▼                          │
合并生成 agent.json ◀──────────┘
    │
    ▼
Schema 校验 (AgentData_schema.json, Draft-07)
    │
    ├─ 通过 → 输出 agent.json
    └─ 失败 → 报告错误，修复后重试
```

### 3.2 从描述中提取的关键属性

根据自然语言描述，LLM 需提取以下信息：

- **实体类型**：车辆/飞机/eVTOL/舰船/潜航器/导弹/卫星等
- **名称**：装备型号名称
- **性能参数**：最大速度、最小速度、最大加速度、最大角速度等
- **传感器配置**：视觉/雷达/激光雷达/电子侦察等
- **所属阵营**：友方/敌方/中立

## 4. 动力学类型选择

### 4.1 动力学目录（12 种）

| 动力学标识 | 适用实体 | 保真度 |
|-----------|---------|--------|
| `iagnt_dynamics_evtol_simple` | 旋翼机 / eVTOL | 低（任务导向） |
| `iagnt_dynamics_carrier_based_aircraft` | 舰载机 | 低（任务导向） |
| `iagnt_dynamics_refined_aircraft` | 精细化固定翼 | 低-中（工程级） |
| `iagnt_dynamics_vehicle_simple` | 车辆 | 极低（行为驱动） |
| `iagnt_dynamics_ship_simple` | 舰船 | 低（任务导向） |
| `iagnt_dynamics_submarine_simple` | 潜航器 | 低（任务导向） |
| `iagnt_dynamics_sgp4` | 卫星 (SGP4 轨道模型) | 中等 |
| `iagnt_dynamics_immobility` | 地面固定设备 | 极低 |
| `iagnt_dynamics_missile_targeting` | 无制导弹体 | 中高 |
| `iagnt_dynamics_pronav` | 有制导弹体（比例导引） | 中等 |
| `iagnt_dynamics_general_mainpath_follower` | 无人艇编队 | 中等 |
| `iagnt_dynamics_afsim_air_mover` | AFSim 兼容飞行器 | 外部集成 |
| `iagnt_dynamics_linear_trajectory` | 机器人 / 机器狗（开发中） | 低 |

### 4.2 自动选择逻辑

通过 `choose_dynamics.py`：
1. 从 LaViC API 获取可用动力学插件列表
2. 将装备描述和插件列表交给 LLM
3. LLM 返回最匹配的 `plugin_name`
4. 构建 `missionableDynamics` 对象写入 agent 数据

## 5. JSON 结构规范

### 5.1 顶层结构

```json
[
  {
    "agentName": "装备名称",
    "agentNameI18n": "装备名称",
    "agentType": "Instagent",
    "missionable": true,
    "modelUrlSlim": "{ModelName}/{ModelName}_AI_Rodin.glb",
    "modelUrlFat": "{ModelName}/{ModelName}_AI_Rodin.glb",
    "modelUrlSymbols": [...],
    "model": {...},
    "missionableDynamics": [...],
    "missionableActions": [...]
  }
]
```

**关键规则**：
- 顶层必须是**数组**，且仅包含 **1 个对象**
- 所有资源路径必须使用**相对路径** `"{ModelName}/{Filename}"`

### 5.2 字段映射规则（严格执行）

以下字段必须**全部更新**，严禁遗漏：

| 层级 | 字段 | 值 |
|------|------|-----|
| 根级 | `agentName` | 模型名称 |
| 根级 | `modelUrlSlim` | `{ModelName}/{ModelName}_AI_Rodin.glb` |
| 根级 | `modelUrlFat` | `{ModelName}/{ModelName}_AI_Rodin.glb` |
| 根级 | `modelUrlSymbols[0].symbolName` | `{ModelName}/{ModelName}_mil.png` (symbolSeries=1) |
| 根级 | `modelUrlSymbols[0].thumbnail` | `{ModelName}/{ModelName}.png` (symbolSeries=1) |
| 嵌套 | `model.modelName` | 与根级 `agentName` 一致 |
| 嵌套 | `model.thumbnail.url` | `{ModelName}/{ModelName}.png` |
| 嵌套 | `model.mapIconUrl.url` | `{ModelName}/{ModelName}_mil.png` |
| 嵌套 | `model.dimModelUrls[*].url` | `{ModelName}/{ModelName}_AI_Rodin.glb` |

### 5.3 modelUrlSymbols 结构

```json
"modelUrlSymbols": [
  {
    "symbolSeries": 1,
    "symbolName": "{ModelName}/{ModelName}_mil.png",
    "thumbnail": "{ModelName}/{ModelName}.png"
  }
]
```

**注意**：`symbolSeries=1` 中 `symbolName` 指向军标，`thumbnail` 指向缩略图。

## 6. Schema 校验

使用 `validator.py` 进行 JSON Schema Draft-07 校验：

```bash
python scripts/validator.py --schema references/AgentData_schema.json --data agent.json
```

校验通过输出 `✅ Data Validation Passed`，失败输出逐条错误路径和信息。

## 7. 参考模板（assets/）

`assets/` 目录下包含 **31 个参考模板**，覆盖所有实体类型：

| 文件 | 类型 | 动力学 |
|------|------|--------|
| `01vehicleAgent.json` | 车辆 | vehicle_simple |
| `02aircraftAgent.json` | 固定翼飞机 | carrier_based_aircraft |
| `03evtolAgent.json` | eVTOL | evtol_simple |
| `04underwaterVehicleAgent.json` | 潜航器 | submarine_simple |
| `05shipAgent.json` | 舰船 | ship_simple |
| `06loiterMunitionAgent.json` | 巡飞弹 | evtol_simple |
| `07missileAgent.json` | 导弹 | missile_targeting / pronav |
| `08boundingMineAgent.json` | 水雷 | submarine_simple |
| `09chargingStationAgent.json` | 充电桩 | immobility |
| `10satelliteAgent.json` | 卫星 | sgp4 |
| `11uuvFlockingAgent.json` | UUV 编队 | submarine_simple |
| `12mainpathFollwerAgent.json` | 无人艇编队 | general_mainpath_follower |
| `13AFSimAgent.json` | AFSim 飞行器 | afsim_air_mover |
| `14~19 fkfd*.json` | 防空反导想定 | 多种 |
| `20~23 wrtwl*.json` | 围猎想定 | 多种 |
| `24~27 slmh*.json` | 森林灭火想定 | 多种 |
| `28~31 csjkz*.json` | 超视距空战想定 | 多种 |

**使用方式**：根据用户描述的实体类型，选取最接近的模板作为基础，替换名称、参数和路径。

## 8. Scripts

| 脚本 | 功能 |
|------|------|
| `scripts/validator.py` | JSON Schema Draft-07 校验 |
| `scripts/fix_and_validate_json.py` | JSON 修复 + 校验一体化 |
| `scripts/choose_dynamics.py` | LLM 自动选择动力学类型 |

## 9. Resources

- `references/AgentData_schema.json` — JSON Schema 定义
- `references/dynamics_catalog.md` — 12 种动力学详细说明（来自 Excel）
- `references/field_mapping_rules.md` — 根级/嵌套字段映射规则
