# 目录结构规范

## 工作目录

```
models/
├── {ModelName}/                   ← 模型工作目录
│   ├── agent.json                 ← 配置文件（此层级，不可更深）
│   └── {ModelName}/               ← 资源子目录（与模型同名）
│       ├── {ModelName}.png            ← 缩略图
│       ├── {ModelName}_mil.png        ← 军标
│       └── {ModelName}_AI_Rodin.glb   ← 3D 模型
│
└── {ModelName}.zip                ← ZIP 输出（models/ 根目录，不在子目录内）
```

## ZIP 内部结构（扁平化）

```
{ModelName}.zip
│
├── agent.json                     ← ZIP 根目录
└── {ModelName}/                   ← 资源文件夹
    ├── {ModelName}.png
    ├── {ModelName}_mil.png
    └── {ModelName}_AI_Rodin.glb
```

## 正确 vs 错误

正确（扁平化）：
```
ZIP/
├── agent.json
└── F-22_Raptor/
    ├── F-22_Raptor.png
    ├── F-22_Raptor_mil.png
    └── F-22_Raptor_AI_Rodin.glb
```

错误（多了一层嵌套）：
```
ZIP/
└── F-22_Raptor/              ← 多了这一层！
    ├── agent.json
    └── F-22_Raptor/
        ├── ...
```

## 文件清单

ZIP 内有且仅有 4 个条目，禁止包含任何其他文件。
