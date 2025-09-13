# CodeLens 系统架构概述

## 项目概况
CodeLens是专为Claude Code设计的智能化任务驱动MCP服务器，提供结构化项目分析、自动化任务管理和5阶段文档生成流程，支持高效的项目理解和协作式文档生成。

## 技术栈分析

### 核心技术栈
- **开发语言**: Python 3.9+ (零外部依赖)
- **协作协议**: MCP (Model Context Protocol)
- **文档架构**: 四层体系 (Architecture/Module/File/Project)
- **文件处理**: pathlib + glob
- **数据格式**: JSON结构化响应

## 架构模式

### 1. 任务引擎层 (Task Engine Layer)
- **TaskManager**: 智能任务管理器，支持依赖关系和优先级调度
- **PhaseController**: 5阶段严格控制器（扫描→文件→模块→架构→项目）
- **StateTracker**: 持久化状态跟踪和进度监控

### 2. 服务层 (Services Layer)
- **FileService**: 项目文件扫描和智能过滤
- **TemplateService**: 16个核心模板统一管理
- **ValidationService**: 文档结构验证和状态报告

### 3. MCP接口层 (MCP Interface Layer)  
- **doc_scan**: 项目文件扫描工具（智能过滤增强）
- **template_get**: 文档模板获取工具
- **doc_verify**: 文档验证工具
- **doc_guide**: 智能项目分析和策略生成工具
- **task_init**: 任务初始化和计划生成工具
- **task_execute**: 任务执行和上下文管理工具
- **task_status**: 进度监控和状态检查工具

### 4. 协作流程层 (Collaboration Layer)
Claude Code协作流程：项目分析 → 任务生成 → 阶段执行 → 进度监控 → 文档验证

## 核心组件

### TaskManager
- 任务创建和依赖管理
- 优先级调度和状态跟踪
- 阶段性任务组织

### PhaseController  
- 5阶段严格流程控制
- 阶段依赖验证
- 进度门控机制

### StateTracker
- 任务状态持久化存储
- 执行历史和性能监控
- 健康检查和异常恢复

### FileService
- 项目文件信息提取和智能过滤
- 目录树生成和项目类型检测
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

### 5阶段工作流程
1. **阶段1 - 项目分析**: 项目路径 → 智能扫描 → 项目特征分析 → 生成策略
2. **阶段2 - 任务规划**: 分析结果 → 任务生成 → 依赖图构建 → 执行计划  
3. **阶段3 - 文件文档**: 核心文件 → 模板匹配 → 内容生成 → 状态跟踪
4. **阶段4 - 模块架构**: 模块分析 → 关系映射 → 架构设计 → 技术栈文档
5. **阶段5 - 项目总结**: 整体梳理 → README生成 → 项目完整性验证

### 严格阶段控制
- 100%完成率要求：每阶段必须达到100%完成率才能进入下一阶段
- 依赖关系验证：自动检查任务依赖关系，确保执行顺序正确
- 状态持久化：实时保存执行状态，支持中断恢复

## 系统边界和约束
- **项目类型**: 支持Python/JavaScript/Java/Go/Rust等主流项目
- **文件大小**: 单文件最大50KB，智能过滤优化性能
- **部署方式**: 命令行工具 + MCP服务器
- **设计原则**: 智能化任务驱动，协作式文档生成

## 部署架构

### 命令行使用
```bash
# 智能项目分析
python src/mcp_tools/doc_guide.py /path/to/project

# 任务管理
python src/mcp_tools/task_init.py /path/to/project --analysis-file analysis.json
python src/mcp_tools/task_execute.py /path/to/project --task-id <task_id> --mode execute
python src/mcp_tools/task_status.py /path/to/project --type overall_status

# 文件和模板操作
python src/mcp_tools/doc_scan.py /path/to/project --no-content
python src/mcp_tools/template_get.py --list-all
python src/mcp_tools/doc_verify.py /path/to/project
```

### MCP服务器集成
支持Claude Code直接调用7个MCP工具，提供完整的智能化文档生成工作流