"""
文档模板服务：为Claude Code提供标准化的文档模板
CodeLens 四层架构精简文档模板系统
为Claude Code提供16个核心文档模板，覆盖架构、模块、文件、项目四个层次
"""
from typing import Dict, List, Any

# 导入日志系统
try:
    from ..logging import get_logger
except ImportError:
    # 如果日志系统不可用，创建一个空日志器
    class DummyLogger:
        def debug(self, msg, context=None): pass
        def info(self, msg, context=None): pass
        def warning(self, msg, context=None): pass
        def error(self, msg, context=None, exc_info=None): pass

    get_logger = lambda **kwargs: DummyLogger()

# 导入三层架构模板
from .templates import ArchitectureTemplates, FileTemplates, ProjectTemplates


class DocumentTemplates:
    """原版文档模板集合 - 保持向后兼容"""

    # 原有的四个基础模板，保持向后兼容
    FILE_SUMMARY_TEMPLATE = FileTemplates.SUMMARY_TEMPLATE
    # MODULE_ANALYSIS_TEMPLATE removed - module layer eliminated
    ARCHITECTURE_TEMPLATE = ArchitectureTemplates.OVERVIEW_TEMPLATE
    PROJECT_README_TEMPLATE = ProjectTemplates.README_TEMPLATE


class TemplateServiceV05:
    """精简模板服务类 - 为Claude Code提供10个核心文档模板"""
    
    def __init__(self):
        # 初始化三层架构模板
        self.arch_templates = ArchitectureTemplates()
        self.file_templates = FileTemplates()
        self.project_templates = ProjectTemplates()
        
        # 模板注册表 - 10个模板
        self.template_registry = {
            # 架构层模板 (6个)
            'architecture': self.arch_templates.OVERVIEW_TEMPLATE,
            'tech_stack': self.arch_templates.TECH_STACK_TEMPLATE,
            'data_flow': self.arch_templates.DATA_FLOW_TEMPLATE,
            'system_architecture': self.arch_templates.SYSTEM_ARCH_TEMPLATE,
            'component_diagram': self.arch_templates.COMPONENT_DIAGRAM_TEMPLATE,
            'deployment_diagram': self.arch_templates.DEPLOYMENT_DIAGRAM_TEMPLATE,
            
            # 文件层模板 (1个)
            'file_summary': self.file_templates.SUMMARY_TEMPLATE,
            
            # 项目层模板 (3个)
            'project_readme': self.project_templates.README_TEMPLATE,
            'changelog': self.project_templates.CHANGELOG_TEMPLATE,
            'roadmap': self.project_templates.ROADMAP_TEMPLATE
        }
        
        # 初始化日志器
        self.logger = get_logger(component="TemplateServiceV05", operation="init")
        self.logger.info("TemplateService 初始化完成", {
            "template_count": len(self.template_registry),
            "architecture_templates": 6,
            "file_templates": 1,
            "project_templates": 3
        })

    def get_template_list(self) -> List[Dict[str, Any]]:
        """获取模板列表 - 10个核心模板"""
        return [
            # ============== 架构层模板 (6个) ==============
            {
                'name': 'architecture',
                'description': '架构概述模板 - 系统整体架构设计',
                'type': 'architecture_level',
                'layer': 'architecture',
                'file_path': '/docs/architecture/overview.md',
                'variables': ['project_name', 'project_overview', 'tech_stack', 'architecture_pattern',
                              'services_layer', 'mcp_interface_layer', 'collaboration_layer',
                              'core_components', 'data_flow', 'system_boundaries', 'deployment_architecture']
            },
            {
                'name': 'tech_stack',
                'description': '技术栈模板 - 详细技术选型和架构原则',
                'type': 'architecture_level',
                'layer': 'architecture',
                'file_path': '/docs/architecture/tech-stack.md',
                'variables': ['project_name', 'programming_languages', 'architecture_patterns',
                              'data_formats', 'filesystem_operations', 'dependency_strategy',
                              'performance_optimization', 'reliability_guarantee', 'observability',
                              'configuration_management', 'version_compatibility', 'deployment_architecture']
            },
            {
                'name': 'data_flow',
                'description': '数据流模板 - 系统数据流转设计',
                'type': 'architecture_level',
                'layer': 'architecture',
                'file_path': '/docs/architecture/data-flow.md',
                'variables': ['project_name', 'flow_1_name', 'flow_1_diagram', 'flow_2_name', 'flow_2_diagram',
                              'flow_3_name', 'flow_3_diagram', 'flow_4_name', 'flow_4_diagram',
                              'detailed_flows', 'data_formats', 'performance_considerations']
            },
            {
                'name': 'system_architecture',
                'description': '系统架构图模板 - 可视化架构图表',
                'type': 'architecture_level',
                'layer': 'architecture',
                'file_path': '/docs/architecture/diagrams/system-architecture.md',
                'variables': ['project_name', 'overall_architecture_diagram', 'layer_1_name', 'layer_1_diagram',
                              'layer_2_name', 'layer_2_diagram', 'layer_3_name', 'layer_3_diagram',
                              'tech_stack_diagram', 'additional_diagrams']
            },
            {
                'name': 'component_diagram',
                'description': '组件图模板 - 组件关系和依赖',
                'type': 'architecture_level',
                'layer': 'architecture',
                'file_path': '/docs/architecture/diagrams/component-diagram.md',
                'variables': ['project_name', 'component_hierarchy', 'component_1_name', 'component_1_desc',
                              'component_1_details', 'component_2_name', 'component_2_desc', 'component_2_details',
                              'component_3_name', 'component_3_desc', 'component_3_details',
                              'component_4_name', 'component_4_desc', 'component_4_details',
                              'dependency_diagram', 'dependency_details', 'data_flow_components']
            },
            {
                'name': 'deployment_diagram',
                'description': '部署图模板 - 部署架构和环境配置',
                'type': 'architecture_level',
                'layer': 'architecture',
                'file_path': '/docs/architecture/diagrams/deployment-diagram.md',
                'variables': ['project_name', 'deployment_overview', 'env_1_name', 'env_1_diagram',
                              'env_2_name', 'env_2_diagram', 'env_3_name', 'env_3_diagram',
                              'configuration_management', 'monitoring_logging', 'scalability_design']
            },

            # ============== 文件层模板 (1个) ==============
            {
                'name': 'file_summary',
                'description': '详细文件分析模板 - 包含流程图、变量作用域、函数依赖的完整文件分析',
                'type': 'file_level',
                'layer': 'file',
                'file_path': '/docs/files/summaries/[file].md',
                'variables': ['filename', 'function_overview', 'imports', 'global_variables', 'constants',
                              'function_summary_table', 'detailed_function_analysis', 'class_summary_table',
                              'detailed_class_analysis', 'function_call_flowchart', 'variable_scope_analysis',
                              'function_dependencies', 'data_flow_analysis', 'error_handling', 'performance_analysis',
                              'algorithm_complexity', 'extensibility_assessment', 'code_quality_assessment',
                              'documentation_completeness', 'notes']
            },

            
            # ============== 项目层模板 (3个) ==============
            {
                'name': 'project_readme',
                'description': '项目README模板 - 项目主文档',
                'type': 'project_level',
                'layer': 'project',
                'file_path': '/docs/project/README.md',
                'variables': ['project_name', 'project_subtitle', 'project_overview', 'core_features',
                              'environment_requirements', 'step_2_name', 'step_2_content', 'step_3_name',
                              'step_3_content', 'current_version', 'project_status', 'tech_architecture',
                              'usage_examples', 'roadmap', 'contribution_guide', 'license']
            },
            {
                'name': 'changelog',
                'description': '变更日志模板 - 变更记录',
                'type': 'project_level',
                'layer': 'project',
                'file_path': '/docs/project/CHANGELOG.md',
                'variables': ['project_name', 'version_entries']
            },

        ]
    
    def get_templates_by_layer(self, layer: str) -> List[Dict[str, Any]]:
        """根据文档层级获取模板列表"""
        return [
            template for template in self.get_template_list()
            if template.get('layer') == layer
        ]
    
    def get_layer_stats(self) -> Dict[str, int]:
        """获取各层级模板统计"""
        templates = self.get_template_list()
        stats = {}
        for template in templates:
            layer = template.get('layer', 'unknown')
            stats[layer] = stats.get(layer, 0) + 1
        return stats

    def get_template_content(self, template_name: str) -> Dict[str, Any]:
        """获取指定模板的内容和元数据"""
        self.logger.debug("获取模板内容", {
            "template_name": template_name,
            "available_templates": list(self.template_registry.keys())
        })

        if template_name not in self.template_registry:
            self.logger.warning("模板不存在", {
                "template_name": template_name,
                "available_templates": list(self.template_registry.keys())
            })
            return {
                'success': False,
                'error': f'Template "{template_name}" not found'
            }

        template_info = next(
            (t for t in self.get_template_list() if t['name'] == template_name),
            {}
        )

        self.logger.info("模板获取成功", {
            "template_name": template_name,
            "template_type": template_info.get('type', 'unknown'),
            "template_layer": template_info.get('layer', 'unknown'),
            "content_length": len(self.template_registry[template_name])
        })

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


class TemplateService(TemplateServiceV05):
    """向后兼容的模板服务"""
    pass


# 兼容性方法，保持向后兼容
def get_file_summary_template() -> str:
    """获取文件摘要模板（兼容方法）"""
    return FileTemplates.SUMMARY_TEMPLATE

# get_module_analysis_template removed - module layer eliminated

def get_architecture_template() -> str:
    """获取架构文档模板（兼容方法）"""
    return ArchitectureTemplates.OVERVIEW_TEMPLATE