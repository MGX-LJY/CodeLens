"""
架构层模板 (Architecture Layer) - 7个模板
系统整体架构设计相关的文档模板
"""


class ArchitectureTemplates:
    """架构层文档模板集合"""
    
    # 1. 架构概述模板
    OVERVIEW_TEMPLATE = """# {project_name} 系统架构概述

## 项目概况
{project_overview}

## 技术栈分析

### 核心技术栈
{tech_stack}

## 架构模式
{architecture_pattern}

### 1. 服务层 (Services Layer)
{services_layer}

### 2. MCP接口层 (MCP Interface Layer)  
{mcp_interface_layer}

### 3. 协作流程层 (Collaboration Layer)
{collaboration_layer}

## 核心组件
{core_components}

## 数据流设计
{data_flow}

## 系统边界和约束
{system_boundaries}

## 部署架构
{deployment_architecture}
"""
    
    # 2. 技术栈模板
    TECH_STACK_TEMPLATE = """# {project_name} 技术栈

## 核心技术

### 编程语言
{programming_languages}

### 架构模式
{architecture_patterns}

### 数据格式
{data_formats}

### 文件系统操作
{filesystem_operations}

### 依赖策略
{dependency_strategy}

## 关键设计原则

### 性能优化
{performance_optimization}

### 可靠性保证
{reliability_guarantee}

### 可观测性
{observability}

### 配置管理
{configuration_management}

## 版本兼容性
{version_compatibility}

## 部署架构
{deployment_architecture}
"""
    
    # 3. 数据流模板
    DATA_FLOW_TEMPLATE = """# {project_name} 数据流设计

## 主要数据流向

### 1. {flow_1_name}
```
{flow_1_diagram}
```

### 2. {flow_2_name}
```
{flow_2_diagram}
```

### 3. {flow_3_name}
```
{flow_3_diagram}
```

### 4. {flow_4_name}
```
{flow_4_diagram}
```

## 详细数据流程
{detailed_flows}

## 数据格式规范
{data_formats}

## 性能考量
{performance_considerations}
"""
    
    # 4. 系统架构图模板
    SYSTEM_ARCH_TEMPLATE = """# {project_name} 系统架构图

## 整体架构

```
{overall_architecture_diagram}
```

## 详细组件架构

### {layer_1_name}
```
{layer_1_diagram}
```

### {layer_2_name}
```
{layer_2_diagram}
```

### {layer_3_name}
```
{layer_3_diagram}
```

## 技术栈架构
```
{tech_stack_diagram}
```

{additional_diagrams}
"""
    
    # 5. 组件图模板
    COMPONENT_DIAGRAM_TEMPLATE = """# {project_name} 组件关系图

## 组件层次结构

```
{component_hierarchy}
```

## 详细组件说明

### 1. **{component_1_name}** - {component_1_desc}
{component_1_details}

### 2. **{component_2_name}** - {component_2_desc}
{component_2_details}

### 3. **{component_3_name}** - {component_3_desc}
{component_3_details}

### 4. **{component_4_name}** - {component_4_desc}
{component_4_details}

## 组件依赖关系

```
{dependency_diagram}
```

### 依赖说明
{dependency_details}

## 数据流组件
{data_flow_components}
"""
    
    # 6. 部署图模板
    DEPLOYMENT_DIAGRAM_TEMPLATE = """# {project_name} 部署架构图

## 部署概览

```
{deployment_overview}
```

## 详细部署架构

### {env_1_name}
```bash
{env_1_diagram}
```

### {env_2_name}
```bash
{env_2_diagram}
```

### {env_3_name}
```bash
{env_3_diagram}
```

## 配置管理
{configuration_management}

## 监控和日志
{monitoring_logging}

## 扩展性设计
{scalability_design}
"""
    
