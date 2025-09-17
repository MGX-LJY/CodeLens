# src/templates/document_templates.py - 文档模板服务

## 文件概述
CodeLens的核心模板服务文件，提供12个标准化文档模板，覆盖架构、文件、项目三个层次，并新增创造模式模板支持。

## 导入模块
```python
from ..logging import get_logger
from .templates import ArchitectureTemplates, FileTemplates, ProjectTemplates
```

## 全局变量
无全局变量，所有状态封装在类中。

## 核心常量
- **模板总数**: 12个（架构6个 + 文件1个 + 项目2个 + 创造模式3个）
- **支持层次**: 架构层、文件层、项目层、创造模式层

## 类汇总表

| 类名 | 功能 | 关键方法 | 模板数量 |
|------|------|----------|----------|
| `DocumentTemplates` | 向后兼容的模板集合 | 静态属性 | 3个 |
| `TemplateService` | 核心模板服务类 | get_template_list, get_template_content等 | 12个 |

## 详细功能分析

### DocumentTemplates类
**向后兼容层**:
```python
class DocumentTemplates:
    FILE_SUMMARY_TEMPLATE = FileTemplates.SUMMARY_TEMPLATE
    ARCHITECTURE_TEMPLATE = ArchitectureTemplates.OVERVIEW_TEMPLATE
    PROJECT_README_TEMPLATE = ProjectTemplates.README_TEMPLATE
```

### TemplateService类核心功能

#### 模板注册表架构
- **架构层模板 (6个)**:
  - `architecture`: 系统整体架构设计
  - `tech_stack`: 技术选型和架构原则
  - `data_flow`: 系统数据流转设计
  - `system_architecture`: 可视化架构图表
  - `component_diagram`: 组件关系和依赖
  - `deployment_diagram`: 部署架构和环境配置

- **文件层模板 (1个)**:
  - `file_summary`: 详细文件分析模板

- **项目层模板 (2个)**:
  - `project_readme`: 项目主文档
  - `changelog`: 变更记录

- **创造模式模板 (3个)**:
  - `create_requirement`: 功能需求确认
  - `create_analysis`: 功能实现分析
  - `create_todo`: 实现计划

## 模板详细分析

### 架构层模板特性
```python
{
    'name': 'architecture',
    'type': 'architecture_level',
    'layer': 'architecture',
    'file_path': '/docs/architecture/overview.md',
    'variables': ['project_name', 'project_overview', 'tech_stack', ...]
}
```

### 文件层模板特性
```python
{
    'name': 'file_summary',
    'type': 'file_level', 
    'layer': 'file',
    'file_path': '/docs/files/summaries/[file].md',
    'variables': ['filename', 'function_overview', 'imports', ...]
}
```

### 创造模式模板创新
新增的创造模式模板支持：
1. **需求确认阶段**: 用户需求理解和确认
2. **分析阶段**: 架构影响和实现方案分析  
3. **计划阶段**: 详细实现步骤规划

## 数据流分析

### 模板获取流程
```
客户端请求 → get_template_list() → 返回模板元数据 → get_template_content() → 返回具体模板
```

### 模板变量处理
```
模板内容 + 变量值 → 变量替换 → 生成最终文档
```

## 日志集成
```python
self.logger = get_logger(component="TemplateService", operation="init")
self.logger.info("TemplateService 初始化完成", {
    "template_count": len(self.template_registry),
    "architecture_templates": 6,
    "file_templates": 1, 
    "project_templates": 5,
    "create_mode_templates": 3
})
```

## 错误处理机制
- 日志系统不可用时的DummyLogger回退
- 模板加载失败的异常处理
- 变量验证和默认值处理

## 性能优化考虑
- 模板内容预加载到内存
- 模板注册表字典查找O(1)复杂度
- 延迟加载三层架构模板类

## 扩展性评估
**高扩展性**:
- 新模板层次可以轻松添加
- 模板变量系统灵活
- 三层架构清晰分离

## 代码质量评估
**优秀**:
- 清晰的类层次结构
- 完整的模板元数据
- 良好的向后兼容性
- 统一的命名规范

## 文档完整性
**完整**: 包含详细的模板描述、变量列表和文件路径规范

## 模板系统架构优势

### 三层清晰分离
1. **架构层**: 系统设计和技术架构
2. **文件层**: 代码文件详细分析
3. **项目层**: 项目整体文档

### 创造模式支持
新增的功能开发生命周期模板：
- 需求 → 分析 → 计划 → 实现

## 注意事项
- 模板变量使用`{variable_name}`格式
- 文件路径支持动态变量如`[file]`
- 创造模式模板需要特定的数据结构
- 向后兼容性通过DocumentTemplates类维护