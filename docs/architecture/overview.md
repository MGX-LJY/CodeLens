# CodeLens 系统架构概述

## 项目概况

CodeLens 是一个文档驱动的MCP（Model Context Protocol）服务器，专门用于AI驱动的代码理解和文档生成。系统通过三层渐进式文档生成架构，将复杂的代码项目转化为结构化的文档，为AI提供更好的代码理解能力。

## 技术栈分析

### 核心技术栈
- **开发语言**: Python 3.9+
- **架构协议**: MCP (Model Context Protocol)
- **AI集成**: 可插拔的AI服务接口（当前支持Mock实现）
- **文档格式**: Markdown + 结构化模板
- **配置管理**: Python字典配置（计划扩展到YAML）
- **文件处理**: 基于pathlib的现代Python文件操作

## 架构模式

CodeLens 采用**服务导向的三层生成架构**：

### 1. 服务层 (Services Layer)
- **FileService**: 文件扫描、读取、路径管理
- **TemplateService**: 文档模板管理和格式化
- **AIService**: AI内容生成抽象接口

### 2. 生成层 (Generation Layer)
- **ThreeLayerDocGenerator**: 核心文档生成器
- **文档生成流程**: 文件层 → 模块层 → 架构层

### 3. 接口层 (Interface Layer)  
- **MCP工具接口**: doc_init等标准MCP工具
- **命令行接口**: 直接调用和测试接口

## 核心组件

### 1. 文件服务 (FileService)
**职责**: 项目文件的扫描、读取和管理
- scan_source_files(): 智能文件扫描
- read_file_safe(): 安全文件读取（带大小限制）
- scan_directory_structure(): 目录结构分析
- get_project_info(): 项目基础信息提取

### 2. 模板服务 (TemplateService)
**职责**: 文档模板管理和AI提示词生成
- 文档模板: FILE_SUMMARY, MODULE_ANALYSIS, ARCHITECTURE
- AI提示词: file_analysis, module_analysis, architecture_analysis
- 格式化方法: 模板填充和内容格式化

### 3. AI服务 (AIService)
**职责**: AI内容生成的抽象接口
- MockAIService: 测试用的模拟实现
- generate_file_summary(): 文件摘要生成
- generate_module_analysis(): 模块分析生成
- generate_architecture_doc(): 架构文档生成

### 4. 三层文档生成器 (ThreeLayerDocGenerator)
**职责**: 核心业务逻辑，协调各服务完成文档生成
- _generate_file_layer(): 第三层文件文档生成
- _generate_module_layer(): 第二层模块文档生成  
- _generate_architecture_layer(): 第一层架构文档生成

## 数据流设计

### 三层渐进生成流程
1. **项目扫描**: 项目路径 → 文件列表 → 文件内容读取
2. **文件层生成**: 逐个文件 → AI分析 → 文件摘要文档
3. **模块层生成**: 收集文件摘要 → AI识别模块 → 模块关系文档
4. **架构层生成**: 基于模块分析 → AI生成架构 → 架构概述文档
5. **报告生成**: 汇总统计信息 → 生成完整报告

### 关键数据流
1. **输入处理**: 项目路径 → 文件列表 → 文件内容
2. **AI处理**: 内容 + 模板 → AI提示词 → 生成结果
3. **输出格式化**: AI结果 → 模板填充 → Markdown文档
4. **层级传递**: 下层结果作为上层输入的上下文

## 系统边界和约束

### 输入边界
- **支持的项目类型**: 当前仅支持Python项目（.py文件）
- **文件大小限制**: 单文件最大50KB（可配置）
- **项目规模**: 适合中小型项目（< 1000文件）

### 输出边界
- **文档格式**: Markdown格式的结构化文档
- **存储位置**: 项目根目录下的docs/目录
- **文档层次**: 三层固定结构（architecture, modules, files）

### 系统约束
- **AI服务依赖**: 当前为Mock实现，需要集成真实AI服务
- **语言支持**: 当前仅支持Python，计划扩展其他语言
- **配置能力**: 配置选项有限，需要增强配置系统

## 部署架构

### 开发部署
```bash
# 直接运行
python src/mcp_tools/doc_init.py /path/to/project

# 作为模块调用
from src.doc_generator import ThreeLayerDocGenerator
generator = ThreeLayerDocGenerator()
generator.generate_project_docs(project_path)
```

### MCP服务部署
```python
# MCP工具定义
{
  "name": "doc_init",
  "description": "初始化项目的三层文档结构",
  "parameters": {
    "project_path": "string",
    "output_path": "string", 
    "config": "object"
  }
}
```

### 扩展性设计
- **AI服务可插拔**: 通过工厂模式支持不同AI实现
- **模板可定制**: 支持自定义文档模板
- **语言可扩展**: 通过语言特定的解析器支持多语言
- **配置可扩展**: 支持YAML/JSON配置文件

