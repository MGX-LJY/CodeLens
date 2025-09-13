# CodeLens 模块总览

## 识别的功能模块

基于重构后的CodeLens项目结构分析，识别出以下主要功能模块：

1. **服务模块** (`src/services/`) - 核心信息提供服务
2. **模板模块** (`src/templates/`) - 文档模板资源管理
3. **MCP工具模块** (`src/mcp_tools/`) - MCP协议接口实现
4. **日志模块** (`src/logging/`) - 企业级日志系统
5. **工具脚本模块** (`generate_docs_structure.py`) - 项目文档结构初始化

## 模块详细信息

### 服务模块 (src/services/)
**包含文件**:
- `file_service.py` - 文件系统操作和信息提取服务
- `validation_service.py` - 文档验证和状态报告服务  
- `__init__.py` - 包初始化

**核心功能**:
- 项目文件扫描、读取和元数据提取
- 目录树结构生成和分析
- 文档生成状态验证和报告
- 文件存在性检查（不读取内容）

**对外接口**:
- `FileService`: 完整的文件信息提供服务
  - `get_project_files_info()`: 获取项目完整信息
  - `get_file_metadata()`: 获取文件元数据
  - `get_directory_tree()`: 生成目录树结构
- `ValidationService`: 文档验证服务
  - `get_generation_status()`: 获取文档生成状态
  - `check_directory_structure()`: 检查目录结构
  - `get_validation_summary()`: 获取验证摘要

### 模板模块 (src/templates/)
**包含文件**:
- `document_templates.py` - 文档模板资源管理
- `__init__.py` - 包初始化

**核心功能**:
- 管理标准化的文档模板资源
- 提供模板查询和元数据服务
- 支持模板变量验证和格式化
- 维护多种文档类型的模板

**提供的模板类型**:
- `file_summary`: 文件摘要模板
- `module_analysis`: 模块分析模板  
- `architecture`: 架构概述模板
- `project_readme`: 项目README模板

**对外接口**:
- `TemplateService`: 模板服务类
  - `get_template_list()`: 获取所有模板列表
  - `get_template_content()`: 获取指定模板内容
  - `get_template_by_type()`: 按类型筛选模板
  - `validate_template_variables()`: 验证模板变量
  - `format_template()`: 格式化模板内容

### MCP工具模块 (src/mcp_tools/)
**包含文件**:
- `doc_scan.py` - 项目文件扫描工具
- `template_get.py` - 模板获取工具
- `doc_verify.py` - 文档验证工具
- `__init__.py` - 包初始化和统一导出

**核心功能**:
- 提供三个独立的MCP协议工具
- 支持命令行和MCP调用两种方式
- 完善的参数验证和错误处理
- JSON格式的结构化响应

**对外接口**:
- `DocScanTool`: 项目扫描工具类
  - `execute()`: 扫描项目并返回文件信息
- `TemplateGetTool`: 模板获取工具类
  - `execute()`: 获取指定类型的文档模板
- `DocVerifyTool`: 文档验证工具类
  - `execute()`: 验证文档生成状态
- 各工具的`create_mcp_tool()`工厂函数
- 命令行接口 `main()`

### 工具脚本模块 (generate_docs_structure.py)
**包含文件**:
- `generate_docs_structure.py` - 文档结构初始化脚本

**核心功能**:
- 快速生成项目文档目录结构
- 创建标准的五层文档目录
- 生成示例文档文件
- 为新项目提供文档初始化功能

**对外接口**:
- `create_file()`: 文件创建函数
- `create_directory()`: 目录创建函数
- `main()`: 脚本主入口

## 模块关系图谱

### 依赖关系
```
MCP工具层 (接口)
├── DocScanTool → FileService
├── TemplateGetTool → TemplateService
└── DocVerifyTool → ValidationService

服务层 (核心)
├── FileService (独立服务)
├── TemplateService (独立服务)
└── ValidationService (独立服务)

工具脚本
└── generate_docs_structure.py (独立脚本)
```

### 详细依赖分析
- **DocScanTool** → FileService
- **TemplateGetTool** → TemplateService  
- **DocVerifyTool** → ValidationService
- **所有服务** → Python标准库（pathlib, os, glob, datetime等）
- **各服务相互独立**，无相互依赖关系

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

