"""
MCP doc_scan 工具实现
扫描项目文件并返回结构化信息供Claude Code使用
"""
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.services.file_service import FileService
from src.logging import get_logger


class DocScanTool:
    """MCP doc_scan 工具类 - 为Claude Code提供项目文件信息"""

    def __init__(self):
        self.tool_name = "doc_scan"
        self.description = "扫描项目文件并返回结构化信息供Claude Code使用"
        self.file_service = FileService()
        self.logger = get_logger(component="DocScanTool", operation="init")
        self.logger.info("DocScanTool 初始化完成")

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
                        "description": "要扫描的项目路径（可选，默认使用当前工作目录）"
                    },
                    "include_content": {
                        "type": "boolean",
                        "description": "是否包含文件内容"
                    },
                    "config": {
                        "type": "object",
                        "properties": {
                            "file_extensions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "要分析的文件扩展名"
                            },
                            "exclude_patterns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "排除的目录或文件模式"
                            },
                            "max_file_size": {
                                "type": "number",
                                "description": "单个文件最大字符数限制"
                            },
                            "max_depth": {
                                "type": "number",
                                "description": "目录树扫描最大深度"
                            },
                            "ignore_patterns": {
                                "type": "object",
                                "properties": {
                                    "files": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "忽略的文件模式"
                                    },
                                    "directories": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "忽略的目录模式"
                                    },
                                    "content_based": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "基于内容的过滤规则"
                                    }
                                }
                            },
                            "smart_filtering": {
                                "type": "object",
                                "properties": {
                                    "enabled": {
                                        "type": "boolean",
                                        "description": "启用智能过滤"
                                    },
                                    "project_type": {
                                        "type": "string",
                                        "enum": ["auto_detect", "python", "javascript", "java", "go", "rust"],
                                        "description": "项目类型"
                                    },
                                    "keep_config_files": {
                                        "type": "boolean",
                                        "description": "保留配置文件"
                                    },
                                    "keep_test_files": {
                                        "type": "boolean",
                                        "description": "保留测试文件"
                                    }
                                }
                            },
                            "analysis_focus": {
                                "type": "object",
                                "properties": {
                                    "main_source_only": {
                                        "type": "boolean",
                                        "description": "仅分析主要源代码文件"
                                    },
                                    "exclude_examples": {
                                        "type": "boolean",
                                        "description": "排除示例文件"
                                    },
                                    "exclude_migrations": {
                                        "type": "boolean",
                                        "description": "排除数据库迁移文件"
                                    }
                                }
                            }
                        }
                    }
                },
                "required": []
            }
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行doc_scan工具"""
        operation_id = self.logger.log_operation_start("execute_doc_scan", 
                                                       project_path=arguments.get("project_path"),
                                                       include_content=arguments.get("include_content", False),
                                                       max_depth=arguments.get("config", {}).get("max_depth", 3))
        start_time = time.time()
        
        self.logger.info("开始doc_scan操作", {
            "arguments": arguments, 
            "operation_id": operation_id
        })

        try:
            # 参数验证 - 如果没有提供project_path，使用当前工作目录
            project_path = arguments.get("project_path")
            if not project_path:
                project_path = os.getcwd()
                self.logger.info("未提供project_path，使用当前工作目录", {
                    "current_working_directory": project_path
                })
            
            self.logger.debug("验证project_path参数", {"project_path": project_path})

            if not os.path.exists(project_path):
                error_msg = f"Project path does not exist: {project_path}"
                self.logger.error(error_msg)
                return self._error_response(error_msg)

            if not os.path.isdir(project_path):
                error_msg = f"Project path is not a directory: {project_path}"
                self.logger.error(error_msg)
                return self._error_response(error_msg)

            # 记录开始扫描
            self.logger.info("开始扫描项目", {"project_path": project_path})

            # 获取参数
            include_content = arguments.get("include_content", True)
            config = arguments.get("config", {})
            
            self.logger.debug("扫描配置参数", {
                "include_content": include_content,
                "config": config
            })

            # 提取配置参数
            file_extensions = config.get("file_extensions", [".py"])
            exclude_patterns = config.get("exclude_patterns",
                                          ["__pycache__", ".git", "node_modules", ".idea", ".vscode"])
            max_file_size = config.get("max_file_size", 122880)
            max_depth = config.get("max_depth", 3)

            # 提取新的过滤配置
            ignore_patterns = config.get("ignore_patterns", {})
            smart_filtering = config.get("smart_filtering", {})
            analysis_focus = config.get("analysis_focus", {})

            # 应用智能过滤逻辑
            self.logger.debug("开始应用智能过滤逻辑")
            enhanced_exclude_patterns = self._apply_smart_filtering(
                project_path, exclude_patterns, ignore_patterns, smart_filtering, analysis_focus
            )
            self.logger.debug("智能过滤逻辑应用完成", {
                "original_patterns_count": len(exclude_patterns),
                "enhanced_patterns_count": len(enhanced_exclude_patterns)
            })

            # 使用FileService获取项目信息
            self.logger.info("开始使用FileService获取项目信息", {
                "extensions": file_extensions,
                "exclude_patterns_count": len(enhanced_exclude_patterns),
                "max_file_size": max_file_size
            })
            
            project_info = self.file_service.get_project_files_info(
                project_path=project_path,
                include_content=include_content,
                extensions=file_extensions,
                exclude_patterns=enhanced_exclude_patterns,
                max_file_size=max_file_size
            )
            
            self.logger.info("FileService项目信息获取完成", {
                "files_found": project_info.get('statistics', {}).get('total_files', 0),
                "total_size": project_info.get('statistics', {}).get('total_size', 0)
            })

            # 应用内容过滤
            if smart_filtering.get("enabled", True):
                self.logger.debug("开始应用内容过滤")
                original_file_count = len(project_info.get('files', []))
                project_info = self._apply_content_filtering(project_info, ignore_patterns, analysis_focus)
                filtered_file_count = len(project_info.get('files', []))
                self.logger.debug("内容过滤完成", {
                    "original_files": original_file_count,
                    "filtered_files": filtered_file_count,
                    "filtered_out": original_file_count - filtered_file_count
                })

            # 获取目录树（使用指定的深度）
            self.logger.debug("开始获取目录树", {"max_depth": max_depth})
            directory_tree = self.file_service.get_directory_tree(project_path, max_depth)
            self.logger.debug("目录树获取完成")

            # 更新directory_tree到project_info中
            project_info['directory_tree'] = directory_tree

            # 记录成功完成
            duration_ms = (time.time() - start_time) * 1000
            summary = {
                "total_files": project_info['statistics']['total_files'],
                "total_size": project_info['statistics']['total_size'],
                "file_types": project_info['statistics']['file_types']
            }

            self.logger.log_operation_end("execute_doc_scan", operation_id, duration_ms, True,
                                        project_path=project_path,
                                        total_files=summary['total_files'],
                                        total_size=summary['total_size'],
                                        file_types_count=len(summary['file_types']))

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
                "summary": summary
            })

        except Exception as e:
            # 记录失败完成
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_operation_end("execute_doc_scan", operation_id, duration_ms, False, error=str(e))
            self.logger.error(f"项目扫描失败: {arguments.get('project_path')}, "
                              f"用时: {duration_ms}ms, 错误: {str(e)}", exc_info=e)

            return self._error_response(f"扫描失败: {str(e)}")

    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """成功响应"""
        self.logger.debug("生成成功响应", {"data_keys": list(data.keys()) if data else []})
        return {
            "success": True,
            "tool": self.tool_name,
            "data": data
        }

    def _apply_smart_filtering(self, project_path: str, base_exclude_patterns: list,
                               ignore_patterns: Dict[str, Any], smart_filtering: Dict[str, Any],
                               analysis_focus: Dict[str, Any]) -> list:
        """应用智能过滤逻辑"""
        self.logger.debug("开始智能过滤处理", {
            "base_patterns_count": len(base_exclude_patterns),
            "smart_filtering_enabled": smart_filtering.get("enabled", True)
        })
        
        enhanced_patterns = base_exclude_patterns.copy()

        # 添加基本忽略模式
        ignore_dirs = ignore_patterns.get("directories", ["__pycache__", ".git", "node_modules", ".idea", "venv"])

        enhanced_patterns.extend(ignore_dirs)

        # 项目类型特定过滤
        project_type = smart_filtering.get("project_type", "auto_detect")
        if project_type == "auto_detect":
            self.logger.debug("自动检测项目类型")
            project_type = self._detect_project_type(project_path)
            self.logger.debug("项目类型检测完成", {"detected_type": project_type})

        type_specific_patterns = self._get_type_specific_excludes(project_type)
        enhanced_patterns.extend(type_specific_patterns)
        self.logger.debug("项目类型特定模式添加完成", {
            "project_type": project_type,
            "added_patterns_count": len(type_specific_patterns)
        })

        # 分析焦点过滤
        if analysis_focus.get("exclude_examples", True):
            enhanced_patterns.extend(["examples", "example", "demo", "demos", "samples"])

        if analysis_focus.get("exclude_migrations", True):
            enhanced_patterns.extend(["migrations", "migrate", "db/migrate"])

        return list(set(enhanced_patterns))  # 去重

    def _apply_content_filtering(self, project_info: Dict[str, Any],
                                 ignore_patterns: Dict[str, Any],
                                 analysis_focus: Dict[str, Any]) -> Dict[str, Any]:
        """应用基于内容的过滤"""
        content_rules = ignore_patterns.get("content_based", ["empty_files", "generated_files", "binary_files"])

        filtered_files = []
        for file_info in project_info.get("files", []):

            # 检查空文件
            if "empty_files" in content_rules and file_info.get("size", 0) == 0:
                continue

            # 检查生成文件
            if "generated_files" in content_rules and self._is_generated_file(file_info):
                continue

            # 检查二进制文件
            if "binary_files" in content_rules and self._is_binary_file(file_info):
                continue

            # 主要源码过滤
            if analysis_focus.get("main_source_only", False) and not self._is_main_source(file_info):
                continue

            filtered_files.append(file_info)

        project_info["files"] = filtered_files

        # 更新统计信息
        if "statistics" in project_info:
            project_info["statistics"]["total_files"] = len(filtered_files)
            project_info["statistics"]["total_size"] = sum(f.get("size", 0) for f in filtered_files)

        return project_info

    def _detect_project_type(self, project_path: str) -> str:
        """检测项目类型"""
        self.logger.debug("开始检测项目类型", {"project_path": project_path})
        project_path = Path(project_path)

        # 检查特征文件
        if (project_path / "requirements.txt").exists() or (project_path / "setup.py").exists():
            return "python"
        elif (project_path / "package.json").exists():
            return "javascript"
        elif (project_path / "pom.xml").exists() or (project_path / "build.gradle").exists():
            return "java"
        elif (project_path / "go.mod").exists():
            return "go"
        elif (project_path / "Cargo.toml").exists():
            return "rust"

        detected_type = "unknown"
        self.logger.debug("项目类型检测结果", {"type": detected_type})
        return detected_type

    def _get_type_specific_excludes(self, project_type: str) -> list:
        """获取项目类型特定的排除模式"""
        # 通用系统文件排除（所有项目类型都适用）
        common_excludes = [".DS_Store", "Thumbs.db", "*.log", ".gitignore", ".gitkeep", "*.tmp", "*.temp"]
        
        type_patterns = {
            "python": ["*.pyc", "*.pyo", "*.pyd", "__pycache__", ".pytest_cache", "venv", "env", ".venv", ".coverage"],
            "javascript": ["node_modules", "dist", "build", "*.min.js", ".next", ".nuxt"],
            "java": ["target", "build", "*.class", "*.jar", "*.war"],
            "go": ["vendor", "*.exe"],
            "rust": ["target", "Cargo.lock"]
        }

        # 合并通用排除和项目特定排除
        project_specific = type_patterns.get(project_type, [])
        return common_excludes + project_specific

    def _is_generated_file(self, file_info: Dict[str, Any]) -> bool:
        """检查是否为生成文件"""
        file_path = file_info.get("path", "")
        content = file_info.get("content", "")

        # 检查文件名模式
        generated_patterns = [
            "generated", "gen_", "_gen", ".generated",
            "dist/", "build/", "out/", ".min.", "bundle."
        ]

        for pattern in generated_patterns:
            if pattern in file_path.lower():
                return True

        # 检查内容特征（如果有内容）
        if content:
            generated_markers = [
                "// This file was automatically generated",
                "# This file is automatically generated",
                "/* Auto-generated",
                "DO NOT EDIT"
            ]

            content_start = content[:500].upper()
            for marker in generated_markers:
                if marker.upper() in content_start:
                    return True

        return False

    def _is_binary_file(self, file_info: Dict[str, Any]) -> bool:
        """检查是否为二进制文件"""
        file_path = file_info.get("path", "")

        binary_extensions = [
            ".exe", ".dll", ".so", ".dylib", ".a", ".lib",
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".zip", ".tar", ".gz", ".rar", ".7z",
            ".mp3", ".mp4", ".avi", ".mov", ".wmv"
        ]

        file_ext = Path(file_path).suffix.lower()
        return file_ext in binary_extensions

    def _is_main_source(self, file_info: Dict[str, Any]) -> bool:
        """检查是否为主要源码文件"""
        file_path = file_info.get("path", "")

        # 排除测试文件
        if any(test_pattern in file_path.lower() for test_pattern in ["test", "spec", "__test__"]):
            return False

        # 排除配置文件
        config_patterns = ["config", "setting", ".env", "Dockerfile"]
        if any(config_pattern in file_path.lower() for config_pattern in config_patterns):
            return False

        # 排除文档文件  
        if any(file_path.lower().endswith(ext) for ext in [".md", ".txt", ".rst"]):
            return False

        return True

    def _error_response(self, message: str) -> Dict[str, Any]:
        """错误响应"""
        self.logger.error("生成错误响应", {"error_message": message})
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
    parser.add_argument("--max-size", type=int, default=122880,
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
