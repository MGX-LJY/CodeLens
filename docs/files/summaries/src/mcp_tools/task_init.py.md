# task_init.py

## 文件概述
智能任务计划生成MCP工具实现，基于项目分析结果生成完整的5阶段任务列表。作为Task Engine模块的核心规划组件，负责将分析结果转化为可执行的任务队列，实现从项目扫描到文档生成的全流程任务调度。

## 核心类定义

### TaskPlanGenerator (任务计划生成器)
基于分析结果生成结构化任务计划

#### 模板映射系统
```python
template_mapping = {
    TaskType.FILE_SUMMARY: "file_summary",
    TaskType.MODULE_ANALYSIS: "module_analysis", 
    TaskType.MODULE_RELATIONS: "module_relations",
    TaskType.DEPENDENCY_GRAPH: "dependency_graph",
    TaskType.ARCHITECTURE: "architecture",
    TaskType.TECH_STACK: "tech_stack",
    TaskType.DATA_FLOW: "data_flow",
    TaskType.PROJECT_README: "project_readme"
    # 支持14种任务类型的模板映射
}
```

#### 智能优先级系统
```python
priority_mapping = {
    "high": ["main.py", "app.py", "index.js", "server.js", "main.go"],
    "normal": ["config", "model", "service", "controller", "handler"],
    "low": ["util", "helper", "test", "spec"]
}
```

#### 核心方法

**generate_tasks(project_path, analysis_result, task_granularity, parallel_tasks, custom_priorities) -> Dict[str, Any]**
- 生成完整的5阶段任务计划
- 根据项目分析结果创建结构化任务列表
- 建立任务间依赖关系图谱
- 计算时间估算和任务分布统计

### TaskInitTool (MCP工具类)
task_init MCP工具主要实现

#### 工具定义
```python
def get_tool_definition(self) -> Dict[str, Any]:
    return {
        "name": "task_init",
        "description": "基于项目分析结果，生成完整的阶段性任务列表",
        "inputSchema": {
            "properties": {
                "project_path": {"type": "string"},
                "analysis_result": {"type": "object", "required": True},
                "task_granularity": {"enum": ["file", "batch", "module"]},
                "parallel_tasks": {"type": "boolean"},
                "custom_priorities": {"type": "object"},
                "create_in_manager": {"type": "boolean"}
            }
        }
    }
```

## 5阶段任务生成详解

### Phase 1: 项目扫描任务
```python
def _generate_phase_1_tasks(self, project_path: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成第一阶段任务（项目扫描）"""
    return [{
        "id": f"scan_{timestamp}",
        "type": "scan",
        "description": "扫描项目文件结构和基本信息",
        "phase": "phase_1_scan",
        "template": None,
        "dependencies": [],
        "priority": "high",
        "estimated_time": "5 minutes"
    }]
```

**特点**:
- 唯一扫描任务，作为所有后续任务的基础依赖
- 无前置依赖，可立即执行
- 高优先级，包含项目元数据

### Phase 2: 文件层文档生成
```python
def _generate_phase_2_tasks(self, project_path: str, plan: Dict[str, Any], custom_priorities: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """生成第二阶段任务（文件层）"""
    tasks = []
    files_to_process = plan.get("phase_2_files", [])
    
    for i, file_path in enumerate(files_to_process):
        task_id = f"file_summary_{timestamp}_{i}"
        priority = self._get_file_priority(file_path, custom_priorities)
        
        task = {
            "id": task_id,
            "type": "file_summary",
            "description": f"生成{file_path}文件摘要",
            "phase": "phase_2_files",
            "target_file": file_path,
            "template": "file_summary",
            "output_path": f"docs/files/summaries/{file_path}.md",
            "dependencies": [scan_task_id],
            "priority": priority,
            "estimated_time": "3 minutes"
        }
```

**特点**:
- 为每个关键文件生成独立任务
- 依赖Phase 1扫描任务完成
- 智能优先级分配
- 标准化输出路径

### Phase 3: 模块层文档生成
创建6类模块层任务:

1. **模块总览任务**
```python
{
    "type": "module_analysis",
    "description": "生成模块总览和功能分析",
    "template": "module_analysis",
    "output_path": "docs/modules/overview.md",
    "dependencies": file_task_ids,  # 依赖所有文件任务
    "estimated_time": "8 minutes"
}
```

2. **模块关系任务**
```python
{
    "type": "module_relations",
    "description": "分析模块间关系和依赖",
    "template": "module_relations",
    "output_path": "docs/modules/module-relations.md",
    "dependencies": [module_analysis_id],
    "estimated_time": "6 minutes"
}
```

3. **依赖图谱任务**
```python
{
    "type": "dependency_graph",
    "description": "生成模块依赖图谱分析",
    "template": "dependency_graph",
    "output_path": "docs/modules/dependency-graph.md",
    "estimated_time": "5 minutes"
}
```

4. **重要模块详细文档** (前3个模块)
   - 模块README: `docs/modules/modules/{module}/README.md`
   - 模块API: `docs/modules/modules/{module}/api.md`
   - 模块流程: `docs/modules/modules/{module}/flow.md`

### Phase 4: 架构层文档生成
创建6类架构层任务:

1. **架构概述**
```python
{
    "type": "architecture",
    "description": "生成系统架构概述",
    "template": "architecture",
    "output_path": "docs/architecture/overview.md",
    "dependencies": module_task_ids,  # 依赖所有模块任务
    "estimated_time": "12 minutes"
}
```

2. **技术栈分析**
```python
{
    "type": "tech_stack",
    "description": "分析技术栈和架构原则",
    "output_path": "docs/architecture/tech-stack.md",
    "estimated_time": "10 minutes"
}
```

3. **数据流设计**
```python
{
    "type": "data_flow",
    "description": "设计系统数据流",
    "output_path": "docs/architecture/data-flow.md",
    "estimated_time": "8 minutes"
}
```

4. **架构图表**
   - 系统架构图: `docs/architecture/diagrams/system-architecture.md`
   - 组件关系图: `docs/architecture/diagrams/component-diagram.md`
   - 部署架构图: `docs/architecture/diagrams/deployment-diagram.md`

### Phase 5: 项目层文档生成
```python
def _generate_phase_5_tasks(self, project_path: str, analysis: Dict[str, Any], phase_4_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """生成第五阶段任务（项目层）"""
    return [{
        "id": f"project_readme_{timestamp}",
        "type": "project_readme",
        "description": "生成项目README文档",
        "phase": "phase_5_project",
        "template": "project_readme",
        "output_path": "docs/project/README.md",
        "dependencies": arch_task_ids,  # 依赖所有架构任务
        "estimated_time": "10 minutes"
    }]
```

**特点**:
- 仅生成README.md文档
- 依赖所有架构层任务完成
- 项目总结性文档

## 智能特性

### 优先级智能分配
```python
def _get_file_priority(self, file_path: str, custom_priorities: Dict[str, Any] = None) -> str:
    """确定文件优先级"""
    # 1. 自定义优先级优先
    if custom_priorities and file_path in custom_priorities:
        return custom_priorities[file_path]
    
    file_lower = file_path.lower()
    
    # 2. 高优先级模式匹配
    for pattern in self.priority_mapping["high"]:
        if pattern in file_lower:
            return "high"
    
    # 3. 普通和低优先级模式匹配
    # 默认返回"normal"
```

### 依赖关系图构建
```python
def _build_dependency_graph(self, all_tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """构建依赖关系图"""
    graph = {}
    for task in all_tasks:
        task_id = task["id"]
        dependencies = task.get("dependencies", [])
        graph[task_id] = dependencies
    return graph
```

### 任务管理器集成
```python
def create_tasks_in_manager(self, task_manager: TaskManager, task_plan: Dict[str, Any]) -> int:
    """在任务管理器中创建所有任务"""
    created_count = 0
    phases = ["phase_1_scan", "phase_2_files", "phase_3_modules", "phase_4_architecture", "phase_5_project"]
    
    for phase in phases:
        if phase in task_plan:
            tasks = phase_data.get("tasks", [])
            for task_data in tasks:
                task_type = TaskType(task_data["type"])
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
                    metadata=task_data.get("metadata", {})
                )
                created_count += 1
```

## 任务计划结构

### 完整响应格式
```json
{
    "task_plan": {
        "total_phases": 5,
        "total_tasks": 45,
        "estimated_duration": "2 hours 30 minutes",
        "dependencies_graph": {"task_id": ["dependency_ids"]},
        "task_distribution": {
            "phase_1_scan": 1,
            "phase_2_files": 20,
            "phase_3_modules": 12,
            "phase_4_architecture": 6,
            "phase_5_project": 1
        }
    },
    "phase_1_scan": {
        "description": "项目扫描和分析",
        "dependencies": [],
        "estimated_time": "5 minutes",
        "tasks": [...]
    },
    "phase_2_files": {
        "description": "文件层文档生成（20个文件）",
        "dependencies": ["phase_1_complete"],
        "estimated_time": "60 minutes",
        "tasks": [...]
    }
    // ... 其他阶段
}
```

### 任务结构标准
```json
{
    "id": "file_summary_1694689200000_0",
    "type": "file_summary",
    "description": "生成app.py文件摘要",
    "phase": "phase_2_files",
    "target_file": "app.py",
    "template": "file_summary",
    "output_path": "docs/files/summaries/app.py.md",
    "dependencies": ["scan_1694689200000"],
    "priority": "high",
    "estimated_time": "3 minutes",
    "status": "pending",
    "metadata": {
        "file_type": ".py",
        "file_size_category": "unknown"
    }
}
```

## 配置选项

### 任务粒度控制
- **file**: 每个文件一个任务（默认）
- **batch**: 批量处理相似文件
- **module**: 按模块组织任务

### 并行任务支持
- **parallel_tasks**: true时生成可并发执行的任务
- 自动检测任务间独立性
- 优化执行效率

### 自定义优先级
```python
custom_priorities = {
    "core/main.py": "high",
    "utils/helper.py": "low",
    "config/settings.py": "high"
}
```

## 时间估算算法

### 基础时间模型
```python
def _estimate_duration(self, file_count: int, module_count: int, arch_count: int) -> str:
    """估计完成时间"""
    # 每个文件3分钟，每个模块5分钟，每个架构组件10分钟
    total_minutes = file_count * 3 + module_count * 5 + arch_count * 10 + 30  # 基础30分钟
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    return f"{hours} hours {minutes} minutes" if hours > 0 else f"{minutes} minutes"
```

### 阶段时间分配
- Phase 1: 固定5分钟
- Phase 2: 文件数 × 3分钟
- Phase 3: 模块数 × 5分钟 + 固定19分钟（总览+关系+依赖图）
- Phase 4: 固定47分钟（6个架构组件）
- Phase 5: 固定10分钟

## 性能特性
- **任务生成**: < 500ms for 100+ tasks
- **依赖图构建**: O(n) 线性复杂度
- **内存使用**: 每个任务约占用1KB
- **批量创建**: 支持批量任务管理器集成

## 使用示例

### MCP工具调用
```python
from src.mcp_tools.task_init import create_mcp_tool

# 创建工具实例
tool = create_mcp_tool()

# 执行任务初始化
arguments = {
    "project_path": "/path/to/project",
    "analysis_result": doc_guide_result,
    "task_granularity": "file",
    "parallel_tasks": False,
    "create_in_manager": True
}

result = tool.execute(arguments)
```

### 命令行测试
```bash
# 基本使用
python src/mcp_tools/task_init.py /path/to/project \
    --analysis-file analysis.json

# 创建任务到管理器
python src/mcp_tools/task_init.py /path/to/project \
    --analysis-file analysis.json \
    --granularity file \
    --create-tasks
```

### 集成使用流程
```python
# 完整工作流
from src.mcp_tools.doc_guide import create_mcp_tool as create_guide_tool
from src.mcp_tools.task_init import create_mcp_tool as create_init_tool

# 1. 项目分析
guide_tool = create_guide_tool()
analysis_result = guide_tool.execute({"project_path": project_path})

# 2. 生成任务计划
init_tool = create_init_tool()
task_plan = init_tool.execute({
    "project_path": project_path,
    "analysis_result": analysis_result["data"],
    "create_in_manager": True
})

print(f"生成了 {task_plan['data']['task_plan']['total_tasks']} 个任务")
print(f"预计耗时: {task_plan['data']['task_plan']['estimated_duration']}")
```

## 错误处理

### 输入验证
- **项目路径验证**: 检查路径存在性和访问权限
- **分析结果验证**: 验证必需字段完整性
- **参数类型验证**: 确保参数类型正确

### 异常处理
- **任务类型转换失败**: 跳过无效任务继续处理
- **依赖关系循环**: 自动检测并报告循环依赖
- **模板映射失败**: 使用默认模板或跳过

### 鲁棒性设计
- **部分失败容错**: 单个任务创建失败不影响整体
- **默认值填充**: 缺失参数使用合理默认值
- **日志记录**: 详细记录任务创建过程

