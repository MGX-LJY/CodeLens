"""
文件层模板 (File Layer) - 1个综合模板
单个文件的完整文档生成模板，整合文件摘要、类分析和函数目录功能
"""


class FileTemplates:
    """文件层文档模板集合"""
    
    # 综合文件摘要模板 - 整合文件摘要、类分析和函数目录功能
    FILE_SUMMARY_TEMPLATE = """# 文件摘要：{filename}

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

{performance_analysis_section}

{architecture_contribution_section}

## 备注
{notes}
"""
    
    # 为了保持向后兼容性，保留旧模板名称作为别名
    SUMMARY_TEMPLATE = FILE_SUMMARY_TEMPLATE
    

