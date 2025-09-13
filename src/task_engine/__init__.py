"""
任务引擎模块

提供智能化的文档生成任务管理功能：
- 任务管理：创建、调度、执行文档生成任务
- 阶段控制：管理五个文档生成阶段的流程控制
- 状态跟踪：跟踪任务执行状态和进度
"""

from .task_manager import TaskManager, Task, TaskStatus, TaskType
from .phase_controller import PhaseController, Phase, PhaseStatus
from .state_tracker import StateTracker

__all__ = [
    'TaskManager', 'Task', 'TaskStatus', 'TaskType',
    'PhaseController', 'Phase', 'PhaseStatus', 
    'StateTracker'
]