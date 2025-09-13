"""
模块层模板 (Module Layer) - 6个模板
模块功能、关系和接口相关的文档模板
"""


class ModuleTemplates:
    """模块层文档模板集合"""
    
    # 1. 模块总览模板
    OVERVIEW_TEMPLATE = """# {project_name} 模块总览

## 识别的功能模块

基于{project_name} {version}架构分析，识别出以下主要功能模块：

{identified_modules}

## 模块详细信息

{module_details}

## 模块关系图谱

### 依赖关系
```
{dependency_graph}
```

### 详细依赖分析
{dependency_analysis}

### 数据流向
{data_flow}

## 核心接口汇总

{core_interfaces}

## 模块设计原则

{design_principles}
"""
    
    # 2. 模块关系模板
    RELATIONS_TEMPLATE = """# {project_name} 模块依赖关系分析

## 整体依赖架构

```
{overall_dependency_arch}
```

## 详细依赖关系

### 1. {layer_1_name}依赖
{layer_1_dependencies}

### 2. {layer_2_name}依赖
{layer_2_dependencies}

### 3. {layer_3_name}依赖
{layer_3_dependencies}

### 4. {layer_4_name}依赖
{layer_4_dependencies}

## 依赖注入模式

{dependency_injection}

## 循环依赖分析

{circular_dependency_analysis}

## 模块替换和扩展性

{module_extensibility}

## 测试依赖

{testing_dependencies}

## 部署依赖

{deployment_dependencies}

## 版本兼容性

{version_compatibility}
"""
    
    # 3. 依赖图谱模板
    DEPENDENCY_GRAPH_TEMPLATE = """# {project_name} 依赖图谱分析

## 依赖层次图

```
{dependency_hierarchy}
```

## 模块依赖矩阵

{dependency_matrix}

## 关键路径分析

{critical_path_analysis}

## 依赖风险评估

{dependency_risk_assessment}

## 依赖优化建议

{optimization_suggestions}
"""
    
    # 4. 模块主文档模板
    MODULE_README_TEMPLATE = """# {module_name} 模块

## 模块概述
{module_overview}

## 核心功能
{core_functions}

## 架构设计
{architecture_design}

## 主要组件
{main_components}

## API接口
{api_interfaces}

## 配置选项
{configuration_options}

## 使用示例
{usage_examples}

## 测试策略
{testing_strategy}

## 性能指标
{performance_metrics}

## 故障排除
{troubleshooting}
"""
    
    # 5. API接口模板
    API_TEMPLATE = """# {module_name} API 接口文档

## API概览
{api_overview}

## 核心接口

{core_apis}

## 数据模型

{data_models}

## 错误处理

{error_handling}

## 使用示例

{usage_examples}

## 性能考量

{performance_considerations}
"""
    
    # 6. 业务流程模板
    FLOW_TEMPLATE = """# {module_name} 业务流程

## 流程概述
{flow_overview}

## 主要业务流程

### 1. {flow_1_name}
{flow_1_description}

### 2. {flow_2_name}
{flow_2_description}

### 3. {flow_3_name}
{flow_3_description}

## 流程图

```
{flow_diagram}
```

## 异常处理流程
{exception_handling}

## 性能优化
{performance_optimization}
"""