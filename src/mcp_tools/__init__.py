# MCP Tools package
"""
CodeLens MCP工具集合
为Claude Code提供项目文件扫描、模板获取和文档验证功能
"""

from .doc_scan import DocScanTool, create_mcp_tool as create_doc_scan_tool
from .template_get import TemplateGetTool, create_mcp_tool as create_template_get_tool  
from .doc_verify import DocVerifyTool, create_mcp_tool as create_doc_verify_tool

__all__ = [
    'DocScanTool',
    'TemplateGetTool', 
    'DocVerifyTool',
    'create_doc_scan_tool',
    'create_template_get_tool',
    'create_doc_verify_tool'
]