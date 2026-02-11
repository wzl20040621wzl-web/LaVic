---
name: zip-packaging
description: "当需要将 agent.json 和资源文件打包为 LaViC 标准 ZIP 包、
  组装目录结构、修复 JSON 中的资源路径引用、执行打包前强校验、
  或检查已有 ZIP 包结构是否合规时触发。"
---

# ZIP Packaging — 最终打包

## 1. Overview

本技能负责将 `agent.json` 和三个资源文件（缩略图、军标、GLB）组装为符合 LaViC 标准的 ZIP 包。打包前执行严格的路径校验和一致性检查。

**产出文件**：`{ModelName}.zip`

## 2. 触发条件

- 需要将生成的模型资产打包为 ZIP
- 需要修复 agent.json 中的资源路径引用
- 需要检查现有 ZIP 包的结构是否合规
- 打包过程中遇到校验失败需要排查

## 3. 目录结构规范

### 3.1 工作目录结构

```text
models/
├── {ModelName}/                 ← 模型工作目录
│   ├── agent.json               ← 必须在此层级，不可放入子目录
│   └── {ModelName}/             ← 资源子目录
│       ├── {ModelName}.png          ← 缩略图
│       ├── {ModelName}_mil.png      ← 军标
│       └── {ModelName}_AI_Rodin.glb ← 3D 模型
└── {ModelName}.zip              ← ZIP 输出位置（models/ 根目录）
```

### 3.2 ZIP 内部结构（扁平化）

```text
{ModelName}.zip
├── agent.json                   ← 直接在 ZIP 根目录
└── {ModelName}/                 ← 资源子目录
    ├── {ModelName}.png
    ├── {ModelName}_mil.png
    └── {ModelName}_AI_Rodin.glb
```

**正确**：ZIP 根目录直接包含 `agent.json` 和 `{ModelName}/` 文件夹。

**错误**：ZIP 根目录是 `{ModelName}/`，里面再包含 `agent.json`（多了一层嵌套）。

### 3.3 内容最小集

ZIP 内有且仅有 **4 个条目**：

| 条目 | 说明 |
|------|------|
| `agent.json` | 模型配置文件 |
| `{ModelName}/{ModelName}.png` | 缩略图 |
| `{ModelName}/{ModelName}_mil.png` | 军标 |
| `{ModelName}/{ModelName}_AI_Rodin.glb` | 3D 模型 |

**必须删除**的残留文件：
- `external.*`
- `materials.*`
- `*_NML.png`
- 任何非上述 4 个条目的文件

## 4. JSON 路径修复流程

### 4.1 必须更新的字段

打包前，`fix_and_zip_models.py` 会自动修复以下字段：

**根级字段**：
```json
{
  "modelUrlSlim": "{ModelName}/{ModelName}_AI_Rodin.glb",
  "modelUrlFat": "{ModelName}/{ModelName}_AI_Rodin.glb"
}
```

**modelUrlSymbols**：
```json
"modelUrlSymbols": [
  {
    "symbolSeries": 1,
    "symbolName": "{ModelName}/{ModelName}_mil.png",
    "thumbnail": "{ModelName}/{ModelName}.png"
  }
]
```

**嵌套 model 对象**：
```json
"model": {
  "modelName": "{ModelName}",
  "thumbnail": {
    "url": "{ModelName}/{ModelName}.png",
    "ossSig": "{ModelName}.png"
  },
  "mapIconUrl": {
    "url": "{ModelName}/{ModelName}_mil.png",
    "ossSig": "{ModelName}_mil.png"
  },
  "dimModelUrls": [{
    "url": "{ModelName}/{ModelName}_AI_Rodin.glb",
    "ossSig": "{ModelName}_AI_Rodin.glb"
  }]
}
```

### 4.2 路径格式

- 所有路径使用**相对格式**：`"{ModelName}/{Filename}"`
- 禁止绝对路径
- 禁止 `models/` 前缀

## 5. 打包前强校验

### 5.1 校验清单

打包前必须通过以下所有检查，任一不通过则**拒绝打包**：

| 序号 | 检查项 | 规则 |
|------|--------|------|
| 1 | 缩略图路径 | 不得为 `*_mil.png` |
| 2 | 缩略图一致性 | 必须通过与 GLB 渲染图的一致性校验 |
| 3 | thumbnail vs mapIconUrl | 分工明确，不可混用 |
| 4 | 资源文件存在性 | 所有引用的文件必须实际存在 |
| 5 | JSON 顶层结构 | 必须是数组，且仅含 1 个对象 |
| 6 | 路径一致性 | 根级与 model 内部路径完全一致 |
| 7 | 无残留文件 | 资源子目录仅含 3 个文件 |

### 5.2 深度路径检查

使用 `deep_check_paths.py` 检查所有路径引用的一致性：

```bash
python scripts/deep_check_paths.py models/{ModelName}/agent.json
```

## 6. ZIP 创建

### 6.1 编码要求

- **UTF-8** 编码（必须支持中文文件名）
- Python `zipfile` 模块默认对非 ASCII 文件名使用 UTF-8

### 6.2 创建代码

```python
import os
import zipfile

def zip_model(model_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(model_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # 相对路径 = 相对于模型目录（扁平化）
                arcname = os.path.relpath(file_path, model_dir)
                zipf.write(file_path, arcname=arcname)
```

### 6.3 输出位置

ZIP 必须放在 `models/` 根目录：`models/{ModelName}.zip`

**禁止**放在 `models/{ModelName}/` 内部。

## 7. 完整打包流程

```
1. 检查工作目录结构是否规范
2. 删除残留文件
3. 执行 JSON 路径修复 (fix_and_zip_models.py)
4. 执行打包前强校验
5. 创建 ZIP (zip_models.py)
6. 验证 ZIP 内容（可选）
```

## 8. 快速校验清单 (Quick Checklist)

**JSON 配置**：
- 顶层为数组且仅 1 个对象
- 根级 `thumbnail` → `{ModelName}/{ModelName}.png`
- 根级 `modelUrlSlim/Fat` → `{ModelName}/{ModelName}_AI_Rodin.glb`
- `model` 内部的 `modelName/thumbnail/mapIconUrl/dimModelUrls` 与根级一致
- `modelUrlSymbols` 中 `symbolSeries=1`，`symbolName` → `_mil.png`

**GLB 姿态**：
- 坐标系：X -90° 后 Y 180°（Y-Up，机头朝 Y+）
- 位置：中心在原点，最低点 Z=0
- 几何：必要时合并为单一网格

**打包结构**：
- ZIP 内仅 4 项
- 路径为相对格式

## 9. Scripts

| 脚本 | 功能 |
|------|------|
| `scripts/zip_models.py` | 创建 UTF-8 编码的扁平化 ZIP |
| `scripts/fix_and_zip_models.py` | 修复 JSON 路径 + 打包一体化 |
| `scripts/deep_check_paths.py` | 深度检查所有资源路径引用的一致性 |

## 10. Resources

- `references/directory_structure.md` — 目录结构规范图解
- `references/pre_packaging_checklist.md` — 打包前完整校验清单
