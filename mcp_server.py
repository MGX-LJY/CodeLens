#!/usr/bin/env python3
"""
CodeLens MCP Server - Standard MCP Protocol Implementation with Hot Reload
为Claude Code提供项目文档生成的信息和模板服务，支持热重载
"""

import sys
import asyncio
import json
import os
from typing import Any, Sequence, Optional
from pathlib import Path

# MCP SDK imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 导入CodeLens工具
from src.mcp_tools.doc_guide import DocGuideTool
from src.mcp_tools.task_init import TaskInitTool
from src.mcp_tools.task_execute import TaskExecuteTool
from src.mcp_tools.task_status import TaskStatusTool
from src.mcp_tools.init_tools import InitTools
from src.mcp_tools.task_complete import TaskCompleteTool
from src.mcp_tools.project_overview import ProjectOverviewTool
from src.mcp_tools.doc_update_init import DocUpdateInitTool
from src.mcp_tools.doc_update import DocUpdateTool

# 导入热重载功能
from src.hot_reload import HotReloadManager

# 创建MCP服务器实例
server = Server("codelens")

# 热重载管理器（全局实例）
hot_reload_manager: Optional[HotReloadManager] = None

def create_tool_instances():
    """创建工具实例"""
    return {
        "init_tools": InitTools(),
        "doc_guide": DocGuideTool(),
        "task_init": TaskInitTool(),
        "task_execute": TaskExecuteTool(),
        "task_status": TaskStatusTool(),
        "task_complete": TaskCompleteTool(),
        "project_overview": ProjectOverviewTool(),
        "doc_update_init": DocUpdateInitTool(),
        "doc_update": DocUpdateTool()
    }

# 初始化CodeLens工具
codelens_tools = create_tool_instances()

def setup_hot_reload():
    """设置热重载功能"""
    global hot_reload_manager
    
    # 检查环境变量是否启用热重载
    enable_hot_reload = os.getenv('CODELENS_HOT_RELOAD', 'true').lower() == 'true'
    
    if enable_hot_reload:
        try:
            hot_reload_manager = HotReloadManager(
                enabled=True,
                debounce_seconds=0.5,
                batch_reload_window=2.0
            )
            
            # 注册工具实例
            for tool_name, tool_instance in codelens_tools.items():
                hot_reload_manager.register_tool_instance(tool_name, tool_instance)
            
            # 添加重载回调
            hot_reload_manager.add_reload_callback(on_module_reloaded)
            
            print("🔥 热重载功能已启用")
            
        except Exception as e:
            print(f"⚠️  热重载初始化失败: {e}")
            hot_reload_manager = None
    else:
        print("ℹ️  热重载功能已禁用")

def on_module_reloaded(reload_event):
    """模块重载回调"""
    if reload_event.success:
        print(f"✅ 模块热重载成功: {reload_event.module_name}")
        # 这里可以添加工具实例更新逻辑
        refresh_tool_instances()
    else:
        print(f"❌ 模块热重载失败: {reload_event.module_name} - {reload_event.error}")

def refresh_tool_instances():
    """刷新工具实例（重新创建）"""
    global codelens_tools
    try:
        # 重新创建工具实例
        new_tools = create_tool_instances()
        codelens_tools.update(new_tools)
        
        # 重新注册到热重载管理器
        if hot_reload_manager:
            for tool_name, tool_instance in new_tools.items():
                hot_reload_manager.register_tool_instance(tool_name, tool_instance)
        
        print("🔄 工具实例已刷新")
        
    except Exception as e:
        print(f"⚠️  刷新工具实例失败: {e}")

def convert_tool_definition(tool_def: dict) -> Tool:
    """将CodeLens工具定义转换为MCP Tool格式"""
    return Tool(
        name=tool_def["name"],
        description=tool_def["description"],
        inputSchema=tool_def.get("inputSchema", {"type": "object", "properties": {}})
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
    # 设置热重载
    setup_hot_reload()
    
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
                    # 测试doc_guide工具
                    result = await call_tool("doc_guide", {"project_path": project_path})
                    print(f"✅ doc_guide test passed")
                    
                    # 测试热重载状态
                    if hot_reload_manager:
                        status = hot_reload_manager.get_status()
                        print(f"🔥 热重载状态: {status}")
                    
                except Exception as e:
                    print(f"❌ Test failed: {e}")
                    
            return
            
        elif sys.argv[1] == "info":
            hot_reload_status = None
            if hot_reload_manager:
                hot_reload_status = hot_reload_manager.get_status()
            
            info = {
                "name": "codelens",
                "version": "1.0.0.3",
                "description": "CodeLens MCP Server - With Hot Reload Support",
                "tools": len(codelens_tools),
                "hot_reload": hot_reload_status
            }
            print(json.dumps(info, indent=2))
            return
            
        elif sys.argv[1] == "reload":
            # 手动触发热重载
            if hot_reload_manager:
                print("🔄 手动触发热重载...")
                results = hot_reload_manager.force_reload_all()
                success_count = sum(1 for result in results.values() if result)
                print(f"✅ 重载完成: {success_count}/{len(results)} 成功")
                for module, success in results.items():
                    status = "✅" if success else "❌"
                    print(f"  {status} {module}")
            else:
                print("❌ 热重载功能未启用")
            return
    
    # 启动热重载管理器
    if hot_reload_manager:
        hot_reload_manager.start()
    
    try:
        # 启动MCP stdio服务器
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    finally:
        # 停止热重载管理器
        if hot_reload_manager:
            hot_reload_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())