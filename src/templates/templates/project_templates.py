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

    # 3. 创造模式：需求确认模板（简化版）
    REQUIREMENT_TEMPLATE = """# 功能需求确认文档

## 基本信息
- **功能名称**: {feature_name}
- **需求ID**: {requirement_id}
- **创建时间**: {created_time}
- **创建者**: {creator}
- **项目**: {project_name}
- **需求类型**: {requirement_type}

## 用户描述
{user_description}

## AI理解和分析
{ai_description}

## 用户确认和修正
{user_revision}

---
*该文档用于确认功能需求，是创造模式第一阶段的输出。下一阶段将基于这个描述阅读相关代码并生成设计文档。*
"""

    # 4. 创造模式：分析实现模板
    ANALYSIS_TEMPLATE = """# 功能实现分析报告

## 基本信息
- **功能名称**: {feature_name}
- **需求ID**: {requirement_id}
- **分析ID**: {analysis_id}
- **分析时间**: {analysis_time}
- **分析者**: {analyzer}

## 架构分析

### 系统架构影响
{architecture_impact}

### 现有组件分析
{existing_components}

### 新增组件设计
{new_components}

## 代码实现分析

### 主要修改文件
{main_files_to_modify}

### 核心函数/类
{core_functions_classes}

### 数据结构变更
{data_structure_changes}

## 影响链分析

### 直接影响的文件
{directly_affected_files}

### 间接影响的文件
{indirectly_affected_files}

### 依赖关系变更
{dependency_changes}

### 接口变更影响
{interface_impact}

## 实现方案

### 技术选型
{technology_choices}

### 实现步骤
{implementation_steps}

### 关键技术点
{key_technical_points}

### 潜在风险点
{potential_risks}

## 测试策略

### 单元测试
{unit_test_strategy}

### 集成测试
{integration_test_strategy}

### 回归测试
{regression_test_strategy}

## 性能影响评估

### 性能影响点
{performance_impact}

### 优化建议
{optimization_suggestions}

## 兼容性分析

### 向后兼容性
{backward_compatibility}

### API兼容性
{api_compatibility}

## 部署考虑

### 部署影响
{deployment_impact}

### 配置变更
{configuration_changes}

### 数据迁移
{data_migration}

## 建议和结论

### 实现建议
{implementation_recommendations}

### 风险规避
{risk_mitigation}

### 下一步行动
{next_actions}

## 等待确认事项
{pending_confirmations}

---
*该文档用于分析功能实现方案，是创造模式第二阶段的输出，需要用户确认后进入第三阶段*
"""

    # 5. 创造模式：Todo实现计划模板
    TODO_TEMPLATE = """# 功能实现计划 (Todo)

## 基本信息
- **功能名称**: {feature_name}
- **需求ID**: {requirement_id}
- **分析ID**: {analysis_id}
- **计划ID**: {todo_id}
- **计划时间**: {plan_time}
- **计划者**: {planner}

## 实现概览

### 总体策略
{overall_strategy}

### 实现阶段
{implementation_phases}

### 预估工时
{estimated_time}

## 详细实现步骤

### 第一阶段：环境准备
{phase_1_preparation}

### 第二阶段：核心实现
{phase_2_core_implementation}

### 第三阶段：集成测试
{phase_3_integration_testing}

### 第四阶段：文档更新
{phase_4_documentation}

## 文件修改清单

### 新建文件
{new_files}

### 修改文件
{modified_files}

### 删除文件
{deleted_files}

## 函数/类实现清单

### 新建函数/类
{new_functions_classes}

### 修改函数/类
{modified_functions_classes}

### 删除函数/类
{deleted_functions_classes}

## 测试计划

### 单元测试任务
{unit_test_tasks}

### 集成测试任务
{integration_test_tasks}

### 手动测试任务
{manual_test_tasks}

## 验证检查点

### 功能验证
{function_verification}

### 性能验证
{performance_verification}

### 兼容性验证
{compatibility_verification}

## 风险控制

### 关键风险点
{critical_risks}

### 风险应对措施
{risk_responses}

### 回滚计划
{rollback_plan}

## 依赖事项

### 外部依赖
{external_dependencies}

### 内部依赖
{internal_dependencies}

### 资源需求
{resource_requirements}

## 完成标准

### 功能完成标准
{completion_criteria}

### 质量门禁
{quality_gates}

### 交付物清单
{deliverables}

## 实施时间表

### 里程碑计划
{milestone_schedule}

### 关键节点
{key_milestones}

### 交付时间
{delivery_timeline}

## 备注
{implementation_notes}

---
*该文档是功能实现的详细执行计划，是创造模式第三阶段的输出，可直接用于指导开发实施*
"""
