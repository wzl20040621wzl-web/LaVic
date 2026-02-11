---
name: simulation-model-generation-pipeline
description: "流程入口与步骤索引"
---

# Simulation Model Generation & Packaging Pipeline (NLP to ZIP)

## Overview

本文件作为入口与索引，串联仿真模型生成与打包流程。

## 操作指南 / 工作流程

本文件作为入口与索引，详细规则拆分到以下文件。

### 文件清单

- 0. 总控与全局规则：skill.orchestrator.md
- 1. 3D 建模：skill.3d-model.md
- 2. 缩略图：skill.thumbnail.md
- 3. 军标：skill.military-symbol.md
- 4. 生成 agent.json：skill.agent-json.md
- 5. UTF-8 扁平化 ZIP 打包：skill.packaging.md

### 执行顺序

3D 建模 → 缩略图 → 军标 → 生成 agent.json → UTF-8 扁平化 ZIP 打包

## Resources

- ../simulation-model-generation-orchestrator/SKILL.md
- ../3d-model/SKILL.md
- ../thumbnail/SKILL.md
- ../military-symbol/SKILL.md
- ../agent-json/SKILL.md
- ../packaging/SKILL.md
