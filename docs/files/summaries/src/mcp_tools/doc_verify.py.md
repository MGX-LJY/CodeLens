# 文件摘要：doc_verify.py

## 功能概述
MCP协议的doc_verify工具实现，为Claude Code提供文档生成状态验证和完整性检查功能。支持多种验证类型，提供详细的状态报告和改进建议。

## 主要组件

### 类定义
- **DocVerifyTool**: MCP doc_verify工具类，封装所有文档验证功能

### 函数定义
- `get_tool_definition()`: 获取MCP工具定义和验证参数
- `execute()`: 执行文档验证，支持多种验证类型
- `_verify_full_status()`: 执行完整状态验证
- `_verify_structure_only()`: 仅验证目录结构
- `_verify_summary()`: 获取验证摘要
- `_verify_missing_files()`: 检查缺失的文件
- `_get_detailed_layer_info()`: 获取详细的层级信息
- `create_mcp_tool()`: 工厂函数
- `main()`: 命令行接口

### 重要常量和配置
- `tool_name`: "doc_verify"
- 验证类型：full_status, structure_only, summary, missing_files
- 验证选项：包含建议、详细层级信息、文件大小检查等

## 依赖关系

### 导入的模块
- `sys, os, json`: 基础系统操作
- `pathlib.Path`: 路径处理
- `typing`: 类型注解
- `services.validation_service.ValidationService`: 验证服务依赖

### 对外接口
- `DocVerifyTool`: 主要验证工具类
- `create_mcp_tool()`: 工具创建函数
- `main()`: 命令行测试接口

## 关键算法和逻辑
- **多类型验证**: 支持完整状态、结构、摘要、缺失文件等多种验证方式
- **详细报告**: 提供层级状态、完成度、改进建议等详细信息
- **自定义结构**: 支持用户自定义的预期文档结构验证
- **灵活选项**: 根据需求调整验证的详细程度和包含内容

## 备注
为Claude Code提供文档生成状态的实时监控和验证能力，帮助确保文档生成的完整性和质量。