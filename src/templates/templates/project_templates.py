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
    
    # 4. 贡献指南模板
    CONTRIBUTING_TEMPLATE = """# {project_name} 贡献指南

## 如何贡献

{how_to_contribute}

## 开发环境设置

{development_setup}

## 代码规范

{coding_standards}

## 提交规范

{commit_standards}

## 测试要求

{testing_requirements}

## 审查流程

{review_process}

## 社区准则

{community_guidelines}
"""
    
    # 5. API参考模板
    API_REFERENCE_TEMPLATE = """# {project_name} API参考

## API概览
{api_overview}

## 认证
{authentication}

## 端点列表

{endpoints}

## 数据模型

{data_models}

## 错误代码

{error_codes}

## 使用限制

{rate_limits}

## SDK和工具

{sdks_tools}
"""
    
    # 6. 故障排除模板
    TROUBLESHOOTING_TEMPLATE = """# {project_name} 故障排除指南

## 常见问题

{common_issues}

## 错误代码解释

{error_codes}

## 调试技巧

{debugging_tips}

## 性能问题

{performance_issues}

## 配置问题

{configuration_issues}

## 获取帮助

{getting_help}
"""
    
    # 7. 性能报告模板
    PERFORMANCE_TEMPLATE = """# {project_name} 性能报告

## 性能概览
{performance_overview}

## 基准测试

{benchmark_results}

## 性能优化

{performance_optimizations}

## 监控指标

{monitoring_metrics}

## 扩展性分析

{scalability_analysis}

## 优化建议

{optimization_recommendations}
"""
    
    # 8. 版本记录模板
    VERSION_RECORD_TEMPLATE = """# 版本 {version_number}

## 发布信息

**发布日期**: {release_date}
**版本类型**: {version_type}
**重要程度**: {importance_level}

## 主要变更

{major_changes}

## 新增功能

{new_features}

## 改进优化

{improvements}

## 问题修复

{bug_fixes}

## 破坏性变更

{breaking_changes}

## 升级指南

{upgrade_guide}

## 已知问题

{known_issues}
"""