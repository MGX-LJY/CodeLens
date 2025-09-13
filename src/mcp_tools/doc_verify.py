"""
MCP doc_verify 工具实现
检查项目文档生成状态供Claude Code使用
"""
import sys
import os
import json
from typing import Dict, Any, Optional, List

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.services.validation_service import ValidationService


class DocVerifyTool:
    """MCP doc_verify 工具类 - 为Claude Code提供文档验证功能"""

    def __init__(self):
        self.tool_name = "doc_verify"
        self.description = "检查项目文档生成状态"
        self.validation_service = ValidationService()

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
                        "description": "要验证的项目路径"
                    },
                    "verification_type": {
                        "type": "string",
                        "description": "验证类型",
                        "enum": ["full_status", "structure_only", "summary", "missing_files"],
                        "default": "full_status"
                    },
                    "expected_structure": {
                        "type": "object",
                        "description": "自定义的预期结构（可选）",
                        "additionalProperties": True
                    },
                    "expected_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "预期的文件列表（用于missing_files验证）"
                    },
                    "options": {
                        "type": "object",
                        "properties": {
                            "include_recommendations": {
                                "type": "boolean",
                                "default": True,
                                "description": "是否包含改进建议"
                            },
                            "detailed_layer_info": {
                                "type": "boolean",
                                "default": False,
                                "description": "是否包含详细的层级信息"
                            },
                            "check_file_sizes": {
                                "type": "boolean",
                                "default": True,
                                "description": "是否检查文件大小统计"
                            }
                        }
                    }
                },
                "required": ["project_path"]
            }
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行doc_verify工具"""
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
            verification_type = arguments.get("verification_type", "full_status")
            expected_structure = arguments.get("expected_structure")
            expected_files = arguments.get("expected_files", [])
            options = arguments.get("options", {})

            # 根据验证类型执行不同的验证
            if verification_type == "full_status":
                return self._verify_full_status(project_path, options)
            elif verification_type == "structure_only":
                return self._verify_structure_only(project_path, expected_structure)
            elif verification_type == "summary":
                return self._verify_summary(project_path, options)
            elif verification_type == "missing_files":
                return self._verify_missing_files(project_path, expected_files)
            else:
                return self._error_response(f"Unsupported verification type: {verification_type}")

        except Exception as e:
            return self._error_response(f"验证失败: {str(e)}")

    def _verify_full_status(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整状态验证"""
        status = self.validation_service.get_generation_status(project_path)

        result_data = {
            "verification_type": "full_status",
            "project_path": project_path,
            "verification_result": status
        }

        # 根据选项添加额外信息
        if options.get("include_recommendations", True):
            summary = self.validation_service.get_validation_summary(project_path)
            result_data["recommendations"] = summary["recommendations"]

        if options.get("detailed_layer_info", False):
            result_data["layer_details"] = self._get_detailed_layer_info(status)

        return self._success_response(result_data)

    def _verify_structure_only(self, project_path: str,
                               expected_structure: Optional[Dict] = None) -> Dict[str, Any]:
        """仅验证目录结构"""
        if expected_structure:
            structure_result = self.validation_service.check_directory_structure(
                project_path, expected_structure
            )
        else:
            structure_result = self.validation_service.validate_expected_structure(project_path)

        return self._success_response({
            "verification_type": "structure_only",
            "project_path": project_path,
            "structure_validation": structure_result,
            "structure_valid": structure_result["structure_valid"],
            "missing_items": structure_result["missing_items"],
            "existing_items": structure_result["existing_items"]
        })

    def _verify_summary(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """获取验证摘要"""
        summary = self.validation_service.get_validation_summary(project_path)

        result_data = {
            "verification_type": "summary",
            "project_path": project_path,
            "summary": summary["summary"]
        }

        if options.get("include_recommendations", True):
            result_data["recommendations"] = summary["recommendations"]

        return self._success_response(result_data)

    def _verify_missing_files(self, project_path: str, expected_files: List[str]) -> Dict[str, Any]:
        """检查缺失的文件"""
        if not expected_files:
            return self._error_response("expected_files list is required for missing_files verification")

        missing_files = self.validation_service.get_missing_files(project_path, expected_files)
        existing_files = [f for f in expected_files if f not in missing_files]

        return self._success_response({
            "verification_type": "missing_files",
            "project_path": project_path,
            "expected_files_count": len(expected_files),
            "existing_files_count": len(existing_files),
            "missing_files_count": len(missing_files),
            "missing_files": missing_files,
            "existing_files": existing_files,
            "completion_percentage": round((len(existing_files) / len(expected_files)) * 100,
                                           2) if expected_files else 100
        })

    def _get_detailed_layer_info(self, status: Dict[str, Any]) -> Dict[str, Any]:
        """获取详细的层级信息"""
        layer_details = {}

        for layer_name, layer_info in status.get("layer_status", {}).items():
            files = layer_info.get("files", [])

            layer_details[layer_name] = {
                "exists": layer_info["exists"],
                "file_count": layer_info["file_count"],
                "expected_count": layer_info["expected_count"],
                "completion": layer_info["completion"],
                "files": files,
                "file_details": {
                    "total_size": sum(f.get("size", 0) for f in files if f.get("size")),
                    "latest_modified": max(
                        f.get("modified", "") for f in files if f.get("modified")) if files else None,
                    "file_extensions": list(set(f.get("extension", "") for f in files if f.get("extension")))
                } if files else {}
            }

        return layer_details

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


def create_mcp_tool() -> DocVerifyTool:
    """创建MCP工具实例"""
    return DocVerifyTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP doc_verify tool")
    parser.add_argument("project_path", help="Project path to verify")
    parser.add_argument("--type", dest="verification_type",
                        choices=["full_status", "structure_only", "summary", "missing_files"],
                        default="full_status", help="Verification type")
    parser.add_argument("--expected-files", nargs="+",
                        help="Expected files list (for missing_files type)")
    parser.add_argument("--no-recommendations", action="store_true",
                        help="Don't include recommendations")
    parser.add_argument("--detailed-layers", action="store_true",
                        help="Include detailed layer information")

    args = parser.parse_args()

    # 构建参数
    arguments = {
        "project_path": args.project_path,
        "verification_type": args.verification_type,
        "options": {
            "include_recommendations": not args.no_recommendations,
            "detailed_layer_info": args.detailed_layers
        }
    }

    if args.expected_files:
        arguments["expected_files"] = args.expected_files

    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
