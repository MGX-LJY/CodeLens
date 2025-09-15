"""
MCP project_overview 工具实现
扫描项目文档文件夹，生成AI阅读提示词
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.logging import get_logger


class ProjectOverviewTool:
    """MCP project_overview 工具类 - 生成项目文档阅读提示词"""

    def __init__(self):
        self.tool_name = "project_overview"
        self.description = "扫描项目docs文件夹，生成文档阅读提示词"
        self.logger = get_logger(component="ProjectOverviewTool", operation="init")
        self.logger.info("ProjectOverviewTool 初始化完成")

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
                        "description": "项目根路径"
                    }
                },
                "required": ["project_path"]
            }
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行project_overview工具"""
        self.logger.info("开始project_overview操作", {"arguments": arguments})

        try:
            # 参数验证
            project_path = arguments.get("project_path")
            
            if not project_path:
                error_msg = "project_path is required"
                self.logger.error(f"{error_msg}: {arguments}")
                return self._error_response(error_msg)

            project_path = Path(project_path)
            if not project_path.exists():
                error_msg = f"Project path does not exist: {project_path}"
                self.logger.error(error_msg)
                return self._error_response(error_msg)

            if not project_path.is_dir():
                error_msg = f"Project path is not a directory: {project_path}"
                self.logger.error(error_msg)
                return self._error_response(error_msg)

            # 生成文件列表提示词
            prompt = self._generate_file_list_prompt(project_path)
            
            self.logger.info("project_overview操作完成", {
                "project_path": str(project_path),
                "prompt_length": len(prompt)
            })

            return self._success_response({
                "prompt": prompt,
                "message": f"已生成项目 {project_path.name} 的文档阅读提示词"
            })

        except Exception as e:
            self.logger.error(f"项目概览生成失败: {arguments.get('project_path')}, 错误: {str(e)}", exc_info=e)
            return self._error_response(f"操作失败: {str(e)}")

    def _generate_file_list_prompt(self, project_path: Path) -> str:
        """简单扫描并生成文件列表提示词"""
        files_to_read = []
        
        # 扫描docs/project文件夹
        project_docs = project_path / "docs" / "project"
        if project_docs.exists():
            for md_file in project_docs.rglob("*.md"):
                files_to_read.append(md_file)
        
        # 扫描docs/architecture文件夹  
        arch_docs = project_path / "docs" / "architecture"
        if arch_docs.exists():
            for md_file in arch_docs.rglob("*.md"):
                files_to_read.append(md_file)
        
        if not files_to_read:
            return "没有找到项目文档文件（docs/project或docs/architecture目录）"
        
        # 简单排序：README优先
        files_to_read.sort(key=lambda f: (0 if "readme" in f.name.lower() else 1, f.name.lower()))
        
        # 生成简单提示词：告诉AI读哪些文件
        project_name = project_path.name
        prompt = f"请按顺序阅读以下{len(files_to_read)}个项目文档文件，了解{project_name}项目：\n\n"
        
        for f in files_to_read:
            relative_path = f.relative_to(project_path)
            prompt += f"- {relative_path}\n"
        
        prompt += "\n阅读完成后，请总结项目的核心功能和架构特点。"
        
        self.logger.debug("生成文件列表提示词完成", {
            "files_count": len(files_to_read),
            "prompt_length": len(prompt)
        })
        
        return prompt

    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """成功响应"""
        return {
            "success": True,
            "tool": self.tool_name,
            "data": data
        }

    def _error_response(self, message: str) -> Dict[str, Any]:
        """错误响应"""
        self.logger.error("生成错误响应", {"error_message": message})
        return {
            "success": False,
            "tool": self.tool_name,
            "error": message
        }


def create_mcp_tool() -> ProjectOverviewTool:
    """创建MCP工具实例"""
    return ProjectOverviewTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP project_overview tool")
    parser.add_argument("project_path", help="Project path to scan")

    args = parser.parse_args()

    # 构建参数
    arguments = {
        "project_path": args.project_path
    }

    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()