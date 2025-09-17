# CodeLens 技术栈

## 核心技术

### 编程语言
- **Python 3.9+**: 主要开发语言，零外部依赖设计
- **强类型系统**: typing模块完整类型注解
- **现代Python特性**: dataclasses、type hints、pathlib

### 架构模式
- **MCP协议**: Model Context Protocol标准实现
- **六层服务架构**: 任务引擎层、服务层、MCP接口层、热重载系统层、配置管理层、协作流程层
- **智能化任务驱动**: 3阶段工作流程，8种核心任务类型支持
- **严格阶段控制**: 100%完成率要求的阶段门控机制
- **模块化微服务**: 各组件独立部署、测试、维护
- **状态感知设计**: 支持任务状态持久化和中断恢复

### 任务引擎技术
- **TaskManager**: 智能任务调度，支持依赖图和优先级算法
- **PhaseController**: 3阶段严格控制，阶段转换验证机制
- **StateTracker**: 实时状态跟踪，执行历史和性能监控
- **智能调度算法**: 基于依赖关系的DAG（有向无环图）调度
- **状态机设计**: PENDING→IN_PROGRESS→COMPLETED/FAILED/BLOCKED状态转换

### 数据格式
- **JSON**: 结构化数据交换格式
- **Markdown**: 文档模板格式
- **JSON持久化**: 任务状态和执行历史存储

### 文件处理技术
- **pathlib**: 现代Python路径操作
- **glob**: 文件模式匹配和智能过滤
- **LargeFileHandler**: 大文件智能分片处理系统
- **AST解析**: 基于抽象语法树的语义分片
- **智能分片策略**: 50KB阈值，120KB上限，语义完整性保持

### 项目分析技术
- **ProjectAnalyzer**: 项目特征分析和复杂度评估
- **框架识别**: Django/Flask/React/Vue等8+主流框架自动识别
- **项目类型检测**: Python/JavaScript/Java/Go/Rust多语言支持
- **多维度评分**: 文件特征(3分) + 目录结构(2分) + 扩展名统计
- **智能过滤算法**: 基于项目类型的动态过滤策略
- **复杂度评估**: simple/medium/complex三级自动分类

### 热重载技术
- **HotReloadManager**: 热重载协调管理器，统一管理文件监控和模块重载
- **FileWatcher**: 双模式文件监控 (watchdog + 轮询备用)，实时检测代码变化
- **ModuleReloader**: 智能模块重载器，支持依赖分析和安全重载
- **依赖分析**: 自动构建模块依赖关系图，确保正确的重载顺序
- **防抖动机制**: 避免频繁重载，提供稳定的开发体验

### 配置管理技术
- **ConfigManager**: 统一配置管理器，支持多环境配置
- **ConfigSchema**: 强类型配置数据模型，严格验证
- **ConfigValidator**: 配置验证器，确保配置完整性
- **分层配置**: 默认配置→环境配置→用户配置的覆盖机制
- **动态重载**: 配置变更时自动重载相关组件

### 依赖策略
- **核心零依赖**: 核心功能仅使用Python标准库
- **可选增强**: 热重载功能可选依赖watchdog库，提供降级方案
- **轻量级设计**: 最小化资源占用
- **跨平台兼容**: 支持Windows、macOS、Linux

## 关键设计原则

### 性能优化
- **智能文件过滤**: 项目类型感知，大幅减少无关文件处理
- **高效任务调度**: 依赖图优化，避免重复执行
- **快速状态检查**: 毫秒级响应实时进度监控
- **内存优化**: 按需加载和状态持久化机制
- **大文件分片**: AST语义分片，保持代码完整性
- **并发处理**: 支持多任务并发执行

### 可靠性保证
- **异常处理**: 完整的错误捕获和恢复机制
- **优雅降级**: 确保系统在故障时正常运行
- **状态持久化**: 支持中断恢复，提升长时间任务执行稳定性
- **阶段控制**: 严格阶段依赖验证，确保执行正确性
- **文件权限检查**: 确保文件可访问性
- **原子操作**: 关键状态更新使用原子操作

### 可观测性
- **结构化输出**: JSON格式便于解析
- **操作追踪**: 完整的调用链路记录
- **实时监控**: 任务执行状态和进度实时跟踪
- **性能指标**: 详细的执行时间和资源使用统计
- **健康检查**: 自动检测系统健康状态和执行异常
- **状态报告**: 验证和状态检查
- **日志系统**: 分层级、分组件的详细日志记录

### 扩展性设计
- **插件架构**: 支持自定义分片器和模板
- **模板系统**: 10个可扩展的文档模板
- **语言支持**: 可扩展的多编程语言支持
- **任务类型**: 可定义新的任务类型和处理逻辑

## 技术栈详细分析

### 核心库使用
```python
# 标准库核心依赖
import pathlib     # 现代文件路径操作
import json        # 数据序列化
import glob        # 文件模式匹配
import ast         # 语法树解析
import logging     # 日志系统
import time        # 时间和性能监控
import hashlib     # 文件指纹和唯一ID生成
import dataclasses # 数据模型定义
import typing      # 类型注解
import enum        # 枚举类型
import abc         # 抽象基类
```

### 可选依赖
```python
# 热重载增强（可选）
import watchdog    # 文件系统监控
import psutil      # 系统资源监控（大文件处理）

# 开发工具（可选）
import pytest      # 单元测试
import coverage    # 代码覆盖率
```

### MCP工具集
- **init_tools**: 工作流指导工具（5阶段标准流程）
- **doc_guide**: 智能项目分析器（项目类型、框架识别）
- **task_init**: 任务计划生成器（3阶段任务生成）
- **task_execute**: 任务执行管理器（模板、上下文、执行）
- **task_status**: 状态监控中心（进度跟踪、健康检查）
- **task_complete**: 任务完成工具（质量验证）
- **project_overview**: 项目概览工具（文档导航）
- **doc_update_init**: 文档更新初始化（指纹基点）
- **doc_update**: 文档更新检测（变化分析）

## 版本兼容性
- **Python版本**: 3.9+ (推荐3.11+)
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **MCP协议**: 兼容标准MCP协议规范

## 部署架构

### 本地开发
```bash
# 智能项目分析
python src/mcp_tools/doc_guide.py /path/to/project

# 任务管理（自动识别分析文件）
python src/mcp_tools/task_init.py /path/to/project
python src/mcp_tools/task_execute.py /path/to/project --task-id <task_id>
python src/mcp_tools/task_status.py /path/to/project --type overall_status

# 项目概览和文档更新
python src/mcp_tools/project_overview.py /path/to/project
python src/mcp_tools/doc_update.py /path/to/project
```

### MCP服务器
```bash
# 启动MCP服务器（支持热重载）
python mcp_server.py

# 禁用热重载启动
CODELENS_HOT_RELOAD=false python mcp_server.py

# 服务器信息和状态
python mcp_server.py info
python mcp_server.py reload
```

### Claude Code集成
标准MCP协议接口，支持Claude Code集成9个MCP工具，提供完整的智能化文档生成工作流

## 性能特征

### 处理能力
- **文件处理**: 支持120KB以内文件，50KB以上自动分片
- **项目规模**: 支持1000+文件的大型项目
- **任务并发**: 支持多任务并发执行
- **内存使用**: 低内存占用，按需加载机制

### 响应时间
- **项目分析**: 1-30秒（取决于项目规模）
- **任务生成**: 0.5-2秒
- **状态查询**: 10-100毫秒
- **热重载**: 0.5-2秒（代码变更检测）

### 扩展性
- **水平扩展**: 支持多实例部署
- **垂直扩展**: 充分利用多核CPU资源
- **插件扩展**: 支持自定义组件和模板
- **语言扩展**: 可扩展支持新的编程语言