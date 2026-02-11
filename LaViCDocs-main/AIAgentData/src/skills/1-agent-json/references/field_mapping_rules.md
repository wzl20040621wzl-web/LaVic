# agent.json 字段映射规则

> **[严格执行]** 以下所有字段必须全部更新，严禁遗漏任何一项。

## 1. 根级字段

| 字段 | 值 | 说明 |
|------|-----|------|
| `agentName` | `{ModelName}` | 模型名称 |
| `agentNameI18n` | `{ModelName}` | 国际化名称（通常与 agentName 相同） |
| `agentType` | `"Instagent"` | 固定值 |
| `missionable` | `true` | 是否可执行任务 |
| `modelUrlSlim` | `{ModelName}/{ModelName}_AI_Rodin.glb` | 轻量 3D 模型路径 |
| `modelUrlFat` | `{ModelName}/{ModelName}_AI_Rodin.glb` | 高精度 3D 模型路径 |

## 2. modelUrlSymbols 数组

```json
"modelUrlSymbols": [
  {
    "symbolSeries": 1,
    "symbolName": "{ModelName}/{ModelName}_mil.png",
    "thumbnail": "{ModelName}/{ModelName}.png"
  }
]
```

**注意**：
- `symbolSeries=1`：`symbolName` 指向军标 `_mil.png`，`thumbnail` 指向缩略图 `.png`
- 仅保留 `symbolSeries=1` 即可

## 3. 嵌套 model 对象（关键）

以下字段**不可保留模板默认值**，必须与根级保持一致：

| 字段路径 | 值 |
|----------|-----|
| `model.modelName` | `{ModelName}`（与根级 `agentName` 一致） |
| `model.thumbnail.url` | `{ModelName}/{ModelName}.png` |
| `model.thumbnail.ossSig` | `{ModelName}.png` |
| `model.mapIconUrl.url` | `{ModelName}/{ModelName}_mil.png` |
| `model.mapIconUrl.ossSig` | `{ModelName}_mil.png` |
| `model.dimModelUrls[*].url` | `{ModelName}/{ModelName}_AI_Rodin.glb` |
| `model.dimModelUrls[*].ossSig` | `{ModelName}_AI_Rodin.glb` |

## 4. 路径格式规范

- 所有资源引用必须使用**相对路径**：`"{ModelName}/{Filename}"`
- 禁止使用绝对路径或带 `models/` 前缀的路径
- `agent.json` 必须位于 `models/{ModelName}/agent.json`，不得放入资源子目录

## 5. 数组包装

`agent.json` 顶层必须是**数组**，且仅包含 **1 个对象**：

```json
[
  {
    "agentName": "...",
    ...
  }
]
```

## 6. 常见错误

| 错误 | 正确做法 |
|------|----------|
| 顶层是对象而非数组 | 用 `[...]` 包裹 |
| `model.modelName` 保留模板值 | 替换为当前模型名 |
| `model.thumbnail` 指向 `_mil.png` | 指向 `{ModelName}.png` |
| `modelUrlSlim` 含绝对路径 | 使用相对路径 `{ModelName}/...` |
| `modelUrlSymbols` 中 thumbnail 和 symbolName 互换 | symbolName=军标, thumbnail=缩略图 |
