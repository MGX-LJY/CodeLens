# task_execute.py

## 文件概述
智能任务执行MCP工具实现，负责执行单个或批量任务，提供完整的模板、上下文信息和执行指导。作为Task Engine模块的核心执行组件，集成任务管理器、阶段控制器和状态跟踪器，实现任务的完整生命周期管理。

## 核心类定义

### TaskExecutor (任务执行器)
任务执行核心实现，集成多个服务组件

#### 组件集成
```python
def __init__(self, project_path: str):
    self.project_path = Path(project_path)
    self.task_manager = TaskManager(str(project_path))
    self.phase_controller = PhaseController(self.task_manager)
    self.state_tracker = StateTracker(str(project_path), self.task_manager, self.phase_controller)
    self.file_service = FileService()
    self.template_service = TemplateService()
```

#### 核心方法

**prepare_task_execution(task_id: str, context_enhancement: bool = True) -> Dict[str, Any]**
- 准备任务执行上下文
- 检查任务依赖关系满足情况
- 获取模板内容和执行指导
- 构建完整的执行上下文环境
- 提供下一个任务建议

**execute_task(task_id: str, mark_in_progress: bool = True) -> Dict[str, Any]**
- 标记任务为执行中状态
- 准备完整的执行上下文
- 记录任务开始事件
- 返回执行指令和上下文信息

**complete_task(task_id: str, success: bool = True, error_message: Optional[str] = None) -> Dict[str, Any]**
- 标记任务完成或失败状态
- 记录任务完成事件
- 获取下一个可执行任务
- 检查阶段完成状态
- 提供完成后建议

### TaskExecuteTool (MCP工具类)
task_execute MCP工具主要实现

#### 工具定义
```python
def get_tool_definition(self) -> Dict[str, Any]:
    return {
        "name": "task_execute",
        "description": "执行单个或批量任务，提供模板和上下文信息",
        "inputSchema": {
            "properties": {
                "project_path": {"type": "string"},
                "task_id": {"type": "string"},
                "execution_mode": {"enum": ["prepare", "execute", "complete"]},
                "context_enhancement": {"type": "boolean", "default": True},
                "mark_in_progress": {"type": "boolean", "default": True},
                "completion_data": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "default": True},
                        "error_message": {"type": "string"}
                    }
                }
            }
        }
    }
```

## 3种执行模式详解

### Prepare Mode (准备模式)
获取任务执行所需的完整信息，不改变任务状态

**功能**:
- 验证任务依赖关系
- 获取模板内容和变量
- 构建执行上下文
- 提供生成指导

**返回结构**:
```json
{
    "task_info": {
        "id": "task_123",
        "type": "file_summary",
        "description": "生成app.py文件摘要",
        "phase": "phase_2_files",
        "target_file": "app.py",
        "template_name": "file_summary",
        "output_path": "docs/files/summaries/app.py.md"
    },
    "dependencies_check": {
        "all_satisfied": true,
        "missing_dependencies": [],
        "satisfied_dependencies": [...]
    },
    "template_info": {
        "available": true,
        "template_name": "file_summary",
        "template_content": "# {file_name}\n\n## 文件概述\n...",
        "template_variables": ["file_name", "file_path"]
    },
    "execution_context": {...},
    "generation_guidance": {...}
}
```

### Execute Mode (执行模式)
标记任务为进行中并提供完整执行上下文

**功能**:
- 检查任务可执行状态
- 标记任务为IN_PROGRESS
- 记录任务开始事件
- 调用prepare_task_execution获取上下文

**状态变更**: PENDING/FAILED → IN_PROGRESS

**返回结构**:
```json
{
    "success": true,
    "task_execution": {
        "task_info": {...},
        "dependencies_check": {...},
        "template_info": {...},
        "execution_context": {...},
        "generation_guidance": {...}
    },
    "instructions": "Use the provided template and context to generate the documentation. Call task_complete when finished."
}
```

### Complete Mode (完成模式)
标记任务完成，更新状态并提供后续建议

**功能**:
- 标记任务为COMPLETED或FAILED
- 记录完成/失败事件
- 获取下一个可执行任务
- 检查阶段进度状态
- 提供完成后建议

**状态变更**: IN_PROGRESS → COMPLETED/FAILED

**返回结构**:
```json
{
    "success": true,
    "task_completed": {
        "task_id": "task_123",
        "status": "completed",
        "error_message": null
    },
    "phase_status": {
        "total_tasks": 20,
        "completed_tasks": 15,
        "completion_percentage": 75.0,
        "can_proceed": false
    },
    "next_task": {
        "id": "task_124",
        "description": "生成models.py文件摘要",
        "phase": "phase_2_files"
    },
    "recommendations": ["还有5个任务未完成，继续当前阶段"]
}
```

## 智能上下文构建

### 依赖检查系统
```python
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
```

**特点**:
- 验证所有依赖任务存在性
- 检查依赖任务完成状态
- 提供详细的未满足依赖信息
- 记录已满足的依赖任务

### 模板信息获取
```python
def _get_template_info(self, task: Task) -> Dict[str, Any]:
    """获取模板信息"""
    if not task.template_name:
        return {"available": False, "reason": "No template specified"}
    
    template_result = self.template_service.get_template_content(task.template_name)
    
    return {
        "available": True,
        "template_name": task.template_name,
        "template_content": template_result["content"],
        "template_metadata": template_result["metadata"],
        "template_variables": template_result["metadata"].get("variables", [])
    }
```

**特点**:
- 从TemplateService获取模板内容
- 提取模板变量和元数据
- 处理模板不可用情况
- 返回结构化模板信息

### 执行上下文构建
支持4种类型的上下文信息:

#### 文件上下文
```python
def _get_file_context(self, target_file: str, enhanced: bool) -> Dict[str, Any]:
    """获取文件上下文"""
    context = {
        "file_path": target_file,
        "exists": file_path.exists(),
        "metadata": metadata,
        "content": content,
        "content_length": len(content),
        "line_count": content.count('\n') + 1
    }
    
    # 增强上下文：相关文件
    if enhanced:
        related_files = self._find_related_files(target_file)
        context["related_files"] = related_files
```

#### 模块上下文
```python
def _get_module_context(self, target_module: str, enhanced: bool) -> Dict[str, Any]:
    """获取模块上下文"""
    module_files = self._find_module_files(target_module)
    
    context = {
        "module_name": target_module,
        "module_files": module_files
    }
    
    # 文件内容摘要
    if module_files and enhanced:
        file_summaries = []
        for file_path in module_files[:5]:
            content = self.file_service.read_file_safe(str(full_path))
            file_summaries.append({
                "file": file_path,
                "lines": content.count('\n') + 1,
                "size": len(content),
                "preview": content[:500] + "..." if len(content) > 500 else content
            })
        context["file_summaries"] = file_summaries
```

#### 项目上下文
```python
def _get_project_context(self) -> Dict[str, Any]:
    """获取项目上下文"""
    project_info = self.file_service.get_project_info(str(self.project_path))
    completed_tasks = [t for t in self.task_manager.tasks.values() if t.status == TaskStatus.COMPLETED]
    
    context = {
        "project_info": project_info,
        "completed_tasks_count": len(completed_tasks),
        "total_tasks_count": len(self.task_manager.tasks),
        "project_progress": self.task_manager.get_overall_progress(),
        "recent_completions": completed_summaries[-10:]  # 最近10个完成任务
    }
```

#### 阶段上下文
```python
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
```

## 智能生成指导系统

### 任务类型特定指导
为不同任务类型提供专门的生成指导:

#### file_summary 任务
```python
if task_type == "file_summary":
    guidance = {
        "focus_points": [
            "分析文件的主要功能和职责",
            "识别类、函数和重要常量",
            "理解文件在项目中的作用",
            "分析代码架构和设计模式"
        ],
        "template_instructions": "使用file_summary模板，重点关注代码结构和功能分析",
        "quality_criteria": [
            "准确识别所有主要组件",
            "清晰描述功能用途",
            "正确分析依赖关系"
        ]
    }
```

#### module_analysis 任务
```python
elif task_type == "module_analysis":
    guidance = {
        "focus_points": [
            "基于文件摘要识别功能模块",
            "分析模块间的关系和依赖",
            "理解模块的业务职责",
            "评估模块的架构设计"
        ],
        "template_instructions": "使用module_analysis模板，基于已完成的文件摘要进行模块识别",
        "quality_criteria": [
            "合理的模块划分",
            "清晰的职责定义",
            "准确的依赖关系"
        ]
    }
```

#### architecture 任务
```python
elif task_type == "architecture":
    guidance = {
        "focus_points": [
            "基于模块分析设计整体架构",
            "选择合适的架构模式",
            "定义系统边界和接口",
            "考虑非功能性需求"
        ],
        "template_instructions": "使用architecture模板，整合所有前期分析结果",
        "quality_criteria": [
            "合理的架构设计",
            "清晰的技术选型理由",
            "完整的系统描述"
        ]
    }
```

#### project_readme 任务
```python
elif task_type == "project_readme":
    guidance = {
        "focus_points": [
            "汇总项目的核心特性",
            "提供清晰的安装和使用指南",
            "展示项目的技术亮点",
            "面向用户的友好说明"
        ],
        "template_instructions": "使用project_readme模板，创建对外展示的项目文档",
        "quality_criteria": [
            "用户友好的表达",
            "完整的使用说明",
            "吸引人的项目介绍"
        ]
    }
```

### 输出要求规范
```python
if task.output_path:
    guidance["output_requirements"] = {
        "file_path": task.output_path,
        "format": "Markdown",
        "encoding": "UTF-8",
        "ensure_directory": True
    }
```

## 智能文件发现

### 相关文件查找
```python
def _find_related_files(self, target_file: str) -> List[str]:
    """查找相关文件"""
    target_path = Path(target_file)
    target_dir = target_path.parent
    target_name = target_path.stem
    
    # 查找同目录下的相关文件
    for file_path in (self.project_path / target_dir).glob("*"):
        if file_path.is_file() and file_path != self.project_path / target_file:
            relative_path = file_path.relative_to(self.project_path)
            # 名字相似或同类型的文件
            if (target_name in file_path.stem or 
                file_path.suffix == target_path.suffix):
                related.append(str(relative_path))
    
    return related[:5]  # 最多5个相关文件
```

### 模块文件查找
```python
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
```

## 完成后智能建议

### 阶段进度建议
```python
def _get_post_completion_recommendations(self, task: Task, phase_progress: Dict[str, Any]) -> List[str]:
    """获取完成后建议"""
    recommendations = []
    
    # 阶段进度建议
    if phase_progress["can_proceed"]:
        recommendations.append(f"{task.phase}阶段已完成，可以进入下一阶段")
    else:
        remaining = phase_progress["total_tasks"] - phase_progress["completed_tasks"]
        recommendations.append(f"还有{remaining}个任务未完成，继续当前阶段")
```

### 任务特定建议
```python
# 任务特定建议
if task.type.value == "file_summary":
    recommendations.append("文件摘要已完成，建议继续分析其他核心文件")
elif task.type.value == "module_analysis":
    recommendations.append("模块分析已完成，可以开始分析模块关系")
elif task.type.value == "architecture":
    recommendations.append("架构分析已完成，建议生成技术栈文档")
```

## 下一个任务智能推荐

### 同阶段任务推荐
```python
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
```

### 跨阶段任务推荐
```python
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
```

## 性能特性
- **上下文构建**: < 100ms
- **依赖检查**: < 50ms  
- **模板获取**: < 20ms
- **状态更新**: < 10ms
- **内存使用**: 每个执行上下文约占用50KB

## 使用示例

### MCP工具调用
```python
from src.mcp_tools.task_execute import create_mcp_tool

# 创建工具实例
tool = create_mcp_tool()

# 准备任务执行
arguments = {
    "project_path": "/path/to/project",
    "task_id": "task_123",
    "execution_mode": "prepare",
    "context_enhancement": True
}
result = tool.execute(arguments)

# 执行任务
arguments["execution_mode"] = "execute"
result = tool.execute(arguments)

# 完成任务
arguments.update({
    "execution_mode": "complete",
    "completion_data": {
        "success": True
    }
})
result = tool.execute(arguments)
```

### 命令行测试
```bash
# 准备任务
python src/mcp_tools/task_execute.py /path/to/project \
    --task-id task_123 \
    --mode prepare

# 执行任务
python src/mcp_tools/task_execute.py /path/to/project \
    --task-id task_123 \
    --mode execute

# 完成任务
python src/mcp_tools/task_execute.py /path/to/project \
    --task-id task_123 \
    --mode complete
```

### 完整工作流集成
```python
# 完整任务执行流程
from src.mcp_tools.task_execute import TaskExecutor

executor = TaskExecutor("/path/to/project")

# 1. 准备任务
task_id = "file_summary_123"
prepare_result = executor.prepare_task_execution(task_id, context_enhancement=True)

if "error" in prepare_result:
    print(f"任务准备失败: {prepare_result['error']}")
    return

# 2. 执行任务
execute_result = executor.execute_task(task_id, mark_in_progress=True)
print(f"任务开始执行: {execute_result['task_execution']['task_info']['description']}")

# 3. 模拟AI生成文档
# ... AI使用模板和上下文生成文档 ...

# 4. 完成任务
complete_result = executor.complete_task(task_id, success=True)
print(f"任务完成，下一个任务: {complete_result['next_task']['description'] if complete_result['next_task'] else 'None'}")
```

## 错误处理

### 任务状态验证
- **任务不存在**: 返回"Task not found"错误
- **状态不匹配**: 检查任务状态是否允许执行
- **依赖未满足**: 提供详细的依赖缺失信息

### 文件系统错误处理
- **文件读取失败**: 优雅降级，提供基础上下文
- **路径不存在**: 标记文件不存在但继续执行
- **权限错误**: 记录错误日志但不中断流程

### 模板系统错误处理
- **模板不存在**: 提供模板缺失信息
- **模板解析失败**: 返回模板解析错误详情
- **变量提取失败**: 使用空变量列表作为回退

