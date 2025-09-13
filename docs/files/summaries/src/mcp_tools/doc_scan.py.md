# 文件摘要：doc_scan.py

## 功能概述
MCP协议的doc_scan工具实现，专门为Claude Code提供项目文件的结构化扫描功能。替代了原有的doc_init工具，专注于信息收集而非文档生成。

## 主要组件

### 类定义
- **DocScanTool**: MCP doc_scan工具类，封装所有项目扫描功能

### 函数定义
- `get_tool_definition()`: 获取MCP工具定义和参数模式
- `execute()`: 执行项目扫描并返回结构化信息
- `_success_response()`: 生成成功响应格式
- `_error_response()`: 生成错误响应格式
- `create_mcp_tool()`: 创建工具实例的工厂函数
- `main()`: 命令行入口函数

### 重要常量和配置
- `tool_name`: "doc_scan"
- `description`: 工具功能描述
- 默认配置参数：文件扩展名、排除模式、文件大小限制等

## 依赖关系

### 导入的模块
- `sys, os`: 系统操作和路径管理
- `json`: JSON数据处理
- `pathlib.Path`: 文件路径操作
- `argparse`: 命令行参数解析
- `services.file_service.FileService`: 文件服务依赖

### 对外接口
- `DocScanTool`: MCP工具类
- `create_mcp_tool()`: 工具创建函数
- `main()`: 命令行接口

## 关键算法和逻辑
- **MCP协议适配**: 将FileService的功能包装成标准MCP工具
- **参数验证**: 完整的项目路径和参数有效性检查
- **结构化响应**: 返回包含文件信息、目录树、统计数据的JSON格式响应
- **配置灵活性**: 支持内容包含、文件过滤、大小限制等多种选项

## 备注
这是重构后CodeLens对外的主要接口，专门为Claude Code提供项目扫描能力，支持命令行和MCP两种调用方式。