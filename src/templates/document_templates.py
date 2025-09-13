"""
文档模板服务：为Claude Code提供标准化的文档模板
"""
from typing import Dict, List, Any


class DocumentTemplates:
    """文档模板集合"""
    
    # 文件摘要模板
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

## 备注
{notes}
"""

    # 模块分析模板
    MODULE_ANALYSIS_TEMPLATE = """# 模块总览

## 识别的功能模块
{identified_modules}

## 模块详细信息

{module_details}

## 模块关系图谱
{module_relations}

## 核心接口汇总
{core_interfaces}
"""

    # 架构文档模板
    ARCHITECTURE_TEMPLATE = """# 系统架构概述

## 项目概况
{project_overview}

## 技术栈分析
{tech_stack}

## 架构模式
{architecture_pattern}

## 核心组件
{core_components}

## 数据流设计
{data_flow}

## 系统边界和约束
{system_boundaries}

## 部署架构
{deployment_architecture}
"""

    # 项目README模板
    PROJECT_README_TEMPLATE = """# {project_name}

## 项目概述
{project_overview}

## 核心特性
{core_features}

## 快速开始
{quick_start}

## 项目状态
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


class TemplateService:
    """模板服务类 - 为Claude Code提供文档模板"""
    
    def __init__(self):
        self.templates = DocumentTemplates()
        self.template_registry = {
            'file_summary': self.templates.FILE_SUMMARY_TEMPLATE,
            'module_analysis': self.templates.MODULE_ANALYSIS_TEMPLATE,
            'architecture': self.templates.ARCHITECTURE_TEMPLATE,
            'project_readme': self.templates.PROJECT_README_TEMPLATE
        }
    
    def get_template_list(self) -> List[Dict[str, Any]]:
        """获取可用模板列表"""
        return [
            {
                'name': 'file_summary',
                'description': '文件摘要模板 - 用于生成单个文件的功能摘要',
                'type': 'file_level',
                'variables': ['filename', 'function_overview', 'class_definitions', 
                            'function_definitions', 'constants', 'imports', 'exports', 
                            'algorithms', 'notes']
            },
            {
                'name': 'module_analysis', 
                'description': '模块分析模板 - 用于生成模块级别的分析文档',
                'type': 'module_level',
                'variables': ['identified_modules', 'module_details', 'module_relations', 
                            'core_interfaces']
            },
            {
                'name': 'architecture',
                'description': '架构文档模板 - 用于生成系统架构概述',
                'type': 'architecture_level', 
                'variables': ['project_overview', 'tech_stack', 'architecture_pattern',
                            'core_components', 'data_flow', 'system_boundaries',
                            'deployment_architecture']
            },
            {
                'name': 'project_readme',
                'description': '项目README模板 - 用于生成项目说明文档',
                'type': 'project_level',
                'variables': ['project_name', 'project_overview', 'core_features',
                            'quick_start', 'project_status', 'tech_architecture',
                            'usage_examples', 'roadmap', 'contribution_guide', 'license']
            }
        ]
    
    def get_template_content(self, template_name: str) -> Dict[str, Any]:
        """获取指定模板的内容和元数据"""
        if template_name not in self.template_registry:
            return {
                'success': False,
                'error': f'Template "{template_name}" not found'
            }
        
        template_info = next(
            (t for t in self.get_template_list() if t['name'] == template_name), 
            {}
        )
        
        return {
            'success': True,
            'template_name': template_name,
            'content': self.template_registry[template_name],
            'metadata': template_info
        }
    
    def get_template_by_type(self, template_type: str) -> List[Dict[str, Any]]:
        """根据类型获取模板列表"""
        return [
            template for template in self.get_template_list() 
            if template['type'] == template_type
        ]
    
    def validate_template_variables(self, template_name: str, variables: Dict[str, str]) -> Dict[str, Any]:
        """验证模板变量是否完整"""
        template_info = self.get_template_content(template_name)
        if not template_info['success']:
            return template_info
        
        required_vars = template_info['metadata'].get('variables', [])
        provided_vars = set(variables.keys())
        required_vars_set = set(required_vars)
        
        missing_vars = required_vars_set - provided_vars
        extra_vars = provided_vars - required_vars_set
        
        return {
            'success': True,
            'template_name': template_name,
            'validation_result': {
                'is_valid': len(missing_vars) == 0,
                'missing_variables': list(missing_vars),
                'extra_variables': list(extra_vars),
                'required_variables': required_vars
            }
        }
    
    def format_template(self, template_name: str, **kwargs) -> Dict[str, Any]:
        """格式化模板内容"""
        template_info = self.get_template_content(template_name)
        if not template_info['success']:
            return template_info
        
        try:
            formatted_content = template_info['content'].format(**kwargs)
            return {
                'success': True,
                'template_name': template_name,
                'formatted_content': formatted_content,
                'variables_used': kwargs
            }
        except KeyError as e:
            return {
                'success': False,
                'error': f'Missing template variable: {str(e)}',
                'template_name': template_name
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Template formatting error: {str(e)}',
                'template_name': template_name
            }
    
    # 兼容性方法，保持向后兼容
    def get_file_summary_template(self) -> str:
        """获取文件摘要模板（兼容方法）"""
        return self.templates.FILE_SUMMARY_TEMPLATE
    
    def get_module_analysis_template(self) -> str:
        """获取模块分析模板（兼容方法）"""
        return self.templates.MODULE_ANALYSIS_TEMPLATE
    
    def get_architecture_template(self) -> str:
        """获取架构文档模板（兼容方法）"""
        return self.templates.ARCHITECTURE_TEMPLATE
    
    def format_file_summary(self, **kwargs) -> str:
        """格式化文件摘要（兼容方法）"""
        result = self.format_template('file_summary', **kwargs)
        return result.get('formatted_content', '') if result['success'] else ''
    
    def format_module_analysis(self, **kwargs) -> str:
        """格式化模块分析（兼容方法）"""
        result = self.format_template('module_analysis', **kwargs)
        return result.get('formatted_content', '') if result['success'] else ''
    
    def format_architecture_doc(self, **kwargs) -> str:
        """格式化架构文档（兼容方法）"""
        result = self.format_template('architecture', **kwargs)
        return result.get('formatted_content', '') if result['success'] else ''