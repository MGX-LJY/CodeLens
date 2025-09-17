#!/usr/bin/env python3
"""
CodeLens 创造模式 - Todo生成工具 (create_todo)
第三阶段：基于确认的分析报告生成详细实现计划
"""

import sys
import json
import argparse
import time
from pathlib import Path
from datetime import datetime, timedelta
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
        def scan_source_files(self, *args, **kwargs):
            return []
            
    TemplateService = DummyTemplateService
    FileService = DummyFileService

class CreateTodoCore:
    """创造模式第三阶段：Todo生成工具"""
    
    def __init__(self, project_path: str):
        """初始化"""
        self.logger = get_logger(component="CreateTodoCore", operation="init")
        self.project_path = Path(project_path).resolve()
        self.create_docs_path = self.project_path / "docs" / "project" / "create"
        self.analysis_dir = self.create_docs_path / "analysis"
        self.todos_dir = self.create_docs_path / "todos"
        
        self.template_service = TemplateService()
        self.file_service = FileService()
        
        # 确保目录存在
        self.todos_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("CreateTodoCore 初始化", {
            "project_path": str(self.project_path),
            "todos_dir": str(self.todos_dir)
        })
    
    def analyze_project_context(self) -> Dict[str, Any]:
        """分析项目上下文，为AI生成Todo提供基础信息"""
        operation_id = self.logger.log_operation_start("analyze_project_context")
        
        try:
            context = {
                "project_name": self.project_path.name,
                "project_type": "Unknown",
                "tech_stack": [],
                "file_structure": {},
                "existing_services": [],
                "test_structure": [],
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
                    elif "test" in file_path.lower():
                        context["test_structure"].append(file_path)
                        
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
    
    def generate_ai_todo_content(self, content_type: str, feature_name: str, context: Dict[str, Any], analysis_info: Dict[str, Any]) -> str:
        """基于项目上下文和分析信息生成AI Todo内容"""
        project_type = context.get("project_type", "Application")
        tech_stack = context.get("tech_stack", [])
        existing_services = context.get("existing_services", [])
        test_structure = context.get("test_structure", [])
        
        if content_type == "detailed_steps_phase1":
            if "Python" in tech_stack:
                return f"""1. 配置Python虚拟环境和依赖管理
2. 在src/services/目录下创建{feature_name.lower().replace(' ', '_')}_service.py模块
3. 设计{feature_name}的数据模型和API接口定义
4. 配置开发环境和调试工具，更新requirements.txt"""
            else:
                return f"""1. 配置{', '.join(tech_stack[:2]) if tech_stack else 'project'}开发环境
2. 创建{feature_name}相关的目录结构和基础文件
3. 设计数据模型和接口定义
4. 准备开发工具和依赖配置"""
                
        elif content_type == "detailed_steps_phase2":
            if "缓存" in feature_name:
                return f"""1. 实现缓存管理器核心类和接口
2. 创建缓存策略配置和TTL管理
3. 集成Redis客户端或内存缓存后端
4. 实现缓存键值生成和数据序列化逻辑
5. 与现有数据访问层进行集成"""
            elif "认证" in feature_name or "登录" in feature_name:
                return f"""1. 实现用户认证服务和会话管理
2. 创建JWT或Session认证中间件
3. 集成密码加密和验证逻辑
4. 实现权限控制和角色管理
5. 与现有API端点进行安全集成"""
            else:
                return f"""1. 实现{feature_name}的核心业务逻辑
2. 创建必要的服务类和工具函数
3. 实现数据处理和验证逻辑
4. 集成现有系统组件和服务
5. 添加错误处理和日志记录"""
                
        elif content_type == "detailed_steps_phase3":
            test_framework = ""
            if "Python" in tech_stack:
                if any("pytest" in str(f).lower() for f in test_structure):
                    test_framework = "使用pytest框架"
                else:
                    test_framework = "使用unittest框架"
            elif "JavaScript/Node.js" in tech_stack:
                test_framework = "使用Jest或Mocha测试框架"
            else:
                test_framework = "使用项目标准测试框架"
                
            return f"""1. {test_framework}编写{feature_name}单元测试
2. 创建集成测试验证功能完整性
3. 进行性能测试和压力测试
4. 执行安全性检查和漏洞扫描
5. 验证与现有系统的兼容性"""
            
        elif content_type == "detailed_steps_phase4":
            return f"""1. 更新项目技术文档和API规范
2. 编写{feature_name}用户使用指南和示例
3. 更新README.md和CHANGELOG.md文件
4. 准备部署脚本和配置文件
5. 创建运维监控和日志配置"""
            
        elif content_type == "new_files":
            safe_name = feature_name.lower().replace(' ', '_').replace('系统', 'system').replace('功能', 'feature')
            if "Python" in tech_stack:
                return f"""- src/services/{safe_name}_service.py: 核心服务实现
- src/models/{safe_name}_model.py: 数据模型定义
- tests/test_{safe_name}.py: 单元测试文件
- docs/features/{safe_name}_guide.md: 功能使用指南"""
            else:
                return f"""- src/{safe_name}_service.{tech_stack[0].split('/')[0].lower()}: 核心服务实现
- src/models/{safe_name}_model: 数据模型定义
- tests/test_{safe_name}: 测试文件
- docs/{safe_name}_guide.md: 功能使用指南"""
                
        elif content_type == "modified_files":
            if "Python" in tech_stack:
                main_file = "main.py" if any("main.py" in str(f) for f in context["file_structure"].get("files", [])) else "app.py"
                return f"""- src/{main_file}: 集成{feature_name}服务初始化
- src/routes/api.py: 添加{feature_name}相关API路由
- src/config/settings.py: 更新配置参数
- requirements.txt: 添加新的依赖包
- README.md: 更新功能说明和使用文档"""
            else:
                return f"""- 主应用文件: 集成{feature_name}服务
- 路由配置文件: 添加{feature_name}接口
- 配置文件: 更新相关设置
- 依赖配置文件: 添加新依赖
- README.md: 更新项目文档"""
                
        elif content_type == "function_changes_new":
            safe_name = feature_name.replace(' ', '').replace('系统', 'System').replace('功能', 'Feature')
            if "缓存" in feature_name:
                return f"""- class {safe_name}Manager: 缓存管理器核心类
- class CacheConfig: 缓存配置管理类
- def get_cache_key(): 生成缓存键值
- def set_cache(): 设置缓存数据
- def get_cache(): 获取缓存数据
- def invalidate_cache(): 清除缓存数据"""
            elif "认证" in feature_name:
                return f"""- class {safe_name}Service: 认证服务核心类
- class UserSession: 用户会话管理类
- def authenticate_user(): 用户认证验证
- def generate_token(): 生成认证令牌
- def verify_token(): 验证令牌有效性
- def logout_user(): 用户登出处理"""
            else:
                return f"""- class {safe_name}Service: {feature_name}核心服务类
- class {safe_name}Model: {feature_name}数据模型类
- def create_{safe_name.lower()}(): 创建{feature_name}
- def get_{safe_name.lower()}(): 获取{feature_name}
- def update_{safe_name.lower()}(): 更新{feature_name}
- def delete_{safe_name.lower()}(): 删除{feature_name}"""
                
        elif content_type == "testing_plan_unit":
            return f"""- test_{feature_name.lower().replace(' ', '_')}_creation(): 测试{feature_name}创建功能
- test_{feature_name.lower().replace(' ', '_')}_retrieval(): 测试{feature_name}获取功能
- test_{feature_name.lower().replace(' ', '_')}_update(): 测试{feature_name}更新功能
- test_{feature_name.lower().replace(' ', '_')}_deletion(): 测试{feature_name}删除功能
- test_{feature_name.lower().replace(' ', '_')}_validation(): 测试{feature_name}验证逻辑
- test_error_handling(): 测试异常处理机制"""
                
        else:
            return f"基于{feature_name}和{project_type}的具体需求进行详细规划和实现。"
        
    def generate_todo_id(self, analysis_id: str) -> str:
        """生成todo ID"""
        timestamp = int(time.time())
        return f"todo_{analysis_id}_{timestamp}"
    
    def load_analysis_document(self, analysis_id: str) -> Dict[str, Any]:
        """加载分析文档"""
        operation_id = self.logger.log_operation_start("load_analysis_document", 
            analysis_id=analysis_id
        )
        
        try:
            analysis_file = self.analysis_dir / f"{analysis_id}.md"
            
            if not analysis_file.exists():
                return {
                    "success": False,
                    "error": f"Analysis document {analysis_id} not found"
                }
            
            # 读取分析文档内容
            with open(analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单解析分析信息
            analysis_info = {
                "analysis_id": analysis_id,
                "content": content,
                "file_path": str(analysis_file)
            }
            
            # 尝试从内容中提取关键信息
            lines = content.split('\n')
            feature_name = "未知功能"
            requirement_id = ""
            
            for line in lines:
                if "功能名称" in line and "**" in line:
                    parts = line.split("**")
                    if len(parts) >= 3:
                        feature_name = parts[2].strip()
                elif "需求ID" in line and "**" in line:
                    parts = line.split("**")
                    if len(parts) >= 3:
                        requirement_id = parts[2].strip()
            
            analysis_info["feature_name"] = feature_name
            analysis_info["requirement_id"] = requirement_id
            
            self.logger.log_operation_end("load_analysis_document", operation_id, 
                success=True, feature_name=feature_name
            )
            
            return {
                "success": True,
                "analysis_info": analysis_info
            }
            
        except Exception as e:
            self.logger.log_operation_end("load_analysis_document", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to load analysis document: {str(e)}"
            }
    
    def generate_implementation_plan(self, analysis_info: Dict[str, Any], 
                                   todo_granularity: str = "function",
                                   include_testing: bool = True) -> Dict[str, Any]:
        """生成实现计划"""
        operation_id = self.logger.log_operation_start("generate_implementation_plan", 
            analysis_id=analysis_info.get("analysis_id")
        )
        
        try:
            feature_name = analysis_info.get("feature_name", "未知功能")
            
            # 生成总体策略
            overall_strategy = f"基于分析报告，采用分阶段实现'{feature_name}'功能的策略"
            
            # 生成实现阶段
            implementation_phases = [
                "阶段1：环境准备和基础架构搭建",
                "阶段2：核心功能逻辑实现",
                "阶段3：集成测试和验证",
                "阶段4：文档更新和部署准备"
            ]
            
            # 估算工时
            estimated_time = self._estimate_development_time(feature_name, todo_granularity)
            
            # 生成详细实现步骤
            detailed_steps = self._generate_detailed_steps(feature_name, include_testing)
            
            # 生成文件修改清单
            file_changes = self._generate_file_changes(feature_name)
            
            # 生成函数/类实现清单
            function_changes = self._generate_function_changes(feature_name, todo_granularity)
            
            # 生成测试计划
            test_plan = self._generate_test_plan(feature_name, include_testing)
            
            # 生成验证检查点
            verification_points = self._generate_verification_points(feature_name)
            
            # 生成风险控制
            risk_control = self._generate_risk_control(feature_name)
            
            # 生成依赖事项
            dependencies = self._generate_dependencies(feature_name)
            
            # 生成完成标准
            completion_criteria = self._generate_completion_criteria(feature_name)
            
            # 生成时间表
            schedule = self._generate_schedule(estimated_time)
            
            plan = {
                "overall_strategy": overall_strategy,
                "implementation_phases": '\n'.join(f"{i+1}. {phase}" for i, phase in enumerate(implementation_phases)),
                "estimated_time": estimated_time,
                **detailed_steps,
                **file_changes,
                **function_changes,
                **test_plan,
                **verification_points,
                **risk_control,
                **dependencies,
                **completion_criteria,
                **schedule
            }
            
            self.logger.log_operation_end("generate_implementation_plan", operation_id, 
                success=True
            )
            
            return plan
            
        except Exception as e:
            self.logger.log_operation_end("generate_implementation_plan", operation_id, 
                success=False, error=str(e)
            )
            return {
                "error": f"Failed to generate implementation plan: {str(e)}"
            }
    
    def _estimate_development_time(self, feature_name: str, granularity: str) -> str:
        """估算开发时间"""
        base_time = 5  # 基础时间（天）
        
        # 根据功能复杂度调整
        if any(keyword in feature_name.lower() for keyword in ["复杂", "大型", "架构", "重构"]):
            base_time *= 2
        elif any(keyword in feature_name.lower() for keyword in ["简单", "小", "修复"]):
            base_time *= 0.5
        
        # 根据粒度调整
        if granularity == "step":
            base_time *= 1.2  # 更细粒度需要更多时间
        elif granularity == "file":
            base_time *= 0.8  # 文件级别相对简单
        
        return f"{int(base_time)}-{int(base_time * 1.5)}天"
    
    def _generate_detailed_steps(self, feature_name: str, include_testing: bool) -> Dict[str, str]:
        """生成详细实现步骤"""
        # 获取项目上下文
        context = self.analyze_project_context()
        analysis_info = {"feature_name": feature_name}
        
        return {
            "phase_1_preparation": self.generate_ai_todo_content("detailed_steps_phase1", feature_name, context, analysis_info),
            "phase_2_core_implementation": self.generate_ai_todo_content("detailed_steps_phase2", feature_name, context, analysis_info),
            "phase_3_integration_testing": self.generate_ai_todo_content("detailed_steps_phase3", feature_name, context, analysis_info) if include_testing else "1. 基础功能验证\n2. 简单集成测试",
            "phase_4_documentation": self.generate_ai_todo_content("detailed_steps_phase4", feature_name, context, analysis_info)
        }
    
    def _generate_file_changes(self, feature_name: str) -> Dict[str, str]:
        """生成文件修改清单"""
        # 获取项目上下文
        context = self.analyze_project_context()
        analysis_info = {"feature_name": feature_name}
        
        return {
            "new_files": self.generate_ai_todo_content("new_files", feature_name, context, analysis_info),
            "modified_files": self.generate_ai_todo_content("modified_files", feature_name, context, analysis_info),
            "deleted_files": "- 无需删除文件（如有冲突文件会在实现时确定）"
        }
    
    def _generate_function_changes(self, feature_name: str, granularity: str) -> Dict[str, str]:
        """生成函数/类实现清单"""
        # 获取项目上下文
        context = self.analyze_project_context()
        analysis_info = {"feature_name": feature_name}
        
        return {
            "new_functions_classes": self.generate_ai_todo_content("function_changes_new", feature_name, context, analysis_info),
            "modified_functions_classes": f"""- main(): 添加{feature_name}初始化
- register_routes(): 注册{feature_name}路由
- get_config(): 添加{feature_name}配置""",
            "deleted_functions_classes": "- 暂无需要删除的函数或类"
        }
    
    def _generate_test_plan(self, feature_name: str, include_testing: bool) -> Dict[str, str]:
        """生成测试计划"""
        if not include_testing:
            return {
                "unit_test_tasks": f"基础{feature_name}功能测试",
                "integration_test_tasks": f"{feature_name}集成验证",
                "manual_test_tasks": f"手动验证{feature_name}核心流程"
            }
        
        # 获取项目上下文
        context = self.analyze_project_context()
        analysis_info = {"feature_name": feature_name}
        
        return {
            "unit_test_tasks": self.generate_ai_todo_content("testing_plan_unit", feature_name, context, analysis_info),
            "integration_test_tasks": f"""- 测试{feature_name}与数据库的集成
- 测试{feature_name}与API的集成
- 测试{feature_name}与其他服务的集成
- 端到端功能测试""",
            "manual_test_tasks": f"""- 手动验证{feature_name}用户界面
- 手动测试{feature_name}业务流程
- 性能和压力测试
- 兼容性测试"""
        }
    
    def _generate_verification_points(self, feature_name: str) -> Dict[str, str]:
        """生成验证检查点"""
        return {
            "function_verification": f"""- {feature_name}核心功能正常工作
- 所有API端点响应正确
- 数据持久化正确
- 错误处理机制有效""",
            
            "performance_verification": f"""- {feature_name}响应时间符合要求
- 内存使用在合理范围
- 并发处理能力验证
- 资源占用优化""",
            
            "compatibility_verification": f"""- {feature_name}向后兼容性
- 与现有功能无冲突
- 数据格式兼容性
- API版本兼容性"""
        }
    
    def _generate_risk_control(self, feature_name: str) -> Dict[str, str]:
        """生成风险控制"""
        return {
            "critical_risks": f"""- {feature_name}实现复杂度超预期
- 与现有系统集成困难
- 性能影响超出预期
- 数据一致性问题""",
            
            "risk_responses": f"""- 分阶段实现，降低复杂度
- 提前进行集成测试
- 持续性能监控
- 数据备份和回滚机制""",
            
            "rollback_plan": f"""1. 保留{feature_name}实现前的代码版本
2. 准备数据库回滚脚本
3. 配置回滚检查点
4. 制定紧急回滚流程"""
        }
    
    def _generate_dependencies(self, feature_name: str) -> Dict[str, str]:
        """生成依赖事项"""
        return {
            "external_dependencies": f"""- 检查{feature_name}所需的第三方库
- 确认外部API可用性
- 验证系统环境要求""",
            
            "internal_dependencies": f"""- 确保相关内部服务正常
- 验证数据库迁移完成
- 确认配置文件更新""",
            
            "resource_requirements": f"""- 开发人员：1-2人
- 测试环境：完整测试环境
- 时间资源：{self._estimate_development_time(feature_name, 'function')}
- 计算资源：标准开发环境"""
        }
    
    def _generate_completion_criteria(self, feature_name: str) -> Dict[str, str]:
        """生成完成标准"""
        return {
            "completion_criteria": f"""- {feature_name}所有核心功能实现完成
- 通过所有单元测试和集成测试
- 代码审查通过
- 文档更新完成""",
            
            "quality_gates": f"""- 代码覆盖率达到80%以上
- 无严重安全漏洞
- 性能测试通过
- 代码规范检查通过""",
            
            "deliverables": f"""- {feature_name}功能代码
- 完整测试套件
- 技术文档和用户指南
- 部署和配置文档"""
        }
    
    def _generate_schedule(self, estimated_time: str) -> Dict[str, str]:
        """生成时间表"""
        # 解析估算时间
        days = int(estimated_time.split('-')[0].replace('天', ''))
        
        start_date = datetime.now()
        
        milestones = []
        milestones.append(f"项目启动：{start_date.strftime('%Y-%m-%d')}")
        milestones.append(f"阶段1完成：{(start_date + timedelta(days=days//4)).strftime('%Y-%m-%d')}")
        milestones.append(f"阶段2完成：{(start_date + timedelta(days=days//2)).strftime('%Y-%m-%d')}")
        milestones.append(f"阶段3完成：{(start_date + timedelta(days=days*3//4)).strftime('%Y-%m-%d')}")
        milestones.append(f"项目完成：{(start_date + timedelta(days=days)).strftime('%Y-%m-%d')}")
        
        return {
            "milestone_schedule": '\n'.join(f"- {milestone}" for milestone in milestones),
            "key_milestones": '\n'.join([
                "- 需求确认完成",
                "- 核心功能实现完成",
                "- 测试验证完成", 
                "- 文档和部署完成"
            ]),
            "delivery_timeline": f"预计 {estimated_time} 完成整体功能开发"
        }
    
    def create_todo_plan(self, analysis_id: str, todo_granularity: str = "function", 
                        include_testing: bool = True) -> Dict[str, Any]:
        """创建Todo计划"""
        operation_id = self.logger.log_operation_start("create_todo_plan", 
            analysis_id=analysis_id, todo_granularity=todo_granularity
        )
        
        try:
            # 1. 加载分析文档
            analysis_result = self.load_analysis_document(analysis_id)
            if not analysis_result.get("success"):
                return analysis_result
            
            analysis_info = analysis_result["analysis_info"]
            
            # 2. 生成实现计划
            implementation_plan = self.generate_implementation_plan(
                analysis_info, todo_granularity, include_testing
            )
            
            # 3. 生成todo ID
            todo_id = self.generate_todo_id(analysis_id)
            
            # 4. 准备模板数据
            template_data = {
                "feature_name": analysis_info.get("feature_name"),
                "requirement_id": analysis_info.get("requirement_id"),
                "analysis_id": analysis_id,
                "todo_id": todo_id,
                "plan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "planner": "CodeLens 创造模式计划工具",
                "implementation_notes": f"基于分析报告 {analysis_id} 生成的详细实现计划",
                **implementation_plan
            }
            
            # 5. 生成todo文档
            doc_result = self.generate_todo_document(todo_id, template_data)
            
            if doc_result.get("success", True):
                result = {
                    "tool": "create_todo",
                    "mode": "create_plan",
                    "todo_id": todo_id,
                    "analysis_id": analysis_id,
                    "status": "completed",
                    
                    "plan_summary": {
                        "feature_name": analysis_info.get("feature_name"),
                        "todo_granularity": todo_granularity,
                        "include_testing": include_testing,
                        "estimated_time": implementation_plan.get("estimated_time"),
                        "total_phases": 4
                    },
                    
                    "document_info": doc_result.get("document_info", {}),
                    
                    "implementation_ready": {
                        "message": "实现计划已生成，可以开始功能开发",
                        "next_steps": [
                            "1. 审阅并确认实现计划",
                            "2. 按阶段执行开发任务",
                            "3. 跟踪进度和质量检查点",
                            "4. 完成后更新文档"
                        ]
                    },
                    
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = doc_result
            
            self.logger.log_operation_end("create_todo_plan", operation_id, 
                success=True, todo_id=todo_id
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("create_todo_plan", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to create todo plan: {str(e)}"
            }
    
    def generate_todo_document(self, todo_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成todo文档"""
        operation_id = self.logger.log_operation_start("generate_todo_document", 
            todo_id=todo_id
        )
        
        try:
            # 获取todo模板
            template_result = self.template_service.get_template_content("create_todo")
            if not template_result.get("success", True):
                return {
                    "success": False,
                    "error": f"Failed to get todo template: {template_result.get('error', 'Unknown error')}"
                }
            
            # 格式化模板
            format_result = self.template_service.format_template("create_todo", **template_data)
            if not format_result.get("success", True):
                return {
                    "success": False,
                    "error": f"Failed to format todo template: {format_result.get('error', 'Unknown error')}"
                }
            
            # 生成文档文件
            doc_filename = f"{todo_id}.md"
            doc_filepath = self.todos_dir / doc_filename
            
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
            
            self.logger.log_operation_end("generate_todo_document", operation_id, 
                success=True, filepath=str(doc_filepath)
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("generate_todo_document", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to generate todo document: {str(e)}"
            }
    
    def list_todo_plans(self) -> Dict[str, Any]:
        """列出Todo计划"""
        operation_id = self.logger.log_operation_start("list_todo_plans")
        
        try:
            plans = []
            
            if self.todos_dir.exists():
                for todo_file in self.todos_dir.glob("*.md"):
                    file_stat = todo_file.stat()
                    plans.append({
                        "filename": todo_file.name,
                        "todo_id": todo_file.stem,
                        "filepath": str(todo_file),
                        "created_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "file_size": file_stat.st_size
                    })
            
            # 按创建时间排序
            plans.sort(key=lambda x: x["created_time"], reverse=True)
            
            result = {
                "tool": "create_todo",
                "mode": "list_plans",
                "total_count": len(plans),
                "todo_plans": plans,
                "todos_dir": str(self.todos_dir),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.log_operation_end("list_todo_plans", operation_id, 
                success=True, count=len(plans)
            )
            
            return result
            
        except Exception as e:
            self.logger.log_operation_end("list_todo_plans", operation_id, 
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": f"Failed to list todo plans: {str(e)}"
            }

class CreateTodoTool:
    """创造模式Todo生成工具 - MCP接口"""
    
    def __init__(self):
        self.tool_name = "create_todo"
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取工具定义"""
        return {
            "name": self.tool_name,
            "description": "📋 CodeLens创造模式第三阶段 - 基于确认的分析报告生成详细实现计划",
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
                        "description": "执行模式: create=创建Todo计划, list=列出Todo计划",
                        "default": "create"
                    },
                    "analysis_id": {
                        "type": "string",
                        "description": "分析报告ID (create模式必需)"
                    },
                    "todo_granularity": {
                        "type": "string",
                        "enum": ["file", "function", "step"],
                        "description": "Todo粒度",
                        "default": "function"
                    },
                    "include_testing": {
                        "type": "boolean",
                        "description": "是否包含详细测试步骤",
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
            analysis_id = arguments.get("analysis_id")
            todo_granularity = arguments.get("todo_granularity", "function")
            include_testing = arguments.get("include_testing", True)
            
            # 初始化todo工具
            todo_tool = CreateTodoCore(project_path)
            
            if mode == "list":
                # 列出todo计划
                result = todo_tool.list_todo_plans()
            elif mode == "create" and analysis_id:
                # 创建todo计划
                result = todo_tool.create_todo_plan(
                    analysis_id, todo_granularity, include_testing
                )
            else:
                result = {
                    "success": False,
                    "error": "请提供必需的参数：create模式需要analysis_id"
                }
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"CreateTodo tool execution failed: {str(e)}"
            }

def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(description="CodeLens 创造模式 - Todo生成工具")
    parser.add_argument("project_path", nargs="?", default=".", 
                        help="项目路径 (默认: 当前目录)")
    parser.add_argument("--analysis-id", required=False,
                        help="分析报告ID")
    parser.add_argument("--todo-granularity", choices=["file", "function", "step"], 
                        default="function", help="Todo粒度 (默认: function)")
    parser.add_argument("--include-testing", action="store_true", default=True,
                        help="是否包含详细测试步骤 (默认: True)")
    parser.add_argument("--list", action="store_true",
                        help="列出现有Todo计划")
    
    args = parser.parse_args()
    
    try:
        # 初始化todo工具
        todo_tool = CreateTodoCore(args.project_path)
        
        if args.list:
            # 列出todo计划
            result = todo_tool.list_todo_plans()
        elif args.analysis_id:
            # 创建todo计划
            result = todo_tool.create_todo_plan(
                args.analysis_id, args.todo_granularity, args.include_testing
            )
        else:
            # 显示帮助信息
            result = {
                "tool": "create_todo",
                "mode": "help",
                "message": "请提供 --analysis-id 参数或使用 --list 查看现有Todo计划",
                "usage_examples": [
                    f"python {sys.argv[0]} /path/to/project --analysis-id analysis_req_login_1234567890_9876543210",
                    f"python {sys.argv[0]} /path/to/project --list",
                    f"python {sys.argv[0]} /path/to/project --analysis-id analysis_req_login_1234567890_9876543210 --todo-granularity step"
                ]
            }
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "tool": "create_todo"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()