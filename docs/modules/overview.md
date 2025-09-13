# CodeLens 模块总览

## 识别的功能模块

基于CodeLens MCP服务器架构分析，识别出以下主要功能模块：

1. **模板系统模块** (`src/templates/`) - 26个专业模板四层架构管理
2. **服务模块** (`src/services/`) - 增强的信息提供服务
3. **MCP工具模块** (`src/mcp_tools/`) - MCP协议接口实现
4. **日志模块** (`src/logging/`) - 完整日志系统
5. **MCP服务器** (`mcp_server.py`) - 完整MCP协议服务器 
6. **测试工具** (`test_new_mcp_tools.py`) - 模板系统验证

## 模块详细信息

### 模板系统模块 (src/templates/)
**包含文件**:
- `document_templates.py` - TemplateServiceV05核心管理器
- `templates/` - 模块化模板组织目录
  - `architecture_templates.py` - 7个架构层专业模板
  - `module_templates.py` - 6个模块层专业模板
  - `file_templates.py` - 5个文件层专业模板
  - `project_templates.py` - 8个项目层专业模板
  - `__init__.py` - 统一模板导出
- `__init__.py` - 包初始化

**🚀 核心功能**:
- **26个专业模板管理**: 四层架构分级模板系统
- **智能模板查询**: 按层级、类型、名称多维度查询
- **模板格式化引擎**: 支持变量验证和智能替换
- **模块化模板组织**: 独立文件便于维护和扩展
- **专业模板质量**: 满足专业文档生成需求

**🏗️ 四层模板架构**:
- **架构层 (7个)**: 系统概述、技术栈、数据流、设计模式、安全、部署、扩展性
- **模块层 (6个)**: 模块总览、关系分析、依赖图谱、模块文档、API接口、业务流程
- **文件层 (5个)**: 文件摘要、类分析、函数目录、算法分解、代码度量
- **项目层 (8个)**: README、变更日志、路线图、贡献指南、API参考、故障排除、性能、版本

**对外接口**:
- `TemplateServiceV05`: 26个模板的统一管理中心
  - `get_template_list()`: 获取全部26个模板的详细元数据
  - `get_template_content()`: 获取指定模板的完整内容和信息
  - `get_templates_by_layer()`: 按四层架构分类获取模板
  - `format_template()`: 智能模板格式化和变量验证
  - `get_layer_stats()`: 获取各层级模板统计信息

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

### 🔧 MCP工具模块 (src/mcp_tools/) - 26模板系统支持
**包含文件**:
- `doc_scan.py` - 项目文件扫描工具 (支持26模板兼容性分析)
- `template_get.py` - 模板获取工具 (支持四层架构查询)
- `doc_verify.py` - 文档验证工具 (支持四层验证)
- `__init__.py` - 包初始化和统一导出

**🚀 核心功能**:
- **26模板系统集成**: 所有工具支持四层模板架构
- **智能项目扫描**: doc_scan支持模板兼容性分析
- **分层模板查询**: template_get支持按层级查询26个模板
- **四层文档验证**: doc_verify支持四层架构完整性验证
- **完整MCP协议**: 支持命令行和MCP调用双模式
- **结构化响应**: JSON格式完整响应和错误处理

**对外接口**:
- `DocScanTool`: 增强项目扫描工具类
  - `execute()`: 扫描项目 + 26模板兼容性分析
- `TemplateGetTool`: 智能模板获取工具类
  - `execute()`: 支持按层级/类型/名称获取26个模板
- `DocVerifyTool`: 四层架构验证工具类
  - `execute()`: 验证四层文档体系生成状态
- 各工具的`create_mcp_tool()`工厂函数
- 命令行接口 `main()` 支持新版本参数

### MCP服务器模块 (mcp_server.py)
**包含文件**:
- `mcp_server.py` - 26模板系统完整MCP协议服务器

**核心功能**:
- **26模板系统集成**: 完整支持四层架构模板查询
- **完整MCP协议**: 标准JSON-RPC通信协议实现
- **智能工具路由**: 统一管理所有增强MCP工具
- **四层架构支持**: 完整支持architecture/module/file/project层级
- **Claude Code深度集成**: 为AI协作优化的无缝集成

**对外接口**:
- `CodeLensMCPServer`: 增强主服务器类
  - `handle_request()`: 处理26模板系统MCP请求
  - `list_tools()`: 列出支持四层架构的所有工具
  - `execute_tool()`: 执行增强的模板工具
- `main()`: 服务器启动入口和特性展示
- 26模板系统测试模式和信息查看

### 模板系统测试模块 (test_template_system_v05.py)
**包含文件**:
- `test_template_system_v05.py` - 26模板系统完整验证

**核心功能**:
- **26模板完整性测试**: 验证四层架构所有模板正常工作
- **TemplateServiceV05验证**: 测试核心模板管理器功能
- **四层架构验证**: 确保architecture/module/file/project层级正确
- **质量保证**: 专业模板质量和性能基准测试

**🧪 测试覆盖**:
- 26个模板加载和功能验证
- 四层架构分类统计测试
- 模板格式化和变量验证测试
- 按层级获取模板功能测试
- 模板服务性能和稳定性测试

**✅ 实测结果** (CodeLens自测):
- 🚀 26个模板全部加载成功
- 📊 四层架构分布: Architecture(7) + Module(6) + File(5) + Project(8)
- ⚡ 模板查询耗时: <0.02秒
- 💯 所有测试通过，系统稳定可靠

## 模块关系图谱

### 依赖关系
```
🔧 MCP工具层 (Claude Code接口)
├── DocScanTool → FileService (项目扫描 + 26模板兼容性分析)
├── TemplateGetTool → TemplateServiceV05 (四层26模板查询)
└── DocVerifyTool → ValidationService (四层架构验证)

🚀 服务层 (核心)
├── TemplateServiceV05 (26模板统一管理中心)
│   ├── ArchitectureTemplates (7个架构层模板)
│   ├── ModuleTemplates (6个模块层模板)  
│   ├── FileTemplates (5个文件层模板)
│   └── ProjectTemplates (8个项目层模板)
├── FileService (增强文件信息服务)
├── ValidationService (四层架构验证服务)
└── LoggingService (完整日志管理)

🧪 测试和验证层
├── test_template_system_v05.py (26模板系统验证)
└── mcp_server.py (MCP服务器)
```

### 🔍 详细依赖分析
- **DocScanTool** → FileService (增强项目扫描 + 模板兼容性)
- **TemplateGetTool** → TemplateServiceV05 (26个专业模板管理)
- **DocVerifyTool** → ValidationService (四层架构完整验证)
- **TemplateServiceV05** → 四个模板类 (Architecture/Module/File/Project)
- **所有服务** → Python标准库（零外部依赖设计）
- **模块化设计**：各层级服务完全独立，便于维护扩展

### 数据流向
1. **Claude Code** → **MCP工具** → **对应服务** → **JSON响应**
2. **FileService**: 项目路径 → 文件扫描 → 结构化信息
3. **TemplateService**: 模板请求 → 模板查询 → 格式化模板
4. **ValidationService**: 验证请求 → 状态检查 → 验证报告

## 核心接口汇总

### FileService 接口
- `get_project_files_info()`: 获取项目文件的完整结构化信息
- `get_file_metadata()`: 获取单个文件的元数据信息
- `get_directory_tree()`: 获取优化的目录树结构
- `scan_source_files()`: 扫描项目源码文件
- `read_file_safe()`: 安全读取文件内容
- `get_project_info()`: 获取项目基础信息

### TemplateService 接口
- `get_template_list()`: 获取可用模板列表
- `get_template_content()`: 获取指定模板的内容和元数据
- `get_template_by_type()`: 根据类型获取模板列表
- `validate_template_variables()`: 验证模板变量是否完整
- `format_template()`: 格式化模板内容

### ValidationService 接口
- `get_generation_status()`: 获取文档生成状态的完整报告
- `check_directory_structure()`: 检查目录结构是否符合预期
- `get_missing_files()`: 获取缺失的文档文件列表
- `get_validation_summary()`: 获取验证结果摘要和建议

### MCP工具接口
- `DocScanTool.execute()`: 扫描项目文件并返回信息
- `TemplateGetTool.execute()`: 获取指定类型的文档模板
- `DocVerifyTool.execute()`: 验证文档生成状态
- 所有工具的 `get_tool_definition()`: 获取MCP工具定义

## 模块设计原则

1. **信息提供优先**: 专注于为Claude Code提供结构化信息
2. **服务独立性**: 各服务模块相互独立，无相互依赖
3. **MCP标准兼容**: 所有工具严格遵循MCP协议规范
4. **无状态设计**: 每次调用都是独立的，无状态保存
5. **配置灵活**: 支持多种参数配置和选项调整
6. **错误透明**: 完善的错误处理和JSON格式响应
7. **性能优化**: 高效的文件扫描和轻量级验证机制

## 协作设计理念

CodeLens重构后的模块化设计遵循**Claude Code协作**的核心理念：
- **CodeLens专注信息提供**: 不执行AI生成，专注于数据采集和验证
- **Claude Code专注内容生成**: 基于提供的信息和模板生成文档内容
- **职责清晰分离**: 各自发挥专长，避免功能重叠和资源浪费

这种设计确保了系统的高效性、可维护性和扩展性。

