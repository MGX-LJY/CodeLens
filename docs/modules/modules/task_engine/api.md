# Task Engine API 文档

## TaskManager API

### 类定义
```python
class TaskManager:
    def __init__(self, project_path: str)
```

### 核心方法

#### create_task()
创建新任务
```python
def create_task(
    self,
    task_type: TaskType,
    description: str,
    phase: str,
    target_file: Optional[str] = None,
    target_module: Optional[str] = None,
    template: Optional[str] = None,
    output_path: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    priority: str = "normal",
    metadata: Optional[Dict[str, Any]] = None
) -> str
```

**参数**:
- `task_type`: 任务类型 (TaskType枚举)
- `description`: 任务描述
- `phase`: 所属阶段
- `target_file`: 目标文件路径 (可选)
- `target_module`: 目标模块名称 (可选)
- `template`: 使用的模板名称 (可选)
- `output_path`: 输出文件路径 (可选)
- `dependencies`: 依赖任务ID列表 (可选)
- `priority`: 优先级 ("high", "normal", "low")
- `metadata`: 额外元数据 (可选)

**返回**: 任务ID (str)

#### get_task()
获取任务详情
```python
def get_task(self, task_id: str) -> Optional[Task]
```

#### update_task_status()
更新任务状态
```python
def update_task_status(
    self,
    task_id: str,
    status: TaskStatus,
    error_message: Optional[str] = None
) -> bool
```

#### get_next_task()
获取下一个可执行任务
```python
def get_next_task(self, phase_filter: Optional[str] = None) -> Optional[Task]
```

#### get_phase_progress()
获取阶段进度
```python
def get_phase_progress(self, phase: str) -> Dict[str, Any]
```

### 任务类型枚举
```python
class TaskType(Enum):
    SCAN = "scan"
    FILE_SUMMARY = "file_summary"
    MODULE_ANALYSIS = "module_analysis"
    MODULE_RELATIONS = "module_relations"
    DEPENDENCY_GRAPH = "dependency_graph"
    MODULE_README = "module_readme"
    MODULE_API = "module_api"
    MODULE_FLOW = "module_flow"
    ARCHITECTURE = "architecture"
    TECH_STACK = "tech_stack"
    DATA_FLOW = "data_flow"
    SYSTEM_ARCHITECTURE = "system_architecture"
    COMPONENT_DIAGRAM = "component_diagram"
    DEPLOYMENT_DIAGRAM = "deployment_diagram"
    PROJECT_README = "project_readme"
```

### 任务状态枚举
```python
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
```

## PhaseController API

### 类定义
```python
class PhaseController:
    def __init__(self, task_manager: TaskManager)
```

### 核心方法

#### can_start_phase()
检查是否可以开始某个阶段
```python
def can_start_phase(self, phase: Phase) -> bool
```

#### can_proceed_to_next_phase()
检查是否可以进入下一阶段
```python
def can_proceed_to_next_phase(self, current_phase: Phase) -> bool
```

#### get_phase_status()
获取阶段状态
```python
def get_phase_status(self, phase: Phase) -> PhaseStatus
```

#### get_current_phase()
获取当前阶段
```python
def get_current_phase(self) -> Phase
```

#### get_phase_progress()
获取阶段进度详情
```python
def get_phase_progress(self, phase: Phase) -> Dict[str, Any]
```

### 阶段枚举
```python
class Phase(Enum):
    PHASE_1_SCAN = "phase_1_scan"
    PHASE_2_FILES = "phase_2_files"
    PHASE_3_MODULES = "phase_3_modules"
    PHASE_4_ARCHITECTURE = "phase_4_architecture"
    PHASE_5_PROJECT = "phase_5_project"
```

### 阶段状态枚举
```python
class PhaseStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
```

## StateTracker API

### 类定义
```python
class StateTracker:
    def __init__(
        self,
        project_path: str,
        task_manager: TaskManager,
        phase_controller: PhaseController
    )
```

### 核心方法

#### record_task_event()
记录任务事件
```python
def record_task_event(
    self,
    event_type: str,
    task_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None
```

#### create_state_snapshot()
创建状态快照
```python
def create_state_snapshot(self, snapshot_type: str = "manual") -> str
```

#### get_execution_statistics()
获取执行统计信息
```python
def get_execution_statistics(self) -> Dict[str, Any]
```

#### get_health_status()
获取健康状态
```python
def get_health_status(self) -> Dict[str, Any]
```

#### get_recommendations()
获取执行建议
```python
def get_recommendations(self) -> List[str]
```

#### estimate_remaining_time()
估算剩余时间
```python
def estimate_remaining_time(self) -> str
```

## Task 数据类

### 属性
```python
@dataclass
class Task:
    id: str
    type: TaskType
    description: str
    phase: str
    target_file: Optional[str]
    target_module: Optional[str]
    template: Optional[str]
    output_path: Optional[str]
    dependencies: List[str]
    priority: str
    status: TaskStatus
    created_at: str
    updated_at: str
    estimated_time: str
    metadata: Dict[str, Any]
    error_message: Optional[str]
```

## 错误处理

### 自定义异常
```python
class TaskEngineError(Exception):
    """任务引擎基础异常"""
    pass

class TaskNotFoundError(TaskEngineError):
    """任务未找到异常"""
    pass

class InvalidPhaseError(TaskEngineError):
    """无效阶段异常"""
    pass

class DependencyError(TaskEngineError):
    """依赖关系异常"""
    pass
```

### 错误响应格式
```json
{
    "success": false,
    "error": {
        "type": "TaskNotFoundError",
        "message": "Task with ID 'task_123' not found",
        "details": {
            "task_id": "task_123",
            "project_path": "/path/to/project"
        }
    }
}
```

## 性能指标

### 响应时间
- **任务创建**: < 10ms
- **状态更新**: < 5ms
- **状态查询**: < 2ms
- **进度检查**: < 3ms

### 并发支持
- **读操作**: 支持高并发读取
- **写操作**: 文件锁保护，确保数据一致性
- **状态持久化**: 原子操作，避免数据损坏

## 使用示例

### 完整工作流示例
```python
from src.task_engine import TaskManager, PhaseController, StateTracker

# 初始化
project_path = "/path/to/project"
task_manager = TaskManager(project_path)
phase_controller = PhaseController(task_manager)
state_tracker = StateTracker(project_path, task_manager, phase_controller)

# 创建扫描任务
scan_task_id = task_manager.create_task(
    task_type=TaskType.SCAN,
    description="扫描项目文件结构和基本信息",
    phase="phase_1_scan",
    priority="high"
)

# 开始执行任务
task_manager.update_task_status(scan_task_id, TaskStatus.IN_PROGRESS)
state_tracker.record_task_event("started", scan_task_id)

# 完成任务
task_manager.update_task_status(scan_task_id, TaskStatus.COMPLETED)
state_tracker.record_task_event("completed", scan_task_id)

# 检查是否可以进入下一阶段
if phase_controller.can_proceed_to_next_phase(Phase.PHASE_1_SCAN):
    print("可以进入文件文档生成阶段")

# 获取健康状态
health = state_tracker.get_health_status()
print(f"系统健康状态: {health['overall_health']}")
```