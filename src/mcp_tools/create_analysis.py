#!/usr/bin/env python3
"""
CodeLens 创造模式 - 分析实现工具 (create_analysis)
第二阶段：基于架构文档分析实现方案和影响链
"""

import sys
import json
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 导入日志系统
try:
    # 添加项目根目录到path
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, project_root)
    from src.logging import get_logger
    from src.templates.document_templates import TemplateService
    from src.services.file_service import FileService
except ImportError:
    # 如果依赖不可用，创建空实现
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
        def __init__(self, *args, **kwargs): pass
        def scan_source_files(self, *args, **kwargs):
            return []
            
    TemplateService = DummyTemplateService
    FileService = DummyFileService

class CreateAnalysisCore:
    """创造模式第二阶段：分析实现工具"""
    
    def __init__(self, project_path: str):
        """初始化"""
        self.logger = get_logger(component="CreateAnalysisCore", operation="init")
        self.project_path = Path(project_path).resolve()
        self.create_docs_path = self.project_path / "docs" / "project" / "create"
        self.requirements_dir = self.create_docs_path / "requirements"
        self.analysis_dir = self.create_docs_path / "analysis"
        self.architecture_docs_path = self.project_path / "docs" / "architecture"
        
        self.template_service = TemplateService()
        self.file_service = FileService()
        
        # 确保目录存在
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("CreateAnalysisCore 初始化", {
            "project_path": str(self.project_path),
            "analysis_dir": str(self.analysis_dir),
            "architecture_docs_path": str(self.architecture_docs_path)
        })
    
    def analyze_project_context(self) -> Dict[str, Any]:
        """分析项目上下文，为AI分析提供基础信息"""
        operation_id = self.logger.log_operation_start("analyze_project_context")
        
        try:
            context = {
                "project_name": self.project_path.name,
                "project_type": "Unknown",
                "tech_stack": [],
                "file_structure": {},
                "architecture_docs": [],
                "existing_services": [],
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
                
                # 分析现有服务和模块
                for file_path in scan_result:
                    if "service" in file_path.lower() or "api" in file_path.lower():
                        context["existing_services"].append(file_path)
                        
            except Exception as e:
                self.logger.warning(f"Failed to scan project files: {e}")
            
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
            
            # 扫描架构文档
            if self.architecture_docs_path.exists():
                for arch_file in self.architecture_docs_path.glob("**/*.md"):
                    context["architecture_docs"].append(str(arch_file.relative_to(self.project_path)))
            
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
    
    def generate_ai_analysis_content(self, field_name: str, feature_name: str, context: Dict[str, Any], requirement_info: Dict[str, Any]) -> str:
        """基于项目上下文和需求信息生成AI分析内容"""
        project_type = context.get("project_type", "Application")
        tech_stack = context.get("tech_stack", [])
        existing_services = context.get("existing_services", [])
        architecture_docs = context.get("architecture_docs", [])
        
        if field_name == "architecture_impact":
            if "缓存" in feature_name:
                return f"实现{feature_name}将在{project_type}中引入新的缓存层架构。需要考虑缓存策略、数据一致性、失效机制等关键架构决策。建议采用Redis或内存缓存方案，确保与现有数据访问层的无缝集成。"
            elif "认证" in feature_name or "登录" in feature_name:
                return f"{feature_name}将影响{project_type}的安全架构。需要集成认证中间件、会话管理、权限控制等组件。建议采用JWT或Session-based认证机制，确保与现有API端点的安全集成。"
            elif "API" in feature_name:
                return f"{feature_name}将扩展{project_type}的API架构。需要考虑路由设计、请求处理、响应格式、错误处理等架构层面的变更。建议遵循RESTful设计原则，确保API版本兼容性。"
            else:
                return f"{feature_name}将对{project_type}产生架构层面的影响。需要分析现有组件依赖关系，确定新增模块的架构位置，评估对整体系统设计的影响。"
                
        elif field_name == "existing_components":
            if existing_services:
                services_list = "、".join(existing_services[:3])
                return f"当前系统包含以下主要组件：{services_list}等。{feature_name}需要与这些现有组件进行集成，确保功能协调和数据一致性。"
            else:
                return f"需要详细分析{project_type}的现有组件结构，识别与{feature_name}相关的核心模块，评估集成复杂度。"
                
        elif field_name == "new_components":
            if "缓存" in feature_name:
                return f"需要新增缓存管理器、缓存策略配置、缓存监控等组件。建议创建独立的缓存服务模块，提供统一的缓存接口。"
            elif "认证" in feature_name:
                return f"需要新增认证服务、会话管理器、权限验证中间件等组件。建议创建独立的认证模块，提供统一的用户验证接口。"
            else:
                return f"基于{feature_name}的功能需求，需要新增相应的服务组件、数据模型、业务逻辑处理器等核心组件。"
                
        elif field_name == "data_structure_changes":
            if "缓存" in feature_name:
                return f"需要新增缓存键值结构设计、缓存数据模型、TTL配置等数据结构。可能需要修改现有数据访问层以支持缓存查询。"
            elif "认证" in feature_name:
                return f"需要新增用户认证表、会话存储结构、权限配置表等。可能需要修改现有用户相关数据模型以支持认证功能。"
            else:
                return f"根据{feature_name}的业务需求，需要分析并设计相应的数据结构变更，包括新增表/集合、修改现有模型、索引优化等。"
                
        elif field_name == "dependency_changes":
            if "Python" in tech_stack:
                if "缓存" in feature_name:
                    return "可能需要新增Redis客户端库（如redis-py）、内存缓存库等依赖。需要更新requirements.txt配置。"
                elif "认证" in feature_name:
                    return "可能需要新增认证库（如PyJWT、Flask-Login）、密码加密库等依赖。需要更新requirements.txt配置。"
                else:
                    return f"根据{feature_name}的技术需求，可能需要新增相关Python库依赖，需要评估对现有依赖树的影响。"
            elif "JavaScript/Node.js" in tech_stack:
                return f"可能需要新增NPM包依赖，需要更新package.json配置，评估与现有Node.js模块的兼容性。"
            else:
                return f"需要分析{feature_name}的技术依赖需求，评估新增依赖对现有技术栈的影响。"
                
        elif field_name == "interface_impact":
            if "API" in feature_name:
                return f"{feature_name}将新增多个API端点，需要确保与现有API的一致性。建议遵循现有API设计规范，保持响应格式统一。"
            elif "认证" in feature_name:
                return f"{feature_name}将影响所有需要权限控制的API接口。需要在现有端点中集成认证中间件，可能导致接口行为变更。"
            else:
                return f"{feature_name}可能影响现有接口的调用方式和响应格式。需要评估对客户端和其他服务调用的影响。"
                
        else:
            return f"基于{feature_name}的具体需求和{project_type}的技术特点，需要进行详细的技术分析和评估。"
        
    def generate_analysis_id(self, requirement_id: str) -> str:
        """生成分析ID"""
        timestamp = int(time.time())
        return f"analysis_{requirement_id}_{timestamp}"
    
    def load_requirement_document(self, requirement_id: str) -> Dict[str, Any]:
        """加载需求文档"""
        operation_id = self.logger.log_operation_start("load_requirement_document", 
            requirement_id=requirement_id
        )
        
        try:
            req_file = self.requirements_dir / f"{requirement_id}.md"
            
            if not req_file.exists():
                return {
                    "success": False,
                    "error": f"Requirement document {requirement_id} not found"
                }
            
            # 读取需求文档内容
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单解析需求信息（实际实现中可以更复杂）
            requirement_info = {
                "requirement_id": requirement_id,
                "content": content,
                "file_path": str(req_file)
            }
            
            # 尝试从内容中提取功能名称
            lines = content.split('\n')
            feature_name = "未知功能"
            for line in lines:
                if "功能名称" in line and "**" in line:
                    parts = line.split("**")
                    if len(parts) >= 3:
                        feature_name = parts[2].strip()
                        break
            
            requirement_info["feature_name"] = feature_name
            
            self.logger.log_operation_end("load_requirement_document", operation_id, 
                success=True, feature_name=feature_name
            )
            
            return {
                "success": True,
                "requirement_info": requirement_info
            }
            
        except Exception as e:
            self.logger.log_operation_end("load_requirement_document", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to load requirement document: {str(e)}"
            }
    
    def detect_project_maturity(self) -> Dict[str, Any]:
        """检测项目成熟度，判断是否有完整的架构文档"""
        operation_id = self.logger.log_operation_start("detect_project_maturity")
        
        try:
            maturity_info = {
                "is_mature_project": False,
                "architecture_docs_exist": False,
                "architecture_docs_count": 0,
                "total_architecture_size": 0,
                "key_docs_found": [],
                "maturity_level": "new",  # new, developing, mature
                "analysis_strategy": "direct_design"  # direct_design, hybrid, architecture_based
            }
            
            # 检查架构文档目录是否存在
            if not self.architecture_docs_path.exists():
                maturity_info["analysis_strategy"] = "direct_design"
                self.logger.log_operation_end("detect_project_maturity", operation_id, 
                    success=True, maturity_level="new"
                )
                return maturity_info
                
            maturity_info["architecture_docs_exist"] = True
            
            # 扫描架构文档
            arch_files = list(self.architecture_docs_path.glob("*.md"))
            arch_files.extend(list(self.architecture_docs_path.glob("**/*.md")))
            
            maturity_info["architecture_docs_count"] = len(arch_files)
            
            # 核心架构文档检查
            key_docs = ["overview.md", "tech-stack.md", "data-flow.md", "architecture.md", "design.md"]
            
            total_size = 0
            for arch_file in arch_files:
                file_size = arch_file.stat().st_size
                total_size += file_size
                
                # 检查是否是关键文档
                if arch_file.name.lower() in [doc.lower() for doc in key_docs]:
                    maturity_info["key_docs_found"].append({
                        "filename": arch_file.name,
                        "size": file_size,
                        "is_substantial": file_size > 1000  # 大于1KB认为是实质性文档
                    })
            
            maturity_info["total_architecture_size"] = total_size
            
            # 判断成熟度级别
            substantial_key_docs = len([doc for doc in maturity_info["key_docs_found"] if doc["is_substantial"]])
            
            if maturity_info["architecture_docs_count"] == 0:
                maturity_info["maturity_level"] = "new"
                maturity_info["analysis_strategy"] = "direct_design"
            elif maturity_info["architecture_docs_count"] < 3 or substantial_key_docs == 0:
                maturity_info["maturity_level"] = "developing" 
                maturity_info["analysis_strategy"] = "hybrid"
            elif substantial_key_docs >= 2 and total_size > 5000:  # 至少2个实质性关键文档，总大小>5KB
                maturity_info["maturity_level"] = "mature"
                maturity_info["analysis_strategy"] = "architecture_based"
                maturity_info["is_mature_project"] = True
            else:
                maturity_info["maturity_level"] = "developing"
                maturity_info["analysis_strategy"] = "hybrid"
            
            self.logger.log_operation_end("detect_project_maturity", operation_id, 
                success=True, 
                maturity_level=maturity_info["maturity_level"],
                docs_count=maturity_info["architecture_docs_count"],
                strategy=maturity_info["analysis_strategy"]
            )
            
            return maturity_info
            
        except Exception as e:
            self.logger.log_operation_end("detect_project_maturity", operation_id, 
                success=False, error=str(e)
            )
            # 默认返回新项目状态
            return {
                "is_mature_project": False,
                "architecture_docs_exist": False,
                "architecture_docs_count": 0,
                "total_architecture_size": 0,
                "key_docs_found": [],
                "maturity_level": "new",
                "analysis_strategy": "direct_design",
                "error_note": f"检测失败: {str(e)}"
            }
    
    def analyze_architecture_impact_adaptive(self, requirement_info: Dict[str, Any]) -> Dict[str, Any]:
        """自适应架构影响分析 - 根据项目成熟度采用不同策略"""
        operation_id = self.logger.log_operation_start("analyze_architecture_impact_adaptive", 
            requirement_id=requirement_info.get("requirement_id")
        )
        
        try:
            # 检测项目成熟度
            maturity_info = self.detect_project_maturity()
            strategy = maturity_info["analysis_strategy"]
            
            # 获取项目上下文
            context = self.analyze_project_context()
            feature_name = requirement_info.get("feature_name", "")
            
            # 基础分析结构
            architecture_analysis = {
                "project_maturity": maturity_info,
                "analysis_strategy": strategy,
                "architecture_docs_found": [],
                "architecture_impact": "",
                "existing_components": "", 
                "new_components": ""
            }
            
            if strategy == "direct_design":
                # 新项目策略：直接基于需求设计，不分析现有架构
                architecture_analysis.update({
                    "architecture_impact": self.generate_direct_design_analysis(feature_name, requirement_info, "architecture_impact"),
                    "existing_components": "新项目无现有组件，将从零开始设计",
                    "new_components": self.generate_direct_design_analysis(feature_name, requirement_info, "new_components")
                })
                
                self.logger.info("使用直接设计策略", {
                    "strategy": "direct_design",
                    "reason": "项目缺少架构文档，采用从零设计策略"
                })
                
            elif strategy == "architecture_based":
                # 成熟项目策略：基于现有架构文档进行分析
                architecture_analysis.update(self.analyze_existing_architecture(requirement_info, context))
                
                self.logger.info("使用架构分析策略", {
                    "strategy": "architecture_based", 
                    "docs_count": maturity_info["architecture_docs_count"],
                    "key_docs": len(maturity_info["key_docs_found"])
                })
                
            else:  # hybrid strategy
                # 混合策略：结合现有文档和直接设计
                existing_analysis = self.analyze_existing_architecture(requirement_info, context)
                direct_analysis = {
                    "architecture_impact": self.generate_direct_design_analysis(feature_name, requirement_info, "architecture_impact"),
                    "new_components": self.generate_direct_design_analysis(feature_name, requirement_info, "new_components")
                }
                
                architecture_analysis.update({
                    "architecture_impact": f"基于有限的架构文档分析：{existing_analysis['architecture_impact']}。补充设计考虑：{direct_analysis['architecture_impact']}",
                    "existing_components": existing_analysis["existing_components"],
                    "new_components": f"结合现有架构和新设计：{direct_analysis['new_components']}"
                })
                
                self.logger.info("使用混合分析策略", {
                    "strategy": "hybrid",
                    "reason": "项目有部分架构文档但不完整"
                })
            
            self.logger.log_operation_end("analyze_architecture_impact_adaptive", operation_id, 
                success=True, 
                strategy=strategy,
                docs_found=len(architecture_analysis["architecture_docs_found"])
            )
            
            return architecture_analysis
            
        except Exception as e:
            self.logger.log_operation_end("analyze_architecture_impact_adaptive", operation_id, 
                success=False, error=str(e)
            )
            return {
                "project_maturity": {"maturity_level": "unknown", "analysis_strategy": "direct_design"},
                "analysis_strategy": "direct_design",
                "architecture_docs_found": [],
                "architecture_impact": "架构影响分析失败，建议基于需求直接设计",
                "existing_components": "组件分析失败，需要手动确定", 
                "new_components": "新组件设计失败，需要手动确定",
                "error_note": f"自适应分析失败: {str(e)}"
            }
    
    def generate_direct_design_analysis(self, feature_name: str, requirement_info: Dict[str, Any], field_type: str) -> str:
        """为新项目生成直接设计分析"""
        user_description = requirement_info.get("user_description", "")
        
        if field_type == "architecture_impact":
            return f"新项目架构设计：{feature_name}将作为核心功能模块实现。建议采用模块化架构，确保功能的独立性和可扩展性。基于需求'{user_description[:100]}...'，建议重点考虑功能的接口设计、数据流向和错误处理机制。"
        elif field_type == "new_components":
            return f"新项目组件设计：为实现{feature_name}，建议创建以下新组件：1) 核心业务逻辑组件；2) 数据处理组件；3) 接口适配组件；4) 配置管理组件。每个组件应有清晰的职责分工和接口定义。"
        else:
            return f"基于需求直接设计{feature_name}相关的{field_type}组件。"
    
    def analyze_existing_architecture(self, requirement_info: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """分析现有架构（原有逻辑的重构版本）"""
        feature_name = requirement_info.get("feature_name", "")
        
        analysis = {
            "architecture_docs_found": [],
            "architecture_impact": self.generate_ai_analysis_content("architecture_impact", feature_name, context, requirement_info),
            "existing_components": self.generate_ai_analysis_content("existing_components", feature_name, context, requirement_info),
            "new_components": self.generate_ai_analysis_content("new_components", feature_name, context, requirement_info)
        }
        
        # 扫描架构文档目录
        if self.architecture_docs_path.exists():
            arch_files = list(self.architecture_docs_path.glob("*.md"))
            arch_files.extend(list(self.architecture_docs_path.glob("**/*.md")))
            
            for arch_file in arch_files:
                analysis["architecture_docs_found"].append({
                    "filename": arch_file.name,
                    "path": str(arch_file.relative_to(self.project_path)),
                    "size": arch_file.stat().st_size
                })
        
        return analysis
    
    def analyze_architecture_impact(self, requirement_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析架构影响（保持向后兼容的包装方法）"""
        # 调用新的自适应方法
        return self.analyze_architecture_impact_adaptive(requirement_info)
    
    def analyze_code_impact(self, requirement_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析代码影响"""
        operation_id = self.logger.log_operation_start("analyze_code_impact", 
            requirement_id=requirement_info.get("requirement_id")
        )
        
        try:
            # 扫描项目文件
            scan_result = self.file_service.scan_source_files(str(self.project_path))
            
            # 获取项目上下文
            context = self.analyze_project_context()
            feature_name = requirement_info.get("feature_name", "")
            
            code_analysis = {
                "total_project_files": len(scan_result) if scan_result else 0,
                "main_files_to_modify": [],
                "core_functions_classes": [],
                "data_structure_changes": self.generate_ai_analysis_content("data_structure_changes", feature_name, context, requirement_info),
                "directly_affected_files": [],
                "indirectly_affected_files": [],
                "dependency_changes": self.generate_ai_analysis_content("dependency_changes", feature_name, context, requirement_info),
                "interface_impact": self.generate_ai_analysis_content("interface_impact", feature_name, context, requirement_info)
            }
            
            # 基于功能名称推断可能影响的文件（简化实现）
            feature_name_lower = feature_name.lower()
            all_files = scan_result if scan_result else []
            
            # 分析主要修改文件
            for file_path in all_files:
                if any(keyword in file_path.lower() for keyword in ["main", "core", "service", "api"]):
                    code_analysis["main_files_to_modify"].append(file_path)
            
            # 分析直接影响的文件
            for file_info in all_files:
                file_path = file_info.get("relative_path", "")
                if any(keyword in feature_name for keyword in ["api", "service", "user", "data"] 
                       if keyword in file_path.lower()):
                    code_analysis["directly_affected_files"].append(file_path)
            
            # 限制数量避免过多
            code_analysis["main_files_to_modify"] = code_analysis["main_files_to_modify"][:10]
            code_analysis["directly_affected_files"] = code_analysis["directly_affected_files"][:15]
            
            self.logger.log_operation_end("analyze_code_impact", operation_id, 
                success=True, files_analyzed=len(all_files)
            )
            
            return code_analysis
            
        except Exception as e:
            self.logger.log_operation_end("analyze_code_impact", operation_id, 
                success=False, error=str(e)
            )
            # 返回包含所有必需字段的默认值
            return {
                "total_project_files": 0,
                "main_files_to_modify": "分析失败，需要手动确定",
                "core_functions_classes": "分析失败，需要手动确定",
                "data_structure_changes": "需要分析数据结构变更",
                "directly_affected_files": "分析失败，需要手动确定",
                "indirectly_affected_files": "分析失败，需要手动确定",
                "dependency_changes": "分析依赖关系变更",
                "interface_impact": "评估接口变更影响",
                "error_note": f"代码影响分析失败: {str(e)}"
            }
    
    def generate_implementation_strategy(self, requirement_info: Dict[str, Any], 
                                       architecture_analysis: Dict[str, Any],
                                       code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成实现策略"""
        operation_id = self.logger.log_operation_start("generate_implementation_strategy", 
            requirement_id=requirement_info.get("requirement_id")
        )
        
        try:
            # 获取项目上下文
            context = self.analyze_project_context()
            feature_name = requirement_info.get("feature_name", "")
            project_type = context.get("project_type", "Application")
            tech_stack = context.get("tech_stack", [])
            
            # 生成AI驱动的实现策略
            if "缓存" in feature_name:
                tech_choices = f"基于{', '.join(tech_stack[:2]) if tech_stack else 'current tech stack'}实现缓存层，推荐使用Redis作为缓存后端，内存缓存作为L1缓存"
                implementation_steps = [
                    "1. 设计缓存键值结构和TTL策略",
                    "2. 实现缓存管理器和缓存接口",
                    "3. 集成现有数据访问层",
                    "4. 实现缓存失效和更新机制",
                    "5. 添加缓存监控和性能测试"
                ]
                key_points = ["缓存一致性保证", "缓存穿透防护", "热点数据识别", "内存使用优化"]
                risks = ["缓存雪崩风险", "数据一致性挑战", "内存泄漏风险", "缓存击穿问题"]
            elif "认证" in feature_name or "登录" in feature_name:
                tech_choices = f"基于{', '.join(tech_stack[:2]) if tech_stack else 'current tech stack'}实现认证系统，推荐JWT或Session-based认证"
                implementation_steps = [
                    "1. 设计用户认证数据模型",
                    "2. 实现认证服务和中间件",
                    "3. 集成现有API端点安全控制",
                    "4. 实现会话管理和权限控制",
                    "5. 添加安全测试和审计日志"
                ]
                key_points = ["密码安全存储", "会话管理策略", "权限控制设计", "安全漏洞防护"]
                risks = ["安全漏洞风险", "认证性能影响", "会话存储压力", "权限设计复杂性"]
            else:
                tech_choices = f"基于现有{project_type}技术栈和{', '.join(tech_stack[:2]) if tech_stack else 'current technologies'}进行实现"
                implementation_steps = [
                    "1. 分析需求并设计技术方案",
                    "2. 实现核心业务逻辑",
                    "3. 集成现有系统组件",
                    "4. 完善测试覆盖",
                    "5. 部署验证和监控"
                ]
                key_points = ["架构一致性", "向后兼容性", "性能优化", "可维护性"]
                risks = ["技术实现复杂度", "系统集成挑战", "性能影响评估", "维护成本增加"]
                
            strategy = {
                "technology_choices": tech_choices,
                "implementation_steps": implementation_steps,
                "key_technical_points": key_points,
                "potential_risks": risks,
                "unit_test_strategy": f"针对{feature_name}核心功能编写单元测试，确保关键业务逻辑正确性",
                "integration_test_strategy": "设计集成测试验证功能完整性",
                "regression_test_strategy": "确保现有功能不受影响",
                "performance_impact": "评估对系统性能的影响",
                "optimization_suggestions": "性能优化建议",
                "backward_compatibility": "确保向后兼容性",
                "api_compatibility": "保持API接口兼容性",
                "deployment_impact": "评估部署相关影响",
                "configuration_changes": "配置变更说明",
                "data_migration": "数据迁移方案",
                "implementation_recommendations": "实现建议和最佳实践",
                "risk_mitigation": "风险缓解措施",
                "next_actions": "下一步行动计划",
                "pending_confirmations": "等待确认的关键决策点"
            }
            
            self.logger.log_operation_end("generate_implementation_strategy", operation_id, 
                success=True
            )
            
            return strategy
            
        except Exception as e:
            self.logger.log_operation_end("generate_implementation_strategy", operation_id, 
                success=False, error=str(e)
            )
            # 返回包含所有必需字段的默认值
            return {
                "technology_choices": "技术选型分析失败，需要手动确定",
                "implementation_steps": "实现步骤分析失败，需要手动确定",
                "key_technical_points": "关键技术点分析失败，需要手动确定",
                "potential_risks": "风险评估失败，需要手动确定",
                "unit_test_strategy": "单元测试策略分析失败，需要手动确定",
                "integration_test_strategy": "集成测试策略分析失败，需要手动确定",
                "regression_test_strategy": "回归测试策略分析失败，需要手动确定",
                "performance_impact": "性能影响评估失败，需要手动确定",
                "optimization_suggestions": "优化建议分析失败，需要手动确定",
                "backward_compatibility": "向后兼容性分析失败，需要手动确定",
                "api_compatibility": "API兼容性分析失败，需要手动确定",
                "deployment_impact": "部署影响评估失败，需要手动确定",
                "configuration_changes": "配置变更分析失败，需要手动确定",
                "data_migration": "数据迁移分析失败，需要手动确定",
                "implementation_recommendations": "实现建议分析失败，需要手动确定",
                "risk_mitigation": "风险缓解措施分析失败，需要手动确定",
                "next_actions": "下一步行动分析失败，需要手动确定",
                "pending_confirmations": "待确认事项分析失败，需要手动确定",
                "error_note": f"实现策略分析失败: {str(e)}"
            }
    
    def create_analysis_report(self, requirement_id: str, analysis_depth: str = "detailed", 
                             include_tests: bool = True) -> Dict[str, Any]:
        """创建分析报告"""
        operation_id = self.logger.log_operation_start("create_analysis_report", 
            requirement_id=requirement_id, analysis_depth=analysis_depth
        )
        
        try:
            # 1. 加载需求文档
            requirement_result = self.load_requirement_document(requirement_id)
            if not requirement_result.get("success"):
                return requirement_result
            
            requirement_info = requirement_result["requirement_info"]
            
            # 2. 分析架构影响
            architecture_analysis = self.analyze_architecture_impact(requirement_info)
            
            # 3. 分析代码影响
            code_analysis = self.analyze_code_impact(requirement_info)
            
            # 4. 生成实现策略
            implementation_strategy = self.generate_implementation_strategy(
                requirement_info, architecture_analysis, code_analysis
            )
            
            # 5. 生成分析ID
            analysis_id = self.generate_analysis_id(requirement_id)
            
            # 6. 准备模板数据
            template_data = {
                "feature_name": requirement_info.get("feature_name"),
                "requirement_id": requirement_id,
                "analysis_id": analysis_id,
                "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "analyzer": "CodeLens 创造模式分析工具",
                
                # 架构分析数据
                **architecture_analysis,
                
                # 代码分析数据
                **code_analysis,
                
                # 实现策略数据
                **implementation_strategy
            }
            
            # 处理列表字段，转换为字符串
            for key, value in template_data.items():
                if isinstance(value, list):
                    if key.endswith('_files') or 'files' in key:
                        template_data[key] = '\n'.join(f"- {item}" for item in value)
                    else:
                        template_data[key] = '\n'.join(f"- {item}" for item in value)
            
            # 7. 生成分析文档
            doc_result = self.generate_analysis_document(analysis_id, template_data)
            
            if doc_result.get("success", True):
                result = {
                    "tool": "create_analysis",
                    "mode": "create_report",
                    "analysis_id": analysis_id,
                    "requirement_id": requirement_id,
                    "status": "completed",
                    
                    "analysis_summary": {
                        "feature_name": requirement_info.get("feature_name"),
                        "analysis_depth": analysis_depth,
                        "include_tests": include_tests,
                        "total_files_analyzed": code_analysis.get("total_project_files", 0),
                        "architecture_docs_found": len(architecture_analysis.get("architecture_docs_found", []))
                    },
                    
                    "document_info": doc_result.get("document_info", {}),
                    
                    "next_stage": {
                        "stage": 3,
                        "tool": "create_todo",
                        "command": f"python src/mcp_tools/create_todo.py {self.project_path} --analysis-id {analysis_id}",
                        "description": "生成详细实现计划",
                        "note": "请先确认分析结果再进入下一阶段"
                    },
                    
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = doc_result
            
            self.logger.log_operation_end("create_analysis_report", operation_id, 
                success=True, analysis_id=analysis_id
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("create_analysis_report", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to create analysis report: {str(e)}"
            }
    
    def generate_analysis_document(self, analysis_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析文档"""
        operation_id = self.logger.log_operation_start("generate_analysis_document", 
            analysis_id=analysis_id
        )
        
        try:
            # 获取分析模板
            template_result = self.template_service.get_template_content("create_analysis")
            if not template_result.get("success", True):
                return {
                    "success": False,
                    "error": f"Failed to get analysis template: {template_result.get('error', 'Unknown error')}"
                }
            
            # 格式化模板
            format_result = self.template_service.format_template("create_analysis", **template_data)
            if not format_result.get("success", True):
                return {
                    "success": False,
                    "error": f"Failed to format analysis template: {format_result.get('error', 'Unknown error')}"
                }
            
            # 生成文档文件
            doc_filename = f"{analysis_id}.md"
            doc_filepath = self.analysis_dir / doc_filename
            
            # 写入文档
            with open(doc_filepath, 'w', encoding='utf-8') as f:
                f.write(format_result["formatted_content"])
            
            result = {
                "success": True,
                "document_info": {
                    "filename": doc_filename,
                    "filepath": str(doc_filepath),
                    "file_size": doc_filepath.stat().st_size,
                    "created_time": datetime.now().isoformat()
                }
            }
            
            self.logger.log_operation_end("generate_analysis_document", operation_id, 
                success=True, filepath=str(doc_filepath)
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("generate_analysis_document", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to generate analysis document: {str(e)}"
            }
    
    def list_analysis_reports(self) -> Dict[str, Any]:
        """列出分析报告"""
        operation_id = self.logger.log_operation_start("list_analysis_reports")
        
        try:
            reports = []
            
            if self.analysis_dir.exists():
                for analysis_file in self.analysis_dir.glob("*.md"):
                    file_stat = analysis_file.stat()
                    reports.append({
                        "filename": analysis_file.name,
                        "analysis_id": analysis_file.stem,
                        "filepath": str(analysis_file),
                        "created_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "file_size": file_stat.st_size
                    })
            
            # 按创建时间排序
            reports.sort(key=lambda x: x["created_time"], reverse=True)
            
            result = {
                "tool": "create_analysis",
                "mode": "list_reports",
                "total_count": len(reports),
                "analysis_reports": reports,
                "analysis_dir": str(self.analysis_dir),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.log_operation_end("list_analysis_reports", operation_id, 
                success=True, count=len(reports)
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("list_analysis_reports", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to list analysis reports: {str(e)}"
            }

class CreateAnalysisTool:
    """创造模式分析实现工具 - MCP接口"""
    
    def __init__(self):
        self.tool_name = "create_analysis"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取工具定义"""
        return {
            "name": self.tool_name,
            "description": "🔍 CodeLens创造模式第二阶段 - 基于架构文档分析实现方案和影响链",
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
                        "enum": ["create", "list"],
                        "description": "执行模式: create=创建分析报告, list=列出分析报告",
                        "default": "create"
                    },
                    "requirement_id": {
                        "type": "string",
                        "description": "需求文档ID (create模式必需)"
                    },
                    "analysis_depth": {
                        "type": "string",
                        "enum": ["basic", "detailed", "comprehensive"],
                        "description": "分析深度",
                        "default": "detailed"
                    },
                    "include_tests": {
                        "type": "boolean",
                        "description": "是否包含测试分析",
                        "default": True
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
            requirement_id = arguments.get("requirement_id")
            analysis_depth = arguments.get("analysis_depth", "detailed")
            include_tests = arguments.get("include_tests", True)
            
            # 初始化分析工具
            analysis_tool = CreateAnalysisCore(project_path)
            
            if mode == "list":
                # 列出分析报告
                result = analysis_tool.list_analysis_reports()
            elif mode == "create" and requirement_id:
                # 创建分析报告
                result = analysis_tool.create_analysis_report(
                    requirement_id, analysis_depth, include_tests
                )
            else:
                result = {
                    "success": False,
                    "error": "请提供必需的参数：create模式需要requirement_id"
                }
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"CreateAnalysis tool execution failed: {str(e)}"
            }

def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(description="CodeLens 创造模式 - 分析实现工具")
    parser.add_argument("project_path", nargs="?", default=".", 
                        help="项目路径 (默认: 当前目录)")
    parser.add_argument("--requirement-id", required=False,
                        help="需求文档ID")
    parser.add_argument("--analysis-depth", choices=["basic", "detailed", "comprehensive"], 
                        default="detailed", help="分析深度 (默认: detailed)")
    parser.add_argument("--include-tests", action="store_true", default=True,
                        help="是否包含测试分析 (默认: True)")
    parser.add_argument("--list", action="store_true",
                        help="列出现有分析报告")
    
    args = parser.parse_args()
    
    try:
        # 初始化分析工具
        analysis_tool = CreateAnalysisCore(args.project_path)
        
        if args.list:
            # 列出分析报告
            result = analysis_tool.list_analysis_reports()
        elif args.requirement_id:
            # 创建分析报告
            result = analysis_tool.create_analysis_report(
                args.requirement_id, args.analysis_depth, args.include_tests
            )
        else:
            # 显示帮助信息
            result = {
                "tool": "create_analysis",
                "mode": "help",
                "message": "请提供 --requirement-id 参数或使用 --list 查看现有分析报告",
                "usage_examples": [
                    f"python {sys.argv[0]} /path/to/project --requirement-id req_login_1234567890",
                    f"python {sys.argv[0]} /path/to/project --list",
                    f"python {sys.argv[0]} /path/to/project --requirement-id req_login_1234567890 --analysis-depth comprehensive"
                ]
            }
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "tool": "create_analysis"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()