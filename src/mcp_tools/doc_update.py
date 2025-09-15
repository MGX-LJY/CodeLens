"""
MCP doc_update 工具实现
检测项目文件变化并生成文档更新建议
"""
import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.logging import get_logger


class DocUpdateTool:
    """MCP doc_update 工具类 - 检测文件变化并生成更新建议"""

    def __init__(self):
        self.tool_name = "doc_update"
        self.description = "检测项目文件变化并生成文档更新建议"
        self.logger = get_logger(component="DocUpdateTool", operation="init")
        self.logger.info("DocUpdateTool 初始化完成")

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
        """执行doc_update工具"""
        self.logger.info("开始doc_update操作", {"arguments": arguments})

        try:
            # 参数验证 - 如果没有提供project_path，使用当前工作目录
            project_path = arguments.get("project_path")
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

            # 检测文件变化
            suggestion = self._detect_file_changes(project_path)
            
            self.logger.info("doc_update操作完成", {
                "project_path": str(project_path),
                "suggestion_length": len(suggestion)
            })

            return self._success_response({
                "suggestion": suggestion,
                "message": "文档更新检测完成"
            })

        except Exception as e:
            self.logger.error(f"文档更新检测失败: {arguments.get('project_path')}, 错误: {str(e)}", exc_info=e)
            return self._error_response(f"检测失败: {str(e)}")

    def _detect_file_changes(self, project_path: Path) -> str:
        """检测文件变化并生成更新建议"""
        fingerprints_file = project_path / ".codelens" / "file_fingerprints.json"
        
        if not fingerprints_file.exists():
            return "请先运行 doc_update_init 初始化指纹基点"
        
        # 加载旧指纹
        with open(fingerprints_file, 'r', encoding='utf-8') as f:
            old_fingerprints = json.load(f)
        
        # 扫描当前文件状态
        current_files = self._scan_current_files(project_path)
        
        # 检测变化
        changed_files, new_files, deleted_files = self._compare_files(
            old_fingerprints.get("files", {}), current_files
        )
        
        # 生成更新建议提示词
        suggestion = self._generate_suggestion(changed_files, new_files, deleted_files)
        
        # 更新指纹基点
        new_fingerprints = {
            "created_at": old_fingerprints.get("created_at"),
            "last_updated": datetime.now().isoformat(),
            "files": current_files
        }
        
        with open(fingerprints_file, 'w', encoding='utf-8') as f:
            json.dump(new_fingerprints, f, indent=2, ensure_ascii=False)
        
        suggestion += f"\n✅ 指纹基点已更新，共记录 {len(current_files)} 个文件。"
        
        return suggestion

    def _scan_current_files(self, project_path: Path) -> Dict[str, Dict[str, Any]]:
        """扫描当前项目文件状态 - 扫描整个项目除了文档文件"""
        current_files = {}
        
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
                    current_files[relative_path] = {
                        "hash": file_hash,
                        "size": file_path.stat().st_size,
                        "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    
                except Exception as e:
                    self.logger.warning(f"跳过文件 {file_path}: {e}")
        
        self.logger.info(f"扫描完成，共检测到 {len(current_files)} 个代码文件")
        return current_files

    def _compare_files(self, old_files: Dict[str, Dict[str, Any]], 
                      current_files: Dict[str, Dict[str, Any]]) -> tuple[List[str], List[str], List[str]]:
        """对比文件变化"""
        changed_files = []
        new_files = []
        deleted_files = []
        
        for file_path, current_info in current_files.items():
            if file_path in old_files:
                if current_info["hash"] != old_files[file_path]["hash"]:
                    changed_files.append(file_path)
            else:
                new_files.append(file_path)
        
        for file_path in old_files:
            if file_path not in current_files:
                deleted_files.append(file_path)
        
        return changed_files, new_files, deleted_files

    def _generate_suggestion(self, changed_files: List[str], new_files: List[str], 
                           deleted_files: List[str]) -> str:
        """生成更新建议提示词"""
        if not changed_files and not new_files and not deleted_files:
            return "没有检测到文件变化，无需更新文档。"
        
        suggestion = "检测到以下文件变化，建议更新相关文档：\n\n"
        
        if changed_files:
            suggestion += "📝 已修改的文件：\n"
            for file in changed_files:
                suggestion += f"- {file}\n"
            suggestion += "\n"
        
        if new_files:
            suggestion += "✨ 新增的文件：\n"
            for file in new_files:
                suggestion += f"- {file}\n"
            suggestion += "\n"
        
        if deleted_files:
            suggestion += "🗑️ 已删除的文件：\n"
            for file in deleted_files:
                suggestion += f"- {file}\n"
            suggestion += "\n"
        
        suggestion += "建议检查并更新这些文件对应的文档内容。"
        
        return suggestion

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


def create_mcp_tool() -> DocUpdateTool:
    """创建MCP工具实例"""
    return DocUpdateTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP doc_update tool")
    parser.add_argument("project_path", help="Project path to check for changes")

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