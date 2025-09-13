# doc_guide.py

## 文件概述
智能项目分析MCP工具实现，为AI提供深度的项目特征分析、文档生成策略建议和任务生成计划。作为Task Engine模块的核心分析组件，负责项目类型检测、框架识别、模块发现和智能文档策略制定。

## 核心类定义

### ProjectAnalyzer (项目分析器)
智能项目分析核心实现

#### 项目类型识别
```python
project_patterns = {
    "python": {
        "files": ["requirements.txt", "setup.py", "pyproject.toml"],
        "directories": ["src", "lib", "tests"],
        "extensions": [".py"]
    },
    "javascript": {
        "files": ["package.json", "package-lock.json"],
        "directories": ["node_modules", "src", "lib"],
        "extensions": [".js", ".jsx", ".ts", ".tsx"]
    }
    # ... 支持Python, JavaScript, Java, Go, Rust
}
```

#### 框架检测模式
```python
framework_patterns = {
    "django": ["django", "settings.py", "urls.py", "models.py"],
    "flask": ["flask", "app.py", "@app.route", "Flask(__name__)"],
    "fastapi": ["fastapi", "FastAPI", "@app.get", "@app.post"],
    "react": ["react", "jsx", "package.json", "src/App.js"],
    "spring": ["spring", "pom.xml", "@SpringBootApplication"]
    # ... 支持8+主流框架
}
```

#### 核心方法

**analyze_project(project_path: str, config: Dict[str, Any]) -> Dict[str, Any]**
- 执行综合项目分析
- 智能项目类型检测和框架识别
- 功能模块自动发现和分类
- 代码复杂度评估和关键文件识别
- 返回完整项目分析结果

**generate_documentation_strategy(analysis: Dict, focus_areas: List) -> Dict[str, Any]**
- 基于分析结果制定文档策略
- 确定推荐阶段执行顺序
- 设置优先级策略(sequential/top_down/bottom_up)
- 识别优先处理文件列表
- 估算文档模板数量需求

**generate_generation_plan(analysis: Dict, strategy: Dict) -> Dict[str, Any]**
- 生成5阶段详细执行计划
- Phase 1: 项目扫描任务
- Phase 2: 文件层文档生成(优先文件+关键文件)
- Phase 3: 模块层分析任务
- Phase 4: 架构层文档组件
- Phase 5: 项目层总结文档

### DocGuideTool (MCP工具类)
MCP doc_guide工具主要实现

#### 工具定义
```python
def get_tool_definition(self) -> Dict[str, Any]:
    return {
        "name": "doc_guide",
        "description": "智能分析项目特征，为AI提供文档生成策略和建议",
        "inputSchema": {
            "properties": {
                "project_path": {"type": "string"},
                "project_type": {"enum": ["auto", "python", "javascript", "java", "go", "rust"]},
                "analysis_depth": {"enum": ["basic", "detailed", "comprehensive"]},
                "ignore_patterns": {"type": "object"},
                "focus_areas": {"type": "array"}
            }
        }
    }
```

## 智能分析特性

### 项目类型检测
- **多维度评分**: 基于特征文件、目录结构、文件扩展名综合评分
- **智能权重**: 文件权重3分，目录权重2分，扩展名按数量计分
- **支持语言**: Python, JavaScript, Java, Go, Rust
- **自动回退**: 检测失败时返回"unknown"类型

### 框架智能识别
- **内容分析**: 读取关键配置文件内容进行模式匹配
- **多文件检测**: 检查requirements.txt, package.json, pom.xml等
- **源码扫描**: 分析前5个源码文件的前2000字符
- **框架覆盖**: Django, Flask, FastAPI, React, Vue, Spring, Gin, Express

### 功能模块发现
- **目录结构分析**: 基于目录名称自动识别功能模块
- **文件名模式匹配**: 识别Auth, Database, API, Config等常见模块
- **项目类型适配**: 针对不同项目类型的特定模块识别
- **智能过滤**: 排除技术性目录如src, lib, test等

### 代码复杂度评估
```python
def _assess_complexity(self, file_info: Dict[str, Any]) -> str:
    file_count = len(file_info["files"])
    dir_count = len(file_info["directory_structure"])
    
    if file_count < 10 and dir_count < 5:
        return "simple"
    elif file_count < 50 and dir_count < 15:
        return "medium"
    else:
        return "complex"
```

### 关键文件识别
- **类型特定优先级**: 每种项目类型定义关键文件模式
- **智能评分系统**: main/app文件10分，配置文件6分，业务文件4-5分
- **位置权重**: 根目录和src目录文件额外+2分
- **Top20排序**: 返回评分最高的前20个关键文件

## 文档策略生成

### 阶段执行策略
```python
# 简单项目: 自下而上
if complexity == "simple" and file_count < 20:
    recommended_phases = ["files_first", "modules_second", "architecture_third", "project_last"]
    priority_strategy = "sequential"

# 复杂项目: 自上而下  
elif complexity == "complex" or file_count > 100:
    recommended_phases = ["architecture_first", "modules_second", "files_third", "project_last"]
    priority_strategy = "top_down"
```

### 优先级调度
- **优先文件选择**: 取关键文件评分前10个
- **模板数量估算**: 文件层+模块层+架构层+项目层
- **复杂度适配**: 基于项目复杂度调整策略
- **焦点建议**: 针对不同关注领域提供具体建议

### 架构组件生成
```python
def _get_architecture_components(self, project_type: str) -> List[str]:
    base_components = ["system_overview", "tech_stack", "data_flow"]
    
    type_specific = {
        "python": ["deployment_architecture", "package_structure"],
        "javascript": ["build_process", "module_system"],
        "java": ["class_hierarchy", "spring_configuration"],
        "go": ["package_organization", "concurrency_model"]
    }
```

## 智能过滤系统

### 默认忽略模式
```python
default_ignore_files = ["*.md", "*.txt", "*.log", "*.tmp", "*.pyc", "*.class"]
default_ignore_dirs = ["__pycache__", ".git", "node_modules", ".idea", "venv", "env"]
```

### 灵活配置支持
- **自定义忽略**: 支持用户自定义文件和目录忽略模式
- **模式合并**: 用户配置与默认配置智能合并
- **路径匹配**: 支持通配符和多层目录匹配
- **性能优化**: 避免扫描大型无关目录

## 执行结果结构

### 项目分析结果
```json
{
    "project_type": "python",
    "main_framework": "flask",
    "identified_modules": ["Auth", "Database", "Api", "Config"],
    "code_complexity": "medium",
    "file_count": 25,
    "key_files": ["app.py", "config.py", "models.py"],
    "file_distribution": {".py": 20, ".json": 3, ".txt": 2},
    "directory_structure": ["src", "tests", "config"]
}
```

### 文档策略结果
```json
{
    "recommended_phases": ["files_first", "modules_second", "architecture_third", "project_last"],
    "priority_strategy": "sequential",
    "priority_files": ["app.py", "config.py", "models.py"],
    "estimated_templates": 41,
    "complexity_level": "medium",
    "focus_recommendations": ["关注技术栈选择和设计模式", "重点梳理核心业务模块的职责划分"]
}
```

### 生成计划结果
```json
{
    "phase_1_scan": ["project_scan_and_analysis"],
    "phase_2_files": ["app.py", "config.py", "models.py"],
    "phase_3_modules": ["module_auth", "module_database", "module_api"],
    "phase_4_architecture": ["system_overview", "tech_stack", "data_flow"],
    "phase_5_project": ["project_readme"],
    "estimated_duration": "2 hours 5 minutes"
}
```

## 性能特性
- **快速扫描**: 项目分析 < 2秒
- **内存优化**: 只读取必要文件内容前2000字符
- **智能缓存**: 避免重复文件系统操作
- **并发安全**: 支持多项目同时分析

## 使用示例

### MCP工具调用
```python
from src.mcp_tools.doc_guide import create_mcp_tool

# 创建工具实例
tool = create_mcp_tool()

# 执行分析
arguments = {
    "project_path": "/path/to/project",
    "project_type": "auto",
    "analysis_depth": "detailed",
    "focus_areas": ["architecture", "modules", "files", "project"]
}

result = tool.execute(arguments)
```

### 命令行测试
```bash
# 基本分析
python src/mcp_tools/doc_guide.py /path/to/project

# 指定参数
python src/mcp_tools/doc_guide.py /path/to/project \
    --type python \
    --depth comprehensive \
    --focus architecture modules
```

### 集成使用
```python
# 项目分析流程
analyzer = ProjectAnalyzer()
config = {"ignore_patterns": {"files": ["*.log"], "directories": [".cache"]}}

# 1. 分析项目
analysis = analyzer.analyze_project(project_path, config)

# 2. 生成策略
strategy = analyzer.generate_documentation_strategy(analysis, ["files", "modules"])

# 3. 制定计划
plan = analyzer.generate_generation_plan(analysis, strategy)

print(f"检测到 {analysis['project_type']} 项目")
print(f"推荐策略: {strategy['priority_strategy']}")
print(f"预计耗时: {plan['estimated_duration']}")
```

## 错误处理

### 异常类型
- **路径错误**: 项目路径不存在或无访问权限
- **编码错误**: 文件读取编码问题自动跳过
- **分析异常**: 项目结构异常时提供默认值
- **配置错误**: 无效配置参数时使用默认配置

### 鲁棒性设计
- **优雅降级**: 分析失败时返回基础结果
- **异常隔离**: 单个文件错误不影响整体分析
- **日志记录**: 详细记录分析过程和异常信息
- **默认值**: 所有分析结果都有合理默认值

## 版本信息
- **引入版本**: 0.6.0.0
- **文件路径**: src/mcp_tools/doc_guide.py
- **依赖模块**: services.file_service
- **最后更新**: 2025-09-13