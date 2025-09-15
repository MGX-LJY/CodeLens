#!/usr/bin/env python3
"""
CodeLens 初始化工具 (init_tools)
纯指导工具 - 只提供标准5阶段workflow操作步骤
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 导入日志系统
try:
    # 添加项目根目录到path
    import os
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

class InitToolsCore:
    """CodeLens 初始化指导工具 - 简化版本，只提供操作指导"""
    
    def __init__(self, project_path: str):
        """初始化"""
        self.logger = get_logger(component="InitToolsCore", operation="init")
        self.project_path = Path(project_path).resolve()
        
        self.logger.info("InitToolsCore 初始化", {
            "project_path": str(self.project_path)
        })
        
    def get_workflow_guidance(self) -> Dict[str, Any]:
        """获取标准CodeLens 5阶段工作流指导"""
        operation_id = self.logger.log_operation_start("get_workflow_guidance", 
            project_path=str(self.project_path)
        )
        
        self.logger.debug("开始生成工作流指导", {
            "operation_id": operation_id
        })
        
        # 检查项目路径
        if not self.project_path.exists() or not self.project_path.is_dir():
            self.logger.error("项目路径无效", {
                "project_path": str(self.project_path),
                "exists": self.project_path.exists(),
                "is_dir": self.project_path.is_dir() if self.project_path.exists() else False
            })
            
            result = {
                "success": False,
                "error": f"项目路径无效: {self.project_path}",
                "solution": "请检查项目路径是否正确"
            }
            
            self.logger.log_operation_end("get_workflow_guidance", operation_id, success=False, error="项目路径无效")
            return result
        
        self.logger.debug("项目路径验证通过")
        
        # 获取项目基本信息
        self.logger.debug("开始获取项目基本信息")
        project_info = self._get_project_info()
        self.logger.debug("项目信息获取完成", project_info)
        
        self.logger.debug("开始生成完整指导文档")
        
        result = {
            "success": True,
            "tool": "init_tools",
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "guidance": {
                "workflow_name": "CodeLens 5阶段智能文档生成工作流",
                "description": "标准化文档生成流程，确保高质量输出",
                "project_info": project_info,
                "phases": self._get_workflow_phases(),
                "detailed_steps": self._get_detailed_steps(),
                "execution_tips": self._get_execution_tips(),
                "workflow_features": self._get_workflow_features()
            }
        }
        
        self.logger.info("工作流指导生成完成", {
            "phases_count": len(result["guidance"]["phases"]),
            "steps_count": len(result["guidance"]["detailed_steps"]),
            "project_scale": project_info.get("项目规模", "未知")
        })
        
        self.logger.log_operation_end("get_workflow_guidance", operation_id, success=True)
        return result
    
    def _get_project_info(self) -> Dict[str, Any]:
        """获取项目基本信息"""
        try:
            self.logger.debug("扫描项目文件")
            python_files = list(self.project_path.glob("**/*.py"))
            all_files = [f for f in self.project_path.glob("**/*") if f.is_file()]
            
            self.logger.debug("文件扫描完成", {
                "python_files_count": len(python_files),
                "total_files_count": len(all_files)
            })
            
            # 简单项目规模评估
            total_files = len(all_files)
            if total_files < 20:
                scale = "小型项目"
                time_estimate = "10-20分钟"
            elif total_files < 100:
                scale = "中型项目"
                time_estimate = "30-60分钟"
            else:
                scale = "大型项目"
                time_estimate = "1-3小时"
            
            result = {
                "总文件数": total_files,
                "Python文件数": len(python_files),
                "项目规模": scale,
                "预计耗时": time_estimate
            }
            
            self.logger.debug("项目规模评估完成", result)
            return result
            
        except Exception as e:
            self.logger.warning("项目信息获取失败", {
                "error": str(e)
            })
            return {"项目规模": "未知", "预计耗时": "视项目而定"}
    
    def _get_workflow_phases(self) -> List[Dict[str, str]]:
        """获取5阶段workflow概述"""
        return [
            {
                "phase": "Phase 1",
                "name": "智能项目分析",
                "tool": "doc_guide",
                "description": "分析项目结构、识别框架、生成文档策略"
            },
            {
                "phase": "Phase 2", 
                "name": "任务计划生成",
                "tool": "task_init",
                "description": "基于分析结果生成完整的文档生成任务计划"
            },
            {
                "phase": "Phase 3",
                "name": "状态监控检查", 
                "tool": "task_status",
                "description": "检查任务状态，获取当前待执行任务信息"
            },
            {
                "phase": "Phase 4",
                "name": "任务循环执行",
                "tool": "task_execute", 
                "description": "循环执行所有任务，生成完整文档体系"
            },
            {
                "phase": "Phase 5",
                "name": "文档验证确认",
                "tool": "doc_verify",
                "description": "验证生成文档的完整性和质量"
            }
        ]
    
    def _get_detailed_steps(self) -> Dict[str, Any]:
        """获取详细执行步骤"""
        return {
            "step_1": {
                "title": "🔍 执行项目分析",
                "command": f"python src/mcp_tools/doc_guide.py {self.project_path}",
                "description": "分析项目类型、识别框架、扫描文件结构",
                "estimated_time": "1-2分钟",
                "output": "生成项目分析报告和文档策略",
                "next": "执行step_2"
            },
            "step_2": {
                "title": "📋 生成任务计划",
                "command": f"python src/mcp_tools/task_init.py {self.project_path} --analysis-file .codelens/analysis.json --create-tasks",
                "description": "基于分析结果创建5阶段任务计划",
                "estimated_time": "30秒",
                "output": "在.codelens/tasks.json中创建完整任务列表",
                "dependency": "必须先执行step_1",
                "next": "执行step_3"
            },
            "step_3": {
                "title": "📊 检查任务状态",
                "command": f"python src/mcp_tools/task_status.py {self.project_path} --type current_task",
                "description": "查看当前可执行的任务",
                "estimated_time": "5秒",
                "output": "显示下一个待执行任务的详细信息",
                "next": "根据输出执行step_4"
            },
            "step_4": {
                "title": "⚙️ 执行文档任务 (循环)",
                "command": f"python src/mcp_tools/task_execute.py {self.project_path} --task-id <TASK_ID>",
                "description": "获取任务执行上下文，生成文档，完成任务",
                "estimated_time": "1-5分钟/任务",
                "note": "这个步骤需要重复执行，直到所有任务完成",
                "workflow": [
                    "1. 执行task_execute获取模板和上下文",
                    "2. 根据模板和文件内容生成文档",
                    "3. 保存文档到指定路径",
                    "4. 使用task_execute --mode complete标记完成",
                    "5. 回到step_3获取下一个任务"
                ],
                "next": "循环执行直到所有任务完成，然后step_5"
            },
            "step_5": {
                "title": "✅ 验证文档完整性",
                "command": f"python src/mcp_tools/doc_verify.py {self.project_path}",
                "description": "验证所有文档是否生成完整",
                "estimated_time": "10-30秒",
                "output": "生成完成报告和文档质量评估",
                "final": True
            }
        }
    
    def _get_execution_tips(self) -> List[str]:
        """获取执行提示"""
        return [
            "💡 严格按照步骤顺序执行：doc_guide → task_init → task_status → task_execute(循环) → doc_verify",
            "💡 Step 4(task_execute)是循环过程，需要重复执行直到所有任务完成",
            "💡 每次执行task_execute前，先用task_status检查当前任务",
            "💡 生成文档时要根据模板结构和文件内容创建高质量内容",
            "💡 如果遇到错误，查看错误信息并根据提示处理",
            "💡 可以随时使用task_status查看整体进度",
            "💡 完成所有任务后务必运行doc_verify验证结果"
        ]
    
    def _get_workflow_features(self) -> Dict[str, str]:
        """获取工作流特性说明"""
        return {
            "智能分析": "自动识别项目类型、框架、模块结构",
            "任务管理": "40+任务类型，智能依赖管理，5阶段流程控制",
            "模板系统": "16个文档模板，四层文档架构(文件→模块→架构→项目)",
            "状态跟踪": "实时进度监控，完整执行历史，支持中断恢复",
            "质量保证": "模板驱动生成，结构化输出，完整性验证"
        }


class InitTools:
    """init_tools MCP工具封装类"""
    
    def __init__(self):
        self.logger = get_logger(component="InitTools", operation="init")
        self.logger.info("InitTools MCP工具初始化完成")
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取工具定义"""
        return {
            "name": "init_tools",
            "description": """🚀 CodeLens 工作流指导工具

这个工具提供标准的CodeLens 5阶段文档生成工作流指导：

Phase 1: 智能项目分析 (doc_guide) - 分析项目结构和类型
Phase 2: 任务计划生成 (task_init) - 创建完整任务列表  
Phase 3: 状态监控检查 (task_status) - 获取当前任务信息
Phase 4: 任务循环执行 (task_execute) - 循环生成文档
Phase 5: 文档验证确认 (doc_verify) - 验证最终结果

使用场景：
- 开始新项目文档生成时
- 需要了解完整工作流程时
- 不确定下一步操作时

注意：这是指导工具，不执行实际操作，只提供标准步骤。""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "项目根目录的绝对路径"
                    }
                },
                "required": ["project_path"]
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行init_tools"""
        operation_id = self.logger.log_operation_start("execute_init_tools", 
                                                       project_path=arguments.get("project_path"))
        
        try:
            project_path = arguments.get("project_path")
            if not project_path:
                self.logger.error("缺少必需参数", {
                    "missing_parameter": "project_path",
                    "provided_args": list(arguments.keys())
                })
                
                result = {
                    "success": False,
                    "error": "缺少必需参数: project_path"
                }
                
                self.logger.log_operation_end("execute_init_tools", operation_id, success=False, error="缺少必需参数")
                return result
            
            self.logger.info("开始生成工作流指导", {
                "project_path": project_path
            })
            
            core = InitToolsCore(project_path)
            result = core.get_workflow_guidance()
            
            self.logger.info("工作流指导生成完成", {
                "success": result["success"]
            })
            
            self.logger.log_operation_end("execute_init_tools", operation_id, success=True)
            return result
            
        except Exception as e:
            self.logger.error("init_tools执行失败", {
                "error": str(e),
                "project_path": arguments.get("project_path")
            }, exc_info=e)
            
            result = {
                "success": False,
                "error": f"init_tools执行失败: {str(e)}"
            }
            
            self.logger.log_operation_end("execute_init_tools", operation_id, success=False, error=str(e))
            return result


def create_mcp_tool() -> InitTools:
    """创建MCP工具实例"""
    return InitTools()


# 命令行接口
def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description="CodeLens 工作流指导工具")
    parser.add_argument("project_path", help="项目路径")
    
    args = parser.parse_args()
    
    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute({"project_path": args.project_path})
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()