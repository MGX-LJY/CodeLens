"""
MCP task_status 工具实现
检查任务完成状态，管理阶段性进展
"""
import sys
import os
import json
from typing import Dict, Any, List, Optional

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.task_engine.task_manager import TaskManager, TaskStatus
from src.task_engine.phase_controller import PhaseController, Phase
from src.task_engine.state_tracker import StateTracker

# 导入日志系统
import logging


class TaskStatusTool:
    """MCP task_status 工具类"""

    def __init__(self):
        self.tool_name = "task_status"
        self.description = "检查任务完成状态，管理阶段性进展"
        self.logger = logging.getLogger('task_status')

    def get_tool_definition(self) -> Dict[str, Any]:
        """获取MCP工具定义"""
        return {
            "name": self.tool_name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "要检查的项目路径"
                    },
                    "check_type": {
                        "type": "string",
                        "enum": ["current_task", "phase_progress", "overall_status", "next_actions", "health_check"],
                        "default": "overall_status",
                        "description": "检查类型"
                    },
                    "phase_filter": {
                        "type": "string",
                        "enum": ["phase_1_scan", "phase_2_files", "phase_3_modules", "phase_4_architecture",
                                 "phase_5_project"],
                        "description": "阶段过滤器（可选）"
                    },
                    "detailed_analysis": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含详细分析"
                    },
                    "include_recommendations": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含推荐行动"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "特定任务ID（用于查询特定任务状态）"
                    }
                },
                "required": ["project_path"]
            }
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行task_status工具"""
        try:
            # 参数验证
            project_path = arguments.get("project_path")
            if not project_path or not os.path.exists(project_path):
                return self._error_response("Invalid project path")

            # 获取参数
            check_type = arguments.get("check_type", "overall_status")
            phase_filter = arguments.get("phase_filter")
            detailed_analysis = arguments.get("detailed_analysis", True)
            include_recommendations = arguments.get("include_recommendations", True)
            task_id = arguments.get("task_id")

            # 创建管理器实例
            task_manager = TaskManager(project_path)
            phase_controller = PhaseController(task_manager)
            state_tracker = StateTracker(project_path, task_manager, phase_controller)

            self.logger.info(f"开始状态检查: {project_path}, 检查类型: {check_type}")

            # 根据检查类型执行不同的检查
            if check_type == "current_task":
                result = self._check_current_task(task_manager, phase_controller, phase_filter)
            elif check_type == "phase_progress":
                result = self._check_phase_progress(phase_controller, phase_filter, detailed_analysis)
            elif check_type == "overall_status":
                result = self._check_overall_status(task_manager, phase_controller, state_tracker, detailed_analysis)
            elif check_type == "next_actions":
                result = self._get_next_actions(task_manager, phase_controller, include_recommendations)
            elif check_type == "health_check":
                result = self._perform_health_check(state_tracker, task_manager, phase_controller)
            elif check_type == "task_detail" and task_id:
                result = self._check_task_detail(task_manager, task_id)
            else:
                return self._error_response(f"Invalid check type: {check_type}")

            self.logger.info(f"状态检查完成: {check_type}, 成功: {'error' not in result}")

            return self._success_response(result)

        except Exception as e:
            self.logger.error(f"状态检查失败: {str(e)}", exc_info=e)
            return self._error_response(f"Status check failed: {str(e)}")

    def _check_current_task(self, task_manager: TaskManager, phase_controller: PhaseController,
                            phase_filter: Optional[str]) -> Dict[str, Any]:
        """检查当前任务"""
        current_phase = phase_controller.get_current_phase()

        if phase_filter:
            target_phase = phase_filter
        elif current_phase:
            target_phase = current_phase.value
        else:
            return {"error": "No active phase found"}

        # 获取当前任务
        current_task = task_manager.get_next_task(target_phase)

        if not current_task:
            # 检查是否有进行中的任务
            in_progress_tasks = [t for t in task_manager.tasks.values()
                                 if t.status == TaskStatus.IN_PROGRESS and t.phase == target_phase]

            if in_progress_tasks:
                current_task = in_progress_tasks[0]
                status = "in_progress"
            else:
                phase_progress = task_manager.get_phase_progress(target_phase)
                if phase_progress["can_proceed"]:
                    status = "phase_complete"
                else:
                    status = "no_ready_tasks"

                return {
                    "current_phase": target_phase,
                    "status": status,
                    "phase_progress": phase_progress,
                    "current_task": None
                }
        else:
            status = "ready_to_execute"

        # 检查依赖状态
        dependencies_satisfied = all(
            task_manager.get_task(dep_id) and task_manager.get_task(dep_id).status == TaskStatus.COMPLETED
            for dep_id in current_task.dependencies
        )

        return {
            "current_phase": target_phase,
            "status": status,
            "current_task": {
                "id": current_task.id,
                "type": current_task.type.value,
                "description": current_task.description,
                "target_file": current_task.target_file,
                "target_module": current_task.target_module,
                "template_name": current_task.template_name,
                "output_path": current_task.output_path,
                "priority": current_task.priority,
                "estimated_time": current_task.estimated_time,
                "dependencies_satisfied": dependencies_satisfied,
                "dependencies_count": len(current_task.dependencies)
            }
        }

    def _check_phase_progress(self, phase_controller: PhaseController, phase_filter: Optional[str],
                              detailed: bool) -> Dict[str, Any]:
        """检查阶段进度"""
        if phase_filter:
            try:
                phase = Phase(phase_filter)
                progress = phase_controller.get_phase_progress_detailed(phase)
                return {
                    "phase_filter": phase_filter,
                    "phase_progress": progress
                }
            except ValueError:
                return {"error": f"Invalid phase: {phase_filter}"}
        else:
            # 获取所有阶段概览
            overview = phase_controller.get_all_phases_overview()

            if detailed:
                return {
                    "all_phases": True,
                    "overview": overview
                }
            else:
                # 简化版本
                simplified = {
                    "current_phase": overview["current_phase"],
                    "overall_progress": overview["overall_progress"],
                    "completed_phases": overview["completed_phases"],
                    "total_phases": overview["total_phases"],
                    "phase_status": {
                        phase: info["status"]
                        for phase, info in overview["phases"].items()
                    }
                }
                return simplified

    def _check_overall_status(self, task_manager: TaskManager, phase_controller: PhaseController,
                              state_tracker: StateTracker, detailed: bool) -> Dict[str, Any]:
        """检查总体状态"""
        # 获取基本统计
        overall_progress = task_manager.get_overall_progress()
        current_phase = phase_controller.get_current_phase()

        # 获取任务统计
        all_tasks = list(task_manager.tasks.values())
        task_stats = {
            "total": len(all_tasks),
            "completed": len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]),
            "in_progress": len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]),
            "pending": len([t for t in all_tasks if t.status == TaskStatus.PENDING]),
            "failed": len([t for t in all_tasks if t.status == TaskStatus.FAILED]),
            "blocked": len([t for t in all_tasks if t.status == TaskStatus.BLOCKED])
        }

        result = {
            "overall_progress": overall_progress,
            "current_phase": current_phase.value if current_phase else None,
            "task_statistics": task_stats,
            "estimated_remaining": self._estimate_remaining_time(task_manager, current_phase)
        }

        if detailed:
            # 添加详细信息
            current_status = state_tracker.get_current_status()
            result.update({
                "phase_overview": current_status["phase_overview"],
                "execution_statistics": current_status["execution_statistics"],
                "health_status": current_status["health_check"]
            })

        return result

    def _get_next_actions(self, task_manager: TaskManager, phase_controller: PhaseController,
                          include_recommendations: bool) -> Dict[str, Any]:
        """获取下一步行动建议"""
        actions = []
        current_phase = phase_controller.get_current_phase()

        if not current_phase:
            actions.append("所有阶段已完成！")
            return {"next_actions": actions}

        # 获取下一个任务
        next_task = task_manager.get_next_task(current_phase.value)
        if next_task:
            actions.append(f"执行任务: {next_task.description}")
            actions.append(f"使用命令: task_execute --task-id {next_task.id}")

        # 检查失败任务
        failed_tasks = task_manager.get_failed_tasks()
        if failed_tasks:
            actions.append(f"重试 {len(failed_tasks)} 个失败的任务")

        # 检查阻塞任务
        blocked_tasks = task_manager.get_blocked_tasks()
        if blocked_tasks:
            actions.append(f"解决 {len(blocked_tasks)} 个被阻塞任务的依赖问题")

        # 阶段建议
        if include_recommendations:
            phase_recommendations = phase_controller.get_phase_recommendations(current_phase)
            actions.extend(phase_recommendations)

        # 阶段转换检查
        can_proceed, message = phase_controller.can_proceed_to_next_phase(current_phase)
        if can_proceed:
            next_phase = phase_controller.get_next_phase(current_phase)
            if next_phase:
                next_phase_info = phase_controller.phases_info[next_phase]
                actions.append(f"可以进入下一阶段: {next_phase_info.name}")

        return {
            "current_phase": current_phase.value,
            "next_actions": actions,
            "can_proceed_next_phase": can_proceed,
            "phase_transition_message": message
        }

    def _perform_health_check(self, state_tracker: StateTracker, task_manager: TaskManager,
                              phase_controller: PhaseController) -> Dict[str, Any]:
        """执行健康检查"""
        current_status = state_tracker.get_current_status()
        health_check = current_status["health_check"]

        # 添加更多健康检查项
        issues = health_check["issues"].copy()
        warnings = health_check["warnings"].copy()

        # 检查任务分布
        all_tasks = list(task_manager.tasks.values())
        if len(all_tasks) == 0:
            issues.append("没有创建任何任务，请先运行task_init")

        # 检查阶段平衡
        phase_counts = {}
        for task in all_tasks:
            phase_counts[task.phase] = phase_counts.get(task.phase, 0) + 1

        if len(phase_counts) < 5:
            warnings.append(f"只有 {len(phase_counts)} 个阶段有任务，可能缺少某些阶段")

        # 检查依赖完整性
        orphan_tasks = []
        for task in all_tasks:
            for dep_id in task.dependencies:
                if not task_manager.get_task(dep_id):
                    orphan_tasks.append(task.id)
                    break

        if orphan_tasks:
            issues.append(f"有 {len(orphan_tasks)} 个任务的依赖不存在")

        # 更新健康状态
        if issues:
            overall_health = "poor"
        elif warnings:
            overall_health = "warning"
        else:
            overall_health = "good"

        return {
            "overall_health": overall_health,
            "issues": issues,
            "warnings": warnings,
            "performance_metrics": state_tracker.get_performance_metrics(),
            "task_distribution": phase_counts,
            "recommendations": self._get_health_recommendations(issues, warnings, task_manager)
        }

    def _check_task_detail(self, task_manager: TaskManager, task_id: str) -> Dict[str, Any]:
        """检查特定任务详情"""
        task = task_manager.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}

        # 检查依赖状态
        dependency_status = []
        for dep_id in task.dependencies:
            dep_task = task_manager.get_task(dep_id)
            if dep_task:
                dependency_status.append({
                    "id": dep_id,
                    "description": dep_task.description,
                    "status": dep_task.status.value,
                    "completed": dep_task.status == TaskStatus.COMPLETED
                })
            else:
                dependency_status.append({
                    "id": dep_id,
                    "status": "not_found",
                    "completed": False
                })

        dependencies_satisfied = all(dep["completed"] for dep in dependency_status)

        return {
            "task": {
                "id": task.id,
                "type": task.type.value,
                "description": task.description,
                "phase": task.phase,
                "status": task.status.value,
                "target_file": task.target_file,
                "target_module": task.target_module,
                "template_name": task.template_name,
                "output_path": task.output_path,
                "priority": task.priority,
                "estimated_time": task.estimated_time,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "error_message": task.error_message,
                "metadata": task.metadata
            },
            "dependencies": dependency_status,
            "dependencies_satisfied": dependencies_satisfied,
            "can_execute": dependencies_satisfied and task.status == TaskStatus.PENDING
        }

    def _estimate_remaining_time(self, task_manager: TaskManager, current_phase: Optional[Phase]) -> str:
        """估计剩余时间"""
        remaining_tasks = [t for t in task_manager.tasks.values()
                           if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]

        if not remaining_tasks:
            return "0 minutes"

        # 简单估算：每个任务平均5分钟
        estimated_minutes = len(remaining_tasks) * 5

        hours = estimated_minutes // 60
        minutes = estimated_minutes % 60

        if hours > 0:
            return f"{hours} hours {minutes} minutes"
        else:
            return f"{minutes} minutes"

    def _get_health_recommendations(self, issues: List[str], warnings: List[str],
                                    task_manager: TaskManager) -> List[str]:
        """获取健康建议"""
        recommendations = []

        if not task_manager.tasks:
            recommendations.append("运行task_init初始化任务")

        failed_tasks = task_manager.get_failed_tasks()
        if failed_tasks:
            recommendations.append("检查并重试失败的任务")

        if issues:
            recommendations.append("解决严重问题以确保系统正常运行")

        if warnings:
            recommendations.append("关注警告信息以优化执行效果")

        return recommendations

    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """成功响应"""
        return {
            "success": True,
            "tool": self.tool_name,
            "data": data
        }

    def _error_response(self, message: str) -> Dict[str, Any]:
        """错误响应"""
        return {
            "success": False,
            "tool": self.tool_name,
            "error": message
        }


def create_mcp_tool() -> TaskStatusTool:
    """创建MCP工具实例"""
    return TaskStatusTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP task_status tool")
    parser.add_argument("project_path", help="Project path to check")
    parser.add_argument("--type", dest="check_type",
                        choices=["current_task", "phase_progress", "overall_status",
                                 "next_actions", "health_check"],
                        default="overall_status", help="Check type")
    parser.add_argument("--phase", dest="phase_filter",
                        choices=["phase_1_scan", "phase_2_files", "phase_3_modules",
                                 "phase_4_architecture", "phase_5_project"],
                        help="Phase filter")
    parser.add_argument("--task-id", help="Specific task ID to check")
    parser.add_argument("--simple", action="store_true",
                        help="Simple output (less detail)")
    parser.add_argument("--no-recommendations", action="store_true",
                        help="Don't include recommendations")

    args = parser.parse_args()

    # 构建参数
    arguments = {
        "project_path": args.project_path,
        "check_type": args.check_type,
        "detailed_analysis": not args.simple,
        "include_recommendations": not args.no_recommendations
    }

    if args.phase_filter:
        arguments["phase_filter"] = args.phase_filter

    if args.task_id:
        arguments["task_id"] = args.task_id
        arguments["check_type"] = "task_detail"

    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
