"""
文件层模板 (File Layer) - 1个综合模板
单个文件的完整文档生成模板，整合文件摘要、类分析和函数目录功能
"""


class FileTemplates:
    """文件层文档模板集合"""
    
    # 综合文件摘要模板 - 详细的文件分析文档，包含流程图和深度分析
    FILE_SUMMARY_TEMPLATE = """# 文件分析报告：{filename}

## 文件概述
{function_overview}

## 代码结构分析

### 导入依赖
{imports}

### 全局变量和常量
{global_variables}

### 配置和设置
{constants}

## 函数详细分析

### 函数概览表
{function_summary_table}

### 函数详细说明
{detailed_function_analysis}

## 类详细分析

### 类概览表
{class_summary_table}

### 类详细说明
{detailed_class_analysis}

## 函数调用流程图
```mermaid
{function_call_flowchart}
```

## 变量作用域分析
{variable_scope_analysis}

## 函数依赖关系
{function_dependencies}

## 数据流分析
{data_flow_analysis}

## 错误处理机制
{error_handling}

## 性能分析
{performance_analysis}

## 算法复杂度
{algorithm_complexity}

## 扩展性评估
{extensibility_assessment}

## 代码质量评估
{code_quality_assessment}

## 文档完整性
{documentation_completeness}

## 备注
{notes}
"""
    
    # 为了保持向后兼容性，保留旧模板名称作为别名
    SUMMARY_TEMPLATE = FILE_SUMMARY_TEMPLATE
    

