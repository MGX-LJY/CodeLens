# 文件摘要：validation_service.py

## 功能概述
文档验证服务实现，专门用于检查文档生成状态和文件结构完整性，但不读取文件内容。为Claude Code提供轻量级的验证和状态报告功能。

## 主要组件

### 类定义
- **ValidationService**: 文档验证服务的主要类，提供完整的文档状态检查功能

### 函数定义
- `check_file_exists()`: 检查单个文件是否存在
- `check_directory_exists()`: 检查目录是否存在
- `get_directory_files()`: 获取目录下的文件列表（不读取内容）
- `check_directory_structure()`: 检查目录结构是否符合预期
- `get_missing_files()`: 获取缺失的文件列表
- `get_generation_status()`: 获取文档生成状态的完整报告
- `validate_expected_structure()`: 验证项目是否具有预期的文档结构
- `get_validation_summary()`: 获取验证结果摘要

### 重要常量和配置
- `expected_structure`: 预期的文档目录结构定义
- 各种状态常量：'not_initialized', 'minimal', 'partial', 'mostly_complete', 'complete'

## 依赖关系

### 导入的模块
- `pathlib.Path`: 文件路径操作
- `typing`: 类型注解支持
- `datetime`: 时间戳处理

### 对外接口
- `ValidationService`: 主要验证服务类
- 完整的验证方法集合

## 关键算法和逻辑
- **轻量级验证**: 只检查文件存在性，不读取文件内容
- **结构化状态报告**: 提供详细的文档生成状态分析
- **完成度计算**: 基于文件数量和预期结构计算完成百分比
- **建议生成**: 根据当前状态自动生成改进建议

## 备注
这是重构后CodeLens的核心验证组件，专注于为Claude Code提供文档状态信息而非内容生成。