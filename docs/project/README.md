# CodeLens - 智能文档协作平台

## 项目概述

CodeLens 0.6.2.0 是一个专为Claude Code设计的智能化MCP（Model Context Protocol）协作服务器。通过**Task Engine智能任务管理**和**4阶段工作流程**，CodeLens为Claude Code提供从项目分析到文档生成的完整智能化协作体验，实现高质量项目文档的自动化生成。

## 🚀 核心特性

🧠 **Task Engine智能任务管理**：完整的任务生命周期管理和5阶段流程控制
🔄 **4阶段智能工作流**：项目扫描→文件文档→架构分析→项目总结
🎯 **7个智能MCP工具**：涵盖项目分析、任务管理、执行监控的完整工具链
📊 **实时状态跟踪**：支持中断恢复的持久化状态管理和进度监控
🧠 **项目智能分析**：自动识别项目类型、框架、模块，生成定制化文档策略
📚 **10个核心模板系统**：覆盖架构、文件、项目三个文档层级
🛠️ **零依赖设计**：仅使用Python标准库，部署简单

## 快速开始

### 1. 环境要求

- Python 3.9+
- 无外部依赖，使用Python标准库

### 2. 4阶段智能工作流

```bash
# 阶段1: 项目扫描和分析
python src/mcp_tools/doc_guide.py /path/to/your/project

# 阶段2: 文件层文档生成
python src/mcp_tools/task_execute.py /path/to/your/project --task-id <file_task_id>

# 阶段3: 架构层文档生成
python src/mcp_tools/task_execute.py /path/to/your/project --task-id <arch_task_id>

# 阶段4: 项目层文档生成
python src/mcp_tools/task_execute.py /path/to/your/project --task-id <project_task_id>

# 传统工具 (兼容)
python src/mcp_tools/doc_scan.py /path/to/your/project
python src/mcp_tools/template_get.py --list-all
python src/mcp_tools/doc_verify.py /path/to/your/project
```

### 3. 智能化Claude Code协作流程

1. **🧠 项目智能分析**: Claude Code调用doc_guide进行深度项目分析和策略制定
2. **📋 任务计划生成**: 调用task_init生成5阶段完整任务计划
3. **⚡ 智能任务执行**: 调用task_execute获取执行上下文和模板信息
4. **📊 实时状态监控**: 调用task_status检查进度和健康状态
5. **✅ 完整性验证**: 使用doc_verify验证最终文档体系

## 项目状态

🚀 **Task Engine智能化重大更新**

**✅ 核心功能特性**:
- ✅ **Task Engine智能管理** - 完整的任务生命周期管理和5阶段流程控制
- ✅ **7个智能MCP工具** - doc_guide, task_init, task_execute, task_status + 原有3工具
- ✅ **智能项目分析** - 自动识别项目类型、框架、模块，生成定制化策略
- ✅ **实时状态跟踪** - 支持中断恢复的持久化状态管理
- ✅ **5阶段工作流程** - 扫描→规划→执行→监控→验证的完整闭环
- ✅ **核心模板库** - 16个核心模板，覆盖主要文档需求
- ✅ **智能模板服务** - 按层级、类型、名称灵活查询模板
- ✅ **完整MCP服务器** - 生产就绪的协议服务器实现

**🚀 v智能化优势**:
- 🧠 **智能化协作**: 从被动信息提供到主动智能协作
- ⚡ **任务驱动**: 完整的任务生命周期管理和进度跟踪
- 📊 **状态感知**: 实时监控和健康检查机制
- 🔧 **流程标准化**: 4阶段严格依赖验证和100%完成率要求
- 🎯 **上下文增强**: 为AI提供丰富的执行上下文和指导信息

## 技术架构

### 🚀 Task Engine智能任务管理架构

CodeLens  引入了Task Engine智能任务管理层，实现4阶段工作流程控制：

```
🧠 Task Engine层 (v核心)
├── TaskManager - 智能任务管理器 (依赖关系、优先级调度)
├── PhaseController - 4阶段严格控制器 (100%完成率要求)
└── StateTracker - 状态跟踪器 (持久化、进度监控、健康检查)

🔧 7个智能MCP工具
├── 基础工具 (3个): doc_scan, template_get, doc_verify
└── Task Engine工具 (4个): doc_guide, task_init, task_execute, task_status

🛠️ 服务支撑层
├── TemplateService - 10个模板管理
├── FileService - 项目文件信息服务  
└── ValidationService - 文档验证服务
```

### 🏗️ 4阶段智能工作流程

```
Phase 1: 项目扫描 → Phase 2: 文件文档 → Phase 3: 架构文档 → Phase 4: 项目总结

每阶段100%完成后才能进入下一阶段，确保文档质量
```

### 📚 三层文档模板体系 (10个)

```
🏛️ 架构层 (6个) - 系统概述、技术栈、数据流、组件图、部署图
📄 文件层 (1个) - 详细文件分析，包含流程图、作用域分析、依赖关系
📈 项目层 (3个) - README、变更日志、发展路线
```

### 🎯 智能化AI协作工作流
1. **🧠 深度项目分析**: doc_guide智能识别项目类型、框架、模块特征
2. **📋 智能任务规划**: task_init生成4阶段完整任务计划和依赖图谱
3. **⚡ 任务执行驱动**: task_execute提供执行上下文、模板和指导信息
4. **📊 实时状态监控**: task_status全面监控进度和健康状态
5. **✅ 完整性验证**: doc_verify确保最终文档体系完整性

## 使用示例

### 🎯 MCP服务器部署

```bash
# 1. 启动Task Engine智能MCP服务器
python mcp_server.py

# 2. 测试智能工作流功能
python mcp_server.py test /path/to/project

# 3. 查看服务器信息和7个工具
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
      }
    }
  }
}
```

### 🚀 Task Engine智能工作流示例

```bash
# 完整4阶段工作流演示
📊 Phase 1: 项目扫描和分析
├── 检测到: Python Flask项目
├── 识别框架: Flask + SQLAlchemy  
├── 文件分析: 20个核心Python文件
└── 生成策略: 文件分析→架构设计→项目文档

⚡ Phase 2-4: 智能执行
├── Phase 2: 文件层文档 (20个文件)
├── Phase 3: 架构层文档 (6个架构文档)
├── Phase 4: 项目层文档 (3个项目文档)
└── 实时进度: 65.5% (19/29任务完成)
```

### 🎭 智能化协作流程

```mermaid
sequenceDiagram
    participant CC as Claude Code
    participant TE as Task Engine
    participant CL as CodeLens Services
    
    CC->>TE: doc_guide(project_path)
    TE-->>CC: 深度项目分析+策略
    
    CC->>TE: task_init(analysis_result)
    TE-->>CC: 4阶段完整任务计划
    
    loop 任务执行循环
        CC->>TE: task_execute(task_id)
        TE-->>CC: 执行上下文+模板+指导
        Note over CC: AI生成文档内容
        CC->>TE: task_execute(complete)
        TE-->>CC: 任务状态更新+下一个任务
    end
    
    CC->>TE: task_status(overall_status)
    TE-->>CC: 完整进度报告+健康状态
```

## 开发路线图

### Phase 1: 基础架构 ✅
- ✅ 重构为Claude Code协作助手
- ✅ 实现三个核心MCP工具
- ✅ 完善服务层架构
- ✅ 100%测试覆盖率

### Phase 2: 可观测性 ✅
- ✅ **完整日志系统**：结构化日志、异步写入
- ✅ **文件轮转机制**：按大小/时间轮转、自动压缩
- ✅ **监控统计**：操作追踪、性能分析
- ✅ **配置管理**：JSON配置文件、运行时更新

### Phase 3: Task Engine智能化 ✅ (v)
- ✅ **Task Engine核心**: TaskManager, PhaseController, StateTracker
- ✅ **4个新增智能工具**: doc_guide, task_init, task_execute, task_status  
- ✅ **4阶段工作流程**: 严格阶段控制和100%完成率要求
- ✅ **智能项目分析**: 自动识别项目类型、框架、模块
- ✅ **状态持久化**: 支持中断恢复的完整状态跟踪
- ✅ **实时监控**: 健康检查和性能监控机制

### Phase 4: 功能增强 (计划中)
- 🔄 支持更多编程语言 (JS/TS, Go, Rust, Java等)
- 🔄 增强模板系统，支持自定义模板和变量
- 🔄 并发任务执行优化
- 🔄 Web界面状态监控仪表板

### Phase 5: 生态集成 (规划中)
- 🔜 Claude Code深度集成优化
- 🔜 Docker容器化部署方案
- 🔜 集成CI/CD工作流
- 🔜 多项目并行支持

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交改动
4. 发起Pull Request

## 许可证

[MIT License](LICENSE)