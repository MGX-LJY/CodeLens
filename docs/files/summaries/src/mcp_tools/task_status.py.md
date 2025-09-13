# task_status.py

## 文件概述
智能任务状态监控MCP工具实现，提供全面的任务完成状态检查、阶段性进展管理和系统健康监控。作为Task Engine模块的核心监控组件，集成任务管理器、阶段控制器和状态跟踪器，实现多维度的状态监控和诊断。

## 核心类定义

### TaskStatusTool (MCP工具类)
task_status MCP工具主要实现

#### 工具定义
```python
def get_tool_definition(self) -> Dict[str, Any]:
    return {
        "name": "task_status",
        "description": "检查任务完成状态，管理阶段性进展",
        "inputSchema": {
            "properties": {
                "project_path": {"type": "string"},
                "check_type": {
                    "enum": ["current_task", "phase_progress", "overall_status", 
                            "next_actions", "health_check"],
                    "default": "overall_status"
                },
                "phase_filter": {
                    "enum": ["phase_1_scan", "phase_2_files", "phase_3_modules", 
                            "phase_4_architecture", "phase_5_project"]
                },
                "detailed_analysis": {"type": "boolean", "default": True},
                "include_recommendations": {"type": "boolean", "default": True},
                "task_id": {"type": "string"}
            }
        }
    }
```

## 5种检查类型详解

### 1. current_task (当前任务检查)
获取当前阶段的可执行任务信息

**功能**:
- 识别当前活跃阶段
- 获取下一个待执行任务
- 检查任务依赖满足情况
- 识别进行中的任务

**实现逻辑**:
```python
def _check_current_task(self, task_manager, phase_controller, phase_filter):
    current_phase = phase_controller.get_current_phase()
    target_phase = phase_filter or current_phase.value
    
    # 获取下一个可执行任务
    current_task = task_manager.get_next_task(target_phase)
    
    if not current_task:
        # 检查进行中的任务
        in_progress_tasks = [t for t in task_manager.tasks.values() 
                           if t.status == TaskStatus.IN_PROGRESS and t.phase == target_phase]
        
        if in_progress_tasks:
            current_task = in_progress_tasks[0]
            status = "in_progress"
        else:
            # 检查阶段是否完成
            phase_progress = task_manager.get_phase_progress(target_phase)
            status = "phase_complete" if phase_progress["can_proceed"] else "no_ready_tasks"
```

**返回结构**:
```json
{
    "current_phase": "phase_2_files",
    "status": "ready_to_execute",
    "current_task": {
        "id": "file_summary_123",
        "type": "file_summary",
        "description": "生成app.py文件摘要",
        "target_file": "app.py",
        "template_name": "file_summary",
        "output_path": "docs/files/summaries/app.py.md",
        "priority": "high",
        "estimated_time": "3 minutes",
        "dependencies_satisfied": true,
        "dependencies_count": 1
    }
}
```

### 2. phase_progress (阶段进度检查)
检查特定阶段或所有阶段的执行进度

**单阶段检查**:
```python
def _check_phase_progress(self, phase_controller, phase_filter, detailed):
    if phase_filter:
        try:
            phase = Phase(phase_filter)
            progress = phase_controller.get_phase_progress_detailed(phase)
            return {
                "phase_filter": phase_filter,
                "phase_progress": progress
            }
        except ValueError:
            return {"error": f"Invalid phase: {phase_filter}"}
```

**全阶段概览**:
```python
else:
    # 获取所有阶段概览
    overview = phase_controller.get_all_phases_overview()
    
    if detailed:
        return {
            "all_phases": True,
            "overview": overview
        }
    else:
        # 简化版本
        simplified = {
            "current_phase": overview["current_phase"],
            "overall_progress": overview["overall_progress"],
            "completed_phases": overview["completed_phases"],
            "total_phases": overview["total_phases"],
            "phase_status": {
                phase: info["status"] 
                for phase, info in overview["phases"].items()
            }
        }
```

**返回结构**:
```json
{
    "all_phases": true,
    "overview": {
        "current_phase": "phase_2_files",
        "overall_progress": 35.5,
        "completed_phases": 1,
        "total_phases": 5,
        "phases": {
            "phase_1_scan": {"status": "completed", "progress": 100.0},
            "phase_2_files": {"status": "in_progress", "progress": 40.0},
            "phase_3_modules": {"status": "not_started", "progress": 0.0}
        }
    }
}
```

### 3. overall_status (总体状态检查)
提供项目整体执行状态的综合视图

**基础统计**:
```python
def _check_overall_status(self, task_manager, phase_controller, state_tracker, detailed):
    # 获取基本统计
    overall_progress = task_manager.get_overall_progress()
    current_phase = phase_controller.get_current_phase()
    
    # 任务状态统计
    all_tasks = list(task_manager.tasks.values())
    task_stats = {
        "total": len(all_tasks),
        "completed": len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]),
        "in_progress": len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]),
        "pending": len([t for t in all_tasks if t.status == TaskStatus.PENDING]),
        "failed": len([t for t in all_tasks if t.status == TaskStatus.FAILED]),
        "blocked": len([t for t in all_tasks if t.status == TaskStatus.BLOCKED])
    }
```

**详细分析**:
```python
if detailed:
    # 添加详细信息
    current_status = state_tracker.get_current_status()
    result.update({
        "phase_overview": current_status["phase_overview"],
        "execution_statistics": current_status["execution_statistics"],
        "health_status": current_status["health_check"]
    })
```

**返回结构**:
```json
{
    "overall_progress": 45.2,
    "current_phase": "phase_2_files",
    "task_statistics": {
        "total": 42,
        "completed": 19,
        "in_progress": 2,
        "pending": 20,
        "failed": 1,
        "blocked": 0
    },
    "estimated_remaining": "1 hour 45 minutes",
    "phase_overview": {...},
    "execution_statistics": {...},
    "health_status": {...}
}
```

### 4. next_actions (下一步行动建议)
提供智能化的下一步执行建议

**行动建议生成**:
```python
def _get_next_actions(self, task_manager, phase_controller, include_recommendations):
    actions = []
    current_phase = phase_controller.get_current_phase()
    
    # 获取下一个任务
    next_task = task_manager.get_next_task(current_phase.value)
    if next_task:
        actions.append(f"执行任务: {next_task.description}")
        actions.append(f"使用命令: task_execute --task-id {next_task.id}")
    
    # 检查失败任务
    failed_tasks = task_manager.get_failed_tasks()
    if failed_tasks:
        actions.append(f"重试 {len(failed_tasks)} 个失败的任务")
    
    # 检查阻塞任务
    blocked_tasks = task_manager.get_blocked_tasks()
    if blocked_tasks:
        actions.append(f"解决 {len(blocked_tasks)} 个被阻塞任务的依赖问题")
```

**阶段转换检查**:
```python
# 阶段转换检查
can_proceed, message = phase_controller.can_proceed_to_next_phase(current_phase)
if can_proceed:
    next_phase = phase_controller.get_next_phase(current_phase)
    if next_phase:
        next_phase_info = phase_controller.phases_info[next_phase]
        actions.append(f"可以进入下一阶段: {next_phase_info.name}")
```

**返回结构**:
```json
{
    "current_phase": "phase_2_files",
    "next_actions": [
        "执行任务: 生成models.py文件摘要",
        "使用命令: task_execute --task-id file_summary_124",
        "重试 1 个失败的任务",
        "关注代码质量和一致性"
    ],
    "can_proceed_next_phase": false,
    "phase_transition_message": "还有15个任务未完成"
}
```

### 5. health_check (系统健康检查)
执行全面的系统健康状态检查和诊断

**基础健康检查**:
```python
def _perform_health_check(self, state_tracker, task_manager, phase_controller):
    current_status = state_tracker.get_current_status()
    health_check = current_status["health_check"]
    
    # 添加更多健康检查项
    issues = health_check["issues"].copy()
    warnings = health_check["warnings"].copy()
```

**任务分布检查**:
```python
# 检查任务分布
all_tasks = list(task_manager.tasks.values())
if len(all_tasks) == 0:
    issues.append("没有创建任何任务，请先运行task_init")

# 检查阶段平衡
phase_counts = {}
for task in all_tasks:
    phase_counts[task.phase] = phase_counts.get(task.phase, 0) + 1

if len(phase_counts) < 5:
    warnings.append(f"只有 {len(phase_counts)} 个阶段有任务，可能缺少某些阶段")
```

**依赖完整性检查**:
```python
# 检查依赖完整性
orphan_tasks = []
for task in all_tasks:
    for dep_id in task.dependencies:
        if not task_manager.get_task(dep_id):
            orphan_tasks.append(task.id)
            break

if orphan_tasks:
    issues.append(f"有 {len(orphan_tasks)} 个任务的依赖不存在")
```

**健康状态评估**:
```python
# 更新健康状态
if issues:
    overall_health = "poor"
elif warnings:
    overall_health = "warning"
else:
    overall_health = "good"
```

**返回结构**:
```json
{
    "overall_health": "warning",
    "issues": [],
    "warnings": [
        "只有 4 个阶段有任务，可能缺少某些阶段"
    ],
    "performance_metrics": {
        "average_task_time": "4.2 minutes",
        "success_rate": 94.5,
        "execution_efficiency": 89.2
    },
    "task_distribution": {
        "phase_1_scan": 1,
        "phase_2_files": 20,
        "phase_3_modules": 15,
        "phase_4_architecture": 6
    },
    "recommendations": [
        "关注警告信息以优化执行效果"
    ]
}
```

## 任务详情检查 (task_detail)
检查特定任务的详细信息和状态

**特定任务查询**:
```python
def _check_task_detail(self, task_manager, task_id):
    task = task_manager.get_task(task_id)
    if not task:
        return {"error": f"Task {task_id} not found"}
    
    # 检查依赖状态
    dependency_status = []
    for dep_id in task.dependencies:
        dep_task = task_manager.get_task(dep_id)
        if dep_task:
            dependency_status.append({
                "id": dep_id,
                "description": dep_task.description,
                "status": dep_task.status.value,
                "completed": dep_task.status == TaskStatus.COMPLETED
            })
        else:
            dependency_status.append({
                "id": dep_id,
                "status": "not_found",
                "completed": False
            })
    
    dependencies_satisfied = all(dep["completed"] for dep in dependency_status)
```

**返回结构**:
```json
{
    "task": {
        "id": "file_summary_123",
        "type": "file_summary",
        "description": "生成app.py文件摘要",
        "phase": "phase_2_files",
        "status": "pending",
        "target_file": "app.py",
        "template_name": "file_summary",
        "output_path": "docs/files/summaries/app.py.md",
        "priority": "high",
        "estimated_time": "3 minutes",
        "created_at": "2025-09-13T10:30:00Z",
        "started_at": null,
        "completed_at": null,
        "error_message": null,
        "metadata": {}
    },
    "dependencies": [
        {
            "id": "scan_123",
            "description": "扫描项目文件结构",
            "status": "completed",
            "completed": true
        }
    ],
    "dependencies_satisfied": true,
    "can_execute": true
}
```

## 智能算法

### 剩余时间估算
```python
def _estimate_remaining_time(self, task_manager, current_phase):
    """估计剩余时间"""
    remaining_tasks = [t for t in task_manager.tasks.values() 
                      if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]
    
    if not remaining_tasks:
        return "0 minutes"
    
    # 简单估算：每个任务平均5分钟
    estimated_minutes = len(remaining_tasks) * 5
    
    hours = estimated_minutes // 60
    minutes = estimated_minutes % 60
    
    return f"{hours} hours {minutes} minutes" if hours > 0 else f"{minutes} minutes"
```

### 健康建议生成
```python
def _get_health_recommendations(self, issues, warnings, task_manager):
    """获取健康建议"""
    recommendations = []
    
    if not task_manager.tasks:
        recommendations.append("运行task_init初始化任务")
    
    failed_tasks = task_manager.get_failed_tasks()
    if failed_tasks:
        recommendations.append("检查并重试失败的任务")
    
    if issues:
        recommendations.append("解决严重问题以确保系统正常运行")
    
    if warnings:
        recommendations.append("关注警告信息以优化执行效果")
    
    return recommendations
```

## 状态检查矩阵

### 任务状态分类
- **ready_to_execute**: 任务准备就绪，可以立即执行
- **in_progress**: 任务正在执行中
- **phase_complete**: 当前阶段已完成，可进入下一阶段
- **no_ready_tasks**: 当前阶段没有准备就绪的任务

### 健康状态分级
- **good**: 系统运行正常，无问题和警告
- **warning**: 存在警告项，需要关注但不影响执行
- **poor**: 存在严重问题，需要立即解决

### 阶段状态监控
- **not_started**: 阶段尚未开始
- **in_progress**: 阶段正在执行中
- **completed**: 阶段已完成
- **blocked**: 阶段被阻塞

## 性能特性
- **状态检查**: < 100ms
- **健康诊断**: < 200ms
- **依赖分析**: < 150ms
- **进度计算**: < 50ms
- **内存使用**: 检查过程约占用10MB

## 使用示例

### MCP工具调用
```python
from src.mcp_tools.task_status import create_mcp_tool

# 创建工具实例
tool = create_mcp_tool()

# 检查总体状态
arguments = {
    "project_path": "/path/to/project",
    "check_type": "overall_status",
    "detailed_analysis": True
}
result = tool.execute(arguments)

# 检查当前任务
arguments = {
    "project_path": "/path/to/project",
    "check_type": "current_task",
    "phase_filter": "phase_2_files"
}
result = tool.execute(arguments)

# 执行健康检查
arguments = {
    "project_path": "/path/to/project",
    "check_type": "health_check"
}
result = tool.execute(arguments)
```

### 命令行测试
```bash
# 检查总体状态
python src/mcp_tools/task_status.py /path/to/project \
    --type overall_status

# 检查阶段进度
python src/mcp_tools/task_status.py /path/to/project \
    --type phase_progress \
    --phase phase_2_files

# 获取下一步建议
python src/mcp_tools/task_status.py /path/to/project \
    --type next_actions

# 检查特定任务
python src/mcp_tools/task_status.py /path/to/project \
    --task-id file_summary_123

# 执行健康检查
python src/mcp_tools/task_status.py /path/to/project \
    --type health_check
```

### 监控工作流
```python
# 项目状态监控流程
from src.mcp_tools.task_status import TaskStatusTool

tool = TaskStatusTool()

# 1. 总体状态检查
overall_result = tool.execute({
    "project_path": "/path/to/project",
    "check_type": "overall_status"
})

print(f"总进度: {overall_result['data']['overall_progress']}%")
print(f"当前阶段: {overall_result['data']['current_phase']}")

# 2. 获取下一步行动
actions_result = tool.execute({
    "project_path": "/path/to/project",
    "check_type": "next_actions"
})

print("建议的下一步行动:")
for action in actions_result['data']['next_actions']:
    print(f"- {action}")

# 3. 健康检查
health_result = tool.execute({
    "project_path": "/path/to/project",
    "check_type": "health_check"
})

print(f"系统健康状态: {health_result['data']['overall_health']}")
if health_result['data']['issues']:
    print("发现问题:")
    for issue in health_result['data']['issues']:
        print(f"- {issue}")
```

## 监控报告示例

### 状态仪表板格式
```
=== CodeLens 项目状态报告 ===
项目路径: /path/to/project
检查时间: 2025-09-13 14:30:00

总体进度: ████████████░░░░░░░░ 45.2% (19/42)
当前阶段: Phase 2 - 文件层文档生成
预计剩余: 1 hour 45 minutes

阶段状态:
✓ Phase 1 - 项目扫描     [已完成] 100%
⚠ Phase 2 - 文件文档     [进行中]  40%
○ Phase 3 - 模块分析     [未开始]   0%
○ Phase 4 - 架构设计     [未开始]   0%
○ Phase 5 - 项目总结     [未开始]   0%

任务分布:
  已完成: 19    进行中: 2
  待处理: 20    失败: 1    阻塞: 0

下一步建议:
- 执行任务: 生成models.py文件摘要
- 使用命令: task_execute --task-id file_summary_124
- 重试 1 个失败的任务

系统健康: 警告 ⚠
- 只有 4 个阶段有任务，可能缺少某些阶段
```

## 错误处理

### 输入验证
- **项目路径验证**: 检查路径存在性和可访问性
- **检查类型验证**: 确保check_type在支持的枚举值内
- **阶段过滤验证**: 验证phase_filter的有效性
- **任务ID验证**: 检查task_id的存在性

### 异常处理
- **管理器初始化失败**: 提供详细错误信息
- **阶段枚举转换失败**: 处理无效阶段名称
- **任务状态查询失败**: 优雅处理任务不存在情况
- **健康检查异常**: 记录错误但不中断检查流程

### 数据一致性检查
- **任务依赖验证**: 检查依赖任务的存在性
- **阶段任务分布**: 验证各阶段任务的合理性
- **状态转换逻辑**: 确保状态转换的一致性
- **时间戳完整性**: 验证任务时间戳的逻辑关系

