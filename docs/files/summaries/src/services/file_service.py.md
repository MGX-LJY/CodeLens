# 文件摘要：file_service.py

## 功能概述
增强的文件系统操作服务，为Claude Code提供完整的项目文件信息、元数据提取和目录树生成功能。重构后专注于信息提供而非文档生成。

## 主要组件

### 类定义
- **FileService**: 增强的文件服务类，提供完整的文件信息服务

### 函数定义
- `get_project_files_info()`: 获取项目文件的完整结构化信息（新增核心方法）
- `get_file_metadata()`: 获取文件元数据信息（新增）
- `get_directory_tree()`: 生成优化的目录树结构（新增）
- `scan_source_files()`: 智能扫描项目源代码文件
- `read_file_safe()`: 安全读取文件内容，带大小限制
- `get_project_info()`: 提取项目基础信息
- `scan_directory_structure()`: 分析目录结构（保留兼容性）
- `create_file_summary_path()`: 生成文件摘要输出路径
- `_should_exclude()`: 文件排除规则判断

### 重要常量和配置
- `default_extensions`: 默认扫描的文件扩展名（['.py']）
- `default_excludes`: 默认排除的目录和文件模式

## 依赖关系

### 导入的模块
- `pathlib.Path`: 现代Python文件路径操作
- `os, glob`: 传统文件系统操作
- `typing`: 类型注解支持（增加Any类型）
- `datetime`: 时间戳处理（新增）
- `time`: 性能测量和操作追踪
- `..logging.get_logger`: 企业级日志系统集成（v0.3.0新增）

### 对外接口
- `FileService`: 增强的主要服务类
- 所有公开方法均为Claude Code优化设计
- 集成日志系统，支持操作追踪和性能监控

## 关键算法和逻辑
- **结构化信息提取**: 新增的get_project_files_info()提供一站式项目信息获取
- **元数据丰富**: 文件大小、修改时间、创建时间等详细元数据
- **优化目录树**: 专为Claude Code设计的层次化目录结构
- **统计分析**: 文件类型统计、最大文件、最新文件等智能分析
- **配置灵活**: 支持内容包含/排除、文件大小限制等多种选项
- **操作追踪**: 完整的操作开始/结束日志记录和耗时统计（v0.3.0新增）
- **性能监控**: 文件扫描性能监控、错误追踪和异常处理日志
- **优雅降级**: 日志系统故障时的DummyLogger降级机制

## 备注
重构后的FileService是CodeLens为Claude Code提供信息服务的核心组件，专注于高效的文件信息提取和结构化数据提供。
