"""
文件层模板 (File Layer) - 1个综合模板
单个文件的完整文档生成模板，整合文件摘要、类分析和函数目录功能
"""


class FileTemplates:
    """文件层文档模板集合"""
    
    # 综合文件摘要模板 - 精简的文件分析文档
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
"""
    
    # 为了保持向后兼容性，保留旧模板名称作为别名
    SUMMARY_TEMPLATE = FILE_SUMMARY_TEMPLATE
    

