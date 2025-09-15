# CodeLens工作流程重新设计

## 🎯 正确的设计理念

**核心原则**：`task_execute → AI手动生成 → 验证文件 → 自动完成`

### 为什么AI手动生成是正确的？

1. **质量保证**：AI能根据上下文生成更高质量、更符合项目特色的文档
2. **灵活性**：AI可以根据不同项目类型调整文档风格和重点
3. **智能化**：AI能理解代码逻辑，生成更准确的分析
4. **可控性**：保持人工智能在文档生成中的主导作用

## 🔍 当前断点问题分析

### 问题1：AI收到信息后不知道做什么

**当前状态**：
```json
{
  "success": true,
  "tool": "task_execute", 
  "data": {
    "template_info": {...},
    "execution_context": {...},
    "instructions": "Use the provided template and context to generate the documentation. Call task_complete when finished."
  }
}
```

**问题所在**：
- ✅ 提供了模板和上下文
- ❌ 指令模糊："Use the provided template"
- ❌ 没有明确的保存路径指令
- ❌ 没有提供保存工具
- ❌ `task_complete`工具不存在

### 问题2：缺少文档生成工具链

**当前工具链**：
- `task_execute` ✅ 提供信息
- `Write` ✅ 写入文件 (但AI不知道要用)
- `task_complete` ❌ 不存在

**缺失环节**：
- 明确的"生成并保存文档"指令
- 任务完成验证工具
- 自动完成机制

### 问题3：任务完成标准错误

**当前逻辑**：
```python
# task_execute.py
self.task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
# ❌ 设置为进行中后就没有后续验证
```

**应该的逻辑**：
```python
# 1. 设置为进行中
# 2. AI生成文档
# 3. 验证文件存在
# 4. 设置为完成
```

## 🛠️ 重新设计方案

### 方案1：增强task_execute的指令清晰度

#### 1.1 明确的指令格式

```python
# task_execute.py 输出改进
return {
    "success": True,
    "tool": "task_execute",
    "data": {
        # ... 现有数据 ...
    },
    "action_required": {
        "type": "generate_document",
        "task_id": task_id,
        "output_path": output_path,
        "template": template_content,
        "context": context_data,
        "instructions": [
            "1. 根据提供的模板和文件内容生成详细的文档",
            "2. 使用Write工具将文档保存到指定路径",
            "3. 使用TaskComplete工具标记任务完成",
            "4. 确保生成的文档包含所有必需章节"
        ]
    },
    "next_steps": {
        "step_1": f"使用Write工具保存文档到: {output_path}",
        "step_2": f"使用TaskComplete工具完成任务: {task_id}",
        "required_tools": ["Write", "TaskComplete"]
    }
}
```

#### 1.2 模板变量预填充

```python
def _prepare_template_with_context(self, template: str, context: Dict) -> str:
    """预填充模板变量，减少AI工作量"""
    
    # 自动分析文件内容
    if context.get("file_context"):
        file_content = context["file_context"]["content"]
        auto_analysis = self._auto_analyze_file(file_content)
        
        # 预填充基础变量
        template = template.replace("{filename}", context["file_context"]["metadata"]["name"])
        template = template.replace("{imports}", auto_analysis["imports"])
        template = template.replace("{function_summary_table}", auto_analysis["functions"])
        
    return template

def _auto_analyze_file(self, content: str) -> Dict[str, str]:
    """自动分析文件，生成基础信息"""
    import ast
    
    analysis = {}
    
    try:
        tree = ast.parse(content)
        
        # 提取导入
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"- `{alias.name}`")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"- `from {module} import {alias.name}`")
        
        analysis["imports"] = "\n".join(imports) if imports else "无导入语句"
        
        # 提取函数
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args_count = len(node.args.args)
                docstring = ast.get_docstring(node) or "无文档"
                functions.append(f"| `{node.name}()` | {args_count} | {docstring[:50]}... |")
        
        if functions:
            analysis["functions"] = "| 函数名 | 参数数量 | 描述 |\n|--------|----------|------|\n" + "\n".join(functions)
        else:
            analysis["functions"] = "该文件中无函数定义"
            
    except Exception:
        analysis = {
            "imports": "无法解析导入语句",
            "functions": "无法解析函数列表"
        }
    
    return analysis
```

### 方案2：添加TaskComplete工具

#### 2.1 创建任务完成工具

```python
# 新文件：src/mcp_tools/task_complete.py

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
            return {"success": False, "error": "Missing required parameters"}
        
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
                from src.task_engine.state_tracker import StateTracker
                state_tracker = StateTracker(project_path, task_manager, None)
                state_tracker.record_task_event("completed", task_id)
                
                return {
                    "success": True,
                    "message": f"Task {task_id} completed successfully",
                    "output_file": str(expected_output),
                    "verification": verification_result
                }
            else:
                return {
                    "success": False, 
                    "error": "Task output verification failed",
                    "issues": verification_result["issues"],
                    "expected_path": str(expected_output)
                }
                
        except Exception as e:
            self.logger.error(f"Task completion failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _verify_task_output(self, output_path: Path, task_type: str) -> Dict[str, Any]:
        """验证任务输出文件"""
        
        result = {
            "valid": False,
            "issues": [],
            "file_size": 0,
            "content_checks": {}
        }
        
        # 检查文件存在
        if not output_path.exists():
            result["issues"].append("输出文件不存在")
            return result
        
        # 检查文件大小
        file_size = output_path.stat().st_size
        result["file_size"] = file_size
        
        if file_size < 100:
            result["issues"].append(f"文件过小 ({file_size} bytes)")
            return result
        
        # 检查内容质量
        try:
            content = output_path.read_text(encoding='utf-8')
            content_checks = self._check_content_quality(content, task_type)
            result["content_checks"] = content_checks
            
            if not content_checks["valid"]:
                result["issues"].extend(content_checks["issues"])
                return result
                
        except Exception as e:
            result["issues"].append(f"文件读取失败: {str(e)}")
            return result
        
        result["valid"] = True
        return result
    
    def _check_content_quality(self, content: str, task_type: str) -> Dict[str, Any]:
        """检查内容质量"""
        
        quality_standards = {
            "file_summary": {
                "min_length": 500,
                "required_sections": [
                    "# 文件分析报告",
                    "## 文件概述", 
                    "## 代码结构分析",
                    "## 函数详细分析"
                ],
                "forbidden_content": [
                    "TODO", "PLACEHOLDER", "待填写", "{", "}"
                ]
            },
            "architecture": {
                "min_length": 800,
                "required_sections": [
                    "# 系统架构",
                    "## 架构概述",
                    "## 技术栈"
                ],
                "forbidden_content": [
                    "TODO", "PLACEHOLDER", "待填写"
                ]
            }
        }
        
        result = {
            "valid": True,
            "issues": [],
            "length": len(content),
            "sections_found": [],
            "quality_score": 0
        }
        
        if task_type not in quality_standards:
            # 对于未定义标准的任务类型，只进行基础检查
            if len(content) < 200:
                result["valid"] = False
                result["issues"].append("内容过短")
            return result
        
        standard = quality_standards[task_type]
        
        # 长度检查
        if len(content) < standard["min_length"]:
            result["valid"] = False
            result["issues"].append(f"内容过短 (需要至少{standard['min_length']}字符)")
        
        # 必需章节检查
        missing_sections = []
        for section in standard["required_sections"]:
            if section in content:
                result["sections_found"].append(section)
            else:
                missing_sections.append(section)
        
        if missing_sections:
            result["valid"] = False
            result["issues"].append(f"缺少必需章节: {', '.join(missing_sections)}")
        
        # 禁止内容检查
        forbidden_found = []
        for forbidden in standard["forbidden_content"]:
            if forbidden in content:
                forbidden_found.append(forbidden)
        
        if forbidden_found:
            result["valid"] = False
            result["issues"].append(f"包含未完成内容: {', '.join(forbidden_found)}")
        
        # 计算质量分数
        quality_score = 0
        quality_score += min(100, len(content) / standard["min_length"] * 50)  # 长度分数
        quality_score += len(result["sections_found"]) / len(standard["required_sections"]) * 30  # 章节分数
        quality_score += (1 - len(forbidden_found) / len(standard["forbidden_content"])) * 20 if forbidden_found else 20  # 完整性分数
        
        result["quality_score"] = int(quality_score)
        
        return result
```

#### 2.2 将TaskComplete工具注册到MCP

```python
# mcp_server.py 中添加
@server.call_tool()
async def task_complete(arguments: dict) -> str:
    """完成任务并验证输出"""
    from src.mcp_tools.task_complete import TaskCompleteTool
    
    tool = TaskCompleteTool()
    result = tool.execute(arguments)
    return json.dumps(result, ensure_ascii=False, indent=2)
```

### 方案3：改进AI工作流程指导

#### 3.1 清晰的步骤指导

```python
# 在task_execute.py的返回中添加
"workflow_guide": {
    "current_step": "document_generation",
    "instructions": [
        "🎯 您的任务：根据提供的模板和文件内容生成app.py的详细分析文档",
        "",
        "📋 具体步骤：",
        "1. 仔细阅读提供的文件内容（147行Python代码）",
        "2. 根据file_summary模板结构组织文档内容",
        "3. 分析代码中的类、函数、导入等结构",
        "4. 使用Write工具保存文档到: docs/files/summaries/app.py.md",
        "5. 使用TaskComplete工具完成任务验证",
        "",
        "⚠️  重要要求：",
        "- 文档必须包含所有模板章节",
        "- 内容不能包含TODO、PLACEHOLDER等占位符",
        "- 确保分析准确且详细",
        "- 必须保存到指定路径"
    ]
}
```

#### 3.2 示例驱动指导

```python
"example_workflow": {
    "description": "参考示例：如何生成文档",
    "steps": [
        {
            "step": 1,
            "action": "分析文件",
            "details": "识别app.py中的ConfigChangeHandler类和main()函数"
        },
        {
            "step": 2, 
            "action": "填充模板",
            "example": "将分析结果填入file_summary模板的各个变量中"
        },
        {
            "step": 3,
            "action": "保存文档",
            "tool": "Write",
            "parameters": {
                "file_path": "/Users/martinezdavid/Documents/MG/code/wechat-automation-project/docs/files/summaries/app.py.md",
                "content": "完整的分析报告内容"
            }
        },
        {
            "step": 4,
            "action": "完成任务",
            "tool": "TaskComplete", 
            "parameters": {
                "project_path": "/Users/martinezdavid/Documents/MG/code/wechat-automation-project",
                "task_id": "file_summary_1757903570898_0"
            }
        }
    ]
}
```

### 方案4：错误处理和恢复机制

#### 4.1 任务状态恢复

```python
# 添加任务重置功能
class TaskReset:
    def reset_failed_task(self, project_path: str, task_id: str) -> Dict[str, Any]:
        """重置失败的任务"""
        task_manager = TaskManager(project_path)
        task = task_manager.get_task(task_id)
        
        if task and task.status in [TaskStatus.FAILED, TaskStatus.IN_PROGRESS]:
            # 重置为pending状态
            task_manager.update_task_status(task_id, TaskStatus.PENDING)
            
            # 清理可能存在的不完整文件
            output_path = Path(project_path) / task.output_path
            if output_path.exists() and output_path.stat().st_size < 100:
                output_path.unlink()
            
            return {"success": True, "message": f"Task {task_id} reset to pending"}
        
        return {"success": False, "error": "Task not found or not in resettable state"}
```

## 🚀 完整工作流程示例

### 理想的执行流程

```bash
# 1. 获取任务信息和指导
python src/mcp_tools/task_execute.py /path/to/project --task-id file_summary_xxx

# 2. AI收到完整信息，包括：
#    - 文件内容
#    - 模板结构  
#    - 明确指令
#    - 保存路径
#    - 完成工具

# 3. AI执行文档生成流程：
#    - 分析文件内容
#    - 根据模板生成文档
#    - 使用Write工具保存
#    - 使用TaskComplete工具完成

# 4. 系统自动验证和完成任务
```

### AI收到的完整信息结构

```json
{
  "task_info": {...},
  "template": "完整的file_summary模板",
  "file_content": "app.py的完整源代码",
  "action_required": {
    "type": "generate_document",
    "clear_instructions": ["详细的步骤指导"],
    "required_tools": ["Write", "TaskComplete"],
    "output_path": "明确的保存路径"
  },
  "workflow_guide": {
    "step_by_step": ["具体操作步骤"],
    "quality_requirements": ["质量标准"],
    "examples": ["参考示例"]
  }
}
```

## 📊 改进效果对比

| 方面 | 当前状态 | 改进后状态 |
|------|----------|------------|
| 指令清晰度 | 模糊 | 明确具体 |
| 工具完整性 | 缺失TaskComplete | 完整工具链 |
| 验证机制 | 无 | 多层验证 |
| 错误处理 | 无 | 完整恢复机制 |
| 质量保证 | 无标准 | 明确质量标准 |

通过这个重新设计，我们保持了"AI手动生成"的灵活性和高质量，同时确保了完整的执行闭环和可靠的验证机制。