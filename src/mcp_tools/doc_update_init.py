"""
MCP doc_update_init 工具实现
初始化项目文件指纹基点，用于后续文档更新检测
"""
import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.logging import get_logger


class DocUpdateInitTool:
    """MCP doc_update_init 工具类 - 初始化文件指纹基点"""

    def __init__(self):
        self.tool_name = "doc_update_init"
        self.description = "初始化项目文件指纹基点，用于后续变化检测"
        self.logger = get_logger(component="DocUpdateInitTool", operation="init")
        self.logger.info("DocUpdateInitTool 初始化完成")

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
                "required": []
            }
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行doc_update_init工具"""
        self.logger.info("开始doc_update_init操作", {"arguments": arguments})

        try:
            # 参数验证
            project_path = arguments.get("project_path")
            
            # 如果没有提供project_path，使用当前工作目录

            
            if not project_path:

            
                project_path = os.getcwd()

            
                self.logger.info("未提供project_path，使用当前工作目录", {

            
                    "current_working_directory": project_path

            
                })

            project_path = Path(project_path)
            if not project_path.exists():
                error_msg = f"Project path does not exist: {project_path}"
                self.logger.error(error_msg)
                return self._error_response(error_msg)

            if not project_path.is_dir():
                error_msg = f"Project path is not a directory: {project_path}"
                self.logger.error(error_msg)
                return self._error_response(error_msg)

            # 初始化文件指纹
            message = self._init_file_fingerprints(project_path)
            
            self.logger.info("doc_update_init操作完成", {
                "project_path": str(project_path),
                "message": message
            })

            return self._success_response({
                "message": message,
                "fingerprints_file": str(project_path / ".codelens" / "file_fingerprints.json")
            })

        except Exception as e:
            self.logger.error(f"指纹初始化失败: {arguments.get('project_path')}, 错误: {str(e)}", exc_info=e)
            return self._error_response(f"初始化失败: {str(e)}")

    def _init_file_fingerprints(self, project_path: Path) -> str:
        """扫描项目文件并记录hash基点 - 扫描整个项目除了文档文件"""
        fingerprints = {
            "created_at": datetime.now().isoformat(),
            "files": {}
        }
        
        files_processed = 0
        
        # 定义需要忽略的目录
        ignore_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.idea', '.vscode', 'venv', 'env', '.env', 'dist', 'build',
            'docs',  # 排除文档目录
            '.codelens'  # 排除codelens工作目录
        }
        
        # 定义需要忽略的文件扩展名（文档文件）
        ignore_extensions = {
            '.md', '.txt', '.rst', '.doc', '.docx', '.pdf',
            '.log', '.tmp', '.temp', '.cache', '.bak',
            '.pyc', '.pyo', '.pyd', '__pycache__'
        }
        
        # 定义需要检测的文件扩展名（代码文件）
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yaml', '.yml',
            '.toml', '.cfg', '.ini', '.conf', '.sh', '.bat', '.ps1',
            '.html', '.css', '.scss', '.less', '.vue', '.go', '.rs',
            '.java', '.kt', '.cpp', '.c', '.h', '.hpp', '.cs', '.php',
            '.rb', '.swift', '.dart', '.sql', '.r', '.m', '.scala'
        }
        
        # 遍历整个项目目录
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                try:
                    # 检查是否在忽略的目录中
                    if any(ignore_dir in file_path.parts for ignore_dir in ignore_dirs):
                        continue
                    
                    # 检查文件扩展名
                    file_suffix = file_path.suffix.lower()
                    
                    # 跳过文档文件和其他忽略的文件
                    if file_suffix in ignore_extensions:
                        continue
                    
                    # 只处理代码文件或者无扩展名的重要文件
                    if file_suffix not in code_extensions and file_suffix != '':
                        # 检查是否是重要的无扩展名文件
                        important_files = {
                            'Dockerfile', 'Makefile', 'requirements.txt', 
                            'package.json', 'Cargo.toml', 'go.mod', 'pom.xml'
                        }
                        if file_path.name not in important_files:
                            continue
                    
                    # 读取文件内容并计算哈希
                    content = file_path.read_text(encoding='utf-8')
                    file_hash = hashlib.md5(content.encode()).hexdigest()
                    
                    relative_path = str(file_path.relative_to(project_path))
                    fingerprints["files"][relative_path] = {
                        "hash": file_hash,
                        "size": file_path.stat().st_size,
                        "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    files_processed += 1
                    
                except Exception as e:
                    self.logger.warning(f"跳过文件 {file_path}: {e}")
        
        self.logger.info(f"扫描完成，共检测到 {files_processed} 个代码文件")
        
        # 保存指纹文件
        fingerprints_dir = project_path / ".codelens"
        fingerprints_dir.mkdir(exist_ok=True)
        
        fingerprints_file = fingerprints_dir / "file_fingerprints.json"
        with open(fingerprints_file, 'w', encoding='utf-8') as f:
            json.dump(fingerprints, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"文件指纹基点已保存", {
            "fingerprints_file": str(fingerprints_file),
            "files_processed": files_processed
        })
        
        return f"已记录 {files_processed} 个文件的指纹基点"

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


def create_mcp_tool() -> DocUpdateInitTool:
    """创建MCP工具实例"""
    return DocUpdateInitTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP doc_update_init tool")
    parser.add_argument("project_path", help="Project path to initialize fingerprints")

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