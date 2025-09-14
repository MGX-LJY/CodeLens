"""
MCP task_init 工具实现
基于项目分析结果，生成完整的阶段性任务列表
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

from src.task_engine.task_manager import TaskManager, TaskType, TaskStatus
from src.task_engine.phase_controller import PhaseController, Phase

# 导入日志系统
import logging


class TaskPlanGenerator:
    """任务计划生成器"""

    def __init__(self):
        # 模板映射关系
        self.template_mapping = {
            TaskType.SCAN: "project_scan_summary",  # 添加scan任务模板映射
            TaskType.FILE_SUMMARY: "file_summary",
            TaskType.MODULE_ANALYSIS: "module_analysis",
            TaskType.MODULE_RELATIONS: "module_relations",
            TaskType.DEPENDENCY_GRAPH: "dependency_graph",
            TaskType.MODULE_README: "module_readme",
            TaskType.MODULE_API: "module_api",
            TaskType.MODULE_FLOW: "module_flow",
            TaskType.ARCHITECTURE: "architecture",
            TaskType.TECH_STACK: "tech_stack",
            TaskType.DATA_FLOW: "data_flow",
            TaskType.SYSTEM_ARCHITECTURE: "system_architecture",
            TaskType.COMPONENT_DIAGRAM: "component_diagram",
            TaskType.DEPLOYMENT_DIAGRAM: "deployment_diagram",
            TaskType.PROJECT_README: "project_readme"
        }

        # 优先级映射
        self.priority_mapping = {
            "high": ["main.py", "app.py", "index.js", "server.js", "main.go", "main.rs"],
            "normal": ["config", "model", "service", "controller", "handler"],
            "low": ["util", "helper", "test", "spec"]
        }

    def generate_tasks(self, project_path: str, analysis_result: Dict[str, Any],
                       task_granularity: str = "file", parallel_tasks: bool = False,
                       custom_priorities: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成完整的任务计划"""

        # 提取分析结果 - 修复嵌套JSON结构解析
        if "data" in analysis_result:
            # 如果是MCP工具的输出格式
            data = analysis_result["data"]
            project_analysis = data.get("project_analysis", {})
            plan = data.get("generation_plan", {})
        else:
            # 如果是直接的分析结果格式
            project_analysis = analysis_result.get("project_analysis", {})
            plan = analysis_result.get("generation_plan", {})

        # 生成全局scan任务ID，确保依赖关系一致
        scan_task_id = f"scan_{int(time.time() * 1000000)}"  # 使用更高精度避免冲突
        
        # 生成各阶段任务
        phase_1_tasks = self._generate_phase_1_tasks(project_path, project_analysis, scan_task_id)
        phase_2_tasks = self._generate_phase_2_tasks(project_path, plan, scan_task_id, custom_priorities)
        phase_3_tasks = self._generate_phase_3_tasks(project_path, project_analysis, phase_2_tasks)
        phase_4_tasks = self._generate_phase_4_tasks(project_path, project_analysis, phase_3_tasks)
        phase_5_tasks = self._generate_phase_5_tasks(project_path, project_analysis, phase_4_tasks)

        # 计算总体统计
        all_tasks = phase_1_tasks + phase_2_tasks + phase_3_tasks + phase_4_tasks + phase_5_tasks

        task_plan = {
            "total_phases": 5,
            "total_tasks": len(all_tasks),
            "estimated_duration": plan.get("estimated_duration", "Unknown"),
            "dependencies_graph": self._build_dependency_graph(all_tasks),
            "task_distribution": {
                "phase_1_scan": len(phase_1_tasks),
                "phase_2_files": len(phase_2_tasks),
                "phase_3_modules": len(phase_3_tasks),
                "phase_4_architecture": len(phase_4_tasks),
                "phase_5_project": len(phase_5_tasks)
            }
        }

        # 构建完整响应
        return {
            "task_plan": task_plan,
            "phase_1_scan": {
                "description": "项目扫描和分析",
                "dependencies": [],
                "estimated_time": "5 minutes",
                "tasks": phase_1_tasks
            },
            "phase_2_files": {
                "description": f"文件层文档生成（{len(phase_2_tasks)}个文件）",
                "dependencies": ["phase_1_complete"],
                "estimated_time": f"{len(phase_2_tasks) * 3} minutes",
                "tasks": phase_2_tasks
            },
            "phase_3_modules": {
                "description": f"模块层文档生成（{len(phase_3_tasks)}个模板）",
                "dependencies": ["phase_2_complete"],
                "estimated_time": f"{len(phase_3_tasks) * 5} minutes",
                "tasks": phase_3_tasks
            },
            "phase_4_architecture": {
                "description": f"架构层文档生成（{len(phase_4_tasks)}个模板）",
                "dependencies": ["phase_3_complete"],
                "estimated_time": f"{len(phase_4_tasks) * 10} minutes",
                "tasks": phase_4_tasks
            },
            "phase_5_project": {
                "description": "项目层文档生成（仅README.md）",
                "dependencies": ["phase_4_complete"],
                "estimated_time": "10 minutes",
                "tasks": phase_5_tasks
            }
        }

    def _generate_phase_1_tasks(self, project_path: str, analysis: Dict[str, Any], scan_task_id: str) -> List[Dict[str, Any]]:
        """生成第一阶段任务（项目扫描）"""

        return [{
            "id": scan_task_id,
            "type": "scan",
            "description": "扫描项目文件结构和基本信息",
            "phase": "phase_1_scan",
            "template": "project_scan_summary",  # 使用模板而不是None
            "output_path": "docs/analysis/project-scan.md",  # 添加输出路径
            "dependencies": [],
            "priority": "high",
            "estimated_time": "5 minutes",
            "status": "pending",
            "metadata": {
                "project_type": analysis.get("project_type", "unknown"),
                "file_count": analysis.get("file_count", 0),
                "complexity": analysis.get("code_complexity", "unknown")
            }
        }]

    def _generate_phase_2_tasks(self, project_path: str, plan: Dict[str, Any], scan_task_id: str,
                                custom_priorities: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """生成第二阶段任务（文件层）"""
        tasks = []
        files_to_process = plan.get("phase_2_files", [])

        for i, file_path in enumerate(files_to_process):
            task_id = f"file_summary_{int(time.time() * 1000)}_{i}"

            # 确定优先级
            priority = self._get_file_priority(file_path, custom_priorities)

            # 生成输出路径
            output_path = f"docs/files/summaries/{file_path}.md"

            task = {
                "id": task_id,
                "type": "file_summary",
                "description": f"生成{file_path}文件摘要",
                "phase": "phase_2_files",
                "target_file": file_path,
                "template": "file_summary",
                "output_path": output_path,
                "dependencies": [scan_task_id],
                "priority": priority,
                "estimated_time": "3 minutes",
                "status": "pending",
                "metadata": {
                    "file_type": Path(file_path).suffix,
                    "file_size_category": "unknown"
                }
            }

            tasks.append(task)

        return tasks

    def _generate_phase_3_tasks(self, project_path: str, analysis: Dict[str, Any],
                                phase_2_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成第三阶段任务（模块层）"""
        tasks = []
        modules = analysis.get("identified_modules", [])

        # 所有文件层任务作为依赖
        file_task_ids = [task["id"] for task in phase_2_tasks]

        # 1. 模块总览任务
        task_id = f"module_analysis_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "module_analysis",
            "description": "生成模块总览和功能分析",
            "phase": "phase_3_modules",
            "template": "module_analysis",
            "output_path": "docs/modules/overview.md",
            "dependencies": file_task_ids,
            "priority": "high",
            "estimated_time": "8 minutes",
            "status": "pending",
            "metadata": {
                "modules_count": len(modules),
                "modules_list": modules
            }
        })

        module_analysis_id = task_id

        # 2. 模块关系任务
        task_id = f"module_relations_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "module_relations",
            "description": "分析模块间关系和依赖",
            "phase": "phase_3_modules",
            "template": "module_relations",
            "output_path": "docs/modules/module-relations.md",
            "dependencies": [module_analysis_id],
            "priority": "high",
            "estimated_time": "6 minutes",
            "status": "pending",
            "metadata": {}
        })

        # 3. 依赖图谱任务
        task_id = f"dependency_graph_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "dependency_graph",
            "description": "生成模块依赖图谱分析",
            "phase": "phase_3_modules",
            "template": "dependency_graph",
            "output_path": "docs/modules/dependency-graph.md",
            "dependencies": [module_analysis_id],
            "priority": "normal",
            "estimated_time": "5 minutes",
            "status": "pending",
            "metadata": {}
        })

        # 4. 为每个重要模块生成详细文档
        important_modules = modules[:3]  # 最多3个重要模块
        for i, module in enumerate(important_modules):
            module_clean = module.lower().replace(" ", "_").replace("-", "_")

            # 模块README
            task_id = f"module_readme_{module_clean}_{int(time.time() * 1000)}"
            tasks.append({
                "id": task_id,
                "type": "module_readme",
                "description": f"生成{module}模块详细文档",
                "phase": "phase_3_modules",
                "target_module": module,
                "template": "module_readme",
                "output_path": f"docs/modules/modules/{module_clean}/README.md",
                "dependencies": [module_analysis_id],
                "priority": "normal",
                "estimated_time": "4 minutes",
                "status": "pending",
                "metadata": {"module_name": module}
            })

            # 模块API
            api_task_id = f"module_api_{module_clean}_{int(time.time() * 1000)}"
            tasks.append({
                "id": api_task_id,
                "type": "module_api",
                "description": f"生成{module}模块API文档",
                "phase": "phase_3_modules",
                "target_module": module,
                "template": "module_api",
                "output_path": f"docs/modules/modules/{module_clean}/api.md",
                "dependencies": [task_id],
                "priority": "normal",
                "estimated_time": "3 minutes",
                "status": "pending",
                "metadata": {"module_name": module}
            })

            # 模块流程
            flow_task_id = f"module_flow_{module_clean}_{int(time.time() * 1000)}"
            tasks.append({
                "id": flow_task_id,
                "type": "module_flow",
                "description": f"生成{module}模块业务流程",
                "phase": "phase_3_modules",
                "target_module": module,
                "template": "module_flow",
                "output_path": f"docs/modules/modules/{module_clean}/flow.md",
                "dependencies": [task_id],
                "priority": "low",
                "estimated_time": "3 minutes",
                "status": "pending",
                "metadata": {"module_name": module}
            })

        return tasks

    def _generate_phase_4_tasks(self, project_path: str, analysis: Dict[str, Any],
                                phase_3_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成第四阶段任务（架构层）"""
        tasks = []

        # 所有模块层任务作为依赖
        module_task_ids = [task["id"] for task in phase_3_tasks]

        # 1. 架构概述
        task_id = f"architecture_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "architecture",
            "description": "生成系统架构概述",
            "phase": "phase_4_architecture",
            "template": "architecture",
            "output_path": "docs/architecture/overview.md",
            "dependencies": module_task_ids,
            "priority": "high",
            "estimated_time": "12 minutes",
            "status": "pending",
            "metadata": {
                "project_type": analysis.get("project_type", "unknown"),
                "complexity": analysis.get("code_complexity", "unknown")
            }
        })

        architecture_id = task_id

        # 2. 技术栈分析
        task_id = f"tech_stack_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "tech_stack",
            "description": "分析技术栈和架构原则",
            "phase": "phase_4_architecture",
            "template": "tech_stack",
            "output_path": "docs/architecture/tech-stack.md",
            "dependencies": [architecture_id],
            "priority": "high",
            "estimated_time": "10 minutes",
            "status": "pending",
            "metadata": {}
        })

        # 3. 数据流设计
        task_id = f"data_flow_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "data_flow",
            "description": "设计系统数据流",
            "phase": "phase_4_architecture",
            "template": "data_flow",
            "output_path": "docs/architecture/data-flow.md",
            "dependencies": [architecture_id],
            "priority": "normal",
            "estimated_time": "8 minutes",
            "status": "pending",
            "metadata": {}
        })

        # 4. 系统架构图
        task_id = f"system_architecture_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "system_architecture",
            "description": "绘制系统架构图",
            "phase": "phase_4_architecture",
            "template": "system_architecture",
            "output_path": "docs/architecture/diagrams/system-architecture.md",
            "dependencies": [architecture_id],
            "priority": "normal",
            "estimated_time": "6 minutes",
            "status": "pending",
            "metadata": {}
        })

        # 5. 组件关系图
        task_id = f"component_diagram_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "component_diagram",
            "description": "绘制组件关系图",
            "phase": "phase_4_architecture",
            "template": "component_diagram",
            "output_path": "docs/architecture/diagrams/component-diagram.md",
            "dependencies": [architecture_id],
            "priority": "normal",
            "estimated_time": "6 minutes",
            "status": "pending",
            "metadata": {}
        })

        # 6. 部署架构图
        task_id = f"deployment_diagram_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "deployment_diagram",
            "description": "设计部署架构",
            "phase": "phase_4_architecture",
            "template": "deployment_diagram",
            "output_path": "docs/architecture/diagrams/deployment-diagram.md",
            "dependencies": [architecture_id],
            "priority": "low",
            "estimated_time": "5 minutes",
            "status": "pending",
            "metadata": {}
        })

        return tasks

    def _generate_phase_5_tasks(self, project_path: str, analysis: Dict[str, Any],
                                phase_4_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成第五阶段任务（项目层）"""
        tasks = []

        # 所有架构层任务作为依赖
        arch_task_ids = [task["id"] for task in phase_4_tasks]

        # 只生成README.md
        task_id = f"project_readme_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "project_readme",
            "description": "生成项目README文档",
            "phase": "phase_5_project",
            "template": "project_readme",
            "output_path": "docs/project/README.md",
            "dependencies": arch_task_ids,
            "priority": "high",
            "estimated_time": "10 minutes",
            "status": "pending",
            "metadata": {
                "project_type": analysis.get("project_type", "unknown"),
                "framework": analysis.get("main_framework", "custom"),
                "complexity": analysis.get("code_complexity", "unknown")
            }
        })

        return tasks

    def _get_file_priority(self, file_path: str, custom_priorities: Dict[str, Any] = None) -> str:
        """确定文件优先级"""
        if custom_priorities and file_path in custom_priorities:
            return custom_priorities[file_path]

        file_lower = file_path.lower()

        # 检查高优先级模式
        for pattern in self.priority_mapping["high"]:
            if pattern in file_lower:
                return "high"

        # 检查普通优先级模式
        for pattern in self.priority_mapping["normal"]:
            if pattern in file_lower:
                return "normal"

        # 检查低优先级模式
        for pattern in self.priority_mapping["low"]:
            if pattern in file_lower:
                return "low"

        return "normal"

    def _build_dependency_graph(self, all_tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """构建依赖关系图"""
        graph = {}

        for task in all_tasks:
            task_id = task["id"]
            dependencies = task.get("dependencies", [])
            graph[task_id] = dependencies

        return graph

    def create_tasks_in_manager(self, task_manager: TaskManager, task_plan: Dict[str, Any]) -> int:
        """在任务管理器中创建所有任务"""
        created_count = 0
        skipped_count = 0
        error_count = 0

        # 按阶段顺序创建任务
        phases = ["phase_1_scan", "phase_2_files", "phase_3_modules", "phase_4_architecture", "phase_5_project"]

        for phase in phases:
            if phase in task_plan:
                phase_data = task_plan[phase]
                tasks = phase_data.get("tasks", [])
                print(f"处理阶段 {phase}: {len(tasks)} 个任务")

                for task_data in tasks:
                    # 转换任务类型
                    task_type_str = task_data["type"]
                    try:
                        task_type = TaskType(task_type_str)
                    except ValueError as e:
                        # 如果无法转换，跳过此任务
                        print(f"跳过无效任务类型: {task_type_str} - {e}")
                        skipped_count += 1
                        continue

                    try:
                        # 🔧 根本修复: 传入预定义task_id确保依赖关系一致性
                        task_id = task_manager.create_task(
                            task_type=task_type,
                            description=task_data["description"],
                            phase=task_data["phase"],
                            target_file=task_data.get("target_file"),
                            target_module=task_data.get("target_module"),
                            template_name=task_data.get("template"),
                            output_path=task_data.get("output_path"),
                            dependencies=task_data.get("dependencies", []),
                            priority=task_data.get("priority", "normal"),
                            estimated_time=task_data.get("estimated_time"),
                            metadata=task_data.get("metadata", {}),
                            task_id=task_data["id"]  # 使用预定义的task_id
                        )

                        created_count += 1
                        
                    except Exception as e:
                        print(f"创建任务失败: {task_data.get('description', 'Unknown')} - {e}")
                        error_count += 1
                        continue

        print(f"任务创建完成 - 成功: {created_count}, 跳过: {skipped_count}, 错误: {error_count}")
        return created_count


class TaskInitTool:
    """MCP task_init 工具类"""

    def __init__(self):
        self.tool_name = "task_init"
        self.description = "基于项目分析结果，生成完整的阶段性任务列表"
        self.generator = TaskPlanGenerator()
        self.logger = logging.getLogger('task_init')

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
                    "analysis_result": {
                        "type": "object",
                        "description": "doc_guide的分析结果",
                        "required": True
                    },
                    "task_granularity": {
                        "type": "string",
                        "enum": ["file", "batch", "module"],
                        "default": "file",
                        "description": "任务粒度"
                    },
                    "parallel_tasks": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否支持并行任务"
                    },
                    "custom_priorities": {
                        "type": "object",
                        "description": "自定义优先级设置",
                        "additionalProperties": {"type": "string"}
                    },
                    "create_in_manager": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否在任务管理器中创建任务"
                    }
                },
                "required": ["project_path", "analysis_result"]
            }
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行task_init工具"""
        try:
            # 参数验证
            project_path = arguments.get("project_path")
            analysis_result = arguments.get("analysis_result")

            if not project_path or not os.path.exists(project_path):
                return self._error_response("Invalid project path")

            if not analysis_result:
                return self._error_response("Analysis result is required")

            # 获取参数
            task_granularity = arguments.get("task_granularity", "file")
            parallel_tasks = arguments.get("parallel_tasks", False)
            custom_priorities = arguments.get("custom_priorities", {})
            create_in_manager = arguments.get("create_in_manager", False)

            self.logger.info(f"开始生成任务计划: {project_path}, 粒度: {task_granularity}")

            # 生成任务计划
            task_plan = self.generator.generate_tasks(
                project_path=project_path,
                analysis_result=analysis_result,
                task_granularity=task_granularity,
                parallel_tasks=parallel_tasks,
                custom_priorities=custom_priorities
            )

            # 如果需要，在任务管理器中创建任务
            created_count = 0
            if create_in_manager:
                task_manager = TaskManager(project_path)
                created_count = self.generator.create_tasks_in_manager(task_manager, task_plan)
                self.logger.info(f"任务已创建在管理器中: {created_count} 个")

            self.logger.info(f"任务计划生成完成 - 总任务: {task_plan['task_plan']['total_tasks']}, "
                             f"阶段: {task_plan['task_plan']['total_phases']}")

            response_data = task_plan.copy()
            if create_in_manager:
                response_data["manager_info"] = {
                    "tasks_created": created_count,
                    "creation_successful": True
                }

            return self._success_response(response_data)

        except Exception as e:
            self.logger.error(f"任务计划生成失败: {str(e)}", exc_info=e)
            return self._error_response(f"Task initialization failed: {str(e)}")

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


def create_mcp_tool() -> TaskInitTool:
    """创建MCP工具实例"""
    return TaskInitTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP task_init tool")
    parser.add_argument("project_path", help="Project path")
    parser.add_argument("--analysis-file", required=True,
                        help="JSON file with analysis result from doc_guide")
    parser.add_argument("--granularity", choices=["file", "batch", "module"],
                        default="file", help="Task granularity")
    parser.add_argument("--create-tasks", action="store_true",
                        help="Create tasks in task manager")

    args = parser.parse_args()

    # 读取分析结果
    try:
        with open(args.analysis_file, 'r', encoding='utf-8') as f:
            analysis_result = json.load(f)
    except Exception as e:
        print(f"Error reading analysis file: {e}")
        return

    # 构建参数
    arguments = {
        "project_path": args.project_path,
        "analysis_result": analysis_result,
        "task_granularity": args.granularity,
        "create_in_manager": args.create_tasks
    }

    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
