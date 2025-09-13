# CodeLens 系统架构概述

## 项目概况

CodeLens 是一个为Claude Code设计的MCP（Model Context Protocol）协作服务器。它不再执行AI驱动的文档生成，而是专门为Claude Code提供结构化的项目文件信息、文档模板资源和验证服务，让Claude Code能够高效地理解和生成项目文档。

## 技术栈分析

### 核心技术栈
- **开发语言**: Python 3.9+
- **架构协议**: MCP (Model Context Protocol)
- **文件处理**: pathlib + glob 高效文件操作
- **模板系统**: 字符串格式化 + 结构化元数据
- **验证机制**: 文件存在性检查（不读取内容）
- **数据格式**: JSON结构化数据交换
- **日志系统**: 企业级本地日志解决方案，支持结构化日志、文件轮转和监控

## 架构模式

CodeLens 采用**Claude Code协作助手架构**：

### 1. 服务层 (Services Layer)
- **FileService**: 项目文件扫描、元数据提取、目录树生成
- **TemplateService**: 文档模板管理、模板查询和格式化
- **ValidationService**: 文档结构验证、生成状态报告
- **LoggingService**: 企业级日志管理、操作追踪和性能监控

### 2. MCP接口层 (MCP Interface Layer)
- **doc_scan**: 扫描项目文件并返回结构化信息
- **template_get**: 提供各种文档模板资源
- **doc_verify**: 验证文档生成状态和完整性

### 3. 协作流程层 (Collaboration Layer)
- **信息提供者**: CodeLens提供项目文件信息和模板
- **内容生成者**: Claude Code基于提供的信息生成文档
- **状态验证**: CodeLens验证生成的文档结构完整性

## 核心组件

### 1. 文件服务 (FileService)
**职责**: 为Claude Code提供完整的项目文件信息
- get_project_files_info(): 获取项目文件的完整结构化信息
- get_file_metadata(): 获取单个文件的元数据（大小、修改时间等）
- get_directory_tree(): 生成优化的目录树结构
- scan_source_files(): 智能文件扫描和过滤
- read_file_safe(): 安全文件读取（带大小限制）

### 2. 模板服务 (TemplateService)
**职责**: 为Claude Code提供标准化的文档模板
- get_template_list(): 获取所有可用模板的元数据
- get_template_content(): 获取特定模板的内容和信息
- get_template_by_type(): 按类型筛选模板
- validate_template_variables(): 验证模板变量完整性
- format_template(): 格式化模板内容

**提供的模板类型**:
- file_summary: 文件摘要模板
- module_analysis: 模块分析模板  
- architecture: 架构概述模板
- project_readme: 项目README模板

### 3. 验证服务 (ValidationService)
**职责**: 验证文档生成状态但不读取内容
- get_generation_status(): 获取文档生成的完整状态报告
- check_directory_structure(): 检查目录结构是否符合预期
- get_missing_files(): 获取缺失的文档文件列表
- get_validation_summary(): 获取验证结果摘要和改进建议

### 4. 日志服务 (LoggingService)
**职责**: 提供企业级日志管理和可观测性能力
- LogManager: 统一日志管理器，支持结构化JSON日志
- FileRotator: 文件轮转器，按大小/时间轮转和gzip压缩
- LogConfig: 配置管理器，支持JSON配置文件和运行时更新
- 操作追踪: 记录操作开始/结束和耗时统计
- 异步写入: 后台线程处理，不阻塞主业务流程
- 监控统计: 操作追踪、性能分析、磁盘使用监控

### 5. MCP工具集合
**职责**: 提供标准MCP协议接口

#### doc_scan工具
- 扫描项目文件并返回结构化信息
- 支持内容包含/排除选项
- 提供文件统计和元数据

#### template_get工具  
- 按名称或类型获取文档模板
- 提供模板使用示例和变量验证
- 支持多种返回格式

#### doc_verify工具
- 验证文档生成状态和结构完整性
- 提供详细的层级信息和改进建议
- 支持自定义验证规则

## 数据流设计

### Claude Code协作流程
1. **项目扫描请求**: Claude Code → doc_scan → 项目文件信息
2. **模板获取请求**: Claude Code → template_get → 文档模板资源
3. **内容生成阶段**: Claude Code基于文件信息和模板生成文档
4. **验证检查请求**: Claude Code → doc_verify → 生成状态报告
5. **迭代优化**: 基于验证结果继续完善文档

### 关键数据流
1. **信息收集**: 项目路径 → 文件扫描 → 结构化数据 → JSON响应
2. **模板提供**: 模板请求 → 模板查询 → 格式化模板 → JSON响应
3. **文档验证**: 验证请求 → 结构检查 → 状态分析 → JSON响应
4. **日志记录**: 操作开始 → 业务执行 → 操作结束 → 日志持久化
5. **协作循环**: 信息 → 生成 → 验证 → 改进 → 完成（全程日志追踪）

## 系统边界和约束

### 输入边界
- **支持的项目类型**: 主要支持Python项目，可扩展其他语言
- **文件大小限制**: 单文件最大50KB（可配置）
- **项目规模**: 适合中小型到大型项目（高效的文件扫描机制）
- **目录深度**: 目录树扫描最大深度3层（可配置）

### 输出边界
- **数据格式**: JSON格式的结构化数据响应
- **模板格式**: Markdown模板，支持变量替换
- **验证范围**: 文件存在性检查，不读取文件内容
- **MCP协议**: 标准MCP工具接口，支持命令行调用

### 系统约束
- **专注信息提供**: 不执行AI内容生成，专注于数据提供
- **无状态设计**: 每次MCP调用都是独立的，无状态保存
- **文件系统依赖**: 依赖本地文件系统访问权限
- **Python环境**: 需要Python 3.9+运行环境

## 部署架构

### 命令行部署
```bash
# 扫描项目文件
python src/mcp_tools/doc_scan.py /path/to/project

# 获取文档模板
python src/mcp_tools/template_get.py --list-all

# 验证文档状态
python src/mcp_tools/doc_verify.py /path/to/project
```

### 🚀 MCP服务器部署 (v0.4.0新增)
```bash
# 启动MCP服务器
python mcp_server.py

# 测试模式 - 验证所有功能
python mcp_server.py test /path/to/project

# 查看服务器信息
python mcp_server.py info
```

### 🔧 Claude Code集成配置
```json
{
  "mcpServers": {
    "codelens": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/codelens",
      "env": {
        "PYTHONPATH": "/path/to/codelens"
      },
      "description": "CodeLens MCP服务器",
      "capabilities": ["tools"]
    }
  }
}
```

### 📊 实际性能验证 (微信自动化项目测试)
```
🎯 测试项目: wechat-automation-project
📁 扫描文件: 118个 (Python, Markdown, JSON)
📊 项目大小: 1.8MB 
⏱️ 扫描耗时: 0.07秒
🎨 生成文档: 7个文件
💯 完成状态: 25.0% → minimal
```

### 模块化设计
- **服务独立**: 各服务组件职责清晰，可独立测试和维护
- **模板可扩展**: 支持添加新的文档模板类型
- **工具可插拔**: MCP工具可独立部署和调用
- **配置灵活**: 支持多种配置参数和选项

