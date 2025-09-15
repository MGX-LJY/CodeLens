# CodeLens 技术栈

## 核心技术

### 编程语言
- **Python 3.9+**: 主要开发语言，零外部依赖设计
- **强类型系统**: typing模块完整类型注解

### 架构模式
- **MCP协议**: Model Context Protocol标准实现
- **五层服务架构**: 任务引擎层、服务层、MCP接口层、热重载系统层、协作流程层
- **智能化任务驱动**: 5阶段工作流程，核心任务类型支持
- **严格阶段控制**: 100%完成率要求的阶段门控机制
- **模块化微服务**: 各组件独立部署、测试、维护
- **状态感知设计**: 支持任务状态持久化和中断恢复

### 任务引擎技术
- **TaskManager**: 智能任务调度，支持依赖图和优先级算法
- **PhaseController**: 5阶段严格控制，阶段转换验证机制
- **StateTracker**: 实时状态跟踪，执行历史和性能监控
- **智能调度算法**: 基于依赖关系的DAG（有向无环图）调度
- **状态机设计**: PENDING→IN_PROGRESS→COMPLETED/FAILED/BLOCKED状态转换

### 数据格式
- **JSON**: 结构化数据交换格式
- **Markdown**: 文档模板格式
- **JSON持久化**: 任务状态和执行历史存储

### 文件系统操作
- **pathlib**: 现代Python路径操作
- **glob**: 文件模式匹配和智能过滤
- **项目类型检测**: 多维度评分算法，支持5种主流语言
- **框架识别**: 内容分析和模式匹配，支持8+主流框架

### 智能分析技术
- **ProjectAnalyzer**: 项目特征分析和复杂度评估
- **模式匹配引擎**: 支持文件名、目录结构、内容模式识别
- **多维度评分**: 文件特征(3分) + 目录结构(2分) + 扩展名统计
- **智能过滤算法**: 基于项目类型的动态过滤策略
- **复杂度评估**: simple/medium/complex三级自动分类

### 热重载技术
- **HotReloadManager**: 热重载协调管理器，统一管理文件监控和模块重载
- **FileWatcher**: 双模式文件监控 (watchdog + 轮询备用)，实时检测代码变化
- **ModuleReloader**: 智能模块重载器，支持依赖分析和安全重载
- **依赖分析**: 自动构建模块依赖关系图，确保正确的重载顺序
- **防抖动机制**: 避免频繁重载，提供稳定的开发体验

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

### 可靠性保证
- **异常处理**: 完整的错误捕获和恢复机制
- **优雅降级**: 确保系统在故障时正常运行
- **状态持久化**: 支持中断恢复，提升长时间任务执行稳定性
- **阶段控制**: 严格阶段依赖验证，确保执行正确性
- **文件权限检查**: 确保文件可访问性

### 可观测性
- **结构化输出**: JSON格式便于解析
- **操作追踪**: 完整的调用链路记录
- **实时监控**: 任务执行状态和进度实时跟踪
- **性能指标**: 详细的执行时间和资源使用统计
- **健康检查**: 自动检测系统健康状态和执行异常
- **状态报告**: 验证和状态检查

### 配置管理
- **JSON配置**: 人类可读的配置格式
- **环境变量**: 支持环境变量覆盖
- **默认配置**: 提供合理的开箱即用配置

## 版本兼容性
- **Python版本**: 3.9+ (推荐3.11+)
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 20.04+

## 部署架构

### 本地开发
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

### MCP服务器
标准MCP协议接口，支持Claude Code集成7个MCP工具，提供完整的智能化文档生成工作流