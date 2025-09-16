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
from src.logging import get_logger

# 导入配置管理器
try:
    from src.config import get_file_filtering_config, get_file_size_limits_config, get_tool_config

    HAS_CONFIG_MANAGER = True
except ImportError:
    HAS_CONFIG_MANAGER = False
    get_file_filtering_config = lambda: None
    get_file_size_limits_config = lambda: None
    get_tool_config = lambda x: {}


class TaskPlanGenerator:
    """任务计划生成器"""

    def __init__(self):
        self.logger = get_logger(component="TaskPlanGenerator", operation="init")
        self.logger.info("TaskPlanGenerator 初始化开始")

        # 模板映射关系
        self.template_mapping = {
            TaskType.SCAN: "project_scan_summary",  # 添加scan任务模板映射
            TaskType.FILE_SUMMARY: "file_summary",
            TaskType.ARCHITECTURE: "architecture",
            TaskType.TECH_STACK: "tech_stack",
            TaskType.DATA_FLOW: "data_flow",
            TaskType.SYSTEM_ARCHITECTURE: "system_architecture",
            TaskType.COMPONENT_DIAGRAM: "component_diagram",
            TaskType.DEPLOYMENT_DIAGRAM: "deployment_diagram",
            TaskType.PROJECT_README: "project_readme"
        }

        # 加载配置
        self._load_config()

        self.logger.info("TaskPlanGenerator 初始化完成", {
            "template_mapping_count": len(self.template_mapping),
            "priority_levels": len(self.priority_mapping),
            "filter_rules": len(self.file_filters["exclude_patterns"]),
            "config_manager_available": HAS_CONFIG_MANAGER
        })

    def _load_config(self):
        """加载配置"""
        if HAS_CONFIG_MANAGER:
            try:
                # 从配置管理器获取配置
                filtering_config = get_file_filtering_config()
                file_size_config = get_file_size_limits_config()
                tool_config = get_tool_config("task_init")

                # 优先级映射（使用配置中的smart_filtering.priority_patterns或默认值）
                if filtering_config and hasattr(filtering_config, 'smart_filtering'):
                    priority_patterns = filtering_config.smart_filtering.get('priority_patterns', {})
                    self.priority_mapping = {
                        "high": priority_patterns.get("high", ["main.py", "app.py", "index.js", "server.js", "main.go",
                                                               "main.rs"]),
                        "normal": priority_patterns.get("normal",
                                                        ["config", "model", "service", "controller", "handler"]),
                        "low": priority_patterns.get("low", ["util", "helper", "test", "spec"])
                    }
                else:
                    self._use_default_priority_mapping()

                # 文件过滤规则（从配置获取）
                if filtering_config:
                    self.file_filters = {
                        "exclude_patterns": filtering_config.exclude_patterns,
                        "exclude_directories": filtering_config.exclude_directories,
                        "min_file_size": file_size_config.min_file_size if file_size_config else 50,
                        "max_files_per_project": filtering_config.smart_filtering.get('max_files_per_project',
                                                                                      25) if hasattr(filtering_config,
                                                                                                     'smart_filtering') else 25
                    }
                else:
                    self._use_default_file_filters()

                self.logger.info("配置加载成功", {
                    "exclude_patterns_count": len(self.file_filters["exclude_patterns"]),
                    "exclude_directories_count": len(self.file_filters["exclude_directories"]),
                    "min_file_size": self.file_filters["min_file_size"],
                    "max_files_per_project": self.file_filters["max_files_per_project"]
                })

            except Exception as e:
                self.logger.warning(f"配置加载失败，使用默认值: {e}")
                self._use_default_config()
        else:
            self.logger.warning("配置管理器不可用，使用默认值")
            self._use_default_config()

    def _use_default_config(self):
        """使用默认配置（向后兼容）"""
        self._use_default_priority_mapping()
        self._use_default_file_filters()

    def _use_default_priority_mapping(self):
        """使用默认优先级映射"""
        self.priority_mapping = {
            "high": ["main.py", "app.py", "index.js", "server.js", "main.go", "main.rs"],
            "normal": ["config", "model", "service", "controller", "handler"],
            "low": ["util", "helper", "test", "spec"]
        }

    def _use_default_file_filters(self):
        """使用默认文件过滤规则"""
        self.file_filters = {
            "exclude_patterns": [
                "__init__.py",  # 空的初始化文件
                "__pycache__",
                ".pyc",
                ".git",
                "node_modules",
                ".venv",
                "venv",
                "test_",
                "_test.py",
                "conftest.py",
                ".env",
                ".example",
                "requirements.txt",
                "package.json",
                "Dockerfile",
                ".yml",
                ".yaml",
                ".json",
                ".md",
                ".txt",
                ".log"
            ],
            "exclude_directories": [
                "tests",
                "test",
                "__pycache__",
                ".git",
                "node_modules",
                ".venv",
                "venv",
                "build",
                "dist",
                "logs",
                "temp",
                "tmp"
            ],
            "min_file_size": 50,  # 最小文件大小（字节）
            "max_files_per_project": 25  # 每个项目最大文件数
        }

    def _get_include_extensions(self) -> List[str]:
        """获取要包含的文件扩展名"""
        if HAS_CONFIG_MANAGER:
            try:
                filtering_config = get_file_filtering_config()
                if filtering_config and hasattr(filtering_config, 'include_extensions'):
                    return filtering_config.include_extensions
            except Exception as e:
                self.logger.warning(f"获取配置扩展名失败，使用默认值: {e}")

        # 默认扩展名列表（与配置文件保持一致）
        return [
            ".py", ".pyw", ".pyi",
            ".js", ".mjs", ".cjs", ".jsx",
            ".ts", ".tsx",
            ".html", ".htm", ".xhtml",
            ".css", ".scss", ".sass", ".less", ".styl",
            ".sh", ".bash", ".zsh", ".fish",
            ".ps1", ".psm1",
            ".bat", ".cmd",
            ".json", ".yml", ".yaml",
            ".md", ".txt"
        ]

    def generate_tasks_auto(self, project_path: str,
                            task_granularity: str = "file",
                            max_files: int = None) -> Dict[str, Any]:
        """智能生成任务计划 - 简化版API"""
        operation_id = self.logger.log_operation_start("generate_tasks_auto",
                                                       project_path=project_path,
                                                       task_granularity=task_granularity,
                                                       max_files=max_files)

        try:
            # 1. 自动加载分析数据
            self.logger.info("自动加载项目分析数据")
            analysis_result = self._auto_load_analysis_data(project_path)
            if not analysis_result:
                raise ValueError("无法加载项目分析数据，请先运行 doc_guide")

            # 2. 智能过滤文件
            self.logger.info("开始智能文件过滤")
            filtered_files = self._smart_filter_files(project_path, analysis_result, max_files or 999999)
            self.logger.info(f"文件过滤完成，从原始文件中筛选出 {len(filtered_files)} 个重要文件")

            # 3. 更新分析结果中的文件列表
            if "generation_plan" not in analysis_result:
                analysis_result["generation_plan"] = {}
            analysis_result["generation_plan"]["phase_2_files"] = filtered_files

            # 4. 调用原始的generate_tasks方法
            return self.generate_tasks(project_path, analysis_result, task_granularity, False, None)

        except Exception as e:
            self.logger.log_operation_end("generate_tasks_auto", operation_id, success=False, error=str(e))
            raise e
        finally:
            self.logger.log_operation_end("generate_tasks_auto", operation_id, success=True)

    def _auto_load_analysis_data(self, project_path: str) -> Dict[str, Any]:
        """自动加载项目分析数据"""
        analysis_file = Path(project_path) / ".codelens" / "analysis.json"

        if not analysis_file.exists():
            self.logger.warning("分析文件不存在", {"analysis_file": str(analysis_file)})
            return None

        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.logger.info("成功加载分析数据", {"file_path": str(analysis_file)})
                return data
        except Exception as e:
            self.logger.error("加载分析数据失败", {"error": str(e), "file_path": str(analysis_file)})
            return None

    def _smart_filter_files(self, project_path: str, analysis_result: Dict[str, Any], max_files: int = 20) -> List[str]:
        """智能过滤文件"""
        # 获取配置中的包含文件扩展名
        all_files = []
        project_root = Path(project_path)

        # 从配置获取要包含的文件扩展名
        include_extensions = self._get_include_extensions()

        # 按扩展名扫描所有目标文件
        for extension in include_extensions:
            # 移除扩展名前的点号，用于glob模式
            glob_pattern = f"*{extension}"
            for file_path in project_root.rglob(glob_pattern):
                try:
                    rel_path = file_path.relative_to(project_root)
                    all_files.append(str(rel_path))
                except ValueError:
                    # 跳过无法计算相对路径的文件
                    continue

        self.logger.info(f"扫描到 {len(all_files)} 个文件（包含所有配置的扩展名）")

        # 应用过滤规则
        filtered_files = []
        for file_path in all_files:
            if self._should_include_file(file_path, project_root):
                filtered_files.append(file_path)

        self.logger.info(f"过滤后剩余 {len(filtered_files)} 个文件")

        # 按重要性排序
        prioritized_files = self._prioritize_files(filtered_files, project_root)

        # 不再限制文件数量，处理所有扫描到的文件
        self.logger.info(f"将处理所有 {len(prioritized_files)} 个文件，不再限制数量")

        return prioritized_files

    def _should_include_file(self, file_path: str, project_root: Path) -> bool:
        """判断是否应该包含某个文件"""
        file_path_lower = file_path.lower()

        # 检查排除模式
        for pattern in self.file_filters["exclude_patterns"]:
            if pattern in file_path_lower:
                return False

        # 检查排除目录
        for exclude_dir in self.file_filters["exclude_directories"]:
            if exclude_dir in file_path_lower:
                return False

        # 检查文件大小
        full_path = project_root / file_path
        try:
            if full_path.stat().st_size < self.file_filters["min_file_size"]:
                return False
        except:
            return False

        # 特殊处理：排除空的__init__.py文件
        if file_path.endswith("__init__.py"):
            try:
                if full_path.stat().st_size < 100:  # 小于100字节认为是空文件
                    return False
            except:
                return False

        return True

    def _prioritize_files(self, files: List[str], project_root: Path) -> List[str]:
        """按重要性对文件进行排序"""
        file_scores = []

        for file_path in files:
            score = self._calculate_file_importance(file_path, project_root)
            file_scores.append((file_path, score))

        # 按分数降序排序
        file_scores.sort(key=lambda x: x[1], reverse=True)

        return [file_path for file_path, score in file_scores]

    def _calculate_file_importance(self, file_path: str, project_root: Path) -> int:
        """计算文件重要性分数"""
        score = 0
        file_path_lower = file_path.lower()
        file_name = Path(file_path).name.lower()

        # 主要入口文件 (+100)
        if file_name in ["main.py", "app.py", "server.py", "index.py"]:
            score += 100

        # 模型和核心业务文件 (+50)
        if "model" in file_path_lower or "service" in file_path_lower:
            score += 50

        # 路由和控制器 (+30)
        if "route" in file_path_lower or "controller" in file_path_lower or "handler" in file_path_lower:
            score += 30

        # 配置文件 (+20)
        if "config" in file_path_lower or "setting" in file_path_lower:
            score += 20

        # 数据库相关 (+25)
        if "db.py" in file_path_lower or "database" in file_path_lower:
            score += 25

        # 文件大小加分
        try:
            full_path = project_root / file_path
            file_size = full_path.stat().st_size
            if file_size > 5000:  # 大于5KB
                score += 10
            if file_size > 15000:  # 大于15KB  
                score += 10
        except:
            pass

        # 目录深度减分（越深越不重要）
        depth = len(Path(file_path).parts) - 1
        score -= depth * 5

        return score

    def generate_tasks(self, project_path: str, analysis_result: Dict[str, Any],
                       task_granularity: str = "file", parallel_tasks: bool = False,
                       custom_priorities: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成完整的任务计划"""
        operation_id = self.logger.log_operation_start("generate_tasks",
                                                       project_path=project_path,
                                                       task_granularity=task_granularity,
                                                       parallel_tasks=parallel_tasks)

        self.logger.info("开始生成任务计划", {
            "project_path": project_path,
            "task_granularity": task_granularity,
            "parallel_tasks": parallel_tasks,
            "has_custom_priorities": custom_priorities is not None,
            "operation_id": operation_id
        })

        # 提取分析结果 - 修复嵌套JSON结构解析
        self.logger.debug("解析分析结果结构")
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
        self.logger.debug("生成scan任务ID", {"scan_task_id": scan_task_id})

        # 生成各阶段任务 (4阶段架构)
        self.logger.info("开始生成各阶段任务")

        self.logger.debug("生成Phase 1任务（扫描阶段）")
        phase_1_tasks = self._generate_phase_1_tasks(project_path, project_analysis, scan_task_id)
        self.logger.info("Phase 1任务生成完成", {"task_count": len(phase_1_tasks)})

        self.logger.debug("生成Phase 2任务（文件层）")
        phase_2_tasks = self._generate_phase_2_tasks(project_path, plan, scan_task_id, custom_priorities)
        self.logger.info("Phase 2任务生成完成", {"task_count": len(phase_2_tasks)})

        self.logger.debug("生成Phase 3任务（架构层）")
        phase_3_tasks = self._generate_phase_3_tasks(project_path, project_analysis, phase_2_tasks)  # 架构层
        self.logger.info("Phase 3任务生成完成", {"task_count": len(phase_3_tasks)})

        self.logger.debug("生成Phase 4任务（项目层）")
        phase_4_tasks = self._generate_phase_4_tasks(project_path, project_analysis, phase_3_tasks)  # 项目层
        self.logger.info("Phase 4任务生成完成", {"task_count": len(phase_4_tasks)})

        # 计算总体统计
        all_tasks = phase_1_tasks + phase_2_tasks + phase_3_tasks + phase_4_tasks
        self.logger.info("任务计划生成完成", {
            "total_tasks": len(all_tasks),
            "phase_breakdown": {
                "phase_1": len(phase_1_tasks),
                "phase_2": len(phase_2_tasks),
                "phase_3": len(phase_3_tasks),
                "phase_4": len(phase_4_tasks)
            }
        })

        task_plan = {
            "total_phases": 4,
            "total_tasks": len(all_tasks),
            "estimated_duration": plan.get("estimated_duration", "Unknown"),
            "dependencies_graph": self._build_dependency_graph(all_tasks),
            "task_distribution": {
                "phase_1_scan": len(phase_1_tasks),
                "phase_2_files": len(phase_2_tasks),
                "phase_3_architecture": len(phase_3_tasks),
                "phase_4_project": len(phase_4_tasks)
            }
        }

        # 构建完整响应
        result = {
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
            "phase_3_architecture": {
                "description": f"架构层文档生成（{len(phase_3_tasks)}个模板）",
                "dependencies": ["phase_2_complete"],
                "estimated_time": f"{len(phase_3_tasks) * 10} minutes",
                "tasks": phase_3_tasks
            },
            "phase_4_project": {
                "description": "项目层文档生成（仅README.md）",
                "dependencies": ["phase_3_complete"],
                "estimated_time": "10 minutes",
                "tasks": phase_4_tasks
            }
        }

        self.logger.log_operation_end("generate_tasks", operation_id, success=True)
        return result

    def _generate_phase_1_tasks(self, project_path: str, analysis: Dict[str, Any], scan_task_id: str) -> List[
        Dict[str, Any]]:
        """生成第一阶段任务（项目扫描）"""

        return [{
            "id": scan_task_id,
            "type": "scan",
            "description": "扫描项目文件结构和基本信息",
            "phase": "phase_1_scan",
            "template": "project_readme",  # 使用project_readme模板
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
        """生成第三阶段任务（架构层）"""
        tasks = []

        # 所有文件层任务作为依赖
        file_task_ids = [task["id"] for task in phase_2_tasks]

        # 1. 架构概述
        task_id = f"architecture_{int(time.time() * 1000)}"
        tasks.append({
            "id": task_id,
            "type": "architecture",
            "description": "生成系统架构概述",
            "phase": "phase_3_architecture",
            "template": "architecture",
            "output_path": "docs/architecture/overview.md",
            "dependencies": file_task_ids,
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
            "phase": "phase_3_architecture",
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
            "phase": "phase_3_architecture",
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
            "phase": "phase_3_architecture",
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
            "phase": "phase_3_architecture",
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
            "phase": "phase_3_architecture",
            "template": "deployment_diagram",
            "output_path": "docs/architecture/diagrams/deployment-diagram.md",
            "dependencies": [architecture_id],
            "priority": "low",
            "estimated_time": "5 minutes",
            "status": "pending",
            "metadata": {}
        })

        return tasks

    def _generate_phase_4_tasks(self, project_path: str, analysis: Dict[str, Any],
                                phase_3_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成第四阶段任务（项目层）"""
        tasks = []

        # 所有架构层任务作为依赖
        arch_task_ids = [task["id"] for task in phase_3_tasks]

        # 1. 生成README.md
        readme_task_id = f"project_readme_{int(time.time() * 1000)}"
        tasks.append({
            "id": readme_task_id,
            "type": "project_readme",
            "description": "生成项目README文档",
            "phase": "phase_4_project",
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

        # 2. 生成CHANGELOG.md
        changelog_task_id = f"changelog_{int(time.time() * 1000)}"
        tasks.append({
            "id": changelog_task_id,
            "type": "changelog",
            "description": "生成项目变更日志文档",
            "phase": "phase_4_project",
            "template": "changelog",
            "output_path": "docs/project/CHANGELOG.md",
            "dependencies": arch_task_ids,
            "priority": "normal",
            "estimated_time": "5 minutes",
            "status": "pending",
            "metadata": {
                "project_type": analysis.get("project_type", "unknown"),
                "framework": analysis.get("main_framework", "custom")
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
        operation_id = self.logger.log_operation_start("create_tasks_in_manager")

        # 检查task_plan是否有效
        if task_plan is None:
            self.logger.error("task_plan为None，无法创建任务")
            self.logger.log_operation_end("create_tasks_in_manager", operation_id, success=False,
                                          error="task_plan is None")
            return 0

        self.logger.info("开始在任务管理器中创建任务", {
            "operation_id": operation_id,
            "total_phases": len([p for p in task_plan.keys() if p.startswith("phase_")])
        })

        created_count = 0
        skipped_count = 0
        error_count = 0

        # 按阶段顺序创建任务
        phases = ["phase_1_scan", "phase_2_files", "phase_3_architecture", "phase_4_project"]

        for phase in phases:
            if phase in task_plan:
                phase_data = task_plan[phase]
                tasks = phase_data.get("tasks", [])
                self.logger.info(f"处理阶段 {phase}", {"task_count": len(tasks)})

                for task_data in tasks:
                    # 转换任务类型
                    task_type_str = task_data["type"]
                    self.logger.debug("处理任务", {"task_type": task_type_str, "task_id": task_data.get("id")})

                    try:
                        task_type = TaskType(task_type_str)
                    except ValueError as e:
                        # 如果无法转换，跳过此任务
                        self.logger.warning(f"跳过无效任务类型: {task_type_str}", {"error": str(e)})
                        skipped_count += 1
                        continue

                    try:
                        # 传入预定义task_id确保依赖关系一致性
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
                        self.logger.debug("任务创建成功", {"task_id": task_id, "type": task_type_str})

                    except Exception as e:
                        self.logger.error("创建任务失败", {
                            "task_description": task_data.get('description', 'Unknown'),
                            "error": str(e)
                        })
                        error_count += 1
                        continue

        self.logger.log_operation_end("create_tasks_in_manager", operation_id, success=True,
                                      created_count=created_count,
                                      skipped_count=skipped_count,
                                      error_count=error_count)

        self.logger.info("任务创建完成", {
            "created": created_count,
            "skipped": skipped_count,
            "errors": error_count,
            "total_processed": created_count + skipped_count + error_count
        })

        return created_count


class TaskInitTool:
    """MCP task_init 工具类"""

    def __init__(self):
        self.tool_name = "task_init"
        self.description = "基于项目分析结果，生成完整的阶段性任务列表"
        self.generator = TaskPlanGenerator()
        self.logger = get_logger(component="TaskInitTool", operation="init")
        self.logger.info("TaskInitTool 初始化完成")

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
                        "description": "项目路径（可选，默认使用当前工作目录）"
                    },
                    "analysis_result": {
                        "type": "object",
                        "description": "doc_guide的分析结果（可选，如果不提供则自动加载）"
                    },
                    "task_granularity": {
                        "type": "string",
                        "enum": ["file", "batch", "module"],
                        "description": "任务粒度"
                    },
                    "max_files": {
                        "type": "number",
                        "description": "最大文件数量（可选，默认20个）"
                    },
                    "create_in_manager": {
                        "type": "boolean",
                        "description": "是否在任务管理器中创建任务"
                    },
                    "auto_mode": {
                        "type": "boolean",
                        "description": "是否使用智能模式（自动过滤文件，简化参数）"
                    }
                },
                "required": ["project_path"]
            }
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行task_init工具"""
        operation_id = self.logger.log_operation_start("execute_task_init",
                                                       project_path=arguments.get("project_path"),
                                                       auto_mode=arguments.get("auto_mode", True))

        try:
            self.logger.info("开始执行task_init工具", {"arguments": arguments, "operation_id": operation_id})

            # 参数验证
            project_path = arguments.get("project_path")
            if not project_path:
                project_path = os.getcwd()  # 默认使用当前目录

            if not os.path.exists(project_path):
                error_msg = "Invalid project path"
                self.logger.error(error_msg, {"project_path": project_path})
                return self._error_response(error_msg)

            # 检查是否使用智能模式 (默认启用)
            auto_mode = arguments.get("auto_mode", True)
            analysis_result = arguments.get("analysis_result")

            self.logger.info("模式检查", {
                "auto_mode": auto_mode,
                "has_analysis_result": analysis_result is not None
            })

            # 获取参数
            task_granularity = arguments.get("task_granularity", "file")
            max_files = arguments.get("max_files", 20)
            create_in_manager = arguments.get("create_in_manager", False)

            # 智能模式：自动加载数据并过滤文件
            if auto_mode:
                self.logger.info("使用智能模式生成任务计划", {
                    "project_path": project_path,
                    "task_granularity": task_granularity,
                    "max_files": max_files,
                    "create_in_manager": create_in_manager
                })

                # 生成任务计划 - 使用智能API
                self.logger.debug("调用TaskPlanGenerator智能模式")
                task_plan = self.generator.generate_tasks_auto(
                    project_path=project_path,
                    task_granularity=task_granularity,
                    max_files=max_files
                )
                self.logger.debug("智能任务计划生成完成")

            else:
                # 传统模式：需要手动提供analysis_result
                if not analysis_result:
                    error_msg = "Analysis result is required when auto_mode is disabled"
                    self.logger.error(error_msg)
                    return self._error_response(error_msg)

                parallel_tasks = arguments.get("parallel_tasks", False)
                custom_priorities = arguments.get("custom_priorities", {})

                self.logger.info("使用传统模式生成任务计划", {
                    "project_path": project_path,
                    "task_granularity": task_granularity,
                    "parallel_tasks": parallel_tasks,
                    "has_custom_priorities": bool(custom_priorities),
                    "create_in_manager": create_in_manager
                })

                # 生成任务计划 - 使用传统API
                self.logger.debug("调用TaskPlanGenerator传统模式")
                task_plan = self.generator.generate_tasks(
                    project_path=project_path,
                    analysis_result=analysis_result,
                    task_granularity=task_granularity,
                    parallel_tasks=parallel_tasks,
                    custom_priorities=custom_priorities
                )
                self.logger.debug("传统任务计划生成完成")

            # 检查任务计划是否生成成功
            if task_plan is None:
                self.logger.error("任务计划生成失败，返回None")
                self.logger.log_operation_end("execute_task_init", operation_id, success=False,
                                              error="Task plan generation failed")
                return self._error_response("Task plan generation failed: generate_tasks returned None")

            # 如果需要，在任务管理器中创建任务
            created_count = 0
            if create_in_manager:
                self.logger.info("开始在任务管理器中创建任务")
                task_manager = TaskManager(project_path)
                created_count = self.generator.create_tasks_in_manager(task_manager, task_plan)
                self.logger.info("任务已创建在管理器中", {"created_count": created_count})

            # 安全地访问task_plan数据
            total_tasks = task_plan.get('task_plan', {}).get('total_tasks', 0) if task_plan else 0
            total_phases = task_plan.get('task_plan', {}).get('total_phases', 0) if task_plan else 0

            self.logger.log_operation_end("execute_task_init", operation_id, success=True,
                                          total_tasks=total_tasks,
                                          total_phases=total_phases,
                                          created_in_manager=create_in_manager,
                                          created_count=created_count)

            # 优化响应：只返回前10个任务详情，防止token过大
            response_data = self._optimize_response_for_display(task_plan)
            if create_in_manager:
                response_data["manager_info"] = {
                    "tasks_created": created_count,
                    "creation_successful": True
                }

            return self._success_response(response_data)

        except Exception as e:
            self.logger.log_operation_end("execute_task_init", operation_id, success=False, error=str(e))
            self.logger.error(f"任务计划生成失败: {str(e)}", exc_info=e)
            return self._error_response(f"Task initialization failed: {str(e)}")

    def _optimize_response_for_display(self, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """优化响应显示，只返回前10个任务详情，防止token过大"""
        optimized = task_plan.copy()
        
        # 保留完整的摘要信息
        task_plan_summary = optimized.get("task_plan", {})
        
        # 对每个阶段只显示前10个任务
        for phase_key in ["phase_1_scan", "phase_2_files", "phase_3_architecture", "phase_4_project"]:
            if phase_key in optimized:
                phase_data = optimized[phase_key]
                tasks = phase_data.get("tasks", [])
                
                if len(tasks) > 10:
                    # 只保留前10个任务详情
                    limited_tasks = tasks[:10]
                    phase_data["tasks"] = limited_tasks
                    
                    # 添加说明信息
                    if "description" in phase_data:
                        total_count = len(tasks)
                        phase_data["description"] = f"{phase_data['description']} [显示前10个，共{total_count}个任务]"
        
        # 添加完整任务保存提示
        optimized["display_notice"] = {
            "message": "为防止响应过大，此处只显示前10个任务详情",
            "full_tasks_location": "完整任务列表已保存到 .codelens/tasks.json",
            "total_tasks": task_plan_summary.get("total_tasks", 0)
        }
        
        return optimized

    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """成功响应"""
        self.logger.debug("生成成功响应", {"data_keys": list(data.keys()) if data else []})
        return {
            "success": True,
            "tool": self.tool_name,
            "data": data
        }

    def _error_response(self, message: str) -> Dict[str, Any]:
        """错误响应"""
        self.logger.error("生成错误响应", {"error_message": message})
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
