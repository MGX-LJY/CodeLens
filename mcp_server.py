#!/usr/bin/env python3
"""
CodeLens MCP Server - Standard MCP Protocol Implementation
为Claude Code提供项目文档生成的信息和模板服务
"""

import sys
import asyncio
import json
from typing import Any, Sequence
from pathlib import Path

# MCP SDK imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 导入CodeLens工具
from src.mcp_tools.doc_scan import DocScanTool
from src.mcp_tools.doc_guide import DocGuideTool
from src.mcp_tools.task_init import TaskInitTool
from src.mcp_tools.task_execute import TaskExecuteTool
from src.mcp_tools.task_status import TaskStatusTool
from src.mcp_tools.init_tools import InitTools
from src.mcp_tools.task_complete import TaskCompleteTool

# 创建MCP服务器实例
server = Server("codelens")

# 初始化CodeLens工具
codelens_tools = {
    "init_tools": InitTools(),
    "doc_scan": DocScanTool(),
    "doc_guide": DocGuideTool(),
    "task_init": TaskInitTool(),
    "task_execute": TaskExecuteTool(),
    "task_status": TaskStatusTool(),
    "task_complete": TaskCompleteTool()
}

def convert_tool_definition(tool_def: dict) -> Tool:
    """将CodeLens工具定义转换为MCP Tool格式"""
    return Tool(
        name=tool_def["name"],
        description=tool_def["description"],
        inputSchema=tool_def.get("input_schema", {"type": "object", "properties": {}})
    )

@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    mcp_tools = []
    for tool_name, tool_instance in codelens_tools.items():
        tool_def = tool_instance.get_tool_definition()
        mcp_tool = convert_tool_definition(tool_def)
        mcp_tools.append(mcp_tool)
    return mcp_tools

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """调用指定的工具"""
    if name not in codelens_tools:
        raise ValueError(f"Unknown tool: {name}")
    
    try:
        tool_instance = codelens_tools[name]
        result = tool_instance.execute(arguments)
        
        # 将结果转换为MCP TextContent格式
        if result.get("success"):
            content = json.dumps(result, indent=2, ensure_ascii=False)
            return [TextContent(type="text", text=content)]
        else:
            error_content = json.dumps({
                "error": result.get("error", "Tool execution failed"),
                "tool": name,
                "arguments": arguments
            }, indent=2, ensure_ascii=False)
            return [TextContent(type="text", text=error_content)]
            
    except Exception as e:
        error_content = json.dumps({
            "error": f"Tool execution failed: {str(e)}",
            "tool": name,
            "arguments": arguments
        }, indent=2, ensure_ascii=False)
        return [TextContent(type="text", text=error_content)]

async def main():
    """主入口函数"""
    # 如果有命令行参数，进入测试模式
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("CodeLens MCP Server - Test Mode")
            print("="*50)
            
            # 测试工具列表
            tools = await list_tools()
            print(f"Available tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # 如果提供了项目路径，测试工具执行
            if len(sys.argv) > 2:
                project_path = sys.argv[2]
                print(f"\nTesting with project: {project_path}")
                
                try:
                    # 测试doc_scan工具
                    result = await call_tool("doc_scan", {"project_path": project_path})
                    print(f"✅ doc_scan test passed")
                    
                except Exception as e:
                    print(f"❌ Test failed: {e}")
                    
            return
            
        elif sys.argv[1] == "info":
            info = {
                "name": "codelens",
                "version": "1.0.0.1",
                "description": "CodeLens MCP Server - Standard Implementation",
                "tools": len(codelens_tools)
            }
            print(json.dumps(info, indent=2))
            return
    
    # 启动MCP stdio服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())