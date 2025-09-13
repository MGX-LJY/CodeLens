"""
阶段控制器：管理文档生成的五个阶段流程控制
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from .task_manager import TaskManager, TaskStatus


class PhaseStatus(Enum):
    """阶段状态枚举"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class Phase(Enum):
    """阶段枚举"""
    PHASE_1_SCAN = "phase_1_scan"  # 项目扫描和分析
    PHASE_2_FILES = "phase_2_files"  # 文件层文档生成
    PHASE_3_MODULES = "phase_3_modules"  # 模块层文档生成
    PHASE_4_ARCHITECTURE = "phase_4_architecture"  # 架构层文档生成
    PHASE_5_PROJECT = "phase_5_project"  # 项目层文档生成


@dataclass
class PhaseInfo:
    """阶段信息"""
    phase: Phase
    name: str
    description: str
    dependencies: List[Phase]
    expected_tasks: List[str]  # 预期的任务类型
    min_completion_rate: float = 1.0  # 最小完成率，默认100%


class PhaseController:
    """阶段控制器"""

    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

        # 定义各阶段信息
        self.phases_info = {
            Phase.PHASE_1_SCAN: PhaseInfo(
                phase=Phase.PHASE_1_SCAN,
                name="项目分析和初始化",
                description="扫描项目文件、分析项目特征、生成任务计划",
                dependencies=[],
                expected_tasks=["scan"],
                min_completion_rate=1.0
            ),
            Phase.PHASE_2_FILES: PhaseInfo(
                phase=Phase.PHASE_2_FILES,
                name="文件层文档生成",
                description="为每个源文件生成详细的摘要文档",
                dependencies=[Phase.PHASE_1_SCAN],
                expected_tasks=["file_summary"],
                min_completion_rate=1.0
            ),
            Phase.PHASE_3_MODULES: PhaseInfo(
                phase=Phase.PHASE_3_MODULES,
                name="模块层文档生成",
                description="基于文件分析生成模块关系和架构文档",
                dependencies=[Phase.PHASE_2_FILES],
                expected_tasks=["module_analysis", "module_relations", "dependency_graph",
                                "module_readme", "module_api", "module_flow"],
                min_completion_rate=1.0
            ),
            Phase.PHASE_4_ARCHITECTURE: PhaseInfo(
                phase=Phase.PHASE_4_ARCHITECTURE,
                name="架构层文档生成",
                description="基于模块分析生成系统架构和技术栈文档",
                dependencies=[Phase.PHASE_3_MODULES],
                expected_tasks=["architecture", "tech_stack", "data_flow",
                                "system_architecture", "component_diagram", "deployment_diagram"],
                min_completion_rate=1.0
            ),
            Phase.PHASE_5_PROJECT: PhaseInfo(
                phase=Phase.PHASE_5_PROJECT,
                name="项目层文档生成",
                description="生成项目README等对外展示文档",
                dependencies=[Phase.PHASE_4_ARCHITECTURE],
                expected_tasks=["project_readme"],
                min_completion_rate=1.0
            )
        }

    def get_phase_status(self, phase: Phase) -> PhaseStatus:
        """获取阶段状态"""
        phase_tasks = self.task_manager.get_phase_tasks(phase.value)

        if not phase_tasks:
            return PhaseStatus.NOT_STARTED

        completed_count = len([t for t in phase_tasks if t.status == TaskStatus.COMPLETED])
        total_count = len(phase_tasks)

        if completed_count == 0:
            # 检查是否有任务在执行中
            in_progress = any(t.status == TaskStatus.IN_PROGRESS for t in phase_tasks)
            return PhaseStatus.IN_PROGRESS if in_progress else PhaseStatus.NOT_STARTED
        elif completed_count == total_count:
            return PhaseStatus.COMPLETED
        else:
            return PhaseStatus.IN_PROGRESS

    def can_start_phase(self, phase: Phase) -> Tuple[bool, str]:
        """检查是否可以开始指定阶段"""
        phase_info = self.phases_info[phase]

        # 检查依赖阶段是否完成
        for dep_phase in phase_info.dependencies:
            dep_status = self.get_phase_status(dep_phase)
            if dep_status != PhaseStatus.COMPLETED:
                dep_info = self.phases_info[dep_phase]
                return False, f"依赖阶段 '{dep_info.name}' 尚未完成"

        # 检查当前阶段是否已完成
        current_status = self.get_phase_status(phase)
        if current_status == PhaseStatus.COMPLETED:
            return False, f"阶段 '{phase_info.name}' 已经完成"

        return True, "可以开始"

    def get_current_phase(self) -> Optional[Phase]:
        """获取当前应该执行的阶段"""
        for phase in Phase:
            status = self.get_phase_status(phase)
            if status in [PhaseStatus.NOT_STARTED, PhaseStatus.IN_PROGRESS]:
                can_start, _ = self.can_start_phase(phase)
                if can_start:
                    return phase

        return None  # 所有阶段都已完成

    def get_next_phase(self, current_phase: Phase) -> Optional[Phase]:
        """获取下一个阶段"""
        phases = list(Phase)
        try:
            current_index = phases.index(current_phase)
            if current_index + 1 < len(phases):
                return phases[current_index + 1]
        except ValueError:
            pass
        return None

    def get_phase_progress_detailed(self, phase: Phase) -> Dict[str, Any]:
        """获取阶段的详细进度信息"""
        phase_info = self.phases_info[phase]
        phase_tasks = self.task_manager.get_phase_tasks(phase.value)
        status = self.get_phase_status(phase)

        # 统计任务状态
        task_stats = {
            "total": len(phase_tasks),
            "completed": len([t for t in phase_tasks if t.status == TaskStatus.COMPLETED]),
            "in_progress": len([t for t in phase_tasks if t.status == TaskStatus.IN_PROGRESS]),
            "pending": len([t for t in phase_tasks if t.status == TaskStatus.PENDING]),
            "failed": len([t for t in phase_tasks if t.status == TaskStatus.FAILED]),
            "blocked": len([t for t in phase_tasks if t.status == TaskStatus.BLOCKED])
        }

        # 计算完成率
        completion_rate = task_stats["completed"] / task_stats["total"] if task_stats["total"] > 0 else 0

        # 检查依赖状态
        dependencies_status = []
        for dep_phase in phase_info.dependencies:
            dep_info = self.phases_info[dep_phase]
            dep_status = self.get_phase_status(dep_phase)
            dependencies_status.append({
                "phase": dep_phase.value,
                "name": dep_info.name,
                "status": dep_status.value,
                "completed": dep_status == PhaseStatus.COMPLETED
            })

        can_start, start_message = self.can_start_phase(phase)

        return {
            "phase": phase.value,
            "name": phase_info.name,
            "description": phase_info.description,
            "status": status.value,
            "can_start": can_start,
            "start_message": start_message,
            "task_statistics": task_stats,
            "completion_rate": round(completion_rate * 100, 2),
            "min_completion_required": phase_info.min_completion_rate * 100,
            "can_proceed_next": completion_rate >= phase_info.min_completion_rate,
            "dependencies": dependencies_status,
            "expected_task_types": phase_info.expected_tasks,
            "tasks": [
                {
                    "id": t.id,
                    "type": t.type.value,
                    "description": t.description,
                    "status": t.status.value,
                    "target_file": t.target_file,
                    "target_module": t.target_module,
                    "priority": t.priority
                }
                for t in phase_tasks
            ]
        }

    def get_all_phases_overview(self) -> Dict[str, Any]:
        """获取所有阶段的概览"""
        overview = {
            "current_phase": None,
            "overall_progress": 0,
            "total_phases": len(Phase),
            "completed_phases": 0,
            "phases": {}
        }

        total_tasks = 0
        completed_tasks = 0

        for phase in Phase:
            phase_progress = self.get_phase_progress_detailed(phase)
            overview["phases"][phase.value] = phase_progress

            # 统计总体进度
            total_tasks += phase_progress["task_statistics"]["total"]
            completed_tasks += phase_progress["task_statistics"]["completed"]

            # 统计完成的阶段
            if phase_progress["status"] == PhaseStatus.COMPLETED.value:
                overview["completed_phases"] += 1

            # 确定当前阶段
            if (phase_progress["status"] in [PhaseStatus.NOT_STARTED.value, PhaseStatus.IN_PROGRESS.value]
                    and phase_progress["can_start"] and overview["current_phase"] is None):
                overview["current_phase"] = phase.value

        # 计算总体进度
        overview["overall_progress"] = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
        overview["total_tasks"] = total_tasks
        overview["completed_tasks"] = completed_tasks

        return overview

    def can_proceed_to_next_phase(self, phase: Phase) -> Tuple[bool, str]:
        """检查是否可以进入下一阶段"""
        phase_info = self.phases_info[phase]
        phase_tasks = self.task_manager.get_phase_tasks(phase.value)

        if not phase_tasks:
            return False, f"阶段 '{phase_info.name}' 没有任务"

        completed_count = len([t for t in phase_tasks if t.status == TaskStatus.COMPLETED])
        total_count = len(phase_tasks)
        completion_rate = completed_count / total_count

        if completion_rate < phase_info.min_completion_rate:
            required_pct = phase_info.min_completion_rate * 100
            current_pct = completion_rate * 100
            return False, f"完成率 {current_pct:.1f}% 低于要求的 {required_pct:.1f}%"

        return True, "可以进入下一阶段"

    def get_phase_recommendations(self, phase: Phase) -> List[str]:
        """获取阶段建议"""
        recommendations = []
        phase_info = self.phases_info[phase]
        status = self.get_phase_status(phase)

        if status == PhaseStatus.NOT_STARTED:
            can_start, message = self.can_start_phase(phase)
            if can_start:
                recommendations.append(f"可以开始 {phase_info.name}")
            else:
                recommendations.append(f"等待依赖阶段完成: {message}")

        elif status == PhaseStatus.IN_PROGRESS:
            phase_tasks = self.task_manager.get_phase_tasks(phase.value)

            # 检查失败的任务
            failed_tasks = [t for t in phase_tasks if t.status == TaskStatus.FAILED]
            if failed_tasks:
                recommendations.append(f"需要重试 {len(failed_tasks)} 个失败的任务")

            # 检查阻塞的任务
            blocked_tasks = [t for t in phase_tasks if t.status == TaskStatus.BLOCKED]
            if blocked_tasks:
                recommendations.append(f"有 {len(blocked_tasks)} 个任务被阻塞，需要检查依赖")

            # 建议下一个任务
            next_task = self.task_manager.get_next_task(phase.value)
            if next_task:
                recommendations.append(f"建议执行任务: {next_task.description}")

            # 检查是否可以进入下一阶段
            can_proceed, message = self.can_proceed_to_next_phase(phase)
            if can_proceed:
                next_phase = self.get_next_phase(phase)
                if next_phase:
                    next_info = self.phases_info[next_phase]
                    recommendations.append(f"当前阶段已完成，可以进入 {next_info.name}")
                else:
                    recommendations.append("所有阶段已完成！")

        elif status == PhaseStatus.COMPLETED:
            next_phase = self.get_next_phase(phase)
            if next_phase:
                next_info = self.phases_info[next_phase]
                recommendations.append(f"进入下一阶段: {next_info.name}")
            else:
                recommendations.append("所有阶段已完成！")

        return recommendations

    def validate_phase_transition(self, from_phase: Phase, to_phase: Phase) -> Tuple[bool, str]:
        """验证阶段转换是否合法"""
        # 检查源阶段是否完成
        can_proceed, message = self.can_proceed_to_next_phase(from_phase)
        if not can_proceed:
            return False, f"无法离开当前阶段: {message}"

        # 检查目标阶段是否可以开始
        can_start, start_message = self.can_start_phase(to_phase)
        if not can_start:
            return False, f"无法开始目标阶段: {start_message}"

        # 检查阶段顺序
        phases = list(Phase)
        try:
            from_index = phases.index(from_phase)
            to_index = phases.index(to_phase)

            # 只允许顺序进入下一阶段或在同一阶段内
            if to_index > from_index + 1:
                return False, "不能跳过阶段"
            elif to_index < from_index:
                return False, "不能回退到之前的阶段"
        except ValueError:
            return False, "无效的阶段"

        return True, "可以进行阶段转换"
