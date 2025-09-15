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

# 导入日志系统
import logging


class TaskCompleteTool:
    """任务完成工具"""
    
    def __init__(self):
        self.logger = logging.getLogger('task_complete')
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        完成任务并验证输出文件
        
        参数:
        - project_path: 项目路径
        - task_id: 任务ID
        - output_file: 输出文件路径 (可选，用于验证)
        """
        
        project_path = arguments.get("project_path")
        task_id = arguments.get("task_id")
        output_file = arguments.get("output_file")
        
        if not project_path or not task_id:
            return {
                "success": False, 
                "error": "Missing required parameters: project_path and task_id are required"
            }
        
        try:
            # 初始化任务管理器
            task_manager = TaskManager(project_path)
            task = task_manager.get_task(task_id)
            
            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}
            
            # 验证输出文件
            expected_output = Path(project_path) / task.output_path
            
            verification_result = self._verify_task_output(expected_output, task.type.value)
            
            if verification_result["valid"]:
                # 标记任务完成
                task_manager.update_task_status(task_id, TaskStatus.COMPLETED)
                
                # 记录完成事件
                try:
                    state_tracker = StateTracker(project_path, task_manager, None)
                    state_tracker.record_task_event("completed", task_id)
                except Exception as e:
                    self.logger.warning(f"Failed to record completion event: {e}")
                
                return {
                    "success": True,
                    "message": f"Task {task_id} completed successfully",
                    "task_id": task_id,
                    "output_file": str(expected_output),
                    "verification": verification_result,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {
                    "success": False, 
                    "error": "Task output verification failed",
                    "issues": verification_result["issues"],
                    "expected_path": str(expected_output),
                    "task_id": task_id
                }
                
        except Exception as e:
            self.logger.error(f"Task completion failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "task_id": task_id}
    
    def _verify_task_output(self, output_path: Path, task_type: str) -> Dict[str, Any]:
        """验证任务输出文件 - 简单检查文件是否存在且不为空"""
        
        result = {
            "valid": False,
            "issues": [],
            "file_size": 0,
            "path_checked": str(output_path)
        }
        
        # 检查文件存在
        if not output_path.exists():
            result["issues"].append("输出文件不存在")
            return result
        
        # 检查文件大小（只要不是空文件就行）
        try:
            file_size = output_path.stat().st_size
            result["file_size"] = file_size
            
            if file_size == 0:
                result["issues"].append("文件为空")
                return result
                
        except Exception as e:
            result["issues"].append(f"无法获取文件信息: {str(e)}")
            return result
        
        # 文件存在且不为空，验证通过
        result["valid"] = True
        return result


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
