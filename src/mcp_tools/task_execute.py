"""
MCP task_execute 工具实现
执行单个或批量任务，提供模板和上下文信息
"""
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.task_engine.task_manager import TaskManager, TaskStatus, Task
from src.task_engine.phase_controller import PhaseController, Phase
from src.task_engine.state_tracker import StateTracker
from src.services.file_service import FileService
from src.templates.document_templates import TemplateService

# 导入日志系统
import logging


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.task_manager = TaskManager(str(project_path))
        self.phase_controller = PhaseController(self.task_manager)
        self.state_tracker = StateTracker(str(project_path), self.task_manager, self.phase_controller)
        self.file_service = FileService()
        self.template_service = TemplateService()
        
        self.logger = logging.getLogger('task_executor')

    def prepare_task_execution(self, task_id: str, context_enhancement: bool = True) -> Dict[str, Any]:
        """准备任务执行上下文"""
        
        # 获取任务信息
        task = self.task_manager.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # 检查依赖
        dependencies_check = self._check_dependencies(task)
        if not dependencies_check["all_satisfied"]:
            return {
                "error": "Dependencies not satisfied",
                "task_info": self._get_task_info(task),
                "dependencies_check": dependencies_check
            }
        
        # 获取模板内容
        template_info = self._get_template_info(task)
        
        # 获取执行上下文
        execution_context = self._build_execution_context(task, context_enhancement)
        
        # 获取生成指导
        generation_guidance = self._get_generation_guidance(task)
        
        # 获取下一个任务
        next_task = self._get_next_task(task)
        
        return {
            "task_info": self._get_task_info(task),
            "dependencies_check": dependencies_check,
            "template_info": template_info,
            "execution_context": execution_context,
            "generation_guidance": generation_guidance,
            "next_task": next_task
        }

    def execute_task(self, task_id: str, mark_in_progress: bool = True) -> Dict[str, Any]:
        """执行任务（标记为进行中并提供执行上下文）"""
        
        task = self.task_manager.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # 检查任务状态
        if task.status not in [TaskStatus.PENDING, TaskStatus.FAILED]:
            return {"error": f"Task {task_id} is not in executable state (current: {task.status.value})"}
        
        # 标记任务为进行中
        if mark_in_progress:
            self.task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
            self.state_tracker.record_task_event("started", task_id)
            self.logger.info(f"任务开始执行: {task_id} - {task.description}")
        
        # 准备执行上下文
        execution_data = self.prepare_task_execution(task_id, context_enhancement=True)
        
        return {
            "success": True,
            "task_execution": execution_data,
            "instructions": "Use the provided template and context to generate the documentation. Call task_complete when finished."
        }

    def complete_task(self, task_id: str, success: bool = True, error_message: Optional[str] = None) -> Dict[str, Any]:
        """完成任务"""
        
        task = self.task_manager.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        if success:
            self.task_manager.update_task_status(task_id, TaskStatus.COMPLETED)
            self.state_tracker.record_task_event("completed", task_id)
            self.logger.info(f"任务完成: {task_id} - {task.description}")
        else:
            self.task_manager.update_task_status(task_id, TaskStatus.FAILED, error_message)
            self.state_tracker.record_task_event("failed", task_id, {"error": error_message})
            self.logger.error(f"任务失败: {task_id} - {error_message}")
        
        # 获取下一个可执行任务
        next_task = self.task_manager.get_next_task(task.phase)
        
        # 检查阶段是否完成
        phase_progress = self.task_manager.get_phase_progress(task.phase)
        
        return {
            "success": True,
            "task_completed": {
                "task_id": task_id,
                "status": "completed" if success else "failed",
                "error_message": error_message
            },
            "phase_status": phase_progress,
            "next_task": self._get_task_info(next_task) if next_task else None,
            "recommendations": self._get_post_completion_recommendations(task, phase_progress)
        }

    def _check_dependencies(self, task: Task) -> Dict[str, Any]:
        """检查任务依赖"""
        missing_dependencies = []
        satisfied_dependencies = []
        
        for dep_id in task.dependencies:
            dep_task = self.task_manager.get_task(dep_id)
            if not dep_task:
                missing_dependencies.append({"id": dep_id, "reason": "Task not found"})
            elif dep_task.status != TaskStatus.COMPLETED:
                missing_dependencies.append({
                    "id": dep_id,
                    "reason": f"Task not completed (status: {dep_task.status.value})",
                    "description": dep_task.description
                })
            else:
                satisfied_dependencies.append({
                    "id": dep_id,
                    "description": dep_task.description
                })
        
        return {
            "all_satisfied": len(missing_dependencies) == 0,
            "missing_dependencies": missing_dependencies,
            "satisfied_dependencies": satisfied_dependencies
        }

    def _get_template_info(self, task: Task) -> Dict[str, Any]:
        """获取模板信息"""
        if not task.template_name:
            return {"available": False, "reason": "No template specified"}
        
        template_result = self.template_service.get_template_content(task.template_name)
        
        if not template_result["success"]:
            return {
                "available": False,
                "reason": template_result["error"],
                "template_name": task.template_name
            }
        
        return {
            "available": True,
            "template_name": task.template_name,
            "template_content": template_result["content"],
            "template_metadata": template_result["metadata"],
            "template_variables": template_result["metadata"].get("variables", [])
        }

    def _build_execution_context(self, task: Task, context_enhancement: bool) -> Dict[str, Any]:
        """构建执行上下文"""
        context = {
            "project_path": str(self.project_path),
            "output_path": task.output_path,
            "task_metadata": task.metadata or {}
        }
        
        # 文件相关上下文
        if task.target_file:
            file_context = self._get_file_context(task.target_file, context_enhancement)
            context["file_context"] = file_context
        
        # 模块相关上下文
        if task.target_module:
            module_context = self._get_module_context(task.target_module, context_enhancement)
            context["module_context"] = module_context
        
        # 项目相关上下文
        if context_enhancement:
            project_context = self._get_project_context()
            context["project_context"] = project_context
        
        # 阶段相关上下文
        phase_context = self._get_phase_context(task.phase)
        context["phase_context"] = phase_context
        
        return context

    def _get_file_context(self, target_file: str, enhanced: bool) -> Dict[str, Any]:
        """获取文件上下文"""
        file_path = self.project_path / target_file
        
        context = {
            "file_path": target_file,
            "exists": file_path.exists()
        }
        
        if not file_path.exists():
            return context
        
        # 获取文件元数据
        metadata = self.file_service.get_file_metadata(str(file_path))
        if metadata:
            context["metadata"] = metadata
        
        # 获取文件内容
        content = self.file_service.read_file_safe(str(file_path))
        if content:
            context["content"] = content
            context["content_available"] = True
            context["content_length"] = len(content)
            context["line_count"] = content.count('\n') + 1
        else:
            context["content_available"] = False
        
        # 增强上下文：相关文件
        if enhanced:
            related_files = self._find_related_files(target_file)
            context["related_files"] = related_files
        
        return context

    def _get_module_context(self, target_module: str, enhanced: bool) -> Dict[str, Any]:
        """获取模块上下文"""
        # 查找模块相关的文件
        module_files = self._find_module_files(target_module)
        
        context = {
            "module_name": target_module,
            "module_files": module_files
        }
        
        # 如果有模块文件，获取其内容摘要
        if module_files and enhanced:
            file_summaries = []
            for file_path in module_files[:5]:  # 最多5个文件
                full_path = self.project_path / file_path
                if full_path.exists():
                    content = self.file_service.read_file_safe(str(full_path))
                    if content:
                        file_summaries.append({
                            "file": file_path,
                            "lines": content.count('\n') + 1,
                            "size": len(content),
                            "preview": content[:500] + "..." if len(content) > 500 else content
                        })
            
            context["file_summaries"] = file_summaries
        
        return context

    def _get_project_context(self) -> Dict[str, Any]:
        """获取项目上下文"""
        # 获取项目基本信息
        project_info = self.file_service.get_project_info(str(self.project_path))
        
        # 获取已完成任务的摘要
        completed_tasks = [t for t in self.task_manager.tasks.values() if t.status == TaskStatus.COMPLETED]
        
        context = {
            "project_info": project_info,
            "completed_tasks_count": len(completed_tasks),
            "total_tasks_count": len(self.task_manager.tasks),
            "project_progress": self.task_manager.get_overall_progress()
        }
        
        # 添加已完成任务的简要信息
        if completed_tasks:
            completed_summaries = []
            for task in completed_tasks[-10]:  # 最近10个完成的任务
                completed_summaries.append({
                    "type": task.type.value,
                    "description": task.description,
                    "target": task.target_file or task.target_module,
                    "output": task.output_path
                })
            context["recent_completions"] = completed_summaries
        
        return context

    def _get_phase_context(self, phase: str) -> Dict[str, Any]:
        """获取阶段上下文"""
        try:
            phase_enum = Phase(phase)
            progress = self.phase_controller.get_phase_progress_detailed(phase_enum)
            recommendations = self.phase_controller.get_phase_recommendations(phase_enum)
            
            return {
                "phase": phase,
                "progress": progress,
                "recommendations": recommendations
            }
        except ValueError:
            return {"phase": phase, "error": "Invalid phase"}

    def _get_generation_guidance(self, task: Task) -> Dict[str, Any]:
        """获取生成指导"""
        guidance = {
            "focus_points": [],
            "template_instructions": "",
            "quality_criteria": [],
            "output_requirements": {}
        }
        
        # 根据任务类型提供不同的指导
        task_type = task.type.value
        
        if task_type == "file_summary":
            guidance["focus_points"] = [
                "分析文件的主要功能和职责",
                "识别类、函数和重要常量",
                "理解文件在项目中的作用",
                "分析代码架构和设计模式"
            ]
            guidance["template_instructions"] = "使用file_summary模板，重点关注代码结构和功能分析"
            guidance["quality_criteria"] = [
                "准确识别所有主要组件",
                "清晰描述功能用途",
                "正确分析依赖关系"
            ]
        
        elif task_type == "module_analysis":
            guidance["focus_points"] = [
                "基于文件摘要识别功能模块",
                "分析模块间的关系和依赖",
                "理解模块的业务职责",
                "评估模块的架构设计"
            ]
            guidance["template_instructions"] = "使用module_analysis模板，基于已完成的文件摘要进行模块识别"
            guidance["quality_criteria"] = [
                "合理的模块划分",
                "清晰的职责定义",
                "准确的依赖关系"
            ]
        
        elif task_type == "architecture":
            guidance["focus_points"] = [
                "基于模块分析设计整体架构",
                "选择合适的架构模式",
                "定义系统边界和接口",
                "考虑非功能性需求"
            ]
            guidance["template_instructions"] = "使用architecture模板，整合所有前期分析结果"
            guidance["quality_criteria"] = [
                "合理的架构设计",
                "清晰的技术选型理由",
                "完整的系统描述"
            ]
        
        elif task_type == "project_readme":
            guidance["focus_points"] = [
                "汇总项目的核心特性",
                "提供清晰的安装和使用指南",
                "展示项目的技术亮点",
                "面向用户的友好说明"
            ]
            guidance["template_instructions"] = "使用project_readme模板，创建对外展示的项目文档"
            guidance["quality_criteria"] = [
                "用户友好的表达",
                "完整的使用说明",
                "吸引人的项目介绍"
            ]
        
        # 输出要求
        if task.output_path:
            guidance["output_requirements"] = {
                "file_path": task.output_path,
                "format": "Markdown",
                "encoding": "UTF-8",
                "ensure_directory": True
            }
        
        return guidance

    def _get_task_info(self, task: Optional[Task]) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        if not task:
            return None
        
        return {
            "id": task.id,
            "type": task.type.value,
            "description": task.description,
            "phase": task.phase,
            "target_file": task.target_file,
            "target_module": task.target_module,
            "template_name": task.template_name,
            "output_path": task.output_path,
            "priority": task.priority,
            "status": task.status.value,
            "estimated_time": task.estimated_time,
            "dependencies": task.dependencies,
            "metadata": task.metadata
        }

    def _get_next_task(self, current_task: Task) -> Optional[Dict[str, Any]]:
        """获取下一个建议任务"""
        # 获取同阶段的下一个任务
        next_task = self.task_manager.get_next_task(current_task.phase)
        
        if next_task:
            return {
                "id": next_task.id,
                "description": next_task.description,
                "phase": next_task.phase,
                "reason": "Next task in current phase"
            }
        
        # 检查是否可以进入下一阶段
        try:
            current_phase = Phase(current_task.phase)
            next_phase = self.phase_controller.get_next_phase(current_phase)
            
            if next_phase:
                next_phase_task = self.task_manager.get_next_task(next_phase.value)
                if next_phase_task:
                    return {
                        "id": next_phase_task.id,
                        "description": next_phase_task.description,
                        "phase": next_phase_task.phase,
                        "reason": "First task in next phase"
                    }
        except ValueError:
            pass
        
        return None

    def _find_related_files(self, target_file: str) -> List[str]:
        """查找相关文件"""
        related = []
        target_path = Path(target_file)
        target_dir = target_path.parent
        target_name = target_path.stem
        
        # 查找同目录下的相关文件
        try:
            for file_path in (self.project_path / target_dir).glob("*"):
                if file_path.is_file() and file_path != self.project_path / target_file:
                    relative_path = file_path.relative_to(self.project_path)
                    # 名字相似或同类型的文件
                    if (target_name in file_path.stem or 
                        file_path.suffix == target_path.suffix):
                        related.append(str(relative_path))
        except:
            pass
        
        return related[:5]  # 最多5个相关文件

    def _find_module_files(self, module_name: str) -> List[str]:
        """查找模块文件"""
        module_files = []
        module_lower = module_name.lower()
        
        # 搜索包含模块名的文件
        for file_path in self.project_path.rglob("*.py"):
            relative_path = file_path.relative_to(self.project_path)
            if module_lower in str(relative_path).lower():
                module_files.append(str(relative_path))
        
        return module_files[:10]  # 最多10个文件

    def _get_post_completion_recommendations(self, task: Task, phase_progress: Dict[str, Any]) -> List[str]:
        """获取完成后建议"""
        recommendations = []
        
        # 阶段进度建议
        if phase_progress["can_proceed"]:
            recommendations.append(f"{task.phase}阶段已完成，可以进入下一阶段")
        else:
            remaining = phase_progress["total_tasks"] - phase_progress["completed_tasks"]
            recommendations.append(f"还有{remaining}个任务未完成，继续当前阶段")
        
        # 任务特定建议
        if task.type.value == "file_summary":
            recommendations.append("文件摘要已完成，建议继续分析其他核心文件")
        elif task.type.value == "module_analysis":
            recommendations.append("模块分析已完成，可以开始分析模块关系")
        elif task.type.value == "architecture":
            recommendations.append("架构分析已完成，建议生成技术栈文档")
        
        return recommendations


class TaskExecuteTool:
    """MCP task_execute 工具类"""
    
    def __init__(self):
        self.tool_name = "task_execute"
        self.description = "执行单个或批量任务，提供模板和上下文信息"
        self.logger = logging.getLogger('task_execute')
    
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
                        "description": "项目路径"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "要执行的任务ID"
                    },
                    "execution_mode": {
                        "type": "string",
                        "enum": ["prepare", "execute", "complete"],
                        "default": "execute",
                        "description": "执行模式"
                    },
                    "context_enhancement": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否启用上下文增强"
                    },
                    "mark_in_progress": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否标记任务为进行中"
                    },
                    "completion_data": {
                        "type": "object",
                        "properties": {
                            "success": {
                                "type": "boolean",
                                "default": True
                            },
                            "error_message": {
                                "type": "string"
                            }
                        },
                        "description": "任务完成数据（仅在complete模式下使用）"
                    }
                },
                "required": ["project_path", "task_id"]
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行task_execute工具"""
        try:
            # 参数验证
            project_path = arguments.get("project_path")
            task_id = arguments.get("task_id")
            
            if not project_path or not os.path.exists(project_path):
                return self._error_response("Invalid project path")
            
            if not task_id:
                return self._error_response("Task ID is required")
            
            # 获取参数
            execution_mode = arguments.get("execution_mode", "execute")
            context_enhancement = arguments.get("context_enhancement", True)
            mark_in_progress = arguments.get("mark_in_progress", True)
            completion_data = arguments.get("completion_data", {})
            
            # 创建任务执行器
            executor = TaskExecutor(project_path)
            
            self.logger.info(f"开始执行任务: {task_id}, 模式: {execution_mode}")
            
            # 根据执行模式处理
            if execution_mode == "prepare":
                result = executor.prepare_task_execution(task_id, context_enhancement)
            elif execution_mode == "execute":
                result = executor.execute_task(task_id, mark_in_progress)
            elif execution_mode == "complete":
                success = completion_data.get("success", True)
                error_message = completion_data.get("error_message")
                result = executor.complete_task(task_id, success, error_message)
            else:
                return self._error_response(f"Invalid execution mode: {execution_mode}")
            
            self.logger.info(f"任务执行完成: {task_id}, 模式: {execution_mode}, "
                           f"成功: {'error' not in result}")
            
            return self._success_response(result)
            
        except Exception as e:
            self.logger.error(f"任务执行失败: {str(e)}", exc_info=e)
            return self._error_response(f"Task execution failed: {str(e)}")
    
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


def create_mcp_tool() -> TaskExecuteTool:
    """创建MCP工具实例"""
    return TaskExecuteTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP task_execute tool")
    parser.add_argument("project_path", help="Project path")
    parser.add_argument("--task-id", required=True, help="Task ID to execute")
    parser.add_argument("--mode", choices=["prepare", "execute", "complete"],
                       default="execute", help="Execution mode")
    parser.add_argument("--no-context-enhancement", action="store_true",
                       help="Disable context enhancement")
    parser.add_argument("--no-mark-progress", action="store_true",
                       help="Don't mark task as in progress")
    
    args = parser.parse_args()
    
    # 构建参数
    arguments = {
        "project_path": args.project_path,
        "task_id": args.task_id,
        "execution_mode": args.mode,
        "context_enhancement": not args.no_context_enhancement,
        "mark_in_progress": not args.no_mark_progress
    }
    
    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()