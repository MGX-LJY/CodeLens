# 文件摘要：template_get.py

## 功能概述
MCP协议的template_get工具实现，为Claude Code提供标准化的文档模板获取功能。支持多种模板类型和查询方式，提供丰富的模板元数据信息。

## 主要组件

### 类定义
- **TemplateGetTool**: MCP template_get工具类，提供完整的模板查询和获取功能

### 函数定义
- `get_tool_definition()`: 获取MCP工具定义，支持多种查询参数
- `execute()`: 执行模板获取逻辑，支持多种查询模式
- `_get_specific_template()`: 获取特定模板的详细信息
- `_generate_usage_example()`: 生成模板使用示例
- `_get_related_templates()`: 获取相关模板列表
- `create_mcp_tool()`: 工厂函数
- `main()`: 命令行接口

### 重要常量和配置
- `tool_name`: "template_get"
- 支持的模板类型：file_summary, module_analysis, architecture, project_readme
- 支持的返回格式：content_only, with_metadata, full_info

## 依赖关系

### 导入的模块
- `sys, os, json`: 基础系统操作
- `pathlib.Path`: 路径处理
- `typing`: 类型注解
- `templates.document_templates.TemplateService`: 模板服务依赖

### 对外接口
- `TemplateGetTool`: 主要工具类
- `create_mcp_tool()`: 工具创建函数
- `main()`: 命令行测试接口

## 关键算法和逻辑
- **多模式查询**: 支持按名称、类型查询，或列出所有模板
- **格式化输出**: 根据需求返回不同详细程度的模板信息
- **使用示例生成**: 为每种模板类型提供使用示例和变量说明
- **关联关系**: 提供模板间的关联关系信息

## 备注
为Claude Code提供模板资源服务，确保文档生成的标准化和一致性。支持灵活的查询方式和丰富的元数据信息。