# phase_controller.py

## 文件概述
5阶段严格控制器实现，负责管理文档生成流程的阶段转换、依赖验证和进度门控。确保每个阶段达到100%完成率后才能进入下一阶段，是Task Engine模块的核心流程控制组件。

## 核心类定义

### Phase (枚举)
定义5个文档生成阶段
```python
class Phase(Enum):
    PHASE_1_SCAN = "phase_1_scan"                    # 阶段1: 项目分析
    PHASE_2_FILES = "phase_2_files"                  # 阶段2: 文件文档生成
    PHASE_3_MODULES = "phase_3_modules"              # 阶段3: 模块架构分析
    PHASE_4_ARCHITECTURE = "phase_4_architecture"    # 阶段4: 架构文档生成
    PHASE_5_PROJECT = "phase_5_project"              # 阶段5: 项目总结文档
```

### PhaseStatus (枚举)
定义阶段状态
```python
class PhaseStatus(Enum):
    NOT_STARTED = "not_started"    # 未开始
    IN_PROGRESS = "in_progress"    # 进行中
    COMPLETED = "completed"        # 已完成
    BLOCKED = "blocked"           # 被阻塞
```

### PhaseController (主类)
阶段控制器主要实现

#### 核心属性
```python
class PhaseController:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.phase_definitions = self._initialize_phase_definitions()
        self.phase_dependencies = self._initialize_phase_dependencies()
        self.min_completion_rate = 100.0  # 最小完成率要求
```

#### 核心方法

**can_start_phase(phase: Phase) -> bool**
- 检查是否可以开始指定阶段
- 验证前置阶段依赖是否满足
- 检查阶段本身是否已完成

**can_proceed_to_next_phase(current_phase: Phase) -> bool**
- 检查是否可以从当前阶段进入下一阶段
- 验证当前阶段完成率是否达到100%
- 检查所有任务状态

**get_phase_status(phase: Phase) -> PhaseStatus**
- 获取阶段当前状态
- 基于任务完成情况判断阶段状态
- 返回NOT_STARTED/IN_PROGRESS/COMPLETED/BLOCKED

**get_current_phase() -> Phase**
- 获取当前活跃阶段
- 基于任务执行情况自动判断
- 返回正在进行或下一个应执行的阶段

**get_next_phase(current_phase: Phase) -> Optional[Phase]**
- 获取指定阶段的下一个阶段
- 按阶段顺序返回
- 最后阶段返回None

**get_phase_progress(phase: Phase) -> Dict[str, Any]**
- 获取阶段详细进度信息
- 包含任务统计、完成率、状态等
- 提供阶段转换建议

**get_phase_dependencies(phase: Phase) -> List[Dict[str, Any]]**
- 获取阶段的依赖关系
- 返回前置阶段列表和状态
- 用于依赖验证和显示

## 阶段定义和依赖关系

### 阶段定义
```python
PHASE_DEFINITIONS = {
    Phase.PHASE_1_SCAN: {
        "name": "项目分析和初始化",
        "description": "扫描项目文件、分析项目特征、生成任务计划",
        "expected_task_types": [TaskType.SCAN],
        "min_tasks": 1,
        "max_tasks": 1
    },
    Phase.PHASE_2_FILES: {
        "name": "文件层文档生成",
        "description": "为每个源文件生成详细的摘要文档",
        "expected_task_types": [TaskType.FILE_SUMMARY],
        "min_tasks": 1,
        "max_tasks": 50
    },
    # ... 其他阶段定义
}
```

### 依赖关系
```python
PHASE_DEPENDENCIES = {
    Phase.PHASE_1_SCAN: [],  # 无依赖
    Phase.PHASE_2_FILES: [Phase.PHASE_1_SCAN],
    Phase.PHASE_3_MODULES: [Phase.PHASE_2_FILES],
    Phase.PHASE_4_ARCHITECTURE: [Phase.PHASE_3_MODULES],
    Phase.PHASE_5_PROJECT: [Phase.PHASE_4_ARCHITECTURE]
}
```

## 关键特性

### 严格阶段控制
- **100%完成率要求**: 每阶段必须达到100%完成率
- **依赖验证**: 自动检查前置阶段依赖
- **原子性转换**: 阶段转换要么成功要么保持原状态

### 进度门控机制
- **门控条件**: 明确的阶段转换条件
- **自动阻塞**: 条件不满足时自动阻塞后续阶段
- **状态一致性**: 确保阶段状态与任务状态一致

### 智能状态推断
- **自动检测**: 基于任务状态自动推断阶段状态
- **实时更新**: 任务状态变化时实时更新阶段状态
- **异常处理**: 处理任务状态异常对阶段的影响

## 阶段转换流程

### 流程图
```
阶段检查 → 依赖验证 → 完成率检查 → 状态更新 → 转换决策
    ↓
如果满足条件: 允许转换到下一阶段
如果不满足: 保持当前阶段，提供改进建议
```

### 转换条件矩阵
```
当前阶段     → 目标阶段        条件
PHASE_1     → PHASE_2         扫描任务100%完成
PHASE_2     → PHASE_3         所有文件任务100%完成
PHASE_3     → PHASE_4         所有模块任务100%完成
PHASE_4     → PHASE_5         所有架构任务100%完成
PHASE_5     → 完成           项目任务100%完成
```

## 状态监控和报告

### 阶段进度结构
```json
{
    "phase": "phase_2_files",
    "name": "文件层文档生成",
    "status": "in_progress",
    "can_start": true,
    "can_proceed_next": false,
    "task_statistics": {
        "total": 10,
        "completed": 7,
        "in_progress": 2,
        "pending": 1,
        "failed": 0,
        "blocked": 0
    },
    "completion_rate": 70.0,
    "min_completion_required": 100.0,
    "dependencies": [
        {
            "phase": "phase_1_scan",
            "name": "项目分析和初始化",
            "completed": true
        }
    ]
}
```

### 健康检查
```python
def health_check(self) -> Dict[str, Any]:
    """阶段控制器健康检查"""
    issues = []
    warnings = []
    
    # 检查阶段一致性
    for phase in Phase:
        phase_status = self.get_phase_status(phase)
        if phase_status == PhaseStatus.BLOCKED:
            issues.append(f"阶段 {phase.value} 被阻塞")
    
    # 检查任务状态一致性
    inconsistent_phases = self._check_task_phase_consistency()
    if inconsistent_phases:
        warnings.extend(inconsistent_phases)
    
    return {
        "overall_health": "good" if not issues else "warning",
        "issues": issues,
        "warnings": warnings
    }
```

## 性能特性
- **状态查询**: < 2ms
- **阶段验证**: < 5ms
- **进度计算**: < 3ms
- **内存占用**: 每个项目约占用100KB

## 使用示例

### 基本阶段控制
```python
from src.task_engine.phase_controller import PhaseController, Phase

# 创建阶段控制器
controller = PhaseController(task_manager)

# 检查阶段状态
current_phase = controller.get_current_phase()
phase_status = controller.get_phase_status(current_phase)

print(f"当前阶段: {current_phase.value}")
print(f"阶段状态: {phase_status.value}")

# 检查是否可以进入下一阶段
if controller.can_proceed_to_next_phase(current_phase):
    next_phase = controller.get_next_phase(current_phase)
    print(f"可以进入下一阶段: {next_phase.value}")
else:
    print("当前阶段尚未完成，无法进入下一阶段")
```

### 阶段进度监控
```python
# 获取所有阶段的进度
for phase in Phase:
    progress = controller.get_phase_progress(phase)
    print(f"阶段: {progress['name']}")
    print(f"状态: {progress['status']}")
    print(f"完成率: {progress['completion_rate']}%")
    print(f"可以开始: {progress['can_start']}")
    print("---")

# 检查特定阶段依赖
dependencies = controller.get_phase_dependencies(Phase.PHASE_3_MODULES)
for dep in dependencies:
    print(f"依赖阶段: {dep['name']}, 已完成: {dep['completed']}")
```

### 阶段转换控制
```python
def execute_phase_transition():
    """执行阶段转换的完整流程"""
    current = controller.get_current_phase()
    
    # 检查当前阶段是否完成
    if controller.can_proceed_to_next_phase(current):
        next_phase = controller.get_next_phase(current)
        if next_phase:
            print(f"从 {current.value} 转换到 {next_phase.value}")
            # 可以安全地开始下一阶段的任务
        else:
            print("所有阶段已完成！")
    else:
        # 获取阻塞原因
        progress = controller.get_phase_progress(current)
        print(f"阶段转换被阻塞: {progress.get('block_reason', '未知原因')}")
```

## 错误处理和异常

### 异常类型
```python
class PhaseControlError(Exception):
    """阶段控制异常基类"""
    pass

class InvalidPhaseError(PhaseControlError):
    """无效阶段异常"""
    pass

class PhaseDependencyError(PhaseControlError):
    """阶段依赖异常"""
    pass

class PhaseTransitionError(PhaseControlError):
    """阶段转换异常"""
    pass
```

### 异常处理示例
```python
try:
    can_proceed = controller.can_proceed_to_next_phase(Phase.PHASE_2_FILES)
except InvalidPhaseError as e:
    print(f"无效的阶段: {e}")
except PhaseDependencyError as e:
    print(f"阶段依赖错误: {e}")
```

