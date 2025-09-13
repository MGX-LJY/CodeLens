"""
文件层模板 (File Layer) - 5个模板
单个文件、类、函数等代码级别的文档模板
"""


class FileTemplates:
    """文件层文档模板集合"""
    
    # 1. 文件摘要模板（增强版）
    SUMMARY_TEMPLATE = """# 文件摘要：{filename}

## 功能概述
{function_overview}

## 主要组件

### 类定义
{class_definitions}

### 函数定义
{function_definitions}

### 重要常量和配置
{constants}

## 依赖关系

### 导入的模块
{imports}

### 对外接口
{exports}

## 关键算法和逻辑
{algorithms}

## 性能分析
{performance_analysis}

## 测试覆盖
{test_coverage}

## 备注
{notes}
"""
    
    # 2. 类分析模板
    CLASS_ANALYSIS_TEMPLATE = """# 类分析：{class_name}

## 类概述
{class_overview}

## 继承关系
{inheritance_hierarchy}

## 属性分析

{attributes_analysis}

## 方法分析

{methods_analysis}

## 设计模式
{design_patterns}

## 职责分析
{responsibility_analysis}

## 协作关系
{collaboration_relationships}

## 优化建议
{optimization_suggestions}
"""
    
    # 3. 函数目录模板
    FUNCTION_CATALOG_TEMPLATE = """# {module_name} 函数目录

## 函数概览
{function_overview}

## 公开函数

{public_functions}

## 私有函数

{private_functions}

## 静态方法

{static_methods}

## 类方法

{class_methods}

## 函数复杂度分析
{complexity_analysis}

## 调用关系图
```
{call_graph}
```
"""
    
    # 4. 算法分解模板
    ALGORITHM_BREAKDOWN_TEMPLATE = """# 算法分解：{algorithm_name}

## 算法概述
{algorithm_overview}

## 核心思路
{core_idea}

## 步骤分解

{step_breakdown}

## 复杂度分析

**时间复杂度**: {time_complexity}
**空间复杂度**: {space_complexity}

## 实现细节

{implementation_details}

## 优化策略

{optimization_strategies}

## 测试用例

{test_cases}
"""
    
    # 5. 代码度量模板
    CODE_METRICS_TEMPLATE = """# {file_name} 代码度量报告

## 基本指标

{basic_metrics}

## 复杂度指标

{complexity_metrics}

## 质量指标

{quality_metrics}

## 测试覆盖率

{test_coverage}

## 代码规范

{code_standards}

## 改进建议

{improvement_suggestions}
"""