"""
MCP doc_sync 统一工具实现
智能文档同步工具 - 合并 doc_update_init 和 doc_update 功能
自动检测项目状态，执行初始化或更新检测，并记录完整变更历史
"""
import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.logging import get_logger


class DocSyncTool:
    """MCP doc_sync 统一工具类 - 智能文档同步"""

    def __init__(self):
        self.tool_name = "doc_sync"
        self.description = "智能文档同步工具 - 自动检测并处理项目文件变更"
        self.logger = get_logger(component="DocSyncTool", operation="init")
        self.logger.info("DocSyncTool 初始化完成")

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
                        "description": "项目根路径（可选，默认使用当前工作目录）"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["auto", "init", "update", "status"],
                        "description": "操作模式：auto=智能检测，init=强制初始化，update=强制更新，status=查看状态"
                    },
                    "record_changes": {
                        "type": "boolean",
                        "description": "是否记录变更历史（默认true）"
                    }
                },
                "required": []
            }
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行doc_sync工具"""
        self.logger.info("开始doc_sync操作", {"arguments": arguments})

        try:
            # 参数解析
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

            mode = arguments.get("mode", "auto")
            record_changes = arguments.get("record_changes", True)

            # 确保.codelens目录存在
            codelens_dir = project_path / ".codelens"
            codelens_dir.mkdir(exist_ok=True)

            # 处理不同模式
            if mode == "status":
                result = self._get_status(project_path)
            elif mode == "auto":
                detected_mode = self._detect_mode(project_path)
                self.logger.info(f"智能检测模式: {detected_mode}")
                if detected_mode == "init":
                    result = self._execute_init(project_path, record_changes)
                else:
                    result = self._execute_update(project_path, record_changes)
            elif mode == "init":
                result = self._execute_init(project_path, record_changes)
            elif mode == "update":
                result = self._execute_update(project_path, record_changes)
            else:
                error_msg = f"不支持的模式: {mode}"
                self.logger.error(error_msg)
                return self._error_response(error_msg)

            self.logger.info("doc_sync操作完成", {
                "project_path": str(project_path),
                "mode": mode,
                "result_type": result.get("data", {}).get("operation", "unknown")
            })

            return result

        except Exception as e:
            self.logger.error(f"doc_sync操作失败: {arguments.get('project_path')}, 错误: {str(e)}", exc_info=e)
            return self._error_response(f"操作失败: {str(e)}")

    def _detect_mode(self, project_path: Path) -> str:
        """智能检测应该使用init还是update模式"""
        fingerprints_file = project_path / ".codelens" / "file_fingerprints.json"
        
        if not fingerprints_file.exists():
            self.logger.info("未找到指纹文件，将执行初始化")
            return "init"
        
        # 检查指纹文件是否有效
        try:
            with open(fingerprints_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "files" in data and isinstance(data["files"], dict) and len(data["files"]) > 0:
                self.logger.info(f"发现有效指纹文件，包含{len(data['files'])}个文件记录，将执行更新检测")
                return "update"
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"指纹文件损坏: {e}，将重新初始化")
        
        return "init"

    def _execute_init(self, project_path: Path, record_changes: bool = True) -> Dict[str, Any]:
        """执行初始化操作"""
        self.logger.info("开始执行初始化操作")
        
        # 扫描项目文件
        current_files = self._scan_project_files(project_path)
        
        # 创建指纹文件
        fingerprints = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "files": current_files
        }
        
        fingerprints_file = project_path / ".codelens" / "file_fingerprints.json"
        with open(fingerprints_file, 'w', encoding='utf-8') as f:
            json.dump(fingerprints, f, indent=2, ensure_ascii=False)
        
        # 记录变更历史
        change_info = {
            "operation": "init",
            "files_count": len(current_files),
            "summary": f"初始化项目指纹基点，记录{len(current_files)}个代码文件"
        }
        
        if record_changes:
            self._record_change_history(project_path, change_info)
        
        self.logger.info(f"初始化完成，共记录{len(current_files)}个文件")
        
        return self._success_response({
            "operation": "init",
            "files_count": len(current_files),
            "message": f"✅ 初始化完成，已记录 {len(current_files)} 个文件的指纹基点",
            "fingerprints_file": str(fingerprints_file)
        })

    def _execute_update(self, project_path: Path, record_changes: bool = True) -> Dict[str, Any]:
        """执行更新检测操作"""
        self.logger.info("开始执行更新检测操作")
        
        fingerprints_file = project_path / ".codelens" / "file_fingerprints.json"
        
        if not fingerprints_file.exists():
            return self._error_response("指纹文件不存在，请先执行初始化")
        
        # 加载旧指纹
        with open(fingerprints_file, 'r', encoding='utf-8') as f:
            old_fingerprints = json.load(f)
        
        old_files = old_fingerprints.get("files", {})
        
        # 扫描当前文件状态
        current_files = self._scan_project_files(project_path)
        
        # 检测变化
        changed_files, new_files, deleted_files = self._compare_files(old_files, current_files)
        
        # 生成更新建议
        suggestion = self._generate_suggestion(changed_files, new_files, deleted_files)
        
        # 更新指纹文件
        new_fingerprints = {
            "created_at": old_fingerprints.get("created_at"),
            "last_updated": datetime.now().isoformat(),
            "files": current_files
        }
        
        with open(fingerprints_file, 'w', encoding='utf-8') as f:
            json.dump(new_fingerprints, f, indent=2, ensure_ascii=False)
        
        # 记录变更历史
        has_changes = bool(changed_files or new_files or deleted_files)
        change_info = {
            "operation": "update",
            "has_changes": has_changes,
            "files_count": len(current_files),
            "changes": {
                "modified": changed_files,
                "added": new_files,
                "deleted": deleted_files
            }
        }
        
        if has_changes:
            change_summary = []
            if changed_files:
                change_summary.append(f"修改{len(changed_files)}个文件")
            if new_files:
                change_summary.append(f"新增{len(new_files)}个文件")
            if deleted_files:
                change_summary.append(f"删除{len(deleted_files)}个文件")
            change_info["summary"] = f"检测到变更：{', '.join(change_summary)}"
        else:
            change_info["summary"] = "未检测到文件变更"
        
        if record_changes:
            self._record_change_history(project_path, change_info)
        
        self.logger.info(f"更新检测完成，变更统计: 修改{len(changed_files)}, 新增{len(new_files)}, 删除{len(deleted_files)}")
        
        return self._success_response({
            "operation": "update",
            "has_changes": has_changes,
            "files_count": len(current_files),
            "changes": {
                "modified": changed_files,
                "added": new_files,
                "deleted": deleted_files
            },
            "suggestion": suggestion,
            "message": f"✅ 更新检测完成，共检测 {len(current_files)} 个文件"
        })

    def _get_status(self, project_path: Path) -> Dict[str, Any]:
        """获取当前状态信息"""
        self.logger.info("获取项目状态信息")
        
        codelens_dir = project_path / ".codelens"
        fingerprints_file = codelens_dir / "file_fingerprints.json"
        history_file = codelens_dir / "change_history.json"
        
        status_info = {
            "project_path": str(project_path),
            "has_fingerprints": fingerprints_file.exists(),
            "has_history": history_file.exists()
        }
        
        # 读取指纹信息
        if fingerprints_file.exists():
            try:
                with open(fingerprints_file, 'r', encoding='utf-8') as f:
                    fingerprints = json.load(f)
                status_info.update({
                    "fingerprints_created": fingerprints.get("created_at"),
                    "fingerprints_updated": fingerprints.get("last_updated"),
                    "tracked_files": len(fingerprints.get("files", {}))
                })
            except Exception as e:
                status_info["fingerprints_error"] = str(e)
        
        # 读取历史信息
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                status_info.update({
                    "history_created": history.get("created_at"),
                    "history_updated": history.get("last_updated"),
                    "total_operations": history.get("total_operations", 0),
                    "last_operation": history.get("history", [])[-1] if history.get("history") else None
                })
            except Exception as e:
                status_info["history_error"] = str(e)
        
        return self._success_response({
            "operation": "status",
            "status": status_info,
            "message": "📊 项目状态信息获取完成"
        })

    def _scan_project_files(self, project_path: Path) -> Dict[str, Dict[str, Any]]:
        """扫描项目文件 - 重用现有逻辑"""
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
                      current_files: Dict[str, Dict[str, Any]]) -> Tuple[List[str], List[str], List[str]]:
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
            return "✅ 没有检测到文件变化，无需更新文档。"
        
        suggestion = "📝 检测到以下文件变化，建议更新相关文档：\n\n"
        
        if changed_files:
            suggestion += "🔄 **已修改的文件：**\n"
            for file in changed_files:
                suggestion += f"- {file}\n"
            suggestion += "\n"
        
        if new_files:
            suggestion += "✨ **新增的文件：**\n"
            for file in new_files:
                suggestion += f"- {file}\n"
            suggestion += "\n"
        
        if deleted_files:
            suggestion += "🗑️ **已删除的文件：**\n"
            for file in deleted_files:
                suggestion += f"- {file}\n"
            suggestion += "\n"
        
        suggestion += "💡 **建议操作：**\n"
        suggestion += "1. 检查并更新这些文件对应的文档内容\n"
        suggestion += "2. 更新项目README中的相关说明\n"
        suggestion += "3. 如有架构变更，请更新架构文档\n"
        
        return suggestion

    def _record_change_history(self, project_path: Path, change_info: Dict[str, Any]):
        """记录变更历史"""
        history_file = project_path / ".codelens" / "change_history.json"
        last_change_file = project_path / ".codelens" / "last_change.json"
        
        # 生成变更记录
        change_record = {
            "id": f"change_{int(datetime.now().timestamp() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            **change_info
        }
        
        # 读取或创建历史记录
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                history = self._create_empty_history()
        else:
            history = self._create_empty_history()
        
        # 添加新记录
        history["history"].append(change_record)
        history["last_updated"] = datetime.now().isoformat()
        history["total_operations"] = len(history["history"])
        
        # 保存历史记录
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        # 保存最新变更
        with open(last_change_file, 'w', encoding='utf-8') as f:
            json.dump(change_record, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"变更历史已记录: {change_record['id']}")

    def _create_empty_history(self) -> Dict[str, Any]:
        """创建空的历史记录结构"""
        return {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_operations": 0,
            "history": []
        }

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


def create_mcp_tool() -> DocSyncTool:
    """创建MCP工具实例"""
    return DocSyncTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP doc_sync unified tool")
    parser.add_argument("project_path", nargs="?", help="Project path (optional)")
    parser.add_argument("--mode", choices=["auto", "init", "update", "status"], 
                       default="auto", help="Operation mode")
    parser.add_argument("--no-record", action="store_true", help="Disable change recording")

    args = parser.parse_args()

    # 构建参数
    arguments = {
        "project_path": args.project_path,
        "mode": args.mode,
        "record_changes": not args.no_record
    }

    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()