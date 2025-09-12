"""
MCP doc_init 工具实现
提供MCP协议的文档初始化功能
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# 添加父目录到path以导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from doc_generator import ThreeLayerDocGenerator


class DocInitTool:
    """MCP doc_init 工具类"""
    
    def __init__(self):
        self.tool_name = "doc_init"
        self.description = "初始化项目的三层文档结构"
        self.doc_generator = None
    
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
                        "description": "要分析的项目路径"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "文档输出路径，默认为项目下的docs目录"
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
                                "default": ["__pycache__", ".git", "node_modules", ".idea"],
                                "description": "排除的目录或文件模式"
                            },
                            "max_file_size": {
                                "type": "number",
                                "default": 50000,
                                "description": "单个文件最大字符数限制"
                            },
                            "ai_service_type": {
                                "type": "string",
                                "enum": ["mock", "real"],
                                "default": "mock",
                                "description": "AI服务类型"
                            }
                        }
                    }
                },
                "required": ["project_path"]
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行doc_init工具"""
        try:
            # 参数验证
            project_path = arguments.get("project_path")
            if not project_path:
                return self._error_response("project_path is required")
            
            if not os.path.exists(project_path):
                return self._error_response(f"Project path does not exist: {project_path}")
            
            # 获取配置
            config = arguments.get("config", {})
            output_path = arguments.get("output_path")
            
            # 初始化文档生成器
            ai_service_type = config.get("ai_service_type", "mock")
            self.doc_generator = ThreeLayerDocGenerator(ai_service_type=ai_service_type)
            
            # 执行文档生成
            success = self.doc_generator.generate_project_docs(
                project_path=project_path,
                output_path=output_path,
                config=config
            )
            
            if success:
                output_dir = output_path or os.path.join(project_path, "docs")
                return self._success_response({
                    "project_path": project_path,
                    "output_path": output_dir,
                    "message": "文档生成完成",
                    "generated_files": self._get_generated_files_list(output_dir)
                })
            else:
                return self._error_response("文档生成失败")
                
        except Exception as e:
            return self._error_response(f"执行失败: {str(e)}")
    
    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """成功响应"""
        return {
            "success": True,
            "data": data
        }
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """错误响应"""
        return {
            "success": False,
            "error": message
        }
    
    def _get_generated_files_list(self, output_dir: str) -> Dict[str, list]:
        """获取生成的文件列表"""
        output_path = Path(output_dir)
        generated_files = {
            "architecture_files": [],
            "module_files": [],
            "file_summaries": [],
            "reports": []
        }
        
        try:
            # 架构文档
            arch_dir = output_path / "architecture"
            if arch_dir.exists():
                generated_files["architecture_files"] = [
                    str(f.relative_to(output_path)) for f in arch_dir.rglob("*.md")
                ]
            
            # 模块文档
            module_dir = output_path / "modules"
            if module_dir.exists():
                generated_files["module_files"] = [
                    str(f.relative_to(output_path)) for f in module_dir.rglob("*.md")
                ]
            
            # 文件摘要
            files_dir = output_path / "files"
            if files_dir.exists():
                generated_files["file_summaries"] = [
                    str(f.relative_to(output_path)) for f in files_dir.rglob("*.md")
                ]
            
            # 报告文件
            report_files = ["generation-report.md"]
            for report_file in report_files:
                if (output_path / report_file).exists():
                    generated_files["reports"].append(report_file)
                    
        except Exception as e:
            print(f"获取文件列表失败: {e}")
        
        return generated_files


def create_mcp_tool() -> DocInitTool:
    """创建MCP工具实例"""
    return DocInitTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP doc_init tool")
    parser.add_argument("project_path", help="Project path to analyze")
    parser.add_argument("--output", help="Output directory for docs")
    parser.add_argument("--ai-service", choices=["mock", "real"], default="mock", 
                       help="AI service type")
    
    args = parser.parse_args()
    
    # 构建参数
    arguments = {
        "project_path": args.project_path,
        "config": {
            "ai_service_type": args.ai_service
        }
    }
    
    if args.output:
        arguments["output_path"] = args.output
    
    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()