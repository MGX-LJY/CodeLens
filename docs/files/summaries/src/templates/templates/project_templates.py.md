# src/templates/templates/project_templates.py - 项目层模板集合

## 文件概述
CodeLens三层架构模板系统的项目层模板文件，提供5个项目整体文档和管理相关的模板，包括传统的README和变更日志，以及创造模式的三阶段模板。

## 导入模块
无外部依赖，纯模板定义文件。

## 全局变量
无全局变量，所有模板封装在类中。

## 核心常量
- **模板总数**: 5个
- **传统模板**: 2个（README + CHANGELOG）
- **创造模式模板**: 3个（需求确认 + 实现分析 + TODO计划）

## 类汇总表

| 类名 | 功能 | 模板数量 | 特性 |
|------|------|----------|------|
| `ProjectTemplates` | 项目层文档模板集合 | 5个 | 传统+创造模式 |

## 详细模板分析

### 1. README_TEMPLATE - 项目主文档模板
**目标文档**: `/docs/project/README.md`

#### 核心结构
```markdown
# {project_name} - {project_subtitle}
## 项目概述
## 核心特性  
## 快速开始
## 项目状态
## 技术架构
## 使用示例
## 开发路线图
## 贡献指南
## 许可证
```

#### 关键变量
- `project_name`: 项目名称
- `project_subtitle`: 项目副标题
- `project_overview`: 项目概述
- `core_features`: 核心特性列表
- `environment_requirements`: 环境要求
- `step_2_name`, `step_2_content`: 自定义安装步骤
- `current_version`: 当前版本
- `tech_architecture`: 技术架构描述
- `usage_examples`: 使用示例
- `roadmap`: 开发路线图

### 2. CHANGELOG_TEMPLATE - 变更日志模板
**目标文档**: `/docs/project/CHANGELOG.md`

#### 核心结构
```markdown
# {project_name} 更新日志
{version_entries}
```

#### 特点
- 简洁的版本记录格式
- 支持动态版本条目
- 标准化变更记录

### 3. REQUIREMENT_TEMPLATE - 需求确认模板（创造模式第一阶段）
**目标文档**: `/docs/project/create/requirements/[requirement_id].md`

#### 核心结构
```markdown
# 功能需求确认文档
## 基本信息
## 用户描述  
## AI理解和分析
## 用户确认和修正
```

#### 创新特性
- **交互式需求确认**: 用户描述 → AI理解 → 用户修正
- **结构化需求记录**: requirement_id, requirement_type等
- **标准化字段**: feature_name, created_time, creator等

#### 关键变量
- `requirement_id`: 唯一需求标识
- `user_description`: 用户原始描述
- `ai_description`: AI理解和分析
- `user_revision`: 用户确认和修正
- `requirement_type`: 需求类型（new_feature, enhancement, fix）

### 4. ANALYSIS_TEMPLATE - 实现分析模板（创造模式第二阶段）
**目标文档**: `/docs/project/create/analysis/[analysis_id].md`

#### 核心结构
```markdown
# 功能实现分析报告
## 基本信息
## 架构分析
### 系统架构影响
```

#### 分析维度
- **架构影响评估**: 对现有系统的影响分析
- **实现方案设计**: 技术实现路径
- **风险评估**: 潜在风险和解决方案
- **依赖分析**: 与现有组件的依赖关系

#### 关键变量
- `analysis_id`: 唯一分析标识
- `requirement_id`: 关联的需求ID
- `architecture_impact`: 架构影响分析
- `implementation_approach`: 实现方法
- `risk_assessment`: 风险评估

### 5. TODO_TEMPLATE - 实现计划模板（创造模式第三阶段）
**开发中模板**，用于生成详细的实现步骤和任务分解。

## 创造模式工作流程

### 三阶段渐进式开发
```
阶段1: 需求确认 → REQUIREMENT_TEMPLATE
     ↓
阶段2: 分析实现 → ANALYSIS_TEMPLATE  
     ↓
阶段3: 生成计划 → TODO_TEMPLATE
```

### 文件组织结构
```
/docs/project/create/
├── requirements/
│   └── [requirement_id].md
├── analysis/
│   └── [analysis_id].md
└── todos/
    └── [todo_id].md
```

## 模板变量系统

### 基础信息变量
- `feature_name`: 功能名称
- `created_time`: 创建时间
- `creator`: 创建者
- `project_name`: 项目名称

### 内容变量
- 描述性变量：`*_description`, `*_overview`
- 结构化变量：`*_requirements`, `*_criteria`  
- 分析变量：`*_impact`, `*_assessment`

### 动态变量
- `version_entries`: 支持多版本记录
- `[file]`: 文件路径占位符
- `[id]`: 唯一标识占位符

## 模板设计原则

### 标准化结构
- 统一的Markdown格式
- 一致的变量命名规范
- 标准化的文档头部信息

### 灵活性支持
- 可扩展的变量系统
- 动态内容插入
- 条件性章节显示

### 用户体验优化
- 清晰的章节划分
- 直观的信息层次
- 易于理解的模板结构

## 使用场景

### 传统文档生成
- 项目初始化时生成README
- 版本发布时更新CHANGELOG
- 项目维护期间更新文档

### 创造模式开发
- 新功能开发前的需求确认
- 技术方案设计和评估
- 开发计划制定和跟踪

## 扩展性评估
**高扩展性**:
- 模板变量易于扩展
- 支持自定义章节结构
- 可适配不同项目类型

## 代码质量评估
**优秀**:
- 清晰的模板结构
- 标准化的变量命名
- 完整的文档覆盖

## 文档完整性
**完整**: 覆盖项目文档的主要需求，支持传统和创新开发模式

## 注意事项
- 模板变量使用`{variable_name}`格式
- 创造模式模板需要配合相应的MCP工具使用
- 文件路径中的`[placeholder]`需要运行时替换
- **创造模式模板是CodeLens的创新特性**，支持AI辅助的功能开发流程