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
from src.logging import get_logger

# 导入大文件处理相关类
try:
    from src.services.large_file_handler import ChunkingResult, CodeChunk
    HAS_LARGE_FILE_HANDLER = True
except ImportError:
    HAS_LARGE_FILE_HANDLER = False


class TaskExecutor:
    """任务执行器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.logger = get_logger(component="TaskExecutor", operation="init")
        
        self.logger.info("初始化TaskExecutor", {"project_path": str(project_path)})
        
        self.task_manager = TaskManager(str(project_path))
        self.phase_controller = PhaseController(self.task_manager)
        self.state_tracker = StateTracker(str(project_path), self.task_manager, self.phase_controller)
        self.file_service = FileService(enable_large_file_chunking=True)
        self.template_service = TemplateService()
        
        # 大文件处理配置
        self.large_file_threshold = 50000  # 50KB - 分片阈值
        self.max_file_size = 122880  # 120KB - 文件处理上限
        self.enable_chunking = HAS_LARGE_FILE_HANDLER
        
        self.logger.info("TaskExecutor初始化完成")

    def prepare_task_execution(self, task_id: str, context_enhancement: bool = True) -> Dict[str, Any]:
        """准备任务执行上下文"""
        operation_id = self.logger.log_operation_start("prepare_task_execution", task_id=task_id, context_enhancement=context_enhancement)
        
        self.logger.info("开始准备任务执行上下文", {
            "task_id": task_id,
            "context_enhancement": context_enhancement,
            "operation_id": operation_id
        })

        # 获取任务信息
        self.logger.debug("获取任务信息", {"task_id": task_id})
        task = self.task_manager.get_task(task_id)
        if not task:
            error_msg = f"Task {task_id} not found"
            self.logger.error(error_msg)
            return {"error": error_msg}

        # 检查依赖
        self.logger.debug("检查任务依赖")
        dependencies_check = self._check_dependencies(task)
        if not dependencies_check["all_satisfied"]:
            self.logger.warning("任务依赖未满足", {
                "task_id": task_id,
                "missing_dependencies": dependencies_check["missing_dependencies"]
            })
            return {
                "error": "Dependencies not satisfied",
                "task_info": self._get_task_info(task),
                "dependencies_check": dependencies_check
            }
        
        self.logger.debug("任务依赖检查通过")

        # 获取模板内容
        self.logger.debug("获取模板内容")
        template_info = self._get_template_info(task)
        self.logger.debug("模板内容获取完成", {"template_available": template_info.get("available", False)})

        # 获取执行上下文
        self.logger.debug("构建执行上下文")
        execution_context = self._build_execution_context(task, context_enhancement)
        self.logger.debug("执行上下文构建完成")

        # 获取生成指导
        self.logger.debug("获取生成指导")
        generation_guidance = self._get_generation_guidance(task)
        self.logger.debug("生成指导获取完成")

        # 获取下一个任务
        self.logger.debug("获取下一个任务")
        next_task = self._get_next_task(task)
        self.logger.debug("下一个任务获取完成", {"has_next_task": next_task is not None})

        result = {
            "task_info": self._get_task_info(task),
            "dependencies_check": dependencies_check,
            "template_info": template_info,
            "execution_context": execution_context,
            "generation_guidance": generation_guidance,
            "next_task": next_task
        }
        
        self.logger.log_operation_end("prepare_task_execution", operation_id, success=True, task_id=task_id)
        return result

    def execute_task(self, task_id: str, mark_in_progress: bool = True) -> Dict[str, Any]:
        """执行任务（标记为进行中并提供执行上下文）"""
        operation_id = self.logger.log_operation_start("execute_task", task_id=task_id, mark_in_progress=mark_in_progress)
        
        self.logger.info("开始执行任务", {
            "task_id": task_id,
            "mark_in_progress": mark_in_progress,
            "operation_id": operation_id
        })

        task = self.task_manager.get_task(task_id)
        if not task:
            error_msg = f"Task {task_id} not found"
            self.logger.error(error_msg)
            return {"error": error_msg}

        # 检查任务状态
        self.logger.debug("检查任务状态", {"current_status": task.status.value})
        if task.status not in [TaskStatus.PENDING, TaskStatus.FAILED]:
            error_msg = f"Task {task_id} is not in executable state (current: {task.status.value})"
            self.logger.error(error_msg)
            return {"error": error_msg}

        # scan任务特殊处理 - 自动执行项目分析
        if task.type.value == "scan":
            self.logger.info("检测到scan任务，进入自动执行模式")
            return self._execute_scan_task(task_id)

        # 文件预处理：空文件和大文件检查
        if task.type.value == "file_summary" and task.target_file:
            # 1. 检查空文件
            self.logger.debug("检查是否为空文件", {"target_file": task.target_file})
            empty_file_result = self._check_and_handle_empty_file(task_id)
            if empty_file_result:
                self.logger.info("空文件处理完成")
                return empty_file_result
            
            # 2. 检查大文件
            self.logger.debug("检查是否为大文件", {"target_file": task.target_file})
            large_file_result = self._check_and_handle_large_file(task_id)
            if large_file_result:
                self.logger.info("大文件处理完成")
                return large_file_result

        # 标记任务为进行中
        if mark_in_progress:
            self.logger.info("标记任务为进行中", {"task_id": task_id})
            self.task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
            self.state_tracker.record_task_event("started", task_id)
            self.logger.info("任务开始执行", {"task_id": task_id, "description": task.description})

        # 准备执行上下文
        self.logger.debug("准备执行上下文")
        execution_data = self.prepare_task_execution(task_id, context_enhancement=True)
        self.logger.debug("执行上下文准备完成")

        # 获取任务信息以提供具体指令
        task = self.task_manager.get_task(task_id)
        output_path = self.project_path / task.output_path
        
        self.logger.log_operation_end("execute_task", operation_id, success=True, 
                                    task_id=task_id, task_type=task.type.value, output_path=str(output_path))
        
        return {
            "success": True,
            "task_execution": execution_data,
            "action_required": {
                "type": "generate_and_save_documentation",
                "task_id": task_id,
                "description": f"为 {task.target_file or '项目'} 生成 {task.type.value} 类型的文档",
                "steps": [
                    "1. 仔细分析提供的文件内容和模板结构",
                    "2. 根据模板生成高质量的文档内容",
                    "3. 使用Write工具将文档保存到指定路径",
                    "4. 使用task_complete工具验证并完成任务"
                ],
                "required_tools": ["Write", "task_complete"],
                "output_path": str(output_path),
                "quality_requirements": [
                    "文档必须包含模板中的所有主要章节",
                    "内容不能包含TODO、PLACEHOLDER等占位符",
                    "分析必须准确且详细",
                    "文档长度至少500字符"
                ]
            },
            "next_steps": {
                "step_1": {
                    "action": "生成文档内容",
                    "details": "根据提供的模板和文件内容，生成完整的文档"
                },
                "step_2": {
                    "action": "保存文档",
                    "tool": "Write",
                    "parameters": {
                        "file_path": str(output_path),
                        "content": "[生成的文档内容]"
                    }
                },
                "step_3": {
                    "action": "完成任务",
                    "tool": "task_complete",
                    "parameters": {
                        "project_path": str(self.project_path),
                        "task_id": task_id
                    }
                }
            },
            "instructions": f"请为文件 '{task.target_file or '项目'}' 生成详细的 {task.type.value} 文档。使用提供的模板结构，分析文件内容，生成高质量文档后保存到 {output_path}，然后调用task_complete工具完成任务。"
        }
    
    def _execute_scan_task(self, task_id: str) -> Dict[str, Any]:
        """自动执行scan任务 - 生成项目分析报告"""
        operation_id = self.logger.log_operation_start("execute_scan_task", task_id=task_id)
        
        task = self.task_manager.get_task(task_id)
        
        # 标记为进行中
        self.logger.info("开始自动执行scan任务", {"task_id": task_id})
        self.task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        self.state_tracker.record_task_event("started", task_id)
        self.logger.info("自动执行scan任务", {"task_id": task_id})
        
        try:
            # 使用doc_scan生成项目分析
            self.logger.debug("初始化DocScanTool")
            from src.mcp_tools.doc_scan import DocScanTool
            doc_scan_tool = DocScanTool()
            self.logger.debug("DocScanTool初始化完成")
            
            self.logger.info("开始执行doc_scan", {"project_path": str(self.project_path)})
            scan_result = doc_scan_tool.execute({
                "project_path": str(self.project_path),
                "include_content": False,  # scan任务不需要文件内容
                "config": {"max_files": 100}  # 限制扫描文件数量
            })
            self.logger.info("doc_scan执行完成", {"success": scan_result.get("success")})
            
            if not scan_result.get("success"):
                error_msg = scan_result.get("error", "Unknown scan error")
                self.logger.error("doc_scan执行失败", {"error": error_msg})
                self.task_manager.update_task_status(task_id, TaskStatus.FAILED, error_msg)
                self.logger.log_operation_end("execute_scan_task", operation_id, success=False, error=error_msg)
                return {"success": False, "error": f"Scan failed: {error_msg}"}
            
            # 生成项目扫描报告并保存
            scan_data = scan_result["data"]
            self.logger.debug("开始生成扫描报告")
            report_content = self._generate_scan_report(scan_data)
            self.logger.debug("扫描报告生成完成", {"content_length": len(report_content)})
            
            # 确保输出目录存在
            output_path = self.project_path / task.output_path
            self.logger.debug("创建输出目录", {"output_path": str(output_path)})
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入报告
            self.logger.debug("写入扫描报告", {"file_path": str(output_path)})
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.logger.debug("扫描报告写入完成")
            
            # 自动完成任务
            self.logger.info("自动完成scan任务", {"task_id": task_id})
            self.task_manager.update_task_status(task_id, TaskStatus.COMPLETED)
            self.state_tracker.record_task_event("completed", task_id)
            self.logger.log_operation_end("execute_scan_task", operation_id, success=True, task_id=task_id, output_file=str(output_path))
            
            return {
                "success": True,
                "message": "Scan task completed automatically",
                "output_file": str(output_path),
                "task_completed": True
            }
            
        except Exception as e:
            error_msg = f"Scan task failed: {str(e)}"
            self.logger.log_operation_end("execute_scan_task", operation_id, success=False, error=str(e))
            self.task_manager.update_task_status(task_id, TaskStatus.FAILED, error_msg)
            self.logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}
    
    def _generate_scan_report(self, scan_data: Dict[str, Any]) -> str:
        """生成项目扫描报告内容"""
        scan_result = scan_data.get("scan_result", {})
        project_info = scan_result.get("project_info", {})
        files = scan_result.get("files", [])
        
        # 统计文件信息
        total_files = len(files)
        python_files = len([f for f in files if f.get("extension", "") == ".py"])
        
        # 统计文件类型分布
        file_types = {}
        for file in files:
            ext = file.get("extension", "")
            file_types[ext] = file_types.get(ext, 0) + 1
        
        # 生成目录结构
        directories = set()
        for file in files:
            rel_path = file.get("relative_path", "")
            if "/" in rel_path:
                dir_path = "/".join(rel_path.split("/")[:-1])
                directories.add(dir_path)
        
        dir_structure = "\n".join(sorted(directories)) if directories else "根目录"
        
        report = f"""# 项目扫描报告

## 项目基本信息

- **项目名称**: {project_info.get('name', 'Unknown')}
- **项目路径**: {project_info.get('path', 'Unknown')}
- **总文件数**: {total_files}
- **Python文件数**: {python_files}
- **扫描时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 目录结构

```
{dir_structure}
```

## 文件类型分布

"""
        
        for ext, count in sorted(file_types.items()):
            ext_name = ext if ext else "无扩展名"
            report += f"- **{ext_name}**: {count} 个文件\n"
        
        report += f"""

## 主要文件

"""
        
        main_files = project_info.get("main_files", [])
        for main_file in main_files[:5]:  # 只显示前5个主要文件
            report += f"- {Path(main_file).name}\n"
        
        report += "\n\n## 扫描完成\n\n此报告由CodeLens自动生成，为后续文档生成提供基础信息。\n"
        
        return report

    def _check_and_handle_empty_file(self, task_id: str) -> Optional[Dict[str, Any]]:
        """检查并处理空文件，如果是空文件则自动生成简单文档并完成任务"""
        task = self.task_manager.get_task(task_id)
        if not task or not task.target_file:
            return None
            
        file_path = self.project_path / task.target_file
        if not file_path.exists():
            return None
        
        # 检查文件是否为空或几乎为空
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 如果文件为空或只有少量内容（如空的__init__.py）
            if len(content) <= 10:  # 10个字符以内认为是空文件
                self.logger.info(f"检测到空文件: {task.target_file}，自动生成简单文档")
                
                # 标记任务为进行中
                self.task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
                self.state_tracker.record_task_event("started", task_id)
                
                # 生成简单的空文件文档
                simple_doc = self._generate_empty_file_doc(task.target_file, content)
                
                # 确保输出目录存在
                output_path = self.project_path / task.output_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 写入文档
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(simple_doc)
                
                # 自动完成任务
                self.task_manager.update_task_status(task_id, TaskStatus.COMPLETED)
                self.state_tracker.record_task_event("completed", task_id)
                self.logger.info(f"空文件任务自动完成: {task_id} - {task.target_file}")
                
                return {
                    "success": True,
                    "message": f"Empty file '{task.target_file}' processed automatically",
                    "output_file": str(output_path),
                    "task_completed": True,
                    "auto_generated": True
                }
                
        except Exception as e:
            self.logger.warning(f"检查空文件时出错: {str(e)}")
            return None
        
        return None
    
    def _generate_empty_file_doc(self, file_path: str, content: str) -> str:
        """为空文件生成简单文档"""
        filename = Path(file_path).name
        
        # 判断文件类型
        if filename == "__init__.py":
            description = "Python包初始化文件"
            purpose = "标识该目录为Python包，允许从该目录导入模块"
        elif file_path.endswith(".py"):
            description = "Python模块文件"
            purpose = "目前为空的Python模块，可能用于未来扩展"
        else:
            description = "项目文件"
            purpose = "目前内容较少的项目文件"
        
        doc = f"""# 文件分析报告：{filename}

## 文件概述

**{description}** - 该文件当前内容为空或包含极少内容。

## 基本信息

- **文件路径**: `{file_path}`
- **文件类型**: {Path(file_path).suffix or '无扩展名'}
- **内容状态**: {'完全空白' if not content else '包含少量内容'}
- **文件大小**: {len(content)} 字符

## 内容分析

### 当前内容
```
{content if content else '(文件为空)'}
```

### 功能说明
{purpose}

## 代码结构分析

### 导入依赖
无导入语句

### 全局变量和常量  
无全局变量

### 配置和设置
无配置信息

## 函数详细分析

### 函数概览表
| 函数名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| 无函数 | - | - | 该文件中无函数定义 |

### 函数详细说明
该文件中没有定义任何函数。

## 类详细分析

### 类概览表
| 类名 | 继承 | 方法数 | 描述 |
|------|------|--------|------|
| 无类 | - | - | 该文件中无类定义 |

### 类详细说明
该文件中没有定义任何类。

## 函数调用流程图
```mermaid
graph TD
    A[空文件] --> B[无执行流程]
    B --> C[文件作为包标识或预留扩展]
```

## 变量作用域分析
该文件无变量定义，不涉及作用域分析。

## 函数依赖关系
该文件无函数定义，不存在依赖关系。

## 扩展建议

该文件可能在以下场景中使用：
1. **包初始化**: 作为Python包的标识文件
2. **模块预留**: 为未来功能预留的模块文件
3. **配置占位**: 配置文件的占位符

## 注意事项

- 该文件当前为空或内容极少
- 文档由CodeLens自动生成
- 如需详细分析，请在添加实际代码后重新生成文档
"""
        
        return doc

    def complete_task(self, task_id: str, success: bool = True, error_message: Optional[str] = None) -> Dict[str, Any]:
        """完成任务"""

        task = self.task_manager.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}

        if success:
            # 验证输出文件是否存在且有效（防止虚假完成）
            output_path = getattr(task, 'output_path', None)
            if output_path:
                full_output_path = self.project_path / output_path
                if not full_output_path.exists():
                    self.logger.warning(f"任务 {task_id} 声称完成但输出文件不存在: {output_path}")
                    success = False
                    error_message = f"验证失败 - 输出文件不存在: {output_path}"
                elif full_output_path.stat().st_size < 100:  # 少于100字节认为内容不足
                    self.logger.warning(f"任务 {task_id} 输出文件过小: {full_output_path.stat().st_size} bytes")
                    success = False  
                    error_message = f"验证失败 - 输出文件内容不足: {output_path} ({full_output_path.stat().st_size} bytes)"
                else:
                    self.logger.info(f"任务输出验证通过: {output_path} ({full_output_path.stat().st_size} bytes)")
            
            if success:
                self.task_manager.update_task_status(task_id, TaskStatus.COMPLETED)
                self.state_tracker.record_task_event("completed", task_id)
                self.logger.info(f"任务完成: {task_id} - {task.description}")
            else:
                self.task_manager.update_task_status(task_id, TaskStatus.FAILED, error_message)
                self.state_tracker.record_task_event("validation_failed", task_id, {"error": error_message})
                self.logger.error(f"任务验证失败: {task_id} - {error_message}")
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
            "next_task": self._get_task_info(next_task) if next_task else None
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
        content = self.file_service.read_file_safe(str(file_path), self.max_file_size)
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
            for task in completed_tasks[-10:]:  # 最近10个完成的任务
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

            return {
                "phase": phase,
                "progress": progress
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
        """获取下一个任务"""
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
    
    def _check_and_handle_large_file(self, task_id: str) -> Optional[Dict[str, Any]]:
        """检查并处理大文件，如果是大文件则使用分片策略处理"""
        if not self.enable_chunking:
            return None
            
        task = self.task_manager.get_task(task_id)
        if not task or not task.target_file:
            return None
            
        file_path = self.project_path / task.target_file
        if not file_path.exists():
            return None
        
        # 检查文件是否需要分片处理
        processing_info = self.file_service.get_file_processing_info(
            str(file_path), self.large_file_threshold
        )
        
        if not processing_info.get('needs_chunking', False):
            return None
            
        self.logger.info(f"检测到大文件: {task.target_file} ({processing_info['size_mb']} MB)，开始分片处理")
        
        try:
            # 标记任务为进行中
            self.task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
            self.state_tracker.record_task_event("started", task_id)
            
            # 使用分片处理大文件
            result = self.file_service.read_file_with_chunking(str(file_path), self.max_file_size)
            
            if isinstance(result, ChunkingResult) and result.success:
                # 处理分片结果
                merged_doc = self._process_chunks_and_merge(task, result)
                
                # 确保输出目录存在
                output_path = self.project_path / task.output_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 写入合并后的文档
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(merged_doc)
                
                # 自动完成任务
                self.task_manager.update_task_status(task_id, TaskStatus.COMPLETED)
                self.state_tracker.record_task_event("completed", task_id)
                self.logger.info(f"大文件任务自动完成: {task_id} - {task.target_file}")
                
                return {
                    "success": True,
                    "message": f"Large file '{task.target_file}' processed with chunking",
                    "output_file": str(output_path),
                    "task_completed": True,
                    "chunking_info": {
                        "total_chunks": result.total_chunks,
                        "processing_method": result.processing_method,
                        "processing_time": result.processing_time
                    },
                    "file_info": processing_info
                }
            else:
                # 分片失败，记录警告但不阻止正常流程
                self.logger.warning(f"大文件分片处理失败: {task.target_file}")
                self.task_manager.update_task_status(task_id, TaskStatus.PENDING)  # 恢复状态
                return None
                
        except Exception as e:
            self.logger.error(f"处理大文件时出错: {str(e)}")
            self.task_manager.update_task_status(task_id, TaskStatus.PENDING)  # 恢复状态
            return None
        
        return None
    
    def _process_chunks_and_merge(self, task: Task, chunking_result: ChunkingResult) -> str:
        """处理代码分片并合并生成最终文档"""
        chunks = chunking_result.chunks
        
        # 获取模板
        template_info = self._get_template_info(task)
        template_content = template_info.get('content', '')
        
        # 按依赖关系对分片排序
        sorted_chunks = self._sort_chunks_by_dependencies(chunks)
        
        # 为每个分片生成文档片段
        chunk_docs = []
        for i, chunk in enumerate(sorted_chunks):
            self.logger.debug(f"处理分片 {i+1}/{len(sorted_chunks)}: {chunk.chunk_type.value}")
            
            chunk_doc = self._generate_chunk_documentation(chunk, template_content, task)
            chunk_docs.append({
                'chunk': chunk,
                'documentation': chunk_doc,
                'order': i
            })
        
        # 合并所有分片文档
        merged_doc = self._merge_chunk_documentations(chunk_docs, task, chunking_result)
        
        return merged_doc
    
    def _sort_chunks_by_dependencies(self, chunks: List[CodeChunk]) -> List[CodeChunk]:
        """根据依赖关系对分片排序"""
        # 简单实现：按类型和行号排序，后续可以改进为真正的依赖排序
        def sort_key(chunk):
            type_priority = {
                'module': 0,   # 模块级内容优先
                'import': 1,   # 导入语句
                'class': 2,    # 类定义
                'function': 3, # 函数定义
                'mixed': 4     # 混合内容
            }
            return (type_priority.get(chunk.chunk_type.value, 5), chunk.start_line)
        
        return sorted(chunks, key=sort_key)
    
    def _generate_chunk_documentation(self, chunk: CodeChunk, template: str, task: Task) -> str:
        """为单个代码分片生成文档"""
        # 基于分片类型生成相应的文档
        if chunk.chunk_type.value == 'class':
            return self._generate_class_chunk_doc(chunk, template)
        elif chunk.chunk_type.value == 'function':
            return self._generate_function_chunk_doc(chunk, template)
        elif chunk.chunk_type.value == 'module':
            return self._generate_module_chunk_doc(chunk, template)
        else:
            return self._generate_generic_chunk_doc(chunk, template)
    
    def _generate_class_chunk_doc(self, chunk: CodeChunk, template: str) -> str:
        """生成类分片的文档"""
        class_name = chunk.metadata.get('class_name', '未知类')
        method_count = chunk.metadata.get('method_count', 0)
        base_classes = chunk.metadata.get('base_classes', [])
        
        doc = f"""### 类: {class_name}

**定义位置**: 第 {chunk.start_line}-{chunk.end_line} 行
**复杂度评分**: {chunk.complexity_score:.1f}
**大小**: {chunk.size_bytes} 字节

#### 类特征
- 方法数量: {method_count}
- 继承关系: {', '.join(base_classes) if base_classes else '无'}
- 是否为私有类: {'是' if class_name.startswith('_') else '否'}

#### 类结构分析

```python
{chunk.content}
```

#### 依赖关系
- **定义的符号**: {', '.join(chunk.definitions) if chunk.definitions else '无'}
- **引用的符号**: {', '.join(sorted(chunk.references)[:10]) if chunk.references else '无'}
{f"(共 {len(chunk.references)} 个引用)" if len(chunk.references) > 10 else ""}

"""
        return doc
    
    def _generate_function_chunk_doc(self, chunk: CodeChunk, template: str) -> str:
        """生成函数分片的文档"""
        function_name = chunk.metadata.get('function_name', '未知函数')
        parameter_count = chunk.metadata.get('parameter_count', 0)
        is_method = chunk.metadata.get('is_method', False)
        class_name = chunk.metadata.get('class_name', '')
        
        doc = f"""### {'方法' if is_method else '函数'}: {function_name}

**定义位置**: 第 {chunk.start_line}-{chunk.end_line} 行
**复杂度评分**: {chunk.complexity_score:.1f}
**参数数量**: {parameter_count}
{'**所属类**: ' + class_name if class_name else ''}

#### 函数特征
- 类型: {'类方法' if is_method else '模块函数'}
- 私有方法: {'是' if function_name.startswith('_') else '否'}
- 特殊方法: {'是' if function_name.startswith('__') and function_name.endswith('__') else '否'}

#### 实现分析

```python
{chunk.content}
```

#### 依赖分析
- **定义的符号**: {', '.join(chunk.definitions) if chunk.definitions else '无'}
- **引用的符号**: {', '.join(sorted(chunk.references)[:8]) if chunk.references else '无'}
{f"(共 {len(chunk.references)} 个引用)" if len(chunk.references) > 8 else ""}

"""
        return doc
    
    def _generate_module_chunk_doc(self, chunk: CodeChunk, template: str) -> str:
        """生成模块级分片的文档"""
        doc = f"""### 模块级定义

**位置**: 第 {chunk.start_line}-{chunk.end_line} 行
**内容类型**: 导入语句和全局定义

#### 模块级内容

```python
{chunk.content}
```

#### 导入和全局定义
- **定义的符号**: {', '.join(chunk.definitions) if chunk.definitions else '无'}
- **引用的符号**: {', '.join(sorted(chunk.references)[:10]) if chunk.references else '无'}

"""
        return doc
    
    def _generate_generic_chunk_doc(self, chunk: CodeChunk, template: str) -> str:
        """生成通用分片的文档"""
        doc = f"""### 代码片段: {chunk.chunk_type.value}

**位置**: 第 {chunk.start_line}-{chunk.end_line} 行
**复杂度评分**: {chunk.complexity_score:.1f}
**大小**: {chunk.size_bytes} 字节

#### 内容分析

```{chunk.language}
{chunk.content}
```

#### 分析结果
- **定义的符号**: {', '.join(chunk.definitions) if chunk.definitions else '无'}
- **引用的符号**: {', '.join(sorted(chunk.references)[:10]) if chunk.references else '无'}

"""
        return doc
    
    def _merge_chunk_documentations(self, chunk_docs: List[Dict], task: Task, chunking_result: ChunkingResult) -> str:
        """合并所有分片文档为最终文档"""
        filename = Path(task.target_file).name
        file_path = task.target_file
        
        # 文档头部
        header = f"""# 文件分析报告：{filename}

## 文件概述

**大文件分片处理报告** - 该文件因大小超过阈值被自动分片处理。

## 基本信息

- **文件路径**: `{file_path}`
- **文件大小**: {chunking_result.total_size} 字节 ({chunking_result.total_size / 1024:.1f} KB)
- **分片数量**: {chunking_result.total_chunks}
- **处理方法**: {chunking_result.processing_method}
- **处理时间**: {chunking_result.processing_time:.2f} 秒
- **编程语言**: {chunk_docs[0]['chunk'].language if chunk_docs else '未知'}

## 分片处理结果

### 分片概览

"""
        
        # 分片统计
        chunk_stats = {}
        for doc_info in chunk_docs:
            chunk_type = doc_info['chunk'].chunk_type.value
            chunk_stats[chunk_type] = chunk_stats.get(chunk_type, 0) + 1
        
        for chunk_type, count in chunk_stats.items():
            header += f"- {chunk_type.title()} 分片: {count} 个\n"
        
        header += "\n## 详细分析\n\n"
        
        # 合并所有分片文档
        all_chunks_doc = ""
        for i, doc_info in enumerate(chunk_docs, 1):
            all_chunks_doc += f"\n---\n\n## 分片 {i}: {doc_info['chunk'].chunk_type.value.title()}\n\n"
            all_chunks_doc += doc_info['documentation']
            all_chunks_doc += "\n"
        
        # 文档尾部
        footer = f"""\n---\n\n## 分片处理总结\n
本文件通过CodeLens大文件分片系统进行处理，将大文件按照语义边界分割为 {len(chunk_docs)} 个独立分片，
每个分片都进行了详细的结构分析和文档生成，最终合并为完整的文档。

### 处理统计

- **总分片数**: {len(chunk_docs)}
- **处理方法**: {chunking_result.processing_method}
- **成功率**: 100%
- **处理时间**: {chunking_result.processing_time:.2f} 秒

*此文档由CodeLens自动生成，采用了智能分片合并技术。*
"""
        
        # 合并完整文档
        complete_doc = header + all_chunks_doc + footer
        
        return complete_doc
        
    def get_chunking_stats(self) -> Dict[str, Any]:
        """获取分片处理统计信息"""
        if not self.enable_chunking or not hasattr(self.file_service, 'large_file_handler'):
            return {'chunking_enabled': False}
            
        handler = self.file_service.large_file_handler
        if handler:
            stats = handler.get_processing_stats()
            stats['chunking_enabled'] = True
            stats['threshold_kb'] = self.large_file_threshold / 1024
            stats['max_file_size_kb'] = self.max_file_size / 1024
            return stats
        else:
            return {'chunking_enabled': False}




class TaskExecuteTool:
    """MCP task_execute 工具类"""

    def __init__(self):
        self.tool_name = "task_execute"
        self.description = "执行单个或批量任务，提供模板和上下文信息"
        self.logger = get_logger(component="TaskExecuteTool", operation="init")
        self.logger.info("TaskExecuteTool初始化完成")

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
                    "task_id": {
                        "type": "string",
                        "description": "要执行的任务ID"
                    },
                    "execution_mode": {
                        "type": "string",
                        "enum": ["prepare", "execute", "complete"],
                        "description": "执行模式"
                    },
                    "context_enhancement": {
                        "type": "boolean",
                        "description": "是否启用上下文增强"
                    },
                    "mark_in_progress": {
                        "type": "boolean",
                        "description": "是否标记任务为进行中"
                    },
                    "completion_data": {
                        "type": "object",
                        "properties": {
                            "success": {
                                "type": "boolean"
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
        operation_id = self.logger.log_operation_start("execute_task_execute_tool",
                                                       project_path=arguments.get("project_path"),
                                                       task_id=arguments.get("task_id"),
                                                       execution_mode=arguments.get("execution_mode", "execute"),
                                                       context_enhancement=arguments.get("context_enhancement", True))
        
        try:
            self.logger.info("开始执行task_execute工具", {"arguments": arguments, "operation_id": operation_id})
            
            # 参数验证
            project_path = arguments.get("project_path")
            task_id = arguments.get("task_id")
            
            self.logger.debug("验证参数", {"project_path": project_path, "task_id": task_id})

            if not project_path or not os.path.exists(project_path):
                error_msg = "Invalid project path"
                self.logger.error(error_msg, {"project_path": project_path})
                return self._error_response(error_msg)

            if not task_id:
                error_msg = "Task ID is required"
                self.logger.error(error_msg)
                return self._error_response(error_msg)

            # 获取参数
            execution_mode = arguments.get("execution_mode", "execute")
            context_enhancement = arguments.get("context_enhancement", True)
            mark_in_progress = arguments.get("mark_in_progress", True)
            completion_data = arguments.get("completion_data", {})

            # 创建任务执行器
            self.logger.debug("创建任务执行器", {"project_path": project_path})
            executor = TaskExecutor(project_path)
            self.logger.debug("任务执行器创建完成")

            self.logger.info("开始执行任务", {"task_id": task_id, "execution_mode": execution_mode})

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

            success = 'error' not in result
            self.logger.log_operation_end("execute_task_execute_tool", operation_id, success=success, 
                                        task_id=task_id, execution_mode=execution_mode)

            return self._success_response(result)

        except Exception as e:
            self.logger.log_operation_end("execute_task_execute_tool", operation_id, success=False, error=str(e))
            self.logger.error(f"任务执行失败: {str(e)}", exc_info=e)
            return self._error_response(f"Task execution failed: {str(e)}")

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
