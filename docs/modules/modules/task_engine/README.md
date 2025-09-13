# Task Engine 模块

## 模块概述
Task Engine是CodeLens 0.6.0.0版本的核心新增模块，提供智能化任务管理、5阶段流程控制和状态持久化功能，实现了从基础MCP工具到智能化任务驱动文档生成系统的重要进化。

## 核心组件

### TaskManager (任务管理器)
智能任务管理器，支持依赖关系和优先级调度
- **任务创建**: 支持23+种任务类型的创建和配置
- **依赖管理**: 构建和维护任务依赖图谱
- **状态跟踪**: 实时跟踪任务执行状态和进度
- **优先级调度**: 基于优先级和依赖关系的智能调度

### PhaseController (阶段控制器)
5阶段严格控制器，确保文档生成流程的正确性
- **阶段定义**: 扫描→文件→模块→架构→项目五个阶段
- **严格依赖**: 100%完成率要求，确保阶段质量
- **进度门控**: 阶段转换权限验证和控制
- **依赖检查**: 自动检查阶段依赖关系

### StateTracker (状态跟踪器)
持久化状态跟踪和进度监控
- **状态持久化**: 实时保存任务和阶段状态到.codelens目录
- **执行历史**: 完整的任务执行历史和事件记录
- **性能监控**: 详细的执行时间和资源使用统计
- **健康检查**: 自动检测系统健康状态和异常

## 关键特性

### 智能化特性
- **项目类型感知**: 自动识别Python/JavaScript/Java/Go/Rust等项目类型
- **框架智能识别**: 支持Flask/Django/React/Vue/Spring等主流框架
- **智能任务生成**: 基于项目分析结果生成定制化任务列表
- **依赖图优化**: 智能任务调度，避免重复执行

### 可靠性保障
- **状态持久化**: 支持中断恢复，提升长时间任务执行稳定性
- **异常处理**: 完整的错误捕获和恢复机制
- **阶段控制**: 严格阶段依赖验证，确保执行正确性
- **事务性操作**: 确保任务状态更新的原子性

### 性能优化
- **毫秒级响应**: 实时状态检查和进度监控
- **高效调度**: 依赖图优化的任务调度算法
- **内存优化**: 按需加载和状态持久化机制
- **并发安全**: 支持多任务并发执行

## 工作流程

### 5阶段执行流程
1. **阶段1 - 项目分析**: 项目路径 → 智能扫描 → 项目特征分析 → 生成策略
2. **阶段2 - 任务规划**: 分析结果 → 任务生成 → 依赖图构建 → 执行计划
3. **阶段3 - 文件文档**: 核心文件 → 模板匹配 → 内容生成 → 状态跟踪
4. **阶段4 - 模块架构**: 模块分析 → 关系映射 → 架构设计 → 技术栈文档
5. **阶段5 - 项目总结**: 整体梳理 → README生成 → 项目完整性验证

### 严格阶段控制
- **100%完成率要求**: 每阶段必须达到100%完成率才能进入下一阶段
- **依赖关系验证**: 自动检查任务依赖关系，确保执行顺序正确
- **状态持久化**: 实时保存执行状态，支持中断恢复

## 技术实现

### 设计原则
- **零外部依赖**: 纯Python标准库实现
- **模块化设计**: 各组件独立可测试
- **类型安全**: 完整的类型注解和验证
- **状态感知**: 支持状态持久化和恢复

### 数据存储
- **JSON格式**: 使用JSON进行状态持久化存储
- **目录结构**: .codelens/tasks.json、task_events.json、state_snapshots.json
- **原子操作**: 确保文件操作的原子性和一致性

### API设计
- **统一接口**: 提供一致的API接口设计
- **错误处理**: 完善的异常捕获和错误信息
- **返回格式**: 标准化的JSON响应格式

## 使用示例

### 任务管理器使用
```python
from src.task_engine import TaskManager, TaskType, TaskStatus

# 创建任务管理器
task_manager = TaskManager("/path/to/project")

# 创建任务
task_id = task_manager.create_task(
    task_type=TaskType.FILE_SUMMARY,
    description="生成app.py文件摘要",
    target_file="app.py",
    phase="phase_2_files"
)

# 更新任务状态
task_manager.update_task_status(task_id, TaskStatus.COMPLETED)
```

### 阶段控制器使用
```python
from src.task_engine import PhaseController, Phase

# 创建阶段控制器
phase_controller = PhaseController(task_manager)

# 检查阶段状态
can_start = phase_controller.can_start_phase(Phase.PHASE_2_FILES)
can_proceed = phase_controller.can_proceed_to_next_phase(Phase.PHASE_1_SCAN)
```

### 状态跟踪器使用
```python
from src.task_engine import StateTracker

# 创建状态跟踪器
state_tracker = StateTracker("/path/to/project", task_manager, phase_controller)

# 记录事件
state_tracker.record_task_event("started", task_id)
state_tracker.record_task_event("completed", task_id)

# 获取健康状态
health_status = state_tracker.get_health_status()
```

## 版本信息
- **引入版本**: 0.6.0.0
- **状态**: 稳定
- **维护者**: CodeLens Team
- **最后更新**: 2025-09-13