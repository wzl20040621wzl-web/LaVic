---
name: 3d-model
description: "当需要获取或生成 3D GLB 模型、执行坐标轴修正(Z-Up→Y-Up)、
  朝向修正(Y轴180°)、3D模型质量校验、真实性校验、
  或排查3D模型在平台中不可见的问题时触发。"
---

# 3D Model — 3D 模型获取与标准化

## 1. Overview

本技能负责获取或生成 3D GLB 模型，并对其进行坐标系修正、朝向修正、质量校验，确保模型在 LaViC 平台（Y-Up 坐标系）中姿态正确且可见。

**产出文件**：`{ModelName}_AI_Rodin.glb`

## 2. 触发条件

- 需要为新模型获取或生成 3D GLB
- 需要修正 GLB 的坐标系（Z-Up → Y-Up）
- 需要修正 GLB 的朝向（机头方向）
- 需要校验 3D 模型的质量（结构/细节/真实性）
- 3D 模型在平台中不可见，需要排查

## 3. 模型来源

| 来源 | 方式 | 质量 |
|------|------|------|
| Rodin (AI) | 通过 Blender MCP 插件调用 Hyper3D Rodin API | 中-高 |
| Blender | 手动建模或从模型库导入 | 高 |
| 现有库 | 从已有 GLB 库中选取 | 视来源而定 |

## 4. 坐标轴与朝向修正（严格执行，不可省略）

### 4.1 修正逻辑（必须按顺序执行）

```
原始 GLB (通常 Z-Up)
    │
    ▼ 步骤1：绕 X 轴旋转 -90°  (Z-Up → Y-Up)
    │
    ▼ 步骤2：绕 Y 轴旋转 180°  (朝向修正，机头朝 Y+)
    │
    ▼
最终 GLB (Y-Up, 机头朝 Y+)
```

### 4.2 Python/trimesh 实现（推荐）

```python
import trimesh
import numpy as np

def fix_glb_rotation(src_path, dst_path):
    scene = trimesh.load(src_path, force='scene')
    
    # 步骤1：绕 X 轴旋转 -90°
    rot_x = trimesh.transformations.rotation_matrix(
        np.radians(-90), [1, 0, 0]
    )
    scene.apply_transform(rot_x)
    
    # 步骤2：绕 Y 轴旋转 180°
    rot_y = trimesh.transformations.rotation_matrix(
        np.radians(180), [0, 1, 0]
    )
    scene.apply_transform(rot_y)
    
    # 导出
    data = trimesh.exchange.gltf.export_glb(scene)
    with open(dst_path, 'wb') as f:
        f.write(data)
```

**注意**：使用 trimesh 时必须先执行 X 轴旋转，再执行 Y 轴旋转。顺序不可颠倒。

### 4.3 Blender/bpy 实现（备选）

```python
import bpy, math

bpy.ops.import_scene.gltf(filepath=glb_path)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.transform.rotate(value=math.radians(-90), orient_axis='X', orient_type='GLOBAL')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', use_selection=True)
```

### 4.4 结果验证

修正后的模型必须满足：
- Y 轴向上（模型正立）
- 机头/车头朝向 Y+ 方向
- 中心在原点附近
- 最低点 Z ≈ 0（停在网格上方）

## 5. 质量门控 (Quality Gate)

### 5.1 结构完整性

必须具备可识别的核心结构（机身、主翼、尾翼、发动机/起落架等）。关键部件缺失或仅靠体块拼接表达，判定为失败。

### 5.2 细节复杂度

模型需包含多个子网格或明显的结构分区，不能为单一几何体。纹理与材质不可为全白/单一材质的纯占位表达。

### 5.3 真实性校验

选取 1-2 张真实参考图或高质量渲染图，比对外形轮廓与比例。重点检查机头、机翼、尾喷等关键部位是否存在拉伸、塌陷或扭曲。

### 5.4 拒收条件（任一触发即停止打包）

- 低多边形占位
- 方块堆叠
- 结构不可辨识
- 材质缺失或纯色占位
- GLB 仅为少量立方体/长方体拼接

处理：必须重新获取高质量参考图或更换高保真 GLB。

## 6. 3D 不可见排查与修复

当缩略图正常但 3D 模型在平台中不可见时，按以下顺序逐项排查：

| 序号 | 原因 | 修复方法 |
|------|------|----------|
| 1 | 几何体过多，平台加载失败 | 合并为单一网格后重新导出 GLB |
| 2 | 模型位置偏移，被相机裁剪 | 将包围盒中心平移到原点 (0,0,0) |
| 3 | 模型未贴地，最低点在平面下方 | 整体上移使最低点 Z=0 |
| 4 | 朝向不符合约定 | 按第 4 节旋转规则修正，确保机头朝 Y+ |
| 5 | agent.json 资源引用不一致 | 确保 modelUrlSlim/Fat 与 model.dimModelUrls 指向同一 GLB |
| 6 | 军标/缩略图混用 | 仅保留 symbolSeries=1，symbolName 指向 _mil.png |

### 6.1 几何体合并代码示例

```python
import trimesh

scene = trimesh.load('model.glb', force='scene')
# 合并所有几何体为单一网格
combined = trimesh.util.concatenate(scene.dump())
# 居中到原点
combined.vertices -= combined.bounding_box.centroid
# 贴地
combined.vertices[:, 2] -= combined.vertices[:, 2].min()
# 导出
combined.export('model_fixed.glb')
```

## 7. 资源去重校验

### 7.1 校验范围

与 `models/*/*/*_AI_Rodin.glb` 的多视角离线渲染图比对。

### 7.2 判定准则

与任一存量模型多视角渲染图 SSIM ≥ 0.70 即视为重复。

### 7.3 处理

更换生成提示词或更换 GLB 来源，重新生成并复检。

## 8. 命名规范

| 项目 | 规范 |
|------|------|
| 文件名 | `{ModelName}_AI_Rodin.glb` |
| 格式 | GLB (Binary glTF) |
| 坐标系 | Y-Up |
| 朝向 | 机头/车头朝 Y+ |

## 9. Scripts

| 脚本 | 功能 | 依赖 |
|------|------|------|
| `scripts/fix_glb_rotation.py` | trimesh GLB 旋转修正（推荐） | `trimesh`, `numpy` |
| `scripts/process_glbs.py` | Blender 批量坐标轴修正 | `bpy` |
| `scripts/rotate_glbs_z180.py` | Blender 批量朝向修正 180° | `bpy` |
| `scripts/blender_mcp_addon.py` | Blender MCP 插件（Rodin 集成） | `bpy`, `requests` |
| `scripts/download_rodin_result.py` | Rodin 3D 模型下载 | `requests` |

## 10. Resources

- `references/coordinate_system.md` — 坐标系变换规则详解
- `references/quality_gate.md` — 质量基准与拒收条件清单
- `references/visibility_troubleshooting.md` — 3D 不可见完整排查流程
