"""
项目层模板 (Project Layer) - 8个模板  
项目整体文档和管理相关的模板
"""


class ProjectTemplates:
    """项目层文档模板集合"""
    
    # 1. 项目README模板（增强版）
    README_TEMPLATE = """# {project_name} - {project_subtitle}

## 项目概述
{project_overview}

## 核心特性
{core_features}

## 快速开始

### 1. 环境要求
{environment_requirements}

### 2. {step_2_name}
{step_2_content}

### 3. {step_3_name}
{step_3_content}

## 项目状态

**当前版本**: {current_version}

{project_status}

## 技术架构

{tech_architecture}

## 使用示例

{usage_examples}

## 开发路线图

{roadmap}

## 贡献指南

{contribution_guide}

## 许可证

{license}
"""
    
    # 2. 变更日志模板
    CHANGELOG_TEMPLATE = """# {project_name} 更新日志

{version_entries}
"""
    
    # 3. 发展路线模板
    ROADMAP_TEMPLATE = """# {project_name} 发展路线图

## 总体目标
{overall_goals}

## 版本规划

{version_planning}

## 长期愿景
{long_term_vision}

## 技术演进
{technology_evolution}

## 社区建设
{community_building}
"""
    




