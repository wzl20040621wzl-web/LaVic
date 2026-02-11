---
name: packaging
description: "UTF-8 扁平化 ZIP 打包规则"
---
# UTF-8 扁平化 ZIP 打包

## Overview
定义模型包的目录结构、文件清单与 UTF-8 扁平化打包要求。

## 操作指南 / 工作流程
## 1. 目录结构
```
models/
├── {ModelName}/
│   ├── agent.json
│   └── {ModelName}/
│       ├── {ModelName}.png
│       ├── {ModelName}_mil.png
│       └── {ModelName}_AI_Rodin.glb
└── {ModelName}.zip
```

## 2. 文件清单要求
- `{ModelName}/` 目录仅包含 `agent.json` 与资源子目录
- 资源子目录仅包含 3 个核心文件：缩略图、军标、GLB
- 任何导出残留文件必须删除后再打包
- ZIP 位于 `models/` 根目录

## 3. 打包要求
- 工具：`src/zip_models.py`（被 `src/fix_and_zip_models.py` 调用）
- 格式：`.zip`
- 编码：UTF-8（支持中文文件名）
- 结构：扁平化
  - 错误：ZIP -> `{ModelName}/` -> `agent.json`
  - 正确：ZIP -> `agent.json`, `{ModelName}/`（资源文件夹）
- 内容最小集：`agent.json` 与 `{ModelName}/` 下的 3 个资源文件
- 产物：`models/{ModelName}.zip`

## 4. 打包前强校验
- 缩略图路径不得为 `*_mil.png`
- 必须完成缩略图一致性校验
- `thumbnail` 与 `mapIconUrl` 分工明确

## Resources
- scripts/zip_models.py
- scripts/fix_and_zip_models.py
