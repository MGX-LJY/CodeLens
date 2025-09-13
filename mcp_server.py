#!/usr/bin/env python3
"""
CodeLens MCP Server
为Claude Code提供项目文档生成的信息和模板服务
"""

import sys
import json
import traceback
from typing import Dict, Any, List

# 导入MCP工具
from src.mcp_tools.doc_scan import DocScanTool
from src.mcp_tools.template_get import TemplateGetTool
from src.mcp_tools.doc_verify import DocVerifyTool


class CodeLensMCPServer:
    """CodeLens MCP服务器"""
    
    def __init__(self):
        """初始化MCP服务器"""
        self.tools = {
            "doc_scan": DocScanTool(),
            "template_get": TemplateGetTool(),
            "doc_verify": DocVerifyTool()
        }
        
    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "name": "codelens",
            "version": "0.3.0",
            "description": "CodeLens MCP服务器 - 为Claude Code提供项目文档生成的信息和模板服务",
            "author": "CodeLens Team",
            "license": "MIT"
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
            print("CodeLens MCP服务器 - 测试模式")
            print("=" * 50)
            
            # 测试服务器信息
            info = server.get_server_info()
            print(f"服务器信息: {json.dumps(info, indent=2, ensure_ascii=False)}")
            
            # 测试工具列表
            tools = server.list_tools()
            print(f"\n可用工具 ({len(tools)} 个):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
            
            # 测试工具执行
            if len(sys.argv) > 2:
                project_path = sys.argv[2]
                print(f"\n测试项目扫描: {project_path}")
                result = server.execute_tool("doc_scan", {"project_path": project_path})
                if result.get("success"):
                    scan_data = result["data"]["scan_result"]
                    print(f"扫描结果: 发现 {len(scan_data['files'])} 个文件")
                else:
                    print(f"扫描失败: {result.get('error')}")
            
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