---
name: military-symbol
description: "当需要为仿真模型生成 NATO APP-6(D) 标准军标 PNG、校验军标正确性、
  维护实体类型到 SIDC 代码的映射、或更新 agent.json 中的 modelUrlSymbols 字段时触发。"
---

# Military Symbol — NATO 军标生成

## 1. Overview

本技能负责为仿真模型生成符合 NATO APP-6(D) 标准的军事符号图标。军标用于 LaViC 平台的地图视图中标识实体类型和阵营。

**产出文件**：`{ModelName}_mil.png`

## 2. 触发条件

- 需要为新模型生成军标图标
- 需要校验现有军标的正确性
- 需要查找某类装备的 SIDC 代码
- 需要更新 `agent.json` 中的军标路径

## 3. 生成流程

```
实体类型 + 阵营
    │
    ▼
查询 SIDC 映射表 (references/sidc_mapping.md)
    │
    ▼
调用 military_symbol 库生成 SVG
    │
    ▼
SVG → PNG 转换 (svglib + reportlab)
    │
    ▼
输出 {ModelName}_mil.png
    │
    ▼
更新 agent.json 的 modelUrlSymbols
```

### 3.1 生成代码核心逻辑

```python
import military_symbol
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# 1. 根据实体描述生成 SVG
svg_string = military_symbol.get_symbol_svg_string_from_name(
    symbol_desc,           # 如 "Friendly Rotary Wing Unmanned Aerial Vehicle"
    style='light',         # 轻色风格
    bounding_padding=4,    # 边距
    use_variants=True      # 启用变体
)

# 2. 保存为临时 SVG
with open(svg_path, 'w', encoding='utf-8') as f:
    f.write(svg_string)

# 3. 转换为 PNG
drawing = svg2rlg(svg_path)
renderPM.drawToFile(drawing, png_path, fmt="PNG")
```

### 3.2 Fallback 机制

如果精确描述无法生成军标，逐级降级：

1. 尝试精确描述（如 `"Friendly Rotary Wing Unmanned Aerial Vehicle"`）
2. 降级到通用描述（如 `"Friendly Unmanned Aerial Vehicle"`）
3. 再降级到大类描述（如 `"Friendly Ground Vehicle"`）

## 4. SIDC 代码映射

### 4.1 常用实体类型映射

| 实体类型 | Symbol Description | 阵营示例 |
|----------|-------------------|----------|
| 多旋翼无人机 | Rotary Wing Unmanned Aerial Vehicle | Friendly / Hostile |
| 固定翼无人机 | Fixed Wing Unmanned Aerial Vehicle | Friendly / Hostile |
| 舰载机 | Fixed Wing Military Aircraft | Friendly / Hostile |
| 装甲车 | Armoured Fighting Vehicle | Friendly / Hostile |
| 货车 | Cargo Truck | Friendly |
| 导弹发射器 | Missile Launcher | Friendly / Hostile |
| 军舰 | Surface Combatant | Friendly / Hostile |
| 航空母舰 | Carrier | Friendly |
| 潜航器 | Subsurface Unmanned Vehicle | Friendly / Hostile |
| 卫星 | Space Vehicle | Friendly |
| 地面设施 | Installation | Friendly |
| 水雷 | Mine | Hostile |

### 4.2 阵营前缀

| 阵营 | 前缀 | 颜色 |
|------|------|------|
| 友方 (Friendly) | `Friendly` | 蓝色 |
| 敌方 (Hostile) | `Hostile` | 红色 |
| 中立 (Neutral) | `Neutral` | 绿色 |
| 未知 (Unknown) | `Unknown` | 黄色 |

### 4.3 组合示例

```
"Friendly Rotary Wing Unmanned Aerial Vehicle"    → 友方多旋翼无人机
"Hostile Fixed Wing Military Aircraft"             → 敌方固定翼战机
"Friendly Surface Combatant"                       → 友方水面战斗舰
"Friendly Armoured Fighting Vehicle"               → 友方装甲战斗车辆
```

## 5. 命名规范

| 项目 | 规范 |
|------|------|
| 文件名 | `{ModelName}_mil.png` |
| 格式 | PNG |
| 用途 | 地图图标标识（mapIconUrl） |
| 禁止 | **严禁用作缩略图** |

## 6. agent.json 更新

生成军标后，必须更新 `agent.json`：

```json
"modelUrlSymbols": [
  {
    "symbolSeries": 1,
    "symbolName": "{ModelName}/{ModelName}_mil.png",
    "thumbnail": "{ModelName}/{ModelName}.png"
  }
]
```

同时更新嵌套字段：

```json
"model": {
  "mapIconUrl": {
    "url": "{ModelName}/{ModelName}_mil.png",
    "ossSig": "{ModelName}_mil.png"
  }
}
```

## 7. 关键依赖

| 库 | 用途 | 安装 |
|----|------|------|
| `military-symbol` | 根据描述生成 NATO APP-6D 军标 SVG | `pip install military-symbol` |
| `svglib` | SVG 解析 | `pip install svglib` |
| `reportlab` | SVG → PNG 渲染 | `pip install reportlab` |

## 8. Scripts

| 脚本 | 功能 |
|------|------|
| `scripts/gen_mil_symbols.py` | 批量生成军标（SVG → PNG）并更新 agent.json |
| `scripts/check_mil_symbol.py` | 校验军标文件是否存在且有效 |
| `scripts/check_mil_sig.py` | 校验军标签名一致性 |

## 9. Resources

- `references/sidc_mapping.md` — 完整的实体类型→Symbol Description 映射表
