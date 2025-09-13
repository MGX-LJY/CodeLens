# CodeLens 系统架构概述

## 项目概况
CodeLens是专为Claude Code设计的Document-Driven MCP服务器，提供结构化文件信息、文档模板和验证服务，支持高效的项目理解和文档生成协作。

## 技术栈分析

### 核心技术栈
- **开发语言**: Python 3.9+ (零外部依赖)
- **协作协议**: MCP (Model Context Protocol)
- **文档架构**: 四层体系 (Architecture/Module/File/Project)
- **文件处理**: pathlib + glob
- **数据格式**: JSON结构化响应

## 架构模式

### 1. 服务层 (Services Layer)
- **FileService**: 项目文件扫描和元数据提取
- **TemplateService**: 16个核心模板统一管理
- **ValidationService**: 文档结构验证和状态报告

### 2. MCP接口层 (MCP Interface Layer)  
- **doc_scan**: 项目文件扫描工具
- **template_get**: 文档模板获取工具
- **doc_verify**: 文档验证工具

### 3. 协作流程层 (Collaboration Layer)
Claude Code协作流程：扫描项目 → 获取模板 → 生成文档 → 验证完整性

## 核心组件

### FileService
- 项目文件信息提取
- 目录树生成
- 文件元数据管理

### TemplateService
- 16个核心模板管理
- 四层模板架构支持
- 智能模板查询

### ValidationService
- 文档结构验证
- 生成状态检查
- 完整性报告

## 数据流设计
1. **信息收集**: 项目路径 → 文件扫描 → 结构化数据
2. **模板提供**: 模板请求 → 模板查询 → 格式化模板
3. **文档验证**: 验证请求 → 结构检查 → 状态分析
4. **协作循环**: 信息 → 生成 → 验证 → 优化

## 系统边界和约束
- **项目类型**: Python项目为主，可扩展
- **文件大小**: 单文件最大50KB
- **部署方式**: 命令行工具 + MCP服务器
- **设计原则**: 信息提供者，不执行内容生成

## 部署架构

### 命令行使用
```bash
python src/mcp_tools/doc_scan.py /path/to/project
python src/mcp_tools/template_get.py --list-all
python src/mcp_tools/doc_verify.py /path/to/project
```

### MCP服务器集成
支持Claude Code直接调用，提供标准MCP协议接口