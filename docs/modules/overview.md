# CodeLens 模块总览

## 识别的功能模块

基于CodeLens项目结构分析，识别出以下主要功能模块：

1. **服务模块** (`src/services/`) - 核心服务实现
2. **模板模块** (`src/templates/`) - 文档模板和AI提示词管理
3. **MCP工具模块** (`src/mcp_tools/`) - MCP协议接口实现
4. **文档生成模块** (`src/doc_generator.py`) - 核心业务逻辑
5. **工具脚本模块** (`generate_docs_structure.py`) - 项目初始化工具

## 模块详细信息

### 服务模块 (src/services/)
**包含文件**:
- `file_service.py` - 文件系统操作服务
- `ai_service.py` - AI内容生成服务
- `__init__.py` - 包初始化

**核心功能**:
- 项目文件扫描和读取
- 目录结构分析
- AI内容生成抽象接口
- Mock AI服务实现（用于测试）

**对外接口**:
- `FileService`: 文件操作相关服务
- `AIService`: AI生成服务抽象基类
- `MockAIService`: 测试用AI服务实现
- `create_ai_service()`: AI服务工厂函数

### 模板模块 (src/templates/)
**包含文件**:
- `document_templates.py` - 文档模板和提示词定义
- `__init__.py` - 包初始化

**核心功能**:
- 管理文档生成模板
- 构建AI提示词
- 格式化输出内容
- 提供标准化文档结构

**对外接口**:
- `DocumentTemplates`: 模板常量类
- `TemplateService`: 模板服务类
- 各种提示词构建方法

### MCP工具模块 (src/mcp_tools/)
**包含文件**:
- `doc_init.py` - doc_init MCP工具实现
- `__init__.py` - 包初始化

**核心功能**:
- MCP协议工具接口
- 命令行接口
- 参数验证和错误处理
- 工具定义和执行

**对外接口**:
- `DocInitTool`: MCP工具类
- `create_mcp_tool()`: 工具创建函数
- 命令行入口 `main()`

### 文档生成模块 (src/doc_generator.py)
**包含文件**:
- `doc_generator.py` - 三层文档生成器

**核心功能**:
- 协调各服务完成文档生成
- 实现三层渐进式生成流程
- 管理生成状态和数据流
- 提供统一的生成接口

**对外接口**:
- `ThreeLayerDocGenerator`: 主要生成器类
- `generate_project_docs()`: 主要生成方法

### 工具脚本模块 (generate_docs_structure.py)
**包含文件**:
- `generate_docs_structure.py` - 文档结构初始化脚本

**核心功能**:
- 快速生成项目文档目录结构
- 创建空白文档文件
- 提供项目初始化功能

**对外接口**:
- `create_file()`: 文件创建函数
- `main()`: 脚本主入口

## 模块关系图谱

### 依赖关系
```
ThreeLayerDocGenerator (核心)
├── FileService (文件操作)
├── TemplateService (模板管理) 
├── AIService (内容生成)
└── DocInitTool (MCP接口)
    └── ThreeLayerDocGenerator
```

### 详细依赖分析
- **ThreeLayerDocGenerator** → FileService, TemplateService, AIService
- **DocInitTool** → ThreeLayerDocGenerator
- **TemplateService** → 独立模块（无依赖）
- **FileService** → 标准库（pathlib, os, glob）
- **AIService** → 独立接口，具体实现可变

### 数据流向
1. **MCP工具** → **文档生成器** → **各个服务**
2. **文件服务** → **模板服务** → **AI服务** → **输出文件**
3. **三层渐进**: 文件层 → 模块层 → 架构层

## 核心接口汇总

### FileService 接口
- `scan_source_files()`: 扫描项目源码文件
- `read_file_safe()`: 安全读取文件内容
- `scan_directory_structure()`: 分析目录结构
- `get_project_info()`: 获取项目基础信息

### TemplateService 接口
- `build_file_analysis_prompt()`: 构建文件分析提示词
- `build_module_analysis_prompt()`: 构建模块分析提示词
- `build_architecture_analysis_prompt()`: 构建架构分析提示词
- `format_file_summary()`: 格式化文件摘要

### AIService 接口
- `generate_file_summary()`: 生成文件摘要
- `generate_module_analysis()`: 生成模块分析
- `generate_architecture_doc()`: 生成架构文档
- `batch_generate_file_summaries()`: 批量生成文件摘要

### ThreeLayerDocGenerator 接口
- `generate_project_docs()`: 主要生成方法
- `_generate_file_layer()`: 生成文件层文档
- `_generate_module_layer()`: 生成模块层文档
- `_generate_architecture_layer()`: 生成架构层文档

### DocInitTool 接口
- `execute()`: 执行MCP工具
- `get_tool_definition()`: 获取工具定义

## 模块设计原则

1. **单一职责**: 每个模块专注于特定功能域
2. **依赖注入**: 通过构造函数注入依赖服务
3. **接口抽象**: AI服务等关键组件提供抽象接口
4. **配置驱动**: 支持通过配置调整行为
5. **错误处理**: 各模块都有完善的错误处理机制

这种模块化设计确保了CodeLens的可扩展性、可测试性和可维护性。

