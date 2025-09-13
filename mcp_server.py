#!/usr/bin/env python3
"""
CodeLens MCP Server
为Claude Code提供项目文档生成的信息和模板服务
"""

import sys
import json
import time
import traceback
from typing import Dict, Any, List

# 导入MCP工具
from src.mcp_tools.doc_scan import DocScanTool
from src.mcp_tools.template_get import TemplateGetTool
from src.mcp_tools.doc_verify import DocVerifyTool

# 导入日志系统
try:
    from src.logging import get_logger
except ImportError:
    # 如果日志系统不可用，创建一个空日志器
    class DummyLogger:
        def debug(self, msg, context=None): pass
        def info(self, msg, context=None): pass
        def warning(self, msg, context=None): pass
        def error(self, msg, context=None, exc_info=None): pass
        def log_operation_start(self, *args, **kwargs): return "dummy"
        def log_operation_end(self, op, op_id, **ctx): pass
    
    get_logger = lambda **kwargs: DummyLogger()


class CodeLensMCPServer:
    """CodeLens MCP服务器"""
    
    def __init__(self):
        """初始化MCP服务器"""
        self.tools = {
            "doc_scan": DocScanTool(),
            "template_get": TemplateGetTool(),
            "doc_verify": DocVerifyTool()
        }
        self.logger = get_logger(component="MCP_Server", operation="server")
        
    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "name": "codelens",
            "version": "0.5.3.2",
            "description": "CodeLens MCP服务器 - 16个核心模板四层架构协作平台，为Claude Code提供专业文档生成服务",
            "author": "CodeLens Team",
            "license": "MIT",
            "features": {
                "template_system": {
                    "total_templates": 16,
                    "architecture_layer": 6,
                    "module_layer": 6, 
                    "file_layer": 1,
                    "project_layer": 3
                },
                "mcp_tools": 3,
                "logging_system": True,
                "zero_dependencies": True
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有可用的MCP工具"""
        tools_list = []
        for tool_name, tool_instance in self.tools.items():
            tool_def = tool_instance.get_tool_definition()
            tools_list.append(tool_def)
        return tools_list
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定的MCP工具"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            tool_instance = self.tools[tool_name]
            result = tool_instance.execute(arguments)
            return result
        except Exception as e:
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Tool execution failed: {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                return {
                    "success": True,
                    "result": {
                        "serverInfo": self.get_server_info(),
                        "capabilities": {
                            "tools": {"supported": True}
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "success": True,
                    "result": {
                        "tools": self.list_tools()
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                return self.execute_tool(tool_name, arguments)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown method: {method}",
                    "supported_methods": ["initialize", "tools/list", "tools/call"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Request handling failed: {str(e)}",
                "traceback": traceback.format_exc()
            }


def main():
    """MCP服务器主入口"""
    server = CodeLensMCPServer()
    
    # 如果是命令行模式，提供交互式测试
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("CodeLens MCP服务器 v0.5.3.2 - 16个核心模板系统测试模式")
            print("=" * 60)
            
            # 测试服务器信息
            info = server.get_server_info()
            print(f"📊 服务器信息:")
            print(f"  版本: {info['version']}")
            print(f"  描述: {info['description']}")
            
            # 显示模板系统特性
            features = info.get('features', {})
            template_system = features.get('template_system', {})
            print(f"\n🎯 16个核心模板系统:")
            print(f"  架构层模板: {template_system.get('architecture_layer', 0)} 个")
            print(f"  模块层模板: {template_system.get('module_layer', 0)} 个")
            print(f"  文件层模板: {template_system.get('file_layer', 0)} 个")
            print(f"  项目层模板: {template_system.get('project_layer', 0)} 个")
            print(f"  模板总数: {template_system.get('total_templates', 0)} 个")
            
            # 测试工具列表
            tools = server.list_tools()
            print(f"\n🔧 可用MCP工具 ({len(tools)} 个):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
            
            # 测试工具执行
            if len(sys.argv) > 2:
                project_path = sys.argv[2]
                print(f"\n📁 测试项目扫描: {project_path}")
                result = server.execute_tool("doc_scan", {"project_path": project_path})
                if result.get("success"):
                    scan_data = result["data"]["scan_result"]
                    print(f"✅ 扫描结果: 发现 {len(scan_data['files'])} 个文件")
                    
                    # 测试模板获取
                    print(f"\n🎨 测试模板系统功能:")
                    template_result = server.execute_tool("template_get", {"list_all": True})
                    if template_result.get("success"):
                        templates = template_result["data"]["templates"]
                        print(f"✅ 模板系统: 加载 {len(templates)} 个模板")
                        
                        # 按层级统计
                        layer_stats = {}
                        for template in templates:
                            layer = template.get('layer', 'unknown')
                            layer_stats[layer] = layer_stats.get(layer, 0) + 1
                        
                        print(f"📊 四层架构分布:")
                        for layer, count in layer_stats.items():
                            print(f"  {layer}: {count} 个模板")
                    else:
                        print(f"❌ 模板获取失败: {template_result.get('error')}")
                else:
                    print(f"❌ 扫描失败: {result.get('error')}")
            
            return
        
        elif sys.argv[1] == "info":
            info = server.get_server_info()
            print(json.dumps(info, indent=2, ensure_ascii=False))
            return
    
    # MCP协议模式 - 从stdin读取JSON-RPC请求
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = server.handle_request(request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                error_response = {
                    "success": False,
                    "error": f"Invalid JSON: {str(e)}"
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        print(json.dumps({"success": True, "message": "Server shutdown"}))
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Server error: {str(e)}",
            "traceback": traceback.format_exc()
        }
        print(json.dumps(error_response))


if __name__ == "__main__":
    main()