---
name: agent-json
description: "agent.json 构建、校验与路径一致性"
---
# 生成 agent.json

## Overview
定义 agent.json 的构建流程、Schema 校验与路径一致性规则。

## 操作指南 / 工作流程
## 1. 构建与校验
- JSON 构建：基于 `src/AI生成AgentData代码参考/` 逻辑，利用 LLM 提取属性生成 `agent.json`
- Schema 校验：`src/validator.py` 校验 `AgentData_schema.json`

## 2. 配置修复与一致性
- 根级字段：`agentName`, `modelUrlSlim`, `modelUrlFat`, `modelUrlSymbols`
- 嵌套 `model` 字段：
  - `model.modelName` 与根级 `agentName` 一致
  - `model.thumbnail` 指向 `{ModelName}/{ModelName}.png`
  - `model.mapIconUrl` 指向 `{ModelName}/{ModelName}_mil.png`
  - `model.dimModelUrls` 指向 `{ModelName}/{ModelName}_AI_Rodin.glb`
- 路径格式：全部使用相对路径 `{ModelName}/{Filename}`
- 文件位置：`models/{ModelName}/agent.json`
- 数组包装：顶层必须是数组且仅 1 个对象

## Resources
- scripts/validator.py
- scripts/add_image_data.py
- scripts/choose_dynamics.py
- scripts/construct_lavicagent_data.py
- scripts/equipment_subgraph.py
- scripts/introduce_equipment.py
- scripts/submit_lavic_agent.py
