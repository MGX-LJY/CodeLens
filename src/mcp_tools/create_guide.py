#!/usr/bin/env python3
"""
CodeLens 创造模式引导工具 (create_guide)
创造模式主入口 - 提供三阶段创新功能开发指导
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

class CreateGuideCore:
    """CodeLens 创造模式引导工具 - 三阶段功能创新开发指导"""
    
    def __init__(self, project_path: str):
        """初始化"""
        self.logger = get_logger(component="CreateGuideCore", operation="init")
        self.project_path = Path(project_path).resolve()
        self.create_docs_path = self.project_path / "docs" / "project" / "create"
        
        self.logger.info("CreateGuideCore 初始化", {
            "project_path": str(self.project_path),
            "create_docs_path": str(self.create_docs_path)
        })
        
    def get_create_mode_guidance(self) -> Dict[str, Any]:
        """获取创造模式三阶段工作流指导"""
        operation_id = self.logger.log_operation_start("get_create_mode_guidance", 
            project_path=str(self.project_path)
        )
        
        try:
            guidance = {
                "tool": "create_guide",
                "mode": "guidance",
                "project_path": str(self.project_path),
                "timestamp": datetime.now().isoformat(),
                
                "workflow": {
                    "title": "🚀 CodeLens 创造模式 - 四阶段功能创新开发流程",
                    "description": "架构理解、智能化功能需求分析、实现方案设计、开发计划生成的完整工作流",
                    "total_stages": 4,
                    
                    "stages": [
                        {
                            "stage": 0,
                            "name": "架构理解 (Architecture)",
                            "description": "深入理解项目架构文档，确保新功能符合现有架构模式",
                            "tool": "architecture_analysis",
                            "input": "项目路径和架构文档",
                            "output": "架构理解报告和设计约束",
                            "file_location": "/docs/project/create/architecture/",
                            "command_example": "阅读 docs/architecture/ 下的所有架构文档，理解系统组件、数据流、技术栈",
                            "required_reading": [
                                "docs/architecture/overview.md - 系统架构概述",
                                "docs/architecture/tech-stack.md - 技术栈详细分析", 
                                "docs/architecture/data-flow.md - 数据流设计",
                                "docs/architecture/diagrams/ - 架构图表"
                            ]
                        },
                        {
                            "stage": 1,
                            "name": "需求确认 (Requirement)",
                            "description": "基于架构理解进行交互式功能需求分析和验收标准确认",
                            "tool": "create_requirement",
                            "input": "功能想法和基本描述，结合架构约束",
                            "output": "结构化需求文档",
                            "file_location": "/docs/project/create/requirements/",
                            "command_example": "python src/mcp_tools/create_requirement.py PROJECT_PATH --feature-name '新功能名称' --mode interactive"
                        },
                        {
                            "stage": 2,
                            "name": "分析实现 (Analysis)", 
                            "description": "基于架构文档分析实现方案和影响链",
                            "tool": "create_analysis",
                            "input": "需求文档ID + 架构理解",
                            "output": "实现分析报告（需用户确认）",
                            "file_location": "/docs/project/create/analysis/",
                            "command_example": "python src/mcp_tools/create_analysis.py PROJECT_PATH --requirement-id REQ_ID --analysis-depth detailed"
                        },
                        {
                            "stage": 3,
                            "name": "生成计划 (Todo)",
                            "description": "生成详细的实现步骤和开发计划",
                            "tool": "create_todo",
                            "input": "确认的分析报告ID",
                            "output": "可执行的实现计划文档",
                            "file_location": "/docs/project/create/todos/",
                            "command_example": "python src/mcp_tools/create_todo.py PROJECT_PATH --analysis-id ANALYSIS_ID --todo-granularity function"
                        }
                    ]
                },
                
                "usage_modes": {
                    "interactive": {
                        "description": "分阶段交互式执行",
                        "commands": [
                            "python src/mcp_tools/create_guide.py PROJECT_PATH --stage 0  # 架构理解",
                            "python src/mcp_tools/create_guide.py PROJECT_PATH --stage 1  # 需求确认",
                            "python src/mcp_tools/create_guide.py PROJECT_PATH --stage 2  # 分析实现", 
                            "python src/mcp_tools/create_guide.py PROJECT_PATH --stage 3  # 生成计划"
                        ]
                    },
                    "full_workflow": {
                        "description": "一键式完整流程（需要用户交互确认）",
                        "command": "python src/mcp_tools/create_guide.py PROJECT_PATH --stage all --feature-name '功能名称'"
                    },
                    "status_check": {
                        "description": "查看当前创造模式状态和进度",
                        "command": "python src/mcp_tools/create_guide.py PROJECT_PATH --show-status"
                    }
                },
                
                "directory_structure": {
                    "create_docs": str(self.create_docs_path),
                    "structure": {
                        "architecture/": "架构理解报告存放目录",
                        "requirements/": "需求确认文档存放目录",
                        "analysis/": "实现分析报告存放目录", 
                        "todos/": "实现计划文档存放目录",
                        "templates/": "创造模式专用模板目录"
                    }
                },
                
                "benefits": [
                    "🏗️ 架构对齐：深入理解现有架构，确保新功能符合设计模式",
                    "🎯 需求精准：基于架构约束进行需求分析，避免设计偏差",
                    "🔍 影响全面：自动分析架构影响和代码修改范围",
                    "⚡ 规划智能：生成详细实现步骤，提高开发效率",
                    "🛡️ 风险预控：提前识别架构冲突和依赖问题",
                    "📋 链路完整：完整的文档链路，支持功能迭代和维护"
                ],
                
                "next_steps": "运行 'python src/mcp_tools/create_guide.py PROJECT_PATH --stage 0' 开始架构理解阶段"
            }
            
            self.logger.log_operation_end("get_create_mode_guidance", operation_id, 
                success=True, guidance_provided=True
            )
            
            return guidance
            
        except Exception as e:
            self.logger.log_operation_end("get_create_mode_guidance", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to get create mode guidance: {str(e)}"
            }
    
    def get_create_status(self) -> Dict[str, Any]:
        """获取当前创造模式状态"""
        operation_id = self.logger.log_operation_start("get_create_status", 
            project_path=str(self.project_path)
        )
        
        try:
            # 检查创造模式目录结构
            architecture_dir = self.create_docs_path / "architecture"
            requirements_dir = self.create_docs_path / "requirements"
            analysis_dir = self.create_docs_path / "analysis"
            todos_dir = self.create_docs_path / "todos"
            
            # 统计各阶段文档数量
            arch_count = len(list(architecture_dir.glob("*.md"))) if architecture_dir.exists() else 0
            req_count = len(list(requirements_dir.glob("*.md"))) if requirements_dir.exists() else 0
            analysis_count = len(list(analysis_dir.glob("*.md"))) if analysis_dir.exists() else 0
            todo_count = len(list(todos_dir.glob("*.md"))) if todos_dir.exists() else 0
            
            # 获取最新文档
            latest_files = {}
            if architecture_dir.exists():
                arch_files = list(architecture_dir.glob("*.md"))
                if arch_files:
                    latest_arch = max(arch_files, key=lambda f: f.stat().st_mtime)
                    latest_files["latest_architecture"] = latest_arch.name
                    
            if requirements_dir.exists():
                req_files = list(requirements_dir.glob("*.md"))
                if req_files:
                    latest_req = max(req_files, key=lambda f: f.stat().st_mtime)
                    latest_files["latest_requirement"] = latest_req.name
            
            if analysis_dir.exists():
                analysis_files = list(analysis_dir.glob("*.md"))
                if analysis_files:
                    latest_analysis = max(analysis_files, key=lambda f: f.stat().st_mtime)
                    latest_files["latest_analysis"] = latest_analysis.name
                    
            if todos_dir.exists():
                todo_files = list(todos_dir.glob("*.md"))
                if todo_files:
                    latest_todo = max(todo_files, key=lambda f: f.stat().st_mtime)
                    latest_files["latest_todo"] = latest_todo.name
            
            status = {
                "tool": "create_guide",
                "mode": "status",
                "project_path": str(self.project_path),
                "timestamp": datetime.now().isoformat(),
                
                "directory_status": {
                    "create_docs_exists": self.create_docs_path.exists(),
                    "architecture_dir_exists": architecture_dir.exists(),
                    "requirements_dir_exists": requirements_dir.exists(),
                    "analysis_dir_exists": analysis_dir.exists(),
                    "todos_dir_exists": todos_dir.exists()
                },
                
                "stage_progress": {
                    "stage_0_architecture": {
                        "count": arch_count,
                        "status": "completed" if arch_count > 0 else "pending"
                    },
                    "stage_1_requirements": {
                        "count": req_count,
                        "status": "completed" if req_count > 0 else "pending"
                    },
                    "stage_2_analysis": {
                        "count": analysis_count,
                        "status": "completed" if analysis_count > 0 else "pending"
                    },
                    "stage_3_todos": {
                        "count": todo_count,
                        "status": "completed" if todo_count > 0 else "pending"
                    }
                },
                
                "latest_files": latest_files,
                
                "recommendations": self._get_recommendations(arch_count, req_count, analysis_count, todo_count)
            }
            
            self.logger.log_operation_end("get_create_status", operation_id, 
                success=True, status_provided=True
            )
            
            return status
            
        except Exception as e:
            self.logger.log_operation_end("get_create_status", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to get create status: {str(e)}"
            }
    
    def _get_recommendations(self, arch_count: int, req_count: int, analysis_count: int, todo_count: int) -> List[str]:
        """根据当前状态生成建议"""
        recommendations = []
        
        if arch_count == 0:
            recommendations.append("🏗️ 开始阶段0：深入理解项目架构")
            recommendations.append("📚 建议：仔细阅读 docs/architecture/ 下的所有架构文档")
            recommendations.append("🔍 重点：理解系统架构概述、技术栈、数据流设计")
        elif req_count == 0:
            recommendations.append("💡 进入阶段1：基于架构理解进行需求确认")
            recommendations.append("📝 命令：python src/mcp_tools/create_requirement.py PROJECT_PATH --feature-name '功能名称'")
        elif analysis_count == 0:
            recommendations.append("🔍 进入阶段2：基于需求文档进行实现分析")
            recommendations.append("📊 命令：python src/mcp_tools/create_analysis.py PROJECT_PATH --requirement-id REQ_ID")
        elif todo_count == 0:
            recommendations.append("📋 进入阶段3：生成详细实现计划")
            recommendations.append("⚡ 命令：python src/mcp_tools/create_todo.py PROJECT_PATH --analysis-id ANALYSIS_ID")
        else:
            recommendations.append("✅ 创造模式四个阶段都有文档，可以开始新功能开发")
            recommendations.append("🔄 或继续添加新功能需求和分析")
        
        return recommendations
    
    def execute_stage(self, stage: str, **kwargs) -> Dict[str, Any]:
        """执行指定阶段"""
        operation_id = self.logger.log_operation_start("execute_stage", 
            project_path=str(self.project_path), stage=stage
        )
        
        try:
            if stage == "all":
                return self._execute_full_workflow(**kwargs)
            elif stage in ["0", "1", "2", "3"]:
                return self._execute_single_stage(int(stage), **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown stage: {stage}. Use 0, 1, 2, 3, or 'all'"
                }
                
        except Exception as e:
            self.logger.log_operation_end("execute_stage", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to execute stage {stage}: {str(e)}"
            }
    
    def _execute_single_stage(self, stage_num: int, **kwargs) -> Dict[str, Any]:
        """执行单个阶段"""
        stage_info = {
            0: {
                "name": "架构理解",
                "tool": "architecture_analysis",
                "next_command": "手动阅读架构文档",
                "reading_list": [
                    "docs/architecture/overview.md - 系统架构概述",
                    "docs/architecture/tech-stack.md - 技术栈详细分析", 
                    "docs/architecture/data-flow.md - 数据流设计",
                    "docs/architecture/diagrams/ - 架构图表"
                ]
            },
            1: {
                "name": "需求确认",
                "tool": "create_requirement",
                "next_command": f"python src/mcp_tools/create_requirement.py {self.project_path}"
            },
            2: {
                "name": "分析实现", 
                "tool": "create_analysis",
                "next_command": f"python src/mcp_tools/create_analysis.py {self.project_path}"
            },
            3: {
                "name": "生成计划",
                "tool": "create_todo", 
                "next_command": f"python src/mcp_tools/create_todo.py {self.project_path}"
            }
        }
        
        if stage_num not in stage_info:
            return {"success": False, "error": f"Invalid stage number: {stage_num}"}
        
        stage = stage_info[stage_num]
        
        result = {
            "tool": "create_guide",
            "mode": "execute_stage",
            "stage": stage_num,
            "stage_name": stage["name"],
            "action": "redirect_to_tool",
            "next_tool": stage["tool"],
            "command_to_run": stage["next_command"],
            "message": f"阶段{stage_num}：{stage['name']} - 请运行对应的工具命令",
            "timestamp": datetime.now().isoformat()
        }
        
        # 为阶段0添加必读文档列表
        if stage_num == 0:
            result["reading_list"] = stage["reading_list"]
            result["action"] = "manual_reading"
            result["message"] = f"阶段{stage_num}：{stage['name']} - 请仔细阅读以下架构文档"
        
        return result
    
    def _execute_full_workflow(self, **kwargs) -> Dict[str, Any]:
        """执行完整的四阶段工作流"""
        return {
            "tool": "create_guide",
            "mode": "full_workflow",
            "message": "完整创造模式工作流需要分阶段执行，每个阶段需要用户确认",
            "workflow_steps": [
                "0. 深入理解项目架构，阅读架构文档",
                "1. 基于架构理解，运行需求确认工具",
                "2. 用户确认需求后，运行分析工具",
                "3. 用户确认分析结果后，运行计划生成工具"
            ],
            "start_command": f"阅读 docs/architecture/ 下的架构文档，然后运行阶段1",
            "timestamp": datetime.now().isoformat()
        }

class CreateGuideTool:
    """创造模式引导工具 - MCP接口"""
    
    def __init__(self):
        self.tool_name = "create_guide"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取工具定义"""
        return {
            "name": self.tool_name,
            "description": "🚀 CodeLens创造模式引导工具 - 三阶段功能创新开发流程指导",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "项目根目录路径",
                        "default": "."
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["guidance", "status", "execute"],
                        "description": "执行模式: guidance=显示指导, status=查看状态, execute=执行阶段",
                        "default": "guidance"
                    },
                    "stage": {
                        "type": "string", 
                        "enum": ["0", "1", "2", "3", "all"],
                        "description": "执行阶段: 0=架构理解, 1=需求确认, 2=分析实现, 3=生成计划, all=完整流程"
                    },
                    "feature_name": {
                        "type": "string",
                        "description": "功能名称 (用于stage=all模式)"
                    }
                },
                "required": ["project_path"]
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        try:
            project_path = arguments.get("project_path", ".")
            mode = arguments.get("mode", "guidance")
            stage = arguments.get("stage")
            feature_name = arguments.get("feature_name")
            
            # 初始化创造模式引导工具
            guide = CreateGuideCore(project_path)
            
            if mode == "status":
                # 显示状态
                result = guide.get_create_status()
            elif mode == "execute" and stage:
                # 执行指定阶段
                result = guide.execute_stage(stage, feature_name=feature_name)
            else:
                # 显示指导信息
                result = guide.get_create_mode_guidance()
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"CreateGuide tool execution failed: {str(e)}"
            }

def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(description="CodeLens 创造模式引导工具")
    parser.add_argument("project_path", nargs="?", default=".", 
                        help="项目路径 (默认: 当前目录)")
    parser.add_argument("--stage", choices=["0", "1", "2", "3", "all"], 
                        help="执行指定阶段 (0:架构理解, 1:需求确认, 2:分析实现, 3:生成计划, all:完整流程)")
    parser.add_argument("--show-status", action="store_true", 
                        help="显示当前创造模式状态")
    parser.add_argument("--feature-name", 
                        help="功能名称 (用于stage=all模式)")
    
    args = parser.parse_args()
    
    try:
        # 初始化创造模式引导工具
        guide = CreateGuideCore(args.project_path)
        
        if args.show_status:
            # 显示状态
            result = guide.get_create_status()
        elif args.stage:
            # 执行指定阶段
            result = guide.execute_stage(args.stage, feature_name=args.feature_name)
        else:
            # 显示指导信息
            result = guide.get_create_mode_guidance()
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "tool": "create_guide"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()