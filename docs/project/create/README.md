# CodeLens 创造模式文档

这个目录包含CodeLens创造模式的三阶段功能开发文档。

## 目录结构

```
docs/project/create/
├── README.md              # 本说明文档
├── requirements/          # 第一阶段：需求确认文档
├── analysis/             # 第二阶段：分析实现文档
└── todos/                # 第三阶段：实现计划文档
```

## 创造模式工作流程

### 🚀 阶段1：需求确认 (Requirements)
- **目标**: 交互式功能需求分析和验收标准确认
- **工具**: `create_requirement`
- **输出**: `/requirements/req_[feature]_[timestamp].md`

### 🔍 阶段2：分析实现 (Analysis)  
- **目标**: 基于架构文档分析实现方案和影响链
- **工具**: `create_analysis`
- **输出**: `/analysis/analysis_[req_id]_[timestamp].md`

### 📋 阶段3：生成计划 (Todos)
- **目标**: 基于确认的分析报告生成详细实现计划
- **工具**: `create_todo`
- **输出**: `/todos/todo_[analysis_id]_[timestamp].md`

## 使用方法

### 通过MCP工具使用

```python
# 1. 开始创造模式
await call_tool("create_guide", {"project_path": "/path/to/project"})

# 2. 阶段1：创建需求
await call_tool("create_requirement", {
    "project_path": "/path/to/project",
    "mode": "create", 
    "feature_name": "新功能名称"
})

# 3. 阶段2：分析实现
await call_tool("create_analysis", {
    "project_path": "/path/to/project",
    "mode": "create",
    "requirement_id": "req_功能_1234567890"
})

# 4. 阶段3：生成计划
await call_tool("create_todo", {
    "project_path": "/path/to/project", 
    "mode": "create",
    "analysis_id": "analysis_req_功能_1234567890_9876543210"
})
```

### 通过命令行使用

```bash
# 1. 查看创造模式指导
python src/mcp_tools/create_guide.py /path/to/project

# 2. 阶段1：创建需求
python src/mcp_tools/create_requirement.py /path/to/project --feature-name "新功能"

# 3. 阶段2：分析实现 
python src/mcp_tools/create_analysis.py /path/to/project --requirement-id req_xxx

# 4. 阶段3：生成计划
python src/mcp_tools/create_todo.py /path/to/project --analysis-id analysis_xxx
```

## 文档模板

创造模式使用以下3个专用模板：

1. **create_requirement**: 需求确认模板
2. **create_analysis**: 分析实现模板  
3. **create_todo**: 实现计划模板

这些模板已集成到CodeLens的模板系统中，支持变量替换和格式化。