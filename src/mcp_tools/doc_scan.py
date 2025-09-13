"""
MCP doc_scan 工具实现
扫描项目文件并返回结构化信息供Claude Code使用
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# 添加父目录到path以导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.file_service import FileService


class DocScanTool:
    """MCP doc_scan 工具类 - 为Claude Code提供项目文件信息"""
    
    def __init__(self):
        self.tool_name = "doc_scan"
        self.description = "扫描项目文件并返回结构化信息供Claude Code使用"
        self.file_service = FileService()
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取MCP工具定义"""
        return {
            "name": self.tool_name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "要扫描的项目路径"
                    },
                    "include_content": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含文件内容"
                    },
                    "config": {
                        "type": "object",
                        "properties": {
                            "file_extensions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "default": [".py"],
                                "description": "要分析的文件扩展名"
                            },
                            "exclude_patterns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "default": ["__pycache__", ".git", "node_modules", ".idea", ".vscode"],
                                "description": "排除的目录或文件模式"
                            },
                            "max_file_size": {
                                "type": "number",
                                "default": 50000,
                                "description": "单个文件最大字符数限制"
                            },
                            "max_depth": {
                                "type": "number",
                                "default": 3,
                                "description": "目录树扫描最大深度"
                            }
                        }
                    }
                },
                "required": ["project_path"]
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行doc_scan工具"""
        try:
            # 参数验证
            project_path = arguments.get("project_path")
            if not project_path:
                return self._error_response("project_path is required")
            
            if not os.path.exists(project_path):
                return self._error_response(f"Project path does not exist: {project_path}")
            
            if not os.path.isdir(project_path):
                return self._error_response(f"Project path is not a directory: {project_path}")
            
            # 获取参数
            include_content = arguments.get("include_content", True)
            config = arguments.get("config", {})
            
            # 提取配置参数
            file_extensions = config.get("file_extensions", [".py"])
            exclude_patterns = config.get("exclude_patterns", 
                                       ["__pycache__", ".git", "node_modules", ".idea", ".vscode"])
            max_file_size = config.get("max_file_size", 50000)
            max_depth = config.get("max_depth", 3)
            
            # 使用FileService获取项目信息
            project_info = self.file_service.get_project_files_info(
                project_path=project_path,
                include_content=include_content,
                extensions=file_extensions,
                exclude_patterns=exclude_patterns,
                max_file_size=max_file_size
            )
            
            # 获取目录树（使用指定的深度）
            directory_tree = self.file_service.get_directory_tree(project_path, max_depth)
            
            # 更新directory_tree到project_info中
            project_info['directory_tree'] = directory_tree
            
            return self._success_response({
                "scan_result": project_info,
                "scan_config": {
                    "project_path": project_path,
                    "include_content": include_content,
                    "file_extensions": file_extensions,
                    "exclude_patterns": exclude_patterns,
                    "max_file_size": max_file_size,
                    "max_depth": max_depth
                },
                "message": f"成功扫描项目：{project_path}",
                "summary": {
                    "total_files": project_info['statistics']['total_files'],
                    "total_size": project_info['statistics']['total_size'],
                    "file_types": project_info['statistics']['file_types']
                }
            })
                
        except Exception as e:
            return self._error_response(f"扫描失败: {str(e)}")
    
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


def create_mcp_tool() -> DocScanTool:
    """创建MCP工具实例"""
    return DocScanTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP doc_scan tool")
    parser.add_argument("project_path", help="Project path to scan")
    parser.add_argument("--no-content", action="store_true", 
                       help="Don't include file content in results")
    parser.add_argument("--extensions", nargs="+", default=[".py"],
                       help="File extensions to include")
    parser.add_argument("--max-size", type=int, default=50000,
                       help="Maximum file size in characters")
    parser.add_argument("--max-depth", type=int, default=3,
                       help="Maximum directory depth for tree scan")
    
    args = parser.parse_args()
    
    # 构建参数
    arguments = {
        "project_path": args.project_path,
        "include_content": not args.no_content,
        "config": {
            "file_extensions": args.extensions,
            "max_file_size": args.max_size,
            "max_depth": args.max_depth
        }
    }
    
    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()