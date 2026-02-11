# Simulation Model Generation & Packaging Pipeline (NLP to ZIP)

## 1. 技能概述 (Overview)

本技能定义了从 **自然语言描述** 到最终 **LaViC 标准模型资产包 (.zip)** 的全自动化生成流水线。该流程不仅适用于无人机，也适用于车辆、船舶、导弹等其他仿真实体。

核心目标：**"One Prompt to Simulation Model"** —— 输入一段描述，输出一个可直接导入 LaViC 系统的标准 ZIP 包。

## 2. 标准流水线 (Pipeline Steps)

### 2.1 步骤一：模型定义与生成 (Definition & Generation)

- **输入**: 自然语言描述（例如：“一辆最大速度 80km/h 的装甲侦察车，配备光电传感器”）。
- **处理**:
  - **JSON 构建**: 基于 `src/AI生成AgentData代码参考/` 中的逻辑，利用 LLM 提取属性，构建 `AgentData.json`。
  - **Schema 校验**: 使用 `src/validator.py` 验证生成的 JSON 是否符合 `AgentData_schema.json`。
- **输出**: 基础 `agent.json` 文件。

### 2.2 步骤二：资产获取与生成 (Asset Acquisition)

根据模型类型自动准备三类核心资源：

1.  **缩略图 (Thumbnail)**:
    - 来源：Web Search (必须使用 Web Research Server MCP)。
    - 策略：**风格一致性与质量优选 (Style Consistency & Quality Selection)**。
      - **强制要求**：必须确保搜索到合适的图片，不得使用无效或低质量占位符。若 Web Research Server 返回结果不佳，需优化搜索词重新尝试。
      - 对每个模型搜索 3-5 张候选图片。
      - **风格标准 (Style Guidelines)**：
        - **优先风格**：**3D 渲染图 (3D Studio Render)** > **干净背景实拍图 (Clean Photo)** > **实拍图 (Real Photo)**。
        - **背景要求**：优先选择 **白色、灰色 (Studio Grey)** 或 **透明** 背景，避免复杂环境干扰。
        - **视角要求**：优先选择 **三分之四前视角 (Front 3/4 View)** 的 **轻俯视 (Slight Top-Down)**，其次为 **3/4 等轴侧视图 (Isometric/3/4 Side View)**，再其次为 **正侧视图 (Side View)**。
          - 俯仰角建议：**15–25°**（能看到机背/车顶）
          - 偏航角建议：**30–45°**（机头朝向画面右前或左前）
          - 画面构图：主体完整入镜、留少量边缘留白，避免极端仰视或正俯视
      - 优选标准：
        - 清晰度高：分辨率 > 800px (宽或高)。
        - 主体完整：车辆主体在图片中占比适中，无严重遮挡。
      - 自动化：脚本下载所有候选图，通过文件大小和分辨率算法自动择优（例如：优先选分辨率最大且文件体积适中的图片）。
      - **去重要求**：候选缩略图必须与 `models/` 目录已有模型的缩略图显著不同。
        - 对比范围：`models/*/{ModelName}/{ModelName}.png|jpg` 与 `models/*/{ModelName}/{ModelName}_mil.png`。
        - 过滤策略：与任一现有缩略图达到“高相似”即剔除该候选。
        - 判定建议：pHash 汉明距离 < 8 或 SSIM ≥ 0.75 视为高相似。
    - 格式：PNG/JPG。
    - 命名：`{ModelName}.png`。
    - 禁止项：**严禁使用军标图 (`*_mil.png`) 作为缩略图**。仅当**无法找到任何可用的线上图片**时，才允许改为**从 GLB 自动离线渲染缩略图**（Blender 无头渲染，三维等轴视角、纯色背景），并写入 `{ModelName}.png`。
    - 兜底顺序（从高到低）：高质量公开版权实拍/渲染图 > GLB离线渲染 > 暂停打包并报错（不允许以军标代替缩略图）。
2.  **军标 (Military Symbol)**:
    - 工具：`src/gen_mil_symbols.py` (基于 `military-symbol` 库)。
    - 标准：NATO APP-6(D)。
    - 命名：`{ModelName}_mil.png`。
3.  **3D 模型 (3D Model)**:
    - 来源：Rodin (AI生成) / Blender / 现有库。
    - 质量要求：整体细节层级与可读性需达到可用标准。
    - 禁止项：**不允许**几何占位、简单方块堆叠、缺失机翼/尾翼等关键结构的低保真模型进入打包流程。
    - 格式：GLB。
    - 命名：`{ModelName}_AI_Rodin.glb`。

### 2.3 步骤三：资产标准化处理 (Asset Standardization)

**[严格执行]** 必须对 3D 模型进行几何修正，确保在 LaViC 场景 (Y-Up 坐标系) 中姿态正确。此步骤不可省略。

- **修正逻辑 (必须按顺序执行)**:
  1.  **坐标轴修正 (Z-Up -> Y-Up)**: 绕 X 轴旋转 **-90°**。
  2.  **朝向修正 (Facing Correction)**: 绕 Y 轴 (即新坐标系下的垂直轴) 旋转 **180°**。
  - **结果验证**: 模型应正立 (Y轴向上)，且机头/车头朝向正确 (通常对应 Y 轴旋转 180 度后的方向)。

- **实现方式**:
  - **Python (推荐)**: 使用 `trimesh` 库直接处理 GLB 文件 (参考 `src/fix_glb_rotation.py`)。
  - **Blender**: 使用 `bpy` 脚本处理。
  - **注意**: 若使用 `trimesh`，请确保先执行 X 轴旋转，再执行 Y 轴旋转。
  - **禁止项**: 若 GLB 几何仅为少量立方体/长方体拼接且无法辨识具体机型，直接判定失败并回退重生成。

### 2.3.1 缩略图一致性校验 (Thumbnail vs 3D Model)

- 目标：确保缩略图与 3D 模型在外形与类别上保持一致，避免出现“缩略图是其他型号或完全不同外形”的情况。
- 校验流程（自动化，任一失败则触发修复或中止打包）：
  - 从 GLB **离线渲染一张预览图**（等轴侧视角、白/灰背景，分辨率≥1024px），仅用于比对，不计入最终包。
  - 计算与缩略图的相似度指标：
    - 结构相似度 SSIM ≥ 0.45
    - 边缘轮廓 IoU（Canny 边缘+形态学闭合）≥ 0.60
    - 颜色直方图相关性（HSV 3x64 bins）≥ 0.50
  - 判定准则：三项指标至少满足两项则通过；否则判定不一致。
  - 自动修复：
    - 若缩略图命名为 `*_mil.png` 或相似度不足，**用 GLB 离线渲染图替换缩略图** 并更新 `agent.json` 的 `thumbnail`。
  - 禁止打包：
    - 若无法生成离线渲染图或相似度仍严重不足，**中止打包并记录错误**，要求更换 GLB 或缩略图来源。

### 2.3.2 资源去重校验 (Deduplication Check)

- 目标：确保新生成的 3D 模型与缩略图不与 `models/` 中现有资产高度相似或重复。
- 校验范围：
  - 缩略图：对比 `models/*/*/*.{png,jpg}` 中的缩略图与军标图。
  - 3D 模型：对比 `models/*/*/*_AI_Rodin.glb` 的多视角离线渲染图。
- 判定准则：
  - 缩略图：pHash 汉明距离 < 8 或 SSIM ≥ 0.75 视为重复。
  - 3D 模型：与任一存量模型多视角渲染图 SSIM ≥ 0.70 即视为重复。
- 处理策略：
  - 缩略图重复：必须更换图片来源或使用新 GLB 离线渲染图替换。
  - 3D 模型重复：更换生成提示词或更换 GLB 来源，重新生成并复检。

### 2.3.3 3D 不可见排查与修复 (3D Visibility Troubleshooting)

- 典型现象：缩略图正常但 3D 模型不可见。
- 常见原因与修复顺序（必须按顺序执行）：
  1. **几何体过多**：GLB 内部几何体数量过大可能导致平台加载失败。
     - 修复：合并为单一网格后重新导出 GLB。
  2. **模型位置偏移**：模型不在原点附近导致被相机裁剪。
     - 修复：将模型包围盒中心平移到原点 (0,0,0)。
  3. **模型未贴地**：模型最低点在网格平面下方或过高。
     - 修复：将模型整体上移，使最低点 Z=0。
  4. **朝向不符合约定**：机头未朝向绿色轴 (Y+) 导致场景判定异常。
     - 修复：按 2.3 的旋转规则执行，确保机头朝向 Y+。
  5. **资源引用不一致**：`agent.json` 中根级与 `model` 内部资源路径不一致。
     - 修复：确保 `modelUrlSlim/Fat` 与 `model.dimModelUrls` 均指向同一 GLB，缩略图与军标路径正确。
  6. **军标/缩略图混用**：`modelUrlSymbols` 结构异常影响平台读取。
     - 修复：参考既有机型仅保留 `symbolSeries=1`，`symbolName` 指向 `_mil.png`，`thumbnail` 指向缩略图。

### 2.4 模型真实性校验 (Reality Check)

- **目标**: 确保生成的 3D 模型贴近现实、比例正确、无明显形变或扭曲。
- **校验方法**:
  - **参考对照**: 选取 1-2 张真实参考图或高质量渲染图，比对外形轮廓与比例。
  - **形变检查**: 重点观察机头、机翼、尾喷等关键部位是否存在拉伸、塌陷或扭曲。
  - **不合格返工**: 若存在明显失真，重新生成 GLB 或更换更高质量源模型。

### 2.4.1 质量基准与拒收条件 (Quality Gate)

- **结构完整性**:
  - 必须具备可识别的机身、主翼、尾翼与发动机/起落架等核心结构。
  - 关键部件缺失或仅靠体块拼接表达，判定为失败。
- **细节复杂度**:
  - 模型需包含多个子网格或明显的结构分区，不能为单一几何体。
  - 纹理与材质不可为全白/单一材质的纯占位表达。
- **一致性校验**:
  - 与参考缩略图在外形轮廓与比例上保持一致，否则回退重生成。
- **拒收条件**:
  - 低多边形占位、方块堆叠、结构不可辨识、材质缺失或纯色占位。
  - 任一拒收条件触发则停止打包，必须重新获取高质量参考图或更换高保真 GLB。

### 2.5 步骤四：目录结构与配置 (Structure & Configuration)

- **工作目录规范**:
  ```text
  models/
  ├── {ModelName}/
  │   ├── agent.json
  │   └── {ModelName}/
  │       ├── {ModelName}.png
  │       ├── {ModelName}_mil.png
  │       └── {ModelName}_AI_Rodin.glb
  └── {ModelName}.zip
  ```
- **文件清单要求**:
  - `{ModelName}/` 目录内仅允许 `agent.json` 与 `{ModelName}/` 资源子目录。
  - 资源子目录仅允许 3 个核心文件：缩略图、军标、GLB。
  - 任何导出残留文件（如 `external.*`、`materials.*`、`*_NML.png`）必须删除后再打包。
  - ZIP 必须放在 `models/` 根目录，不得放在 `{ModelName}/` 内。
- **配置修复 (Configuration Fixes)**:
  - 脚本：`src/fix_and_zip_models.py` 或生成脚本内部逻辑。
  - **[严格执行] 必须更新以下所有字段，严禁遗漏**:
    1.  **根级字段**: `agentName`, `modelUrlSlim`, `modelUrlFat`, `modelUrlSymbols`。
    2.  **嵌套 model 对象 (关键)**: 必须同步更新 `model` 对象内部的以下字段，**不可保留模板默认值**：
        - `model.modelName`: 必须与根级 `agentName` 一致。
        - `model.thumbnail`: 必须指向 `{ModelName}/{ModelName}.png`。
        - `model.mapIconUrl`: 必须指向 `{ModelName}/{ModelName}_mil.png`。
        - `model.dimModelUrls`: 必须指向 `{ModelName}/{ModelName}_AI_Rodin.glb`。
    - **路径格式**: 所有资源引用必须使用相对路径 `"{ModelName}/{Filename}"`。
    - **文件位置**: `agent.json` 必须位于 `models/{ModelName}/agent.json`，不得放入资源子目录。
    - **数组包装**: `agent.json` 顶层必须是数组，且仅包含一个对象。

### 2.6 步骤五：最终打包 (Final Packaging)

- **工具**: `src/zip_models.py` (被 `fix_and_zip_models.py` 调用)。
- **要求**:
  - **格式**: `.zip`。
  - **编码**: **UTF-8** (必须支持中文文件名)。
  - **结构**: **Flat Structure** (扁平化)。
    - 错误：ZIP -> `{ModelName}/` -> `agent.json`
    - 正确：ZIP -> `agent.json`, `{ModelName}/` (资源文件夹)
  - **内容最小集**: ZIP 内仅包含 4 个条目：`agent.json` 与 `{ModelName}/` 下的 3 个资源文件。
- **产物**: `models/{ModelName}.zip`。
- **打包前强校验**：
  - 缩略图路径不得为 `*_mil.png`。
  - 必须完成“缩略图一致性校验”，未通过则**拒绝打包**。
  - `thumbnail` 与 `mapIconUrl` 分工明确：缩略图用于模型预览，军标仅用于地图标识。

## 3. 核心脚本工具箱 (Toolbox)

| 脚本文件                           | 功能描述                          | 关键依赖                       |
| :--------------------------------- | :-------------------------------- | :----------------------------- |
| `src/validator.py`                 | 校验 `agent.json` 结构合法性      | `jsonschema`                   |
| `src/gen_mil_symbols.py`           | 生成 APP-6D 标准军标 PNG          | `military-symbol`, `reportlab` |
| `src/process_glbs.py`              | 批量调整 GLB 坐标轴 (Y-Up)        | `bpy` (Blender API)            |
| `src/rotate_glbs_z180.py`          | 批量调整 GLB 朝向 (Rotate 180)    | `bpy` (Blender API)            |
| `src/fix_and_zip_models.py`        | 批量修复 JSON 路径并打包          | `src/zip_models.py`            |
| `src/zip_models.py`                | 创建 UTF-8 编码的扁平化 ZIP       | `zipfile`                      |
| `src/generate_vehicle_packages.py` | 批量生成车辆模型包 (Orchestrator) | `pandas`, `military_symbol`    |
| `src/fetch_images.py`              | 自动获取参考图片                  | `requests`                     |
| `src/check_and_convert_images.py`  | 图片格式检查与转换 (RGB PNG)      | `Pillow`                       |
| `src/blender_mcp_addon.py`         | Blender MCP 插件 (Hyper3D 集成)   | `bpy`, `requests`              |

## 4. 扩展指南 (Extension Guide)

若要支持新类型的模型（如“潜艇”）：

1.  **JSON 生成**: 确保 `agentType` 和 `dynamics` 选择正确（如 `HydroDynamics`）。
2.  **军标生成**: 在 `gen_mil_symbols.py` 中添加对应的 SIDC 代码映射。
3.  **3D 模型**: 获取潜艇 GLB 模型，并运行 Blender 脚本修正坐标。
4.  **执行打包**: 运行 `python src/fix_and_zip_models.py` 即可自动完成修复与打包。

## 5. 快速校验清单 (Quick Checklist)

- JSON 配置
  - 顶层为数组且仅 1 个对象
  - 根级 `thumbnail` 指向 `{ModelName}/{ModelName}.png`
  - 根级 `modelUrlSlim/Fat` 指向 `{ModelName}/{ModelName}_AI_Rodin.glb`
  - `model` 内部的 `modelName/thumbnail/mapIconUrl/dimModelUrls` 与根级保持一致
  - `modelUrlSymbols` 结构与参考机型一致（`symbolSeries=1`，`symbolName` 指向 `_mil.png`）
- GLB 姿态
  - 坐标系：X -90° 后 Y 180°（Y-Up，机头朝 Y+）
  - 位置：中心在原点，最低点 Z=0（停在网格上方）
  - 几何：必要时合并为单一网格以提升兼容性
- 打包结构
  - ZIP 内仅 4 项：`agent.json`、`{ModelName}.png`、`{ModelName}_mil.png`、`{ModelName}_AI_Rodin.glb`
  - 路径为相对格式 `{ModelName}/{Filename}`
