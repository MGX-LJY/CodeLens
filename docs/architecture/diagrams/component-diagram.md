
# CodeLens 组件关系图

## 组件层次结构

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                             │
│                      Claude Code                           │
│                   (智能化文档生成)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP 协议通信 (7个专业工具)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   MCP接口层 (7个工具)                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│   doc_guide     │    task_init    │    task_execute         │
│ DocGuideTool    │ TaskInitTool    │  TaskExecuteTool        │
├─────────────────┼─────────────────┼─────────────────────────┤
│  task_status    │    doc_scan     │   template_get          │
│TaskStatusTool   │ DocScanTool     │ TemplateGetTool         │
├─────────────────┼─────────────────┼─────────────────────────┤
│   doc_verify    │                 │                         │
│ DocVerifyTool   │                 │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   任务引擎层                                │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│ TaskManager  │PhaseController│ StateTracker │   调度算法       │
│ 任务生命周期  │ 阶段流程控制  │ 状态跟踪监控  │  智能调度引擎    │
└──────────────┼──────────────┼──────────────┼─────────────────┘
               │              │              │
               ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                      服务层                                │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│ FileService  │TemplateService│ValidationService│              │
│ 智能文件服务  │   模板管理    │   验证服务     │                 │
└──────────────┼──────────────┼──────────────┼─────────────────┘
               │              │              │
               ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                      基础层                                │
├─────────────────┬─────────────────┬─────────────────────────┤
│   文件系统       │    模板资源      │     状态存储            │
│ Python pathlib  │  10个核心模板    │   JSON持久化文件        │
│  智能过滤       │  三层架构模板     │  .codelens/tasks.json   │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## 详细组件说明

### 1. **MCP 工具组件** - 对外接口层 (7个专业工具)
- **DocGuideTool**: 智能项目分析器，自动识别项目类型、框架和生成文档策略
- **TaskInitTool**: 任务计划生成器，基于分析结果创建4阶段执行计划
- **TaskExecuteTool**: 任务执行管理器，提供模板、上下文和执行指导
- **TaskStatusTool**: 状态监控中心，实时进度跟踪和健康诊断
- **DocScanTool**: 项目文件扫描工具，智能过滤和结构化数据提取
- **TemplateGetTool**: 模板获取工具，支持多维度查询和格式化
- **DocVerifyTool**: 文档验证工具，完整性检查和改进建议

### 2. **任务引擎组件** - 智能化任务驱动核心
- **TaskManager**: 智能任务管理器，支持核心任务类型、依赖关系和优先级调度
- **PhaseController**: 4阶段严格控制器，确保100%完成率的阶段转换
- **StateTracker**: 实时状态跟踪，支持执行历史、性能监控和健康检查
- **调度算法**: 基于依赖关系的DAG调度和优先级算法

### 3. **服务组件** - 核心业务逻辑
- **FileService**: 智能文件分析服务，项目类型检测、框架识别和智能过滤
- **TemplateService**: 模板管理服务，10个核心模板统一管理，三层架构支持
- **ValidationService**: 验证服务，文档结构验证、完整性检查和多种验证模式

### 4. **基础组件** - 底层支撑
- **文件系统接口**: 基于 pathlib 的智能文件操作和过滤
- **模板资源**: 10个核心模板，三层架构(Architecture/File/Project)支持
- **状态存储**: JSON持久化文件系统，支持任务状态和执行历史保存

## 组件依赖关系

```
DocGuideTool ──────────────→ FileService + ProjectAnalyzer
                                │
                                ▼
TaskInitTool ──────────────→ TaskManager + TaskPlanGenerator
                                │
                                ▼
TaskExecuteTool ───────────→ TaskManager + TaskExecutor + TemplateService
                                │
                                ▼
TaskStatusTool ────────────→ TaskManager + PhaseController + StateTracker
                                │
                                ▼
DocScanTool ───────────────→ FileService
                                │
                                ▼
TemplateGetTool ───────────→ TemplateService
                                │
                                ▼
DocVerifyTool ─────────────→ ValidationService

任务引擎内部组件关系：
TaskManager ←→ PhaseController ←→ StateTracker
     │              │                  │
     ▼              ▼                  ▼
   依赖图管理    阶段控制逻辑      状态持久化存储
     │              │                  │
     ▼              ▼                  ▼
  优先级调度    100%完成验证      性能监控分析
```

### 依赖说明
- **MCP 工具** → **任务引擎/服务层**: MCP工具依赖任务引擎和对应服务组件
- **任务引擎组件** → **相互协作**: TaskManager、PhaseController、StateTracker紧密协作
- **任务引擎** → **服务层**: 任务引擎调用FileService、TemplateService、ValidationService
- **服务间无依赖**: FileService、TemplateService、ValidationService 相互独立
- **状态持久化**: 任务状态保存到JSON文件，支持中断恢复

## 数据流组件

### 智能化协作处理流
```
Claude Code 请求 → MCP 工具(7个) → 参数验证 → 任务引擎调用
```

### 任务引擎处理流  
```
任务引擎调用 → TaskManager/PhaseController/StateTracker → 服务层调用 → 智能分析执行
```

### 服务层处理流
```
服务层调用 → FileService/TemplateService/ValidationService → 业务逻辑 → 数据处理
```

### 输出处理流
```
数据处理 → 结果生成 → JSON 格式化 → MCP 响应 → Claude Code
```

### 状态持久化流
```
任务状态变更 → StateTracker → JSON持久化 → .codelens/tasks.json → 中断恢复支持
```
