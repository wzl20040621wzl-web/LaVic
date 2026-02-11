# 打包前完整校验清单

> 以下所有项目必须全部通过，任一不通过则拒绝打包。

## JSON 配置校验

- [ ] `agent.json` 顶层为数组 `[...]`
- [ ] 数组仅包含 1 个对象
- [ ] `agentName` 已正确设置
- [ ] `modelUrlSlim` = `{ModelName}/{ModelName}_AI_Rodin.glb`
- [ ] `modelUrlFat` = `{ModelName}/{ModelName}_AI_Rodin.glb`
- [ ] `model.modelName` 与 `agentName` 一致
- [ ] `model.thumbnail.url` = `{ModelName}/{ModelName}.png`
- [ ] `model.mapIconUrl.url` = `{ModelName}/{ModelName}_mil.png`
- [ ] `model.dimModelUrls[*].url` = `{ModelName}/{ModelName}_AI_Rodin.glb`
- [ ] `modelUrlSymbols` 包含 `symbolSeries=1` 条目
- [ ] `symbolSeries=1` 的 `symbolName` 指向 `_mil.png`
- [ ] `symbolSeries=1` 的 `thumbnail` 指向 `.png`（非 `_mil.png`）

## 资源文件校验

- [ ] `{ModelName}.png` 存在且非军标图
- [ ] `{ModelName}_mil.png` 存在
- [ ] `{ModelName}_AI_Rodin.glb` 存在
- [ ] 资源子目录内无残留文件

## 缩略图校验

- [ ] 缩略图路径不为 `*_mil.png`
- [ ] 缩略图与 3D 模型一致性校验通过（三项指标满足两项）
- [ ] 缩略图与现有模型去重通过

## 路径格式校验

- [ ] 所有路径为相对格式 `{ModelName}/{Filename}`
- [ ] 无绝对路径
- [ ] 无 `models/` 前缀
- [ ] `agent.json` 位于正确层级（不在资源子目录内）

## 打包结构校验

- [ ] ZIP 输出在 `models/` 根目录
- [ ] ZIP 内为扁平化结构（agent.json 在 ZIP 根目录）
- [ ] ZIP 内仅 4 个条目
- [ ] ZIP 编码为 UTF-8
