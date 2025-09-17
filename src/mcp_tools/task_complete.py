"""
MCP task_complete 工具实现
验证任务输出并标记任务完成
"""
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.task_engine.task_manager import TaskManager, TaskStatus
from src.task_engine.state_tracker import StateTracker
from src.task_engine.phase_controller import PhaseController, Phase, PhaseStatus

# 导入日志系统
try:
    # 添加项目根目录到path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, project_root)
    from src.logging import get_logger
except ImportError:
    # 如果日志系统不可用，创建一个空日志器
    class DummyLogger:
        def debug(self, msg, context=None): pass
        def info(self, msg, context=None): pass
        def warning(self, msg, context=None): pass
        def error(self, msg, context=None, exc_info=None): pass
        def log_operation_start(self, operation, *args, **kwargs): return "dummy_id"
        def log_operation_end(self, operation, operation_id, success=True, **kwargs): pass

    get_logger = lambda **kwargs: DummyLogger()


class TaskCompleteTool:
    """任务完成工具"""
    
    def __init__(self):
        self.logger = get_logger(component="TaskCompleteTool", operation="init")
        self.logger.info("TaskCompleteTool 初始化完成")
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取MCP工具定义"""
        return {
            "name": "task_complete",
            "description": "完成任务并验证输出质量",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "项目路径（可选，默认使用当前工作目录）"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "要完成的任务ID"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "输出文件路径（可选，用于验证）"
                    }
                },
                "required": ["project_path", "task_id"]
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        完成任务并验证输出文件
        
        参数:
        - project_path: 项目路径
        - task_id: 任务ID
        - output_file: 输出文件路径 (可选，用于验证)
        """
        operation_id = self.logger.log_operation_start("execute_task_complete",
                                                       project_path=arguments.get("project_path"),
                                                       task_id=arguments.get("task_id"),
                                                       output_file=arguments.get("output_file"))
        
        project_path = arguments.get("project_path")
        task_id = arguments.get("task_id")
        output_file = arguments.get("output_file")
        
        self.logger.debug("开始执行任务完成操作", {
            "project_path": project_path,
            "task_id": task_id,
            "output_file": output_file
        })
        
        if not project_path or not task_id:
            self.logger.error("缺少必需参数", {
                "project_path_provided": bool(project_path),
                "task_id_provided": bool(task_id),
                "all_args": list(arguments.keys())
            })
            
            result = {
                "success": False, 
                "error": "Missing required parameters: project_path and task_id are required"
            }
            
            self.logger.log_operation_end("execute_task_complete", operation_id, success=False, error="缺少必需参数")
            return result
        
        try:
            # 初始化任务管理器
            self.logger.debug("初始化任务管理器", {
                "project_path": project_path
            })
            task_manager = TaskManager(project_path)
            
            self.logger.debug("获取任务信息", {
                "task_id": task_id
            })
            task = task_manager.get_task(task_id)
            
            if not task:
                self.logger.error("任务不存在", {
                    "task_id": task_id
                })
                
                result = {"success": False, "error": f"Task {task_id} not found"}
                self.logger.log_operation_end("execute_task_complete", operation_id, success=False, error="任务不存在")
                return result
            
            self.logger.info("任务信息获取成功", {
                "task_id": task_id,
                "task_type": task.type.value,
                "task_status": task.status.value,
                "output_path": task.output_path
            })
            
            # 验证输出文件
            expected_output = Path(project_path) / task.output_path
            
            self.logger.debug("开始验证输出文件", {
                "expected_output": str(expected_output)
            })
            
            verification_result = self._verify_task_output(expected_output, task.type.value)
            
            self.logger.debug("文件验证完成", {
                "verification_result": verification_result
            })
            
            if verification_result["valid"]:
                self.logger.info("输出文件验证通过，开始标记任务完成", {
                    "task_id": task_id,
                    "file_size": verification_result["file_size"]
                })
                
                # 标记任务完成
                task_manager.update_task_status(task_id, TaskStatus.COMPLETED)
                
                self.logger.debug("任务状态更新为完成")
                
                # 记录完成事件
                try:
                    state_tracker = StateTracker(project_path, task_manager, None)
                    state_tracker.record_task_event("completed", task_id)
                    self.logger.debug("任务完成事件记录成功")
                except Exception as e:
                    self.logger.warning("任务完成事件记录失败", {
                        "error": str(e)
                    })
                
                # 检查是否需要执行项目清理
                cleanup_result = self._check_and_cleanup_project(project_path, task_manager)
                
                result = {
                    "success": True,
                    "message": f"Task {task_id} completed successfully",
                    "task_id": task_id,
                    "output_file": str(expected_output),
                    "verification": verification_result,
                    "cleanup": cleanup_result,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                self.logger.info("任务完成操作成功", {
                    "task_id": task_id,
                    "output_file": str(expected_output)
                })
                
                self.logger.log_operation_end("execute_task_complete", operation_id, success=True)
                return result
            else:
                self.logger.error("输出文件验证失败", {
                    "task_id": task_id,
                    "issues": verification_result["issues"],
                    "expected_path": str(expected_output)
                })
                
                result = {
                    "success": False, 
                    "error": "Task output verification failed",
                    "issues": verification_result["issues"],
                    "expected_path": str(expected_output),
                    "task_id": task_id
                }
                
                self.logger.log_operation_end("execute_task_complete", operation_id, success=False, error="输出文件验证失败")
                return result
                
        except Exception as e:
            self.logger.error("任务完成操作失败", {
                "error": str(e),
                "task_id": task_id,
                "project_path": project_path
            }, exc_info=True)
            
            result = {"success": False, "error": str(e), "task_id": task_id}
            self.logger.log_operation_end("execute_task_complete", operation_id, success=False, error=str(e))
            return result
    
    def _verify_task_output(self, output_path: Path, task_type: str) -> Dict[str, Any]:
        """验证任务输出文件 - 简单检查文件是否存在且不为空"""
        self.logger.debug("开始验证任务输出文件", {
            "output_path": str(output_path),
            "task_type": task_type
        })
        
        result = {
            "valid": False,
            "issues": [],
            "file_size": 0,
            "path_checked": str(output_path)
        }
        
        # 检查文件存在
        if not output_path.exists():
            self.logger.warning("输出文件不存在", {
                "output_path": str(output_path)
            })
            result["issues"].append("输出文件不存在")
            return result
        
        # 检查文件大小（只要不是空文件就行）
        try:
            file_size = output_path.stat().st_size
            result["file_size"] = file_size
            
            self.logger.debug("文件大小检查", {
                "file_size": file_size
            })
            
            if file_size == 0:
                self.logger.warning("输出文件为空", {
                    "output_path": str(output_path)
                })
                result["issues"].append("文件为空")
                return result
                
        except Exception as e:
            self.logger.error("无法获取文件信息", {
                "output_path": str(output_path),
                "error": str(e)
            })
            result["issues"].append(f"无法获取文件信息: {str(e)}")
            return result
        
        # 文件存在且不为空，验证通过
        self.logger.info("文件验证通过", {
            "output_path": str(output_path),
            "file_size": file_size
        })
        result["valid"] = True
        return result
    
    def _check_and_cleanup_project(self, project_path: str, task_manager: TaskManager) -> Dict[str, Any]:
        """检查项目状态并在所有阶段完成时执行清理操作"""
        cleanup_result = {
            "cleanup_performed": False,
            "files_cleaned": [],
            "cleanup_errors": [],
            "project_status": "in_progress"
        }
        
        try:
            # 初始化阶段控制器
            phase_controller = PhaseController(task_manager)
            
            # 检查所有阶段状态
            all_phases_completed = True
            phases_status = {}
            
            for phase in Phase:
                status = phase_controller.get_phase_status(phase)
                phases_status[phase.value] = status.value
                if status != PhaseStatus.COMPLETED:
                    all_phases_completed = False
            
            cleanup_result["phases_status"] = phases_status
            
            self.logger.info("项目阶段状态检查", {
                "all_phases_completed": all_phases_completed,
                "phases_status": phases_status
            })
            
            # 如果所有阶段都完成，执行清理操作
            if all_phases_completed:
                cleanup_result["project_status"] = "completed"
                cleanup_result.update(self._perform_cleanup(project_path))
                
                self.logger.info("项目所有阶段已完成，执行清理操作", {
                    "cleanup_performed": cleanup_result["cleanup_performed"],
                    "files_cleaned_count": len(cleanup_result["files_cleaned"])
                })
            else:
                self.logger.debug("项目仍有未完成阶段，跳过清理操作")
                
        except Exception as e:
            cleanup_result["cleanup_errors"].append(f"清理检查失败: {str(e)}")
            self.logger.error("项目清理检查失败", {
                "error": str(e)
            }, exc_info=True)
        
        return cleanup_result
    
    def _perform_cleanup(self, project_path: str) -> Dict[str, Any]:
        """执行项目清理操作"""
        cleanup_info = {
            "cleanup_performed": True,
            "files_cleaned": [],
            "cleanup_errors": []
        }
        
        project_path = Path(project_path)
        codelens_dir = project_path / ".codelens"
        
        # 定义需要清理的临时文件模式
        temp_file_patterns = [
            "analysis*.json",
            "temp_*.json", 
            "cache_*.json",
            "scan_*.json",
            "*_temp.json",
            "*_cache.json",
            "*.tmp",
            "*.temp"
        ]
        
        # 保留的重要文件
        keep_files = {
            "file_fingerprints.json",
            "change_history.json",
            "last_change.json",
            "task_state.json",
            "config.json"
        }
        
        try:
            if codelens_dir.exists():
                # 清理临时文件
                for pattern in temp_file_patterns:
                    for file_path in codelens_dir.glob(pattern):
                        if file_path.name not in keep_files:
                            try:
                                file_path.unlink()
                                cleanup_info["files_cleaned"].append(str(file_path.relative_to(project_path)))
                                self.logger.debug(f"清理临时文件: {file_path}")
                            except Exception as e:
                                error_msg = f"删除文件失败 {file_path}: {str(e)}"
                                cleanup_info["cleanup_errors"].append(error_msg)
                                self.logger.warning(error_msg)
                
                # 清理空的缓存目录
                cache_dirs = ["cache", "temp", "analysis"]
                for cache_dir_name in cache_dirs:
                    cache_dir = codelens_dir / cache_dir_name
                    if cache_dir.exists() and cache_dir.is_dir():
                        try:
                            # 只删除空目录
                            if not any(cache_dir.iterdir()):
                                cache_dir.rmdir()
                                cleanup_info["files_cleaned"].append(str(cache_dir.relative_to(project_path)))
                                self.logger.debug(f"清理空缓存目录: {cache_dir}")
                        except Exception as e:
                            error_msg = f"删除缓存目录失败 {cache_dir}: {str(e)}"
                            cleanup_info["cleanup_errors"].append(error_msg)
                            self.logger.warning(error_msg)
                
            self.logger.info("项目清理操作完成", {
                "files_cleaned_count": len(cleanup_info["files_cleaned"]),
                "errors_count": len(cleanup_info["cleanup_errors"])
            })
            
        except Exception as e:
            error_msg = f"项目清理操作失败: {str(e)}"
            cleanup_info["cleanup_errors"].append(error_msg)
            self.logger.error(error_msg, exc_info=True)
        
        return cleanup_info


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete and verify a documentation task")
    parser.add_argument("project_path", help="Path to the project")
    parser.add_argument("--task-id", required=True, help="Task ID to complete")
    parser.add_argument("--output-file", help="Expected output file path")
    
    args = parser.parse_args()
    
    tool = TaskCompleteTool()
    
    arguments = {
        "project_path": args.project_path,
        "task_id": args.task_id
    }
    
    if args.output_file:
        arguments["output_file"] = args.output_file
    
    result = tool.execute(arguments)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 返回适当的退出码
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
