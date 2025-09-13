# CodeLens 模块总览

## 识别的功能模块

基于CodeLens架构分析，识别出以下主要功能模块：

1. **Task Engine模块** (`src/task_engine/`) - 智能任务管理和5阶段流程控制
2. **模板系统模块** (`src/templates/`) - 16个专业模板四层架构管理
3. **服务模块** (`src/services/`) - 增强的信息提供服务
4. **MCP工具模块** (`src/mcp_tools/`) - 7个MCP协议工具实现
5. **MCP服务器** (`mcp_server.py`) - 完整MCP协议服务器

## 模块详细信息

### Task Engine模块 (src/task_engine/) - 🚀 核心新增
**包含文件**:
- `task_manager.py` - 智能任务管理器核心实现
- `phase_controller.py` - 5阶段严格控制器实现
- `state_tracker.py` - 持久化状态跟踪和进度监控
- `__init__.py` - 包初始化和统一导出

**🚀 核心功能**:
- **智能任务管理**: 支持依赖关系和优先级调度的任务管理系统
- **5阶段流程控制**: 严格的阶段依赖验证和100%完成率要求
- **状态持久化**: 支持中断恢复的状态跟踪和事件记录
- **进度监控**: 实时进度计算和性能监控
- **健康检查**: 自动检测系统健康状态和异常

**🏗️ 5阶段工作流程**:
- **Phase 1 - 项目扫描**: 项目路径 → 智能扫描 → 项目特征分析 → 生成策略
- **Phase 2 - 文件文档**: 核心文件 → 模板匹配 → 内容生成 → 状态跟踪
- **Phase 3 - 模块分析**: 模块分析 → 关系映射 → 依赖图谱 → 模块文档
- **Phase 4 - 架构设计**: 整体架构 → 技术栈 → 数据流 → 架构图表
- **Phase 5 - 项目总结**: 项目README → 完整性验证 → 项目文档

**对外接口**:
- `TaskManager`: 智能任务管理器
  - `create_task()`: 创建新任务并分配唯一ID
  - `update_task_status()`: 更新任务状态和持久化
  - `get_next_task()`: 获取下一个可执行任务
  - `get_phase_progress()`: 获取阶段进度信息
- `PhaseController`: 5阶段严格控制器
  - `can_proceed_to_next_phase()`: 检查阶段转换权限
  - `get_current_phase()`: 获取当前活跃阶段
  - `get_phase_progress()`: 获取阶段详细进度
- `StateTracker`: 状态跟踪器
  - `record_task_event()`: 记录任务事件
  - `get_current_status()`: 获取当前系统状态
  - `get_health_status()`: 获取健康检查结果

### 模板系统模块 (src/templates/)
**包含文件**:
- `document_templates.py` - TemplateService核心管理器
- `__init__.py` - 包初始化

**🚀 核心功能**:
- **16个专业模板管理**: 四层架构分级模板系统
- **智能模板查询**: 按层级、类型、名称多维度查询
- **模板格式化引擎**: 支持变量验证和智能替换
- **标准化模板质量**: 满足专业文档生成需求

**🏗️ 四层模板架构**:
- **架构层 (4个)**: 系统概述、技术栈、数据流
- **模块层 (6个)**: 模块总览、关系分析、依赖图谱、模块文档、API接口、业务流程  
- **文件层 (3个)**: 文件摘要、类分析、函数目录
- **项目层 (3个)**: README、变更日志、路线图

**对外接口**:
- `TemplateService`: 16个模板的统一管理中心
  - `get_template_list()`: 获取全部16个模板的详细元数据
  - `get_template_content()`: 获取指定模板的完整内容和信息
  - `get_template_by_type()`: 按类型获取模板列表
  - `format_template()`: 智能模板格式化和变量验证
  - `validate_template_variables()`: 验证模板变量完整性

### 📊 服务模块 (src/services/) - 增强信息提供
**包含文件**:
- `file_service.py` - 文件系统操作和信息提取服务
- `validation_service.py` - 文档验证和状态报告服务  
- `__init__.py` - 包初始化

**核心功能**:
- 项目文件扫描、读取和元数据提取
- 目录树结构生成和分析
- 文档生成状态验证和报告
- 文件存在性检查（不读取内容）
- 与26模板系统协作的信息提供

**对外接口**:
- `FileService`: 完整的文件信息提供服务
  - `get_project_files_info()`: 获取项目完整信息
  - `get_file_metadata()`: 获取文件元数据
  - `get_directory_tree()`: 生成目录树结构
- `ValidationService`: 四层架构文档验证服务
  - `get_generation_status()`: 获取文档生成状态
  - `check_directory_structure()`: 检查目录结构
  - `get_validation_summary()`: 获取验证摘要

### 🔧 MCP工具模块 (src/mcp_tools/) - 🚀 智能化升级
**包含文件**:
- `doc_scan.py` - 项目文件扫描工具 (智能过滤增强)
- `template_get.py` - 模板获取工具 (16模板架构查询)
- `doc_verify.py` - 文档验证工具 (四层验证)
- `doc_guide.py` - 🆕 项目分析和策略生成工具
- `task_init.py` - 🆕 任务计划生成工具
- `task_execute.py` - 🆕 任务执行和上下文提供工具
- `task_status.py` - 🆕 任务状态监控和健康检查工具
- `__init__.py` - 包初始化和统一导出

**🚀 核心功能**:
- **智能任务驱动**: 新增4个Task Engine集成工具
- **项目智能分析**: doc_guide提供深度项目分析和文档策略
- **完整任务生命周期**: 从分析→规划→执行→监控的闭环流程
- **智能过滤系统**: 自动忽略无关文件，专注核心代码
- **上下文增强**: 为AI提供丰富的执行上下文和模板信息
- **实时状态监控**: 全面的任务和阶段进度监控
- **健康检查机制**: 自动诊断系统健康状态

**🏗️ 7工具分类**:
- **基础工具 (3个)**: doc_scan, template_get, doc_verify
- **智能分析工具 (1个)**: doc_guide (项目分析和策略制定)
- **任务管理工具 (3个)**: task_init, task_execute, task_status

**对外接口**:
- `DocScanTool`: 增强项目扫描工具类
  - `execute()`: 智能文件扫描 + 过滤配置
- `TemplateGetTool`: 模板获取工具类  
  - `execute()`: 按层级/类型获取16个模板
- `DocVerifyTool`: 文档验证工具类
  - `execute()`: 四层文档体系验证
- `DocGuideTool`: 🆕 项目分析工具类
  - `execute()`: 深度项目分析 + 策略生成
- `TaskInitTool`: 🆕 任务初始化工具类
  - `execute()`: 生成5阶段完整任务计划
- `TaskExecuteTool`: 🆕 任务执行工具类
  - `execute()`: 提供执行上下文 + 模板信息
- `TaskStatusTool`: 🆕 状态监控工具类
  - `execute()`: 任务和阶段状态检查

### MCP服务器模块 (mcp_server.py) - 🚀 智能化升级
**包含文件**:
- `mcp_server.py` - Task Engine + 16模板系统完整MCP协议服务器

**核心功能**:
- **Task Engine集成**: 完整支持智能任务驱动工作流
- **7工具统一管理**: 统一路由和调度所有MCP工具
- **完整MCP协议**: 标准JSON-RPC通信协议实现
- **16模板系统集成**: 完整支持四层架构模板查询
- **Claude Code深度集成**: 为AI协作优化的智能化无缝集成

**对外接口**:
- `CodeLensMCPServer`: 智能化主服务器类
  - `handle_request()`: 处理Task Engine + 模板系统MCP请求
  - `list_tools()`: 列出支持智能工作流的所有7个工具
  - `execute_tool()`: 执行Task Engine集成工具
- `main()`: 服务器启动入口
- 智能任务驱动模式和16模板系统测试

## 模块关系图谱

### 依赖关系
```
🔧 MCP工具层 (Claude Code接口) - 7个智能工具
├── 基础工具 (3个)
│   ├── DocScanTool → FileService (智能文件扫描 + 过滤配置)
│   ├── TemplateGetTool → TemplateService (16模板四层查询)
│   └── DocVerifyTool → ValidationService (四层架构验证)
└── Task Engine工具 (4个)
    ├── DocGuideTool → FileService (项目分析 + 策略生成)
    ├── TaskInitTool → TaskManager (任务计划生成)
    ├── TaskExecuteTool → TaskManager + PhaseController + StateTracker (任务执行)
    └── TaskStatusTool → TaskManager + PhaseController + StateTracker (状态监控)

🚀 Task Engine层 - 智能任务管理
├── TaskManager (智能任务管理器)
├── PhaseController (5阶段严格控制器)  
└── StateTracker (状态跟踪和监控)

🛠️ 服务层 (信息提供)
├── TemplateService (16模板统一管理中心)
│   ├── Architecture Templates (4个架构层模板)
│   ├── Module Templates (6个模块层模板)  
│   ├── File Templates (3个文件层模板)
│   └── Project Templates (3个项目层模板)
├── FileService (增强文件信息服务)
└── ValidationService (四层架构验证服务)

🌐 MCP协议层
└── CodeLensMCPServer (7工具 + Task Engine统一管理)
```

### 🔍 详细依赖分析
- **Task Engine工具** → Task Engine三大核心组件 (智能工作流管理)
- **DocGuideTool** → FileService (深度项目分析 + 智能策略生成)
- **TaskInitTool** → TaskManager (基于分析结果生成完整任务计划)
- **TaskExecuteTool** → 全部Task Engine组件 (任务执行和上下文提供)
- **TaskStatusTool** → 全部Task Engine组件 (全面状态监控)
- **传统工具** → 对应服务层 (信息查询和验证)
- **Task Engine** → Python标准库（零外部依赖设计）
- **智能化架构**：Task Engine驱动，服务层支撑，工具层展现

### 数据流向
1. **智能任务工作流**: doc_guide → task_init → task_execute → task_status
2. **Claude Code** → **7个MCP工具** → **Task Engine + 服务层** → **JSON响应**
3. **FileService**: 项目路径 → 文件扫描 → 结构化信息
4. **TemplateService**: 模板请求 → 模板查询 → 格式化模板  
5. **ValidationService**: 验证请求 → 状态检查 → 验证报告
6. **Task Engine**: 任务创建 → 阶段控制 → 状态跟踪 → 进度报告

## 核心接口汇总

### Task Engine接口
- **TaskManager**:
  - `create_task()`: 创建新任务并分配唯一ID
  - `update_task_status()`: 更新任务状态和持久化
  - `get_next_task()`: 获取下一个可执行任务
  - `get_phase_progress()`: 获取阶段进度信息
  - `get_overall_progress()`: 获取总体进度统计
- **PhaseController**:
  - `can_proceed_to_next_phase()`: 检查阶段转换权限
  - `get_current_phase()`: 获取当前活跃阶段  
  - `get_phase_progress()`: 获取阶段详细进度
  - `get_all_phases_overview()`: 获取所有阶段概览
- **StateTracker**:
  - `record_task_event()`: 记录任务事件
  - `get_current_status()`: 获取当前系统状态
  - `get_health_status()`: 获取健康检查结果
  - `get_performance_metrics()`: 获取性能指标

### FileService 接口
- `get_project_files_info()`: 获取项目文件的完整结构化信息
- `get_file_metadata()`: 获取单个文件的元数据信息
- `get_directory_tree()`: 获取优化的目录树结构
- `scan_source_files()`: 扫描项目源码文件
- `read_file_safe()`: 安全读取文件内容
- `get_project_info()`: 获取项目基础信息

### TemplateService 接口
- `get_template_list()`: 获取16个可用模板列表
- `get_template_content()`: 获取指定模板的内容和元数据
- `get_template_by_type()`: 根据类型获取模板列表
- `validate_template_variables()`: 验证模板变量是否完整
- `format_template()`: 格式化模板内容

### ValidationService 接口
- `get_generation_status()`: 获取文档生成状态的完整报告
- `check_directory_structure()`: 检查目录结构是否符合预期
- `get_missing_files()`: 获取缺失的文档文件列表
- `get_validation_summary()`: 获取验证结果摘要和建议

### MCP工具接口 (7个)
- **基础工具**:
  - `DocScanTool.execute()`: 智能文件扫描和过滤
  - `TemplateGetTool.execute()`: 获取16个模板
  - `DocVerifyTool.execute()`: 四层架构验证
- **Task Engine工具**:
  - `DocGuideTool.execute()`: 项目分析和策略生成
  - `TaskInitTool.execute()`: 5阶段任务计划生成  
  - `TaskExecuteTool.execute()`: 任务执行和上下文提供
  - `TaskStatusTool.execute()`: 状态监控和健康检查
- 所有工具的 `get_tool_definition()`: 获取MCP工具定义

## 模块设计原则

1. **智能任务驱动**: 🆕 Task Engine提供完整的任务生命周期管理
2. **5阶段流程控制**: 🆕 严格的阶段依赖验证和100%完成率要求
3. **状态持久化**: 🆕 支持中断恢复的状态跟踪和进度监控
4. **信息提供优先**: 专注于为Claude Code提供结构化信息和执行上下文
5. **服务独立性**: 各服务模块相互独立，便于维护扩展
6. **MCP标准兼容**: 所有7个工具严格遵循MCP协议规范
7. **智能化配置**: 支持项目分析、智能过滤和策略生成
8. **错误透明**: 完善的错误处理和健康检查机制
9. **性能优化**: 毫秒级响应和高效的任务调度算法

## 协作设计理念

CodeLens的智能化模块设计遵循**Task Engine驱动的Claude Code协作**理念：
- **CodeLens提供智能化信息**: 不仅提供数据，还提供分析、策略和执行指导
- **Task Engine管理工作流**: 完整的5阶段任务生命周期管理和状态跟踪
- **Claude Code专注内容生成**: 基于丰富的上下文和模板生成高质量文档内容
- **智能协作闭环**: 分析→规划→执行→监控的完整智能化协作流程

这种设计实现了从简单的信息提供到智能化任务协作的重要进化，确保了系统的高效性、智能性和可扩展性。

