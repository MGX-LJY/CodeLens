"""
MCP template_get 工具实现
获取指定类型的文档模板供Claude Code使用
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加父目录到path以导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from templates.document_templates import TemplateService


class TemplateGetTool:
    """MCP template_get 工具类 - 为Claude Code提供文档模板"""
    
    def __init__(self):
        self.tool_name = "template_get"
        self.description = "获取指定类型的文档模板"
        self.template_service = TemplateService()
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取MCP工具定义"""
        return {
            "name": self.tool_name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "description": "模板名称",
                        "enum": ["file_summary", "module_analysis", "architecture", "project_readme"]
                    },
                    "template_type": {
                        "type": "string",
                        "description": "模板类型（可选，用于筛选）",
                        "enum": ["file_level", "module_level", "architecture_level", "project_level"]
                    },
                    "format": {
                        "type": "string",
                        "description": "返回格式",
                        "enum": ["content_only", "with_metadata", "full_info"],
                        "default": "with_metadata"
                    },
                    "list_all": {
                        "type": "boolean",
                        "description": "是否列出所有可用模板",
                        "default": False
                    }
                },
                "anyOf": [
                    {"required": ["template_name"]},
                    {"required": ["template_type"]},
                    {"properties": {"list_all": {"const": True}}}
                ]
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行template_get工具"""
        try:
            template_name = arguments.get("template_name")
            template_type = arguments.get("template_type")
            format_type = arguments.get("format", "with_metadata")
            list_all = arguments.get("list_all", False)
            
            # 如果请求列出所有模板
            if list_all:
                return self._success_response({
                    "action": "list_all_templates",
                    "templates": self.template_service.get_template_list(),
                    "total_count": len(self.template_service.get_template_list())
                })
            
            # 如果按类型筛选
            if template_type and not template_name:
                templates = self.template_service.get_template_by_type(template_type)
                return self._success_response({
                    "action": "get_templates_by_type",
                    "template_type": template_type,
                    "templates": templates,
                    "count": len(templates)
                })
            
            # 获取特定模板
            if template_name:
                return self._get_specific_template(template_name, format_type)
            
            return self._error_response("必须指定 template_name、template_type 或设置 list_all=true")
                
        except Exception as e:
            return self._error_response(f"获取模板失败: {str(e)}")
    
    def _get_specific_template(self, template_name: str, format_type: str) -> Dict[str, Any]:
        """获取特定模板的详细信息"""
        template_info = self.template_service.get_template_content(template_name)
        
        if not template_info['success']:
            return self._error_response(template_info['error'])
        
        # 根据格式要求返回不同的信息
        if format_type == "content_only":
            return self._success_response({
                "action": "get_template_content",
                "template_name": template_name,
                "content": template_info['content']
            })
        elif format_type == "with_metadata":
            return self._success_response({
                "action": "get_template_with_metadata",
                "template_name": template_name,
                "content": template_info['content'],
                "metadata": template_info['metadata']
            })
        elif format_type == "full_info":
            # 获取模板变量验证信息
            validation_info = self.template_service.validate_template_variables(
                template_name, {}
            )
            
            return self._success_response({
                "action": "get_template_full_info",
                "template_name": template_name,
                "content": template_info['content'],
                "metadata": template_info['metadata'],
                "validation_info": validation_info.get('validation_result', {}),
                "usage_example": self._generate_usage_example(template_name),
                "related_templates": self._get_related_templates(template_name)
            })
        
        return self._error_response(f"不支持的格式类型: {format_type}")
    
    def _generate_usage_example(self, template_name: str) -> Dict[str, Any]:
        """生成模板使用示例"""
        examples = {
            "file_summary": {
                "description": "用于生成单个源文件的功能摘要",
                "typical_usage": "在分析Python文件后，使用此模板生成结构化的文件摘要文档",
                "sample_variables": {
                    "filename": "example.py",
                    "function_overview": "文件的主要功能描述",
                    "class_definitions": "- ClassName: 类的作用描述",
                    "function_definitions": "- function_name(): 函数功能描述"
                }
            },
            "module_analysis": {
                "description": "用于生成模块级别的分析文档",
                "typical_usage": "基于文件摘要，识别和分析项目的功能模块",
                "sample_variables": {
                    "identified_modules": "识别出的功能模块列表",
                    "module_details": "每个模块的详细信息",
                    "module_relations": "模块间的依赖关系"
                }
            },
            "architecture": {
                "description": "用于生成系统架构概述文档",
                "typical_usage": "基于模块分析，生成整体系统架构文档",
                "sample_variables": {
                    "project_overview": "项目整体功能概述",
                    "tech_stack": "使用的技术栈分析",
                    "architecture_pattern": "采用的架构模式"
                }
            },
            "project_readme": {
                "description": "用于生成项目README文档",
                "typical_usage": "生成标准化的项目说明文档",
                "sample_variables": {
                    "project_name": "项目名称",
                    "project_overview": "项目概述",
                    "core_features": "核心特性列表"
                }
            }
        }
        
        return examples.get(template_name, {
            "description": "通用文档模板",
            "typical_usage": "根据具体需求使用",
            "sample_variables": {}
        })
    
    def _get_related_templates(self, template_name: str) -> List[str]:
        """获取相关模板列表"""
        relations = {
            "file_summary": ["module_analysis"],
            "module_analysis": ["file_summary", "architecture"],
            "architecture": ["module_analysis", "project_readme"],
            "project_readme": ["architecture"]
        }
        
        return relations.get(template_name, [])
    
    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """成功响应"""
        return {
            "success": True,
            "tool": self.tool_name,
            "data": data
        }
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """错误响应"""
        return {
            "success": False,
            "tool": self.tool_name,
            "error": message
        }


def create_mcp_tool() -> TemplateGetTool:
    """创建MCP工具实例"""
    return TemplateGetTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP template_get tool")
    parser.add_argument("--template", dest="template_name", 
                       choices=["file_summary", "module_analysis", "architecture", "project_readme"],
                       help="Template name to retrieve")
    parser.add_argument("--type", dest="template_type",
                       choices=["file_level", "module_level", "architecture_level", "project_level"],
                       help="Template type to filter")
    parser.add_argument("--format", choices=["content_only", "with_metadata", "full_info"],
                       default="with_metadata", help="Output format")
    parser.add_argument("--list-all", action="store_true", 
                       help="List all available templates")
    
    args = parser.parse_args()
    
    # 构建参数
    arguments = {
        "format": args.format,
        "list_all": args.list_all
    }
    
    if args.template_name:
        arguments["template_name"] = args.template_name
    if args.template_type:
        arguments["template_type"] = args.template_type
    
    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()