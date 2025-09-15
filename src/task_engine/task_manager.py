"""
任务管理器：管理文档生成任务的创建、调度和执行
"""
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"  # 等待执行
    READY = "ready"  # 依赖满足，可执行
    IN_PROGRESS = "in_progress"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 执行失败
    BLOCKED = "blocked"  # 被阻塞


class TaskType(Enum):
    """任务类型枚举"""
    SCAN = "scan"  # 项目扫描
    FILE_SUMMARY = "file_summary"  # 文件摘要生成
    ARCHITECTURE = "architecture"  # 架构概述
    TECH_STACK = "tech_stack"  # 技术栈
    DATA_FLOW = "data_flow"  # 数据流
    SYSTEM_ARCHITECTURE = "system_architecture"  # 系统架构图
    COMPONENT_DIAGRAM = "component_diagram"  # 组件图
    DEPLOYMENT_DIAGRAM = "deployment_diagram"  # 部署图
    PROJECT_README = "project_readme"  # 项目README


@dataclass
class Task:
    """任务数据类"""
    id: str
    type: TaskType
    description: str
    phase: str
    target_file: Optional[str] = None
    target_module: Optional[str] = None
    template_name: Optional[str] = None
    output_path: Optional[str] = None
    dependencies: List[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: str = "normal"  # low, normal, high
    estimated_time: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['type'] = self.type.value
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建任务对象"""
        data = data.copy()
        data['type'] = TaskType(data['type'])
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


class TaskManager:
    """任务管理器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.tasks: Dict[str, Task] = {}
        self.task_file = self.project_path / ".codelens" / "tasks.json"
        self.load_tasks()

    def create_task(self, task_type: TaskType, description: str, phase: str,
                    target_file: Optional[str] = None, target_module: Optional[str] = None,
                    template_name: Optional[str] = None, output_path: Optional[str] = None,
                    dependencies: List[str] = None, priority: str = "normal",
                    estimated_time: Optional[str] = None, metadata: Optional[Dict] = None,
                    task_id: Optional[str] = None) -> str:
        """创建新任务（带去重检查）"""
        
        # 🔧 修复1: 添加任务去重检查
        existing_task_id = self._find_existing_task(task_type, phase, target_file, target_module, description)
        if existing_task_id:
            print(f"跳过重复任务: {description} (已存在ID: {existing_task_id})")
            return existing_task_id
        
        # 🔧 根本修复: 统一ID生成逻辑，支持预定义ID
        if task_id is None:
            # 没有提供预定义ID，生成新的
            import uuid
            task_id = f"{task_type.value}_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
            
            # 确保ID不会冲突
            while task_id in self.tasks:
                task_id = f"{task_type.value}_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
        else:
            # 使用预定义ID，检查是否已存在
            if task_id in self.tasks:
                print(f"警告: 任务ID {task_id} 已存在，跳过创建")
                return task_id

        task = Task(
            id=task_id,
            type=task_type,
            description=description,
            phase=phase,
            target_file=target_file,
            target_module=target_module,
            template_name=template_name,
            output_path=output_path,
            dependencies=dependencies or [],
            priority=priority,
            estimated_time=estimated_time,
            metadata=metadata or {}
        )

        self.tasks[task_id] = task
        self.save_tasks()
        return task_id
    
    def _find_existing_task(self, task_type: TaskType, phase: str, target_file: Optional[str], 
                           target_module: Optional[str], description: str) -> Optional[str]:
        """查找现有的相同任务"""
        for task_id, task in self.tasks.items():
            if (task.type == task_type and 
                task.phase == phase and
                task.target_file == target_file and
                task.target_module == target_module and
                task.description == description):
                return task_id
        return None

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取指定任务"""
        return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus,
                           error_message: Optional[str] = None) -> bool:
        """更新任务状态"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        old_status = task.status
        task.status = status

        # 更新时间戳
        if status == TaskStatus.IN_PROGRESS and old_status != TaskStatus.IN_PROGRESS:
            task.started_at = datetime.now().isoformat()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            task.completed_at = datetime.now().isoformat()

        if error_message:
            task.error_message = error_message

        self.save_tasks()
        return True

    def get_ready_tasks(self, phase: Optional[str] = None) -> List[Task]:
        """获取可执行的任务（依赖已满足）"""
        ready_tasks = []

        for task in self.tasks.values():
            if phase and task.phase != phase:
                continue

            if task.status != TaskStatus.PENDING:
                continue

            # 检查依赖是否满足
            if self._are_dependencies_satisfied(task):
                ready_tasks.append(task)

        # 按优先级排序
        priority_order = {"high": 0, "normal": 1, "low": 2}
        ready_tasks.sort(key=lambda t: priority_order.get(t.priority, 1))

        return ready_tasks

    def get_next_task(self, phase: Optional[str] = None) -> Optional[Task]:
        """获取下一个应该执行的任务"""
        ready_tasks = self.get_ready_tasks(phase)
        return ready_tasks[0] if ready_tasks else None

    def get_phase_tasks(self, phase: str) -> List[Task]:
        """获取指定阶段的所有任务"""
        return [task for task in self.tasks.values() if task.phase == phase]

    def get_phase_progress(self, phase: str) -> Dict[str, Any]:
        """获取阶段进度"""
        phase_tasks = self.get_phase_tasks(phase)
        if not phase_tasks:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "pending_tasks": 0,
                "failed_tasks": 0,
                "completion_percentage": 0,
                "can_proceed": True
            }

        completed = len([t for t in phase_tasks if t.status == TaskStatus.COMPLETED])
        in_progress = len([t for t in phase_tasks if t.status == TaskStatus.IN_PROGRESS])
        pending = len([t for t in phase_tasks if t.status == TaskStatus.PENDING])
        failed = len([t for t in phase_tasks if t.status == TaskStatus.FAILED])

        return {
            "total_tasks": len(phase_tasks),
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "pending_tasks": pending,
            "failed_tasks": failed,
            "completion_percentage": round((completed / len(phase_tasks)) * 100, 2),
            "can_proceed": completed == len(phase_tasks)  # 所有任务都完成才能进入下一阶段
        }

    def get_overall_progress(self) -> Dict[str, Any]:
        """获取总体进度"""
        all_tasks = list(self.tasks.values())
        if not all_tasks:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_percentage": 0,
                "current_phase": None,
                "phases_progress": {}
            }

        completed = len([t for t in all_tasks if t.status == TaskStatus.COMPLETED])
        phases = ["phase_1_scan", "phase_2_files", "phase_3_architecture", "phase_4_project"]

        phases_progress = {}
        current_phase = None

        for phase in phases:
            progress = self.get_phase_progress(phase)
            phases_progress[phase] = progress

            # 确定当前阶段
            if progress["total_tasks"] > 0 and not progress["can_proceed"]:
                current_phase = phase
                break

        return {
            "total_tasks": len(all_tasks),
            "completed_tasks": completed,
            "completion_percentage": round((completed / len(all_tasks)) * 100, 2),
            "current_phase": current_phase,
            "phases_progress": phases_progress
        }

    def get_blocked_tasks(self) -> List[Task]:
        """获取被阻塞的任务"""
        blocked = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING and not self._are_dependencies_satisfied(task):
                blocked.append(task)
        return blocked

    def get_failed_tasks(self) -> List[Task]:
        """获取失败的任务"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.FAILED]

    def retry_failed_task(self, task_id: str) -> bool:
        """重试失败的任务"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if task.status != TaskStatus.FAILED:
            return False

        task.status = TaskStatus.PENDING
        task.error_message = None
        task.started_at = None
        task.completed_at = None

        self.save_tasks()
        return True

    def clear_tasks(self):
        """清空所有任务"""
        self.tasks.clear()
        self.save_tasks()

    def delete_task(self, task_id: str) -> bool:
        """删除指定任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()
            return True
        return False

    def _are_dependencies_satisfied(self, task: Task) -> bool:
        """检查任务的依赖是否已满足"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True

    def load_tasks(self):
        """从文件加载任务"""
        try:
            if self.task_file.exists():
                with open(self.task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = {
                        task_id: Task.from_dict(task_data)
                        for task_id, task_data in data.items()
                    }
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = {}

    def save_tasks(self):
        """保存任务到文件"""
        try:
            # 确保目录存在
            self.task_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                task_id: task.to_dict()
                for task_id, task in self.tasks.items()
            }

            with open(self.task_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def export_tasks_summary(self) -> Dict[str, Any]:
        """导出任务摘要"""
        return {
            "project_path": str(self.project_path),
            "total_tasks": len(self.tasks),
            "overall_progress": self.get_overall_progress(),
            "task_summary": {
                status.value: len([t for t in self.tasks.values() if t.status == status])
                for status in TaskStatus
            },
            "phase_summary": {
                phase: self.get_phase_progress(phase)
                for phase in ["phase_1_scan", "phase_2_files", "phase_3_architecture",
                              "phase_4_project"]
            }
        }
