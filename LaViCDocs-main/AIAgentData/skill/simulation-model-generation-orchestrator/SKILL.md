---
name: simulation-model-generation-orchestrator
description: "全流程编排、执行顺序与失败回退"
---
# Simulation Model Generation Orchestrator

## Overview
从自然语言描述到标准模型包的总控流程与执行约束。

## 操作指南 / 工作流程
### 1. 目标与输出
- 目标：从自然语言描述生成可导入 LaViC 的标准模型包
- 输入：自然语言描述、ModelName
- 输出：`models/{ModelName}.zip`

### 2. 文件清单与职责
- 3D 建模：skill.3d-model.md
- 缩略图：skill.thumbnail.md
- 军标：skill.military-symbol.md
- 生成 agent.json：skill.agent-json.md
- UTF-8 扁平化打包：skill.packaging.md

### 3. 严格执行顺序
1. 3D 建模
2. 缩略图
3. 军标
4. 生成 agent.json
5. UTF-8 扁平化 ZIP 打包

### 4. 共享命名与路径规则
- 缩略图：`{ModelName}.png`
- 军标：`{ModelName}_mil.png`
- 3D 模型：`{ModelName}_AI_Rodin.glb`
- 相对路径统一格式：`{ModelName}/{Filename}`
- agent.json 位置：`models/{ModelName}/agent.json`
- ZIP 产物：`models/{ModelName}.zip`

### 5. 失败回退策略
- 任一校验失败即停止打包
- 3D 质量失败：重生成或更换来源
- 缩略图一致性/去重失败：更换图片或离线渲染替换
- agent.json 校验失败：修复字段与路径后再校验

### 6. 自动化入口
- `src/fix_and_zip_models.py` 可作为总控入口执行修复与打包

### 7. 核心脚本工具箱
| 脚本文件                           | 功能描述                          | 关键依赖                       |
| :--------------------------------- | :-------------------------------- | :----------------------------- |
| `src/validator.py`                 | 校验 `agent.json` 结构合法性      | `jsonschema`                   |
| `src/gen_mil_symbols.py`           | 生成 APP-6D 标准军标 PNG          | `military-symbol`, `reportlab` |
| `src/process_glbs.py`              | 批量调整 GLB 坐标轴 (Y-Up)        | `bpy` (Blender API)            |
| `src/rotate_glbs_z180.py`          | 批量调整 GLB 朝向 (Rotate 180)    | `bpy` (Blender API)            |
| `src/fix_and_zip_models.py`        | 批量修复 JSON 路径并打包          | `src/zip_models.py`            |
| `src/zip_models.py`                | 创建 UTF-8 编码的扁平化 ZIP       | `zipfile`                      |
| `src/generate_vehicle_packages.py` | 批量生成车辆模型包 (Orchestrator) | `pandas`, `military_symbol`    |
| `src/fetch_images.py`              | 自动获取参考图片                  | `requests`                     |
| `src/check_and_convert_images.py`  | 图片格式检查与转换 (RGB PNG)      | `Pillow`                       |
| `src/blender_mcp_addon.py`         | Blender MCP 插件 (Hyper3D 集成)   | `bpy`, `requests`              |

### 8. 扩展指南
若要支持新类型模型（如潜艇）：
1. 在 agent.json 中选择正确 `agentType` 与 `dynamics`
2. 在 `gen_mil_symbols.py` 中添加对应 SIDC 映射
3. 获取 GLB 并按 3D 规则修正坐标
4. 运行 `python src/fix_and_zip_models.py` 完成修复与打包

### 9. 快速校验清单
- 3D 建模：质量门槛与坐标修正通过
- 缩略图：一致性与去重校验通过
- 军标：命名正确且 APP-6(D) 规范
- agent.json：Schema 校验通过，路径一致
- 打包：UTF-8 扁平化结构与最小条目集通过

## Resources
- scripts/validator.py
- scripts/gen_mil_symbols.py
- scripts/process_glbs.py
- scripts/rotate_glbs_z180.py
- scripts/fix_and_zip_models.py
- scripts/zip_models.py
- scripts/generate_vehicle_packages.py
- scripts/fetch_images.py
- scripts/check_and_convert_images.py
- scripts/blender_mcp_addon.py
