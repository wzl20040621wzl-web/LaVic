# 3D 不可见排查与修复流程

> 典型现象：缩略图正常显示，但 3D 模型在平台中不可见。

## 排查顺序（必须按顺序执行）

### 1. 几何体过多

**症状**：GLB 文件正常，但平台加载超时或白屏。

**检查**：
```python
import trimesh
scene = trimesh.load('model.glb', force='scene')
print(f"几何体数量: {len(scene.geometry)}")
```

**修复**：合并为单一网格后重新导出。

### 2. 模型位置偏移

**症状**：模型导入后看不见，但旋转视角后能找到很远处的模型。

**检查**：
```python
bounds = scene.bounds
center = (bounds[0] + bounds[1]) / 2
print(f"中心点: {center}")  # 应接近 (0,0,0)
```

**修复**：将包围盒中心平移到原点。

### 3. 模型未贴地

**症状**：模型半截在地面以下或悬浮很高。

**检查**：
```python
z_min = scene.bounds[0][2]
print(f"最低点 Z: {z_min}")  # 应为 0
```

**修复**：整体上移使最低点 Z=0。

### 4. 朝向不符合约定

**症状**：模型可见但朝向错误（侧身或背面朝前）。

**修复**：按坐标系变换规则执行 X -90° + Y 180°。

### 5. agent.json 资源引用不一致

**症状**：平台报 404 或资源加载失败。

**检查**：确保以下路径全部一致且指向同一 GLB：
- `modelUrlSlim`
- `modelUrlFat`
- `model.dimModelUrls[*].url`

### 6. 军标/缩略图混用

**症状**：地图图标显示异常。

**修复**：
- `modelUrlSymbols` 仅保留 `symbolSeries=1`
- `symbolName` → `_mil.png`
- `thumbnail` → `.png`
