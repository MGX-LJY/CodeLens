#!/usr/bin/env python3
"""
CodeLens 创造模式 - 需求确认工具 (create_requirement)
第一阶段：交互式功能需求分析和验收标准确认
"""

import sys
import json
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 导入日志系统和文件服务
try:
    # 添加项目根目录到path
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, project_root)
    from src.logging import get_logger
    from src.templates.document_templates import TemplateService
    from src.services.file_service import FileService
except ImportError:
    # 如果日志系统不可用，创建一个空日志器
    class DummyLogger:
        def debug(self, msg, context=None): pass
        def info(self, msg, context=None): pass
        def warning(self, msg, context=None): pass
        def error(self, msg, context=None, exc_info=None): pass
        def log_operation_start(self, operation, *args, **kwargs): return "dummy_id"
        def log_operation_end(self, operation, operation_id, success=True, **kwargs): pass

    get_logger = lambda **kwargs: DummyLogger()
    
    class DummyTemplateService:
        def get_template_content(self, name): 
            return {"success": False, "error": "Template service not available"}
        def format_template(self, name, **kwargs):
            return {"success": False, "error": "Template service not available"}
            
    class DummyFileService:
        def scan_source_files(self, path): 
            return {"files": [], "directories": []}
        def get_project_info(self, path):
            return {"name": "Unknown", "type": "Unknown"}
            
    TemplateService = DummyTemplateService
    FileService = DummyFileService

class CreateRequirementCore:
    """创造模式第一阶段：需求确认工具"""
    
    def __init__(self, project_path: str):
        """初始化"""
        self.logger = get_logger(component="CreateRequirementCore", operation="init")
        self.project_path = Path(project_path).resolve()
        self.create_docs_path = self.project_path / "docs" / "project" / "create"
        self.requirements_dir = self.create_docs_path / "requirements"
        self.template_service = TemplateService()
        self.file_service = FileService()
        
        # 确保目录存在
        self.requirements_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("CreateRequirementCore 初始化", {
            "project_path": str(self.project_path),
            "requirements_dir": str(self.requirements_dir)
        })
        
    def generate_requirement_id(self, feature_name: str) -> str:
        """生成需求ID"""
        timestamp = int(time.time())
        # 将功能名称转换为安全的文件名格式
        safe_name = "".join(c for c in feature_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()[:20]  # 限制长度
        return f"req_{safe_name}_{timestamp}"
    
    def analyze_project_context(self) -> Dict[str, Any]:
        """分析项目上下文，为AI生成内容提供基础信息"""
        operation_id = self.logger.log_operation_start("analyze_project_context")
        
        try:
            context = {
                "project_name": self.project_path.name,
                "project_type": "Unknown",
                "tech_stack": [],
                "existing_features": [],
                "file_structure": {},
                "readme_content": None,
                "config_files": []
            }
            
            # 扫描项目文件结构
            try:
                scan_result = self.file_service.scan_source_files(str(self.project_path))
                context["file_structure"] = {"files": scan_result}
                
                # 分析技术栈
                if scan_result:
                    tech_indicators = {
                        "Python": [".py", "requirements.txt", "setup.py", "pyproject.toml"],
                        "JavaScript/Node.js": ["package.json", ".js", ".ts", "node_modules"],
                        "Java": [".java", "pom.xml", "build.gradle"],
                        "Go": [".go", "go.mod", "go.sum"],
                        "Rust": [".rs", "Cargo.toml"],
                        "C/C++": [".c", ".cpp", ".h", "Makefile", "CMakeLists.txt"]
                    }
                    
                    for tech, indicators in tech_indicators.items():
                        for file_path in scan_result:
                            if any(indicator in file_path for indicator in indicators):
                                if tech not in context["tech_stack"]:
                                    context["tech_stack"].append(tech)
                                break
            except Exception as e:
                self.logger.warning(f"Failed to scan project files: {e}")
            
            # 读取README文件
            readme_files = ["README.md", "README.txt", "README.rst", "readme.md"]
            for readme_name in readme_files:
                readme_path = self.project_path / readme_name
                if readme_path.exists():
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            content = f.read()[:2000]  # 限制长度
                            context["readme_content"] = content
                            break
                    except Exception:
                        continue
            
            # 检测项目类型
            if "Python" in context["tech_stack"]:
                files = context["file_structure"].get("files", [])
                if any("flask" in str(f).lower() for f in files):
                    context["project_type"] = "Flask Web Application"
                elif any("django" in str(f).lower() for f in files):
                    context["project_type"] = "Django Web Application"
                elif any("fastapi" in str(f).lower() for f in files):
                    context["project_type"] = "FastAPI Application"
                else:
                    context["project_type"] = "Python Application"
            elif "JavaScript/Node.js" in context["tech_stack"]:
                context["project_type"] = "JavaScript/Node.js Application"
            elif context["tech_stack"]:
                context["project_type"] = f"{context['tech_stack'][0]} Application"
            
            # 检测配置文件
            config_patterns = ["config", "settings", ".env", "docker", "compose"]
            for file_path in context["file_structure"].get("files", []):
                if any(pattern in file_path.lower() for pattern in config_patterns):
                    context["config_files"].append(file_path)
            
            self.logger.log_operation_end("analyze_project_context", operation_id, success=True)
            return context
            
        except Exception as e:
            self.logger.log_operation_end("analyze_project_context", operation_id, 
                success=False, error=str(e)
            )
            return {
                "project_name": self.project_path.name,
                "project_type": "Unknown",
                "tech_stack": [],
                "error": str(e)
            }
    
    
    def collect_requirements_with_ai(self, feature_name: str, requirement_type: str = "new_feature") -> Dict[str, Any]:
        """使用AI智能收集需求信息（简化版）"""
        operation_id = self.logger.log_operation_start("collect_requirements_with_ai", 
            feature_name=feature_name, requirement_type=requirement_type
        )
        
        try:
            requirement_id = self.generate_requirement_id(feature_name)
            
            # 分析项目上下文
            context = self.analyze_project_context()
            
            # 基础信息
            base_info = {
                "feature_name": feature_name,
                "requirement_id": requirement_id,
                "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "creator": "Claude Code User",
                "project_name": context.get("project_name", self.project_path.name),
                "requirement_type": requirement_type
            }
            
            # 简化的需求数据：只包含三个核心字段
            requirement_data = base_info.copy()
            user_description = f"用户想要实现'{feature_name}'功能。"
            requirement_data.update({
                "user_description": user_description,
                "ai_description": self.generate_enhanced_ai_description(feature_name, user_description, context),
                "user_revision": "请在此处提供您的确认和修正..."
            })
            
            result = {
                "tool": "create_requirement",
                "mode": "simplified_generation",
                "requirement_id": requirement_id,
                "feature_name": feature_name,
                "status": "generated",
                
                "requirement_data": requirement_data,
                "project_context": context,
                
                "next_steps": [
                    "1. 审核AI生成的理解和分析",
                    "2. 在'用户确认和修正'部分提供更详细的描述和修正", 
                    "3. 生成简化需求文档",
                    "4. 进入第二阶段：基于确认的描述阅读相关代码并生成设计文档"
                ],
                
                "workflow_info": {
                    "stage": 1,
                    "stage_name": "需求确认",
                    "next_stage": "代码分析和设计文档生成",
                    "simplified": True
                },
                
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.log_operation_end("collect_requirements_with_ai", operation_id, 
                success=True, requirement_id=requirement_id
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("collect_requirements_with_ai", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to collect requirements with AI: {str(e)}"
            }
    
    def collect_requirements_interactive(self, feature_name: str, requirement_type: str = "new_feature") -> Dict[str, Any]:
        """交互式收集需求信息（简化版）"""
        operation_id = self.logger.log_operation_start("collect_requirements_interactive", 
            feature_name=feature_name, requirement_type=requirement_type
        )
        
        try:
            requirement_id = self.generate_requirement_id(feature_name)
            
            # 基础信息
            base_info = {
                "feature_name": feature_name,
                "requirement_id": requirement_id,
                "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "creator": "Claude Code User",
                "project_name": self.project_path.name,
                "requirement_type": requirement_type
            }
            
            # 简化的交互式问题集合 - 只有三个核心字段
            interactive_questions = {
                "user_description": {
                    "question": f"请详细描述您要实现的'{feature_name}'功能：",
                    "placeholder": "请在此处描述您的具体需求，包括功能目标、使用场景、核心要求等...",
                    "required": True,
                    "type": "textarea"
                },
                "ai_description": {
                    "question": "AI理解和分析（自动生成，请检查是否准确）：",
                    "generated": True,
                    "editable": False,
                    "description": "基于您的描述和项目上下文，AI生成的理解和分析"
                },
                "user_revision": {
                    "question": "请确认AI理解是否正确，或提供修正和补充：",
                    "placeholder": "如果AI理解有误或不完整，请在此处提供修正和更详细的描述...",
                    "required": True,
                    "type": "textarea"
                }
            }
            
            # 生成简化的需求数据
            requirement_data = base_info.copy()
            requirement_data.update({
                "user_description": f"用户想要实现'{feature_name}'功能。\n请提供更详细的功能描述...",
                "ai_description": "AI理解将在用户提供详细描述后自动生成",
                "user_revision": "请在此处提供您的确认和修正..."
            })
            
            result = {
                "tool": "create_requirement", 
                "mode": "simplified_interactive",
                "requirement_id": requirement_id,
                "feature_name": feature_name,
                "status": "collected",
                
                "requirement_data": requirement_data,
                "interactive_questions": interactive_questions,
                
                "workflow_info": {
                    "stage": 1,
                    "stage_name": "需求确认",
                    "simplified": True,
                    "interactive_fields": ["user_description", "user_revision"]
                },
                
                "next_steps": [
                    "1. 填写详细的用户功能描述",
                    "2. 审核AI生成的理解和分析", 
                    "3. 提供确认和修正信息",
                    "4. 生成简化需求文档",
                    "5. 进入第二阶段：基于确认的描述阅读相关代码并生成设计文档"
                ],
                
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.log_operation_end("collect_requirements_interactive", operation_id, 
                success=True, requirement_id=requirement_id
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("collect_requirements_interactive", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to collect requirements: {str(e)}"
            }
    
    def generate_requirement_document(self, requirement_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成需求文档"""
        operation_id = self.logger.log_operation_start("generate_requirement_document", 
            requirement_id=requirement_data.get("requirement_id")
        )
        
        try:
            # 获取需求确认模板
            template_result = self.template_service.get_template_content("create_requirement")
            if not template_result.get("success", True):
                return {
                    "success": False,
                    "error": f"Failed to get requirement template: {template_result.get('error', 'Unknown error')}"
                }
            
            # 格式化模板
            format_result = self.template_service.format_template("create_requirement", **requirement_data)
            if not format_result.get("success", True):
                return {
                    "success": False,
                    "error": f"Failed to format requirement template: {format_result.get('error', 'Unknown error')}"
                }
            
            # 生成文档文件
            requirement_id = requirement_data["requirement_id"]
            doc_filename = f"{requirement_id}.md"
            doc_filepath = self.requirements_dir / doc_filename
            
            # 写入文档
            with open(doc_filepath, 'w', encoding='utf-8') as f:
                f.write(format_result["formatted_content"])
            
            result = {
                "tool": "create_requirement",
                "mode": "document_generation",
                "requirement_id": requirement_id,
                "status": "completed",
                
                "document_info": {
                    "filename": doc_filename,
                    "filepath": str(doc_filepath),
                    "file_size": doc_filepath.stat().st_size,
                    "created_time": datetime.now().isoformat()
                },
                
                "requirement_summary": {
                    "feature_name": requirement_data.get("feature_name"),
                    "priority": requirement_data.get("priority_level"),
                    "urgency": requirement_data.get("urgency_level"),
                    "estimated_effort": requirement_data.get("estimated_effort")
                },
                
                "next_stage": {
                    "stage": 2,
                    "tool": "create_analysis",
                    "command": f"python src/mcp_tools/create_analysis.py {self.project_path} --requirement-id {requirement_id}",
                    "description": "分析功能实现方案和影响"
                },
                
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.log_operation_end("generate_requirement_document", operation_id, 
                success=True, document_created=True, filepath=str(doc_filepath)
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("generate_requirement_document", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to generate requirement document: {str(e)}"
            }
    
    def list_requirements(self) -> Dict[str, Any]:
        """列出现有需求文档"""
        operation_id = self.logger.log_operation_start("list_requirements")
        
        try:
            requirements = []
            
            if self.requirements_dir.exists():
                for req_file in self.requirements_dir.glob("*.md"):
                    file_stat = req_file.stat()
                    requirements.append({
                        "filename": req_file.name,
                        "requirement_id": req_file.stem,
                        "filepath": str(req_file),
                        "created_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "file_size": file_stat.st_size
                    })
            
            # 按创建时间排序
            requirements.sort(key=lambda x: x["created_time"], reverse=True)
            
            result = {
                "tool": "create_requirement",
                "mode": "list_requirements",
                "total_count": len(requirements),
                "requirements": requirements,
                "requirements_dir": str(self.requirements_dir),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.log_operation_end("list_requirements", operation_id, 
                success=True, count=len(requirements)
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("list_requirements", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to list requirements: {str(e)}"
            }
    
    def get_requirement_by_id(self, requirement_id: str) -> Dict[str, Any]:
        """根据ID获取需求文档"""
        operation_id = self.logger.log_operation_start("get_requirement_by_id", 
            requirement_id=requirement_id
        )
        
        try:
            req_file = self.requirements_dir / f"{requirement_id}.md"
            
            if not req_file.exists():
                return {
                    "success": False,
                    "error": f"Requirement {requirement_id} not found"
                }
            
            # 读取文档内容
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_stat = req_file.stat()
            
            result = {
                "tool": "create_requirement",
                "mode": "get_requirement",
                "requirement_id": requirement_id,
                "found": True,
                
                "document_info": {
                    "filename": req_file.name,
                    "filepath": str(req_file),
                    "content": content,
                    "file_size": file_stat.st_size,
                    "created_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                },
                
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.log_operation_end("get_requirement_by_id", operation_id, 
                success=True, found=True
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("get_requirement_by_id", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to get requirement {requirement_id}: {str(e)}"
            }
    
    def parse_existing_document(self, requirement_id: str) -> Dict[str, Any]:
        """解析现有需求文档，提取各个字段"""
        operation_id = self.logger.log_operation_start("parse_existing_document", 
            requirement_id=requirement_id
        )
        
        try:
            req_file = self.requirements_dir / f"{requirement_id}.md"
            
            if not req_file.exists():
                return {
                    "success": False,
                    "error": f"Requirement document {requirement_id} not found"
                }
            
            # 读取文档内容
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析文档结构
            parsed_data = {
                "feature_name": "",
                "requirement_id": requirement_id,
                "created_time": "",
                "creator": "",
                "project_name": "",
                "requirement_type": "",
                "user_description": "",
                "ai_description": "",
                "user_revision": ""
            }
            
            # 简单的文档解析（基于markdown结构）
            lines = content.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                if line.startswith('- **功能名称**:'):
                    parsed_data["feature_name"] = line.split(':')[1].strip()
                elif line.startswith('- **创建时间**:'):
                    parsed_data["created_time"] = line.split(':', 1)[1].strip()
                elif line.startswith('- **创建者**:'):
                    parsed_data["creator"] = line.split(':', 1)[1].strip()
                elif line.startswith('- **项目**:'):
                    parsed_data["project_name"] = line.split(':', 1)[1].strip()
                elif line.startswith('- **需求类型**:'):
                    parsed_data["requirement_type"] = line.split(':', 1)[1].strip()
                elif line.startswith('## 用户描述'):
                    current_section = "user_description"
                    current_content = []
                elif line.startswith('## AI理解和分析'):
                    if current_section == "user_description":
                        parsed_data["user_description"] = '\n'.join(current_content).strip()
                    current_section = "ai_description"
                    current_content = []
                elif line.startswith('## 用户确认和修正'):
                    if current_section == "ai_description":
                        parsed_data["ai_description"] = '\n'.join(current_content).strip()
                    current_section = "user_revision"
                    current_content = []
                elif line.startswith('---'):
                    if current_section == "user_revision":
                        parsed_data["user_revision"] = '\n'.join(current_content).strip()
                    break
                elif current_section:
                    if line.strip() and not line.startswith('#'):
                        current_content.append(line)
            
            # 处理最后一个section
            if current_section == "user_revision":
                parsed_data["user_revision"] = '\n'.join(current_content).strip()
            
            result = {
                "success": True,
                "requirement_id": requirement_id,
                "parsed_data": parsed_data,
                "original_content": content,
                "file_path": str(req_file)
            }
            
            self.logger.log_operation_end("parse_existing_document", operation_id, 
                success=True, requirement_id=requirement_id
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("parse_existing_document", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to parse requirement document {requirement_id}: {str(e)}"
            }
    
    def refine_requirement_with_feedback(self, requirement_id: str, user_feedback: str, refinement_type: str = "ai_regeneration") -> Dict[str, Any]:
        """基于用户反馈完善需求文档"""
        operation_id = self.logger.log_operation_start("refine_requirement_with_feedback", 
            requirement_id=requirement_id, refinement_type=refinement_type
        )
        
        try:
            # 解析现有文档
            parse_result = self.parse_existing_document(requirement_id)
            if not parse_result["success"]:
                return parse_result
            
            parsed_data = parse_result["parsed_data"]
            
            # 分析项目上下文
            context = self.analyze_project_context()
            
            # 基于用户反馈和现有内容重新生成AI理解
            enhanced_user_description = parsed_data["user_description"]
            if user_feedback.strip() and user_feedback.strip() != "请在此处提供您的确认和修正...":
                enhanced_user_description += f"\n\n**用户补充反馈**: {user_feedback}"
            
            # 重新生成AI理解和分析
            new_ai_description = self.generate_enhanced_ai_description(
                parsed_data["feature_name"], 
                enhanced_user_description, 
                context
            )
            
            # 更新需求数据
            refined_data = parsed_data.copy()
            refined_data.update({
                "user_description": enhanced_user_description,
                "ai_description": new_ai_description,
                "user_revision": "请确认以上AI理解是否准确，或继续提供修正意见...",
                # 更新时间戳，但保持原始创建时间
                "refined_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # 生成更新的文档
            update_result = self.update_requirement_document(requirement_id, refined_data)
            
            if update_result["success"]:
                result = {
                    "tool": "create_requirement",
                    "mode": "refinement_with_feedback",
                    "requirement_id": requirement_id,
                    "status": "refined",
                    
                    "refinement_info": {
                        "user_feedback": user_feedback,
                        "refinement_type": refinement_type,
                        "refined_time": refined_data["refined_time"]
                    },
                    
                    "refined_data": refined_data,
                    "document_info": update_result["document_info"],
                    
                    "next_options": [
                        "1. 继续完善 - 如果AI理解仍有不准确的地方，请提供更多反馈",
                        "2. 进入下一阶段 - 如果满意当前需求描述，可以开始代码分析和设计文档生成"
                    ],
                    
                    "refinement_cycle": {
                        "current_status": "等待用户确认",
                        "options": {
                            "continue_refine": "提供更多修正意见继续完善",
                            "proceed_next": "确认需求准确，进入第二阶段"
                        }
                    },
                    
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = update_result
            
            self.logger.log_operation_end("refine_requirement_with_feedback", operation_id, 
                success=update_result["success"], requirement_id=requirement_id
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("refine_requirement_with_feedback", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to refine requirement with feedback: {str(e)}"
            }
    
    def generate_enhanced_ai_description(self, feature_name: str, enhanced_user_description: str, context: Dict[str, Any]) -> str:
        """基于增强的用户描述重新生成AI理解和分析 - 通用方法"""
        project_type = context.get("project_type", "Application")
        tech_stack = context.get("tech_stack", [])
        
        # 构造通用AI分析提示词
        analysis_prompt = f"""
作为AI分析助手，请基于以下信息客观分析用户需求：

**项目背景**: {project_type}，使用{', '.join(tech_stack) if tech_stack else '通用技术栈'}
**功能名称**: {feature_name}
**用户完整描述**: {enhanced_user_description}

**分析要求**:
1. 仅基于用户明确提到的内容进行分析，不要添加用户未要求的功能
2. 特别注意用户说"不要"、"不需要"、"避免"的内容
3. 如果用户需求有变化或矛盾，以最新的表述为准
4. 保持客观，不要美化或夸大需求
5. 分析应该实用且贴近实际技术实现

**输出格式**:
基于您提供的详细功能描述，我对'{feature_name}'有了更深入的理解：

**技术栈分析**: [简短分析技术栈和项目类型]

**功能理解**: [总结用户想要实现什么，基于实际描述]

**核心需求**: [列出用户明确提到的关键需求点]

**实现方式**: [用户提到的实现方法和技术要求]

**明确排除**: [用户明确说不要的内容，如果有的话]

**技术考虑**: [与现有系统集成、性能、安全等基本考虑]

如果以上理解有偏差或遗漏，请继续提供修正意见。如果理解准确，可以确认进入下一阶段。
"""
        
        # 模拟AI分析过程（这里简化为基本的文本分析）
        ai_analysis = f"基于您提供的详细功能描述，我对'{feature_name}'有了更深入的理解：\n\n"
        
        # 技术栈分析
        if tech_stack:
            ai_analysis += f"**技术栈分析**: 项目使用{project_type}架构，基于{', '.join(tech_stack[:2])}技术栈进行开发。\n\n"
        
        # 功能理解 - 从用户描述中提取核心意图
        ai_analysis += "**功能理解**: "
        user_desc_clean = enhanced_user_description.replace("**用户补充反馈**: ", "").strip()
        
        # 简单的意图分析
        if any(keyword in enhanced_user_description.lower() for keyword in ["修复", "fix", "bug", "问题", "错误"]):
            ai_analysis += f"用户希望实现{feature_name}，这是一个问题修复和代码改进功能。"
        elif any(keyword in enhanced_user_description.lower() for keyword in ["创建", "新增", "开发", "实现"]):
            ai_analysis += f"用户希望创建{feature_name}，这是一个新功能开发需求。"
        elif any(keyword in enhanced_user_description.lower() for keyword in ["优化", "改进", "提升"]):
            ai_analysis += f"用户希望通过{feature_name}来优化和改进现有功能。"
        else:
            ai_analysis += f"用户希望实现{feature_name}功能。"
        ai_analysis += "\n\n"
        
        # 核心需求 - 从描述中提取关键点
        ai_analysis += "**核心需求**: \n"
        key_requirements = []
        
        # 基于文本内容提取需求，不做过多假设
        sentences = enhanced_user_description.split('。')
        for sentence in sentences:
            if any(word in sentence for word in ["需要", "应该", "要求", "包含", "支持"]):
                key_requirements.append(f"- {sentence.strip()}")
        
        if not key_requirements:
            key_requirements.append(f"- 实现{feature_name}的基本功能")
        
        for req in key_requirements[:5]:  # 限制数量
            ai_analysis += req + "\n"
        ai_analysis += "\n"
        
        # 实现方式 - 仅基于用户明确提到的
        ai_analysis += "**实现方式**: \n"
        implementation_notes = []
        
        if "命令行" in enhanced_user_description:
            implementation_notes.append("- 命令行工具形式")
        if "MCP" in enhanced_user_description or "mcp" in enhanced_user_description.lower():
            implementation_notes.append("- 通过MCP协议提供服务")
        if "阶段" in enhanced_user_description or "流程" in enhanced_user_description:
            implementation_notes.append("- 分阶段处理流程")
        
        if not implementation_notes:
            implementation_notes.append(f"- 与现有{project_type}架构集成")
        
        for note in implementation_notes:
            ai_analysis += note + "\n"
        ai_analysis += "\n"
        
        # 明确排除 - 用户说不要的内容
        exclusions = []
        negation_phrases = ["不需要", "不要", "无需", "避免", "不包含", "不涉及"]
        
        for phrase in negation_phrases:
            if phrase in enhanced_user_description:
                # 找到否定短语后的内容
                parts = enhanced_user_description.split(phrase)
                for i, part in enumerate(parts[1:], 1):
                    words = part.strip().split()[:5]  # 取前几个词
                    if words:
                        exclusions.append(f"- {phrase}{' '.join(words)}")
        
        if exclusions:
            ai_analysis += "**明确排除**: \n"
            for excl in exclusions[:3]:  # 限制数量
                ai_analysis += excl + "\n"
            ai_analysis += "\n"
        
        # 技术考虑 - 通用的技术考虑
        ai_analysis += "**技术考虑**: \n"
        ai_analysis += f"- 与现有{project_type}系统的兼容性和集成\n"
        ai_analysis += "- 遵循项目现有的代码规范和设计模式\n"
        ai_analysis += "- 确保功能的稳定性和可维护性\n"
        ai_analysis += "- 适当的错误处理和日志记录\n\n"
        
        ai_analysis += "如果以上理解有偏差或遗漏，请继续提供修正意见。如果理解准确，可以确认进入下一阶段。"
        
        return ai_analysis
    
    def update_requirement_document(self, requirement_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新需求文档"""
        operation_id = self.logger.log_operation_start("update_requirement_document", 
            requirement_id=requirement_id
        )
        
        try:
            # 使用模板生成更新的文档
            format_result = self.template_service.format_template("create_requirement", **updated_data)
            if not format_result.get("success", True):
                return {
                    "success": False,
                    "error": f"Failed to format updated requirement template: {format_result.get('error', 'Unknown error')}"
                }
            
            # 写入更新的文档
            req_file = self.requirements_dir / f"{requirement_id}.md"
            with open(req_file, 'w', encoding='utf-8') as f:
                f.write(format_result["formatted_content"])
            
            file_stat = req_file.stat()
            
            result = {
                "success": True,
                "requirement_id": requirement_id,
                "document_info": {
                    "filename": req_file.name,
                    "filepath": str(req_file),
                    "file_size": file_stat.st_size,
                    "updated_time": datetime.now().isoformat()
                }
            }
            
            self.logger.log_operation_end("update_requirement_document", operation_id, 
                success=True, requirement_id=requirement_id
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("update_requirement_document", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to update requirement document: {str(e)}"
            }

class CreateRequirementTool:
    """创造模式需求确认工具 - MCP接口"""
    
    def __init__(self):
        self.tool_name = "create_requirement"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取工具定义"""
        return {
            "name": self.tool_name,
            "description": "📝 CodeLens创造模式第一阶段 - 交互式功能需求分析和验收标准确认",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "项目根目录路径",
                        "default": "."
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["create", "list", "get", "refine"],
                        "description": "执行模式: create=创建需求, list=列出需求, get=获取需求, refine=完善需求",
                        "default": "create"
                    },
                    "feature_name": {
                        "type": "string",
                        "description": "功能名称 (create模式必需)"
                    },
                    "requirement_type": {
                        "type": "string",
                        "enum": ["new_feature", "enhancement", "fix"],
                        "description": "需求类型",
                        "default": "new_feature"
                    },
                    "requirement_id": {
                        "type": "string",
                        "description": "需求ID (get和refine模式必需)"
                    },
                    "user_feedback": {
                        "type": "string",
                        "description": "用户反馈内容 (refine模式必需)"
                    },
                    "refinement_type": {
                        "type": "string",
                        "enum": ["ai_regeneration", "user_clarification"],
                        "description": "完善类型 (refine模式可选)",
                        "default": "ai_regeneration"
                    }
                },
                "required": ["project_path"]
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        try:
            project_path = arguments.get("project_path", ".")
            mode = arguments.get("mode", "create")
            feature_name = arguments.get("feature_name")
            requirement_type = arguments.get("requirement_type", "new_feature")
            requirement_id = arguments.get("requirement_id")
            user_feedback = arguments.get("user_feedback")
            refinement_type = arguments.get("refinement_type", "ai_regeneration")
            
            # 初始化需求确认工具
            requirement_tool = CreateRequirementCore(project_path)
            
            if mode == "list":
                # 列出需求文档
                result = requirement_tool.list_requirements()
            elif mode == "get" and requirement_id:
                # 获取指定需求文档
                result = requirement_tool.get_requirement_by_id(requirement_id)
            elif mode == "refine" and requirement_id and user_feedback:
                # 基于用户反馈完善需求文档
                result = requirement_tool.refine_requirement_with_feedback(
                    requirement_id, user_feedback, refinement_type
                )
            elif mode == "create" and feature_name:
                # 使用AI收集需求并生成文档
                collect_result = requirement_tool.collect_requirements_with_ai(
                    feature_name, requirement_type
                )
                
                if collect_result.get("status") == "generated":
                    # 生成文档
                    requirement_data = collect_result["requirement_data"]
                    result = requirement_tool.generate_requirement_document(requirement_data)
                else:
                    result = collect_result
            else:
                error_msg = "请提供必需的参数："
                if mode == "create":
                    error_msg += "create模式需要feature_name"
                elif mode == "get":
                    error_msg += "get模式需要requirement_id"
                elif mode == "refine":
                    error_msg += "refine模式需要requirement_id和user_feedback"
                else:
                    error_msg += "无效的模式或缺少参数"
                
                result = {
                    "success": False,
                    "error": error_msg
                }
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"CreateRequirement tool execution failed: {str(e)}"
            }

def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(description="CodeLens 创造模式 - 需求确认工具")
    parser.add_argument("project_path", nargs="?", default=".", 
                        help="项目路径 (默认: 当前目录)")
    parser.add_argument("--feature-name", required=False,
                        help="功能名称")
    parser.add_argument("--mode", choices=["interactive", "batch"], default="interactive",
                        help="执行模式 (默认: interactive)")
    parser.add_argument("--requirement-type", choices=["new_feature", "enhancement", "fix"], 
                        default="new_feature", help="需求类型 (默认: new_feature)")
    parser.add_argument("--list", action="store_true",
                        help="列出现有需求文档")
    parser.add_argument("--get-requirement", 
                        help="获取指定ID的需求文档")
    parser.add_argument("--refine-requirement",
                        help="完善指定ID的需求文档")
    parser.add_argument("--user-feedback",
                        help="用户反馈内容 (用于refine模式)")
    
    args = parser.parse_args()
    
    try:
        # 初始化需求确认工具
        requirement_tool = CreateRequirementCore(args.project_path)
        
        if args.list:
            # 列出需求文档
            result = requirement_tool.list_requirements()
        elif args.get_requirement:
            # 获取指定需求文档
            result = requirement_tool.get_requirement_by_id(args.get_requirement)
        elif args.refine_requirement and args.user_feedback:
            # 完善指定需求文档
            result = requirement_tool.refine_requirement_with_feedback(
                args.refine_requirement, args.user_feedback
            )
        elif args.feature_name:
            # 使用AI收集需求并生成文档
            collect_result = requirement_tool.collect_requirements_with_ai(
                args.feature_name, args.requirement_type
            )
            
            if collect_result.get("status") == "generated":
                # 生成文档
                requirement_data = collect_result["requirement_data"]
                result = requirement_tool.generate_requirement_document(requirement_data)
            else:
                result = collect_result
        else:
            # 显示帮助信息
            result = {
                "tool": "create_requirement",
                "mode": "help",
                "message": "请提供 --feature-name 参数或使用 --list 查看现有需求",
                "usage_examples": [
                    f"python {sys.argv[0]} /path/to/project --feature-name '用户登录功能'",
                    f"python {sys.argv[0]} /path/to/project --list",
                    f"python {sys.argv[0]} /path/to/project --get-requirement req_login_1234567890",
                    f"python {sys.argv[0]} /path/to/project --refine-requirement req_login_1234567890 --user-feedback '需要支持第三方登录'"
                ]
            }
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "tool": "create_requirement"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()