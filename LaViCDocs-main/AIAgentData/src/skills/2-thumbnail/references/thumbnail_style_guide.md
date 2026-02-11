# 缩略图风格指南 (Thumbnail Style Guide)

## 风格优先级

| 排名 | 风格 | 描述 | 示例关键词 |
|------|------|------|-----------|
| 1 | 3D Studio Render | 专业 3D 渲染，Studio 灯光 | "3D render", "studio render" |
| 2 | Clean Background Photo | 白/灰/透明背景实拍 | "white background", "isolated" |
| 3 | Real Photo | 真实环境拍摄 | "photo", "real" |

## 视角参数

```
         俯仰角 15-25°
           ↓
    ┌──────────────┐
    │    ╱  ╲      │  偏航角 30-45°
    │   ╱ TOP ╲    │  ←──────
    │  ╱       ╲   │
    │ ╱  FRONT  ╲  │
    │╱     3/4   ╲ │
    └──────────────┘
```

- **最佳**：Front 3/4 View + Slight Top-Down
- **可接受**：Isometric 3/4 Side View
- **可接受**：Side View (正侧视图)
- **避免**：极端仰视、正俯视、正后视

## 评分算法

```python
def score_image(width, height, file_size_kb):
    # 基础分 = 分辨率
    score = width * height
    
    # 宽高比惩罚
    aspect = width / height
    if aspect > 2.5 or aspect < 0.5:
        score *= 0.5
    
    # 最低门槛
    if width < 400 or height < 300:
        return -1  # 不合格
    
    return score
```

## 去重算法

```python
from PIL import Image
import imagehash

def is_duplicate(new_img_path, existing_img_path):
    """pHash 汉明距离 < 8 视为重复"""
    hash1 = imagehash.phash(Image.open(new_img_path))
    hash2 = imagehash.phash(Image.open(existing_img_path))
    return (hash1 - hash2) < 8
```

```python
from skimage.metrics import structural_similarity as ssim
import cv2

def is_similar_ssim(img1_path, img2_path, threshold=0.75):
    """SSIM ≥ 0.75 视为重复"""
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    score = ssim(img1, img2)
    return score >= threshold
```

## 一致性校验算法

```python
def check_thumbnail_consistency(thumbnail_path, glb_render_path):
    """三项指标至少满足两项即通过"""
    passed = 0
    
    # 1. SSIM ≥ 0.45
    ssim_score = compute_ssim(thumbnail_path, glb_render_path)
    if ssim_score >= 0.45:
        passed += 1
    
    # 2. 边缘 IoU ≥ 0.60
    edge_iou = compute_edge_iou(thumbnail_path, glb_render_path)
    if edge_iou >= 0.60:
        passed += 1
    
    # 3. 颜色直方图相关性 ≥ 0.50
    color_corr = compute_color_histogram_correlation(thumbnail_path, glb_render_path)
    if color_corr >= 0.50:
        passed += 1
    
    return passed >= 2
```
