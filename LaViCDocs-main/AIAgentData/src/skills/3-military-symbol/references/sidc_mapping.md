# SIDC 代码映射表 (Symbol Description Mapping)

> 基于 NATO APP-6(D) 标准，使用 `military-symbol` 库的文本描述接口。

## 空中平台 (Air)

| 中文名称 | Symbol Description | 典型型号 |
|----------|-------------------|----------|
| 友方固定翼军用飞机 | Friendly Fixed Wing Military Aircraft | F-22, Su-57, J-20 |
| 友方固定翼无人机 | Friendly Fixed Wing Unmanned Aerial Vehicle | CW-15, MQ-9 |
| 友方旋翼无人机 | Friendly Rotary Wing Unmanned Aerial Vehicle | DJI M300, EH216-S |
| 友方旋翼飞行器 | Friendly Rotary Wing Aircraft | 直升机类 |
| 友方预警机 | Friendly Airborne Early Warning Aircraft | KJ-500, E-2C |
| 敌方固定翼军用飞机 | Hostile Fixed Wing Military Aircraft | 对手战机 |
| 敌方固定翼无人机 | Hostile Fixed Wing Unmanned Aerial Vehicle | 对手无人机 |

## 地面平台 (Ground)

| 中文名称 | Symbol Description | 典型型号 |
|----------|-------------------|----------|
| 友方装甲战斗车辆 | Friendly Armoured Fighting Vehicle | JLTV, CSK181, MRZR |
| 友方货车 | Friendly Cargo Truck | M1083 |
| 友方导弹发射器 | Friendly Missile Launcher | DF-15 |
| 友方地面设施 | Friendly Installation | 充电桩, 塔台 |
| 友方地面车辆 | Friendly Ground Vehicle | 通用车辆 |

## 水面平台 (Surface)

| 中文名称 | Symbol Description | 典型型号 |
|----------|-------------------|----------|
| 友方水面战斗舰 | Friendly Surface Combatant | 驱逐舰, 护卫舰 |
| 友方航空母舰 | Friendly Carrier | 航母 |
| 友方巡逻艇 | Friendly Patrol Boat | 无人艇 |
| 敌方水面战斗舰 | Hostile Surface Combatant | 对手舰船 |

## 水下平台 (Subsurface)

| 中文名称 | Symbol Description | 典型型号 |
|----------|-------------------|----------|
| 友方潜航器 | Friendly Subsurface Unmanned Vehicle | UUV |
| 友方潜艇 | Friendly Submarine | 潜艇 |
| 敌方水雷 | Hostile Mine | 水雷 |

## 太空平台 (Space)

| 中文名称 | Symbol Description | 典型型号 |
|----------|-------------------|----------|
| 友方太空飞行器 | Friendly Space Vehicle | 卫星 |

## 导弹 (Missile)

| 中文名称 | Symbol Description | 典型型号 |
|----------|-------------------|----------|
| 友方防空导弹 | Friendly Surface to Air Missile | SM-3, HQ-9 |
| 友方反舰导弹 | Friendly Surface to Surface Missile | 反舰导弹 |
| 友方巡飞弹 | Friendly Unmanned Aerial Vehicle | 巡飞弹 |

## 使用说明

```python
import military_symbol

# 组合方式：{阵营} + {类型描述}
desc = "Friendly Fixed Wing Unmanned Aerial Vehicle"
svg = military_symbol.get_symbol_svg_string_from_name(
    desc, style='light', bounding_padding=4, use_variants=True
)
```

如果精确描述失败，逐级降级到更通用的描述。
