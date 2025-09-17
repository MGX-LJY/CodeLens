"""
MCP doc_guide 工具实现
智能分析项目特征，为AI提供文档生成策略
"""
import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到path以导入其他模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# 必须在sys.path修改后再导入
from src.services.file_service import FileService  # noqa: E402
from src.logging import get_logger  # noqa: E402

# 导入配置管理器
try:
    from src.config import get_file_filtering_config
    HAS_CONFIG_MANAGER = True
except ImportError:
    HAS_CONFIG_MANAGER = False
    get_file_filtering_config = lambda: None


class ProjectAnalyzer:
    """项目分析器"""

    def __init__(self):
        self.file_service = FileService()
        self.logger = get_logger(component="ProjectAnalyzer", operation="init")
        self.logger.info("ProjectAnalyzer 初始化完成")

        # 项目类型特征模式
        self.project_patterns = {
            "python": {
                "files": ["requirements.txt", "setup.py", "pyproject.toml", "main.py", "app.py"],
                "directories": ["src", "lib", "tests"],
                "extensions": [".py"],
                "imports": ["import", "from", "django", "flask", "fastapi", "requests"]
            },
            "javascript": {
                "files": ["package.json", "package-lock.json", "yarn.lock", "index.js", "app.js"],
                "directories": ["node_modules", "src", "lib", "dist"],
                "extensions": [".js", ".jsx", ".ts", ".tsx"],
                "imports": ["require", "import", "export", "react", "vue", "angular"]
            },
            "java": {
                "files": ["pom.xml", "build.gradle", "gradle.properties"],
                "directories": ["src/main", "src/test", "target", "build"],
                "extensions": [".java", ".kt"],
                "imports": ["package", "import", "spring", "maven", "gradle"]
            },
            "go": {
                "files": ["go.mod", "go.sum", "main.go"],
                "directories": ["cmd", "internal", "pkg"],
                "extensions": [".go"],
                "imports": ["package", "import", "func", "gin", "echo"]
            },
            "rust": {
                "files": ["Cargo.toml", "Cargo.lock"],
                "directories": ["src", "target"],
                "extensions": [".rs"],
                "imports": ["use", "mod", "extern", "actix", "tokio"]
            }
        }

        # 框架检测模式
        self.framework_patterns = {
            "django": ["django", "settings.py", "urls.py", "models.py", "views.py"],
            "flask": ["flask", "app.py", "@app.route", "Flask(__name__)"],
            "fastapi": ["fastapi", "FastAPI", "@app.get", "@app.post", "uvicorn"],
            "react": ["react", "jsx", "package.json", "src/App.js", "public/index.html"],
            "vue": ["vue", "package.json", "src/main.js", "public/index.html"],
            "spring": ["spring", "pom.xml", "@SpringBootApplication", "@RestController"],
            "gin": ["gin", "go.mod", "gin.Engine", "gin.Default"],
            "express": ["express", "package.json", "app.use", "app.listen"]
        }

    def analyze_project(self, project_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """分析项目特征"""
        operation_id = self.logger.log_operation_start("analyze_project", project_path=str(project_path))
        start_time = time.time()
        
        project_path = Path(project_path)
        self.logger.info("开始分析项目", {
            "project_path": str(project_path),
            "config": config,
            "operation_id": operation_id
        })

        # 获取项目文件信息
        self.logger.debug("开始获取项目文件信息")
        file_info = self._get_file_info(project_path, config)
        self.logger.debug("文件信息获取完成", {"file_count": len(file_info["files"])})

        # 检测项目类型
        self.logger.debug("开始检测项目类型")
        project_type = self._detect_project_type(project_path, file_info)
        self.logger.info("项目类型检测完成", {"project_type": project_type})

        # 检测主要框架
        self.logger.debug("开始检测主要框架")
        main_framework = self._detect_framework(project_path, file_info, project_type)
        self.logger.info("主要框架检测完成", {"main_framework": main_framework})

        # 识别功能模块
        self.logger.debug("开始识别功能模块")
        identified_modules = self._identify_modules(project_path, file_info, project_type)
        self.logger.info("功能模块识别完成", {"modules_count": len(identified_modules), "modules": identified_modules})

        # 评估代码复杂度
        self.logger.debug("开始评估代码复杂度")
        complexity = self._assess_complexity(file_info)
        self.logger.info("代码复杂度评估完成", {"complexity": complexity})

        # 识别关键文件
        self.logger.debug("开始识别关键文件")
        key_files = self._identify_key_files(project_path, file_info, project_type)
        self.logger.info("关键文件识别完成", {"key_files_count": len(key_files)})

        analysis_result = {
            "project_type": project_type,
            "main_framework": main_framework,
            "identified_modules": identified_modules,
            "code_complexity": complexity,
            "file_count": len(file_info["files"]),
            "key_files": key_files,
            "file_distribution": file_info["file_distribution"],
            "directory_structure": file_info["directory_structure"]
        }
        
        duration_ms = (time.time() - start_time) * 1000
        self.logger.log_operation_end("analyze_project", operation_id, duration_ms, True, **analysis_result)
        
        return analysis_result

    def generate_documentation_strategy(self, analysis: Dict[str, Any], focus_areas: List[str]) -> Dict[str, Any]:
        """生成文档策略"""
        operation_id = self.logger.log_operation_start("generate_documentation_strategy", 
                                                       project_type=analysis.get("project_type"),
                                                       complexity=analysis.get("code_complexity"),
                                                       file_count=analysis.get("file_count"))
        
        project_type = analysis["project_type"]
        complexity = analysis["code_complexity"]
        file_count = analysis["file_count"]
        
        self.logger.info("开始生成文档策略", {
            "project_type": project_type,
            "complexity": complexity,
            "file_count": file_count,
            "focus_areas": focus_areas
        })

        # 确定执行阶段顺序
        if complexity == "simple" and file_count < 20:
            execution_phases = ["files_first", "architecture_second", "project_last"]
            priority_strategy = "sequential"
        elif complexity == "complex" or file_count > 100:
            execution_phases = ["architecture_first", "files_second", "project_last"]
            priority_strategy = "top_down"
        else:
            execution_phases = ["files_first", "architecture_second", "project_last"]
            priority_strategy = "bottom_up"

        # 确定优先文件
        priority_files = analysis["key_files"][:10]  # 最多10个优先文件

        # 估计模板数量
        estimated_files = min(file_count, 30)  # 文件层最多30个
        estimated_templates = estimated_files + 6 + 4  # 文件+架构+项目

        strategy_result = {
            "execution_phases": execution_phases,
            "priority_strategy": priority_strategy,
            "priority_files": priority_files,
            "estimated_templates": estimated_templates,
            "complexity_level": complexity
        }
        
        self.logger.log_operation_end("generate_documentation_strategy", operation_id, success=True, **strategy_result)
        
        return strategy_result

    def generate_generation_plan(self, analysis: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """生成具体的生成计划"""
        # Phase 1: 文件层任务
        priority_files = strategy["priority_files"]
        other_files = [f for f in analysis["key_files"] if f not in priority_files]
        phase_1_files = priority_files + other_files[:20]  # 最多处理20个文件

        # Phase 2: 架构层任务
        project_type = analysis["project_type"]
        phase_2_architecture = self._get_architecture_components(project_type)

        # Phase 3: 项目层任务
        phase_3_project = ["project_readme"]

        return {
            "phase_1_files": phase_1_files,
            "phase_2_architecture": phase_2_architecture,
            "phase_3_project": phase_3_project,
            "estimated_duration": self._estimate_duration(
                len(phase_1_files), len(phase_2_architecture)
            )
        }

    def _get_file_info(self, project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取文件信息 - 优先使用配置系统"""
        ignore_patterns = config.get("ignore_patterns", {})
        file_patterns = ignore_patterns.get("files", [])
        dir_patterns = ignore_patterns.get("directories", [])

        # 从配置系统获取屏蔽规则
        if HAS_CONFIG_MANAGER:
            try:
                filtering_config = get_file_filtering_config()
                if filtering_config:
                    # 使用配置系统的过滤规则
                    config_exclude_patterns = filtering_config.exclude_patterns
                    config_exclude_dirs = filtering_config.exclude_directories
                    
                    # 合并用户指定和配置系统的规则
                    all_ignore_files = list(set(file_patterns + config_exclude_patterns))
                    all_ignore_dirs = list(set(dir_patterns + config_exclude_dirs))
                    
                    self.logger.debug("使用配置系统的过滤规则", {
                        "config_exclude_patterns_count": len(config_exclude_patterns),
                        "config_exclude_dirs_count": len(config_exclude_dirs),
                        "user_file_patterns_count": len(file_patterns),
                        "user_dir_patterns_count": len(dir_patterns)
                    })
                else:
                    # 配置为空，使用默认规则
                    all_ignore_files, all_ignore_dirs = self._get_default_ignore_patterns(file_patterns, dir_patterns)
            except Exception as e:
                self.logger.warning(f"配置系统访问失败，使用默认规则: {e}")
                all_ignore_files, all_ignore_dirs = self._get_default_ignore_patterns(file_patterns, dir_patterns)
        else:
            # 配置系统不可用，使用默认规则
            self.logger.debug("配置系统不可用，使用默认屏蔽规则")
            all_ignore_files, all_ignore_dirs = self._get_default_ignore_patterns(file_patterns, dir_patterns)

        # 扫描文件
        files = []
        file_distribution = Counter()
        directory_structure = []

        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                # 检查是否应该忽略
                if self._should_ignore_file(file_path, all_ignore_files, all_ignore_dirs):
                    continue

                relative_path = file_path.relative_to(project_path)
                files.append(str(relative_path))
                file_distribution[file_path.suffix] += 1

                # 记录目录结构
                parent_dir = str(relative_path.parent)
                if parent_dir != "." and parent_dir not in directory_structure:
                    directory_structure.append(parent_dir)

        return {
            "files": files,
            "file_distribution": dict(file_distribution),
            "directory_structure": directory_structure
        }
    
    def _get_default_ignore_patterns(self, file_patterns: List[str], dir_patterns: List[str]) -> tuple:
        """获取默认的忽略模式"""
        # 默认忽略文件模式 - 强化版本，排除所有非代码文件
        default_ignore_files = [
            # 文档和文本文件
            "*.md", "*.txt", "*.log", "*.tmp", "*.cache", "*.temp",
            # 编译和中间文件  
            "*.pyc", "*.pyo", "*.class", "*.o", "*.obj", "*.exe", "*.dll", "*.so", "*.dylib",
            # 图片和媒体文件
            "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.svg", "*.ico", "*.bmp", "*.tiff",
            "*.mp4", "*.avi", "*.mov", "*.wmv", "*.mp3", "*.wav", "*.flac",
            # 数据库文件
            "*.db", "*.sqlite", "*.sqlite3", "*.db3", "*.s3db", "*.sl3",
            # 压缩文件
            "*.zip", "*.tar", "*.gz", "*.rar", "*.7z", "*.bz2",
            # 系统文件
            ".DS_Store", "Thumbs.db", "desktop.ini", "*.lnk",
            # 备份和临时文件
            "*.bak", "*.backup", "*.swp", "*.swo", "*~"
        ]
        default_ignore_dirs = [
            # 版本控制和IDE
            "__pycache__", ".git", ".svn", ".hg", ".idea", ".vscode", ".vs",
            # 依赖和构建
            "node_modules", "venv", "env", ".venv", ".env", "dist", "build", "target", "out",
            # 数据和日志目录
            "data", "logs", ".logs", "backups", ".mg_kiro", ".pytest_cache", ".coverage",
            # 临时和缓存目录
            "tmp", "temp", ".tmp", ".temp", "cache", ".cache", "uploads", "downloads"
        ]

        all_ignore_files = list(set(file_patterns + default_ignore_files))
        all_ignore_dirs = list(set(dir_patterns + default_ignore_dirs))
        
        return all_ignore_files, all_ignore_dirs

    @staticmethod
    def _should_ignore_file(file_path: Path, ignore_files: List[str], ignore_dirs: List[str]) -> bool:
        """检查文件是否应该被忽略"""
        # 检查文件名模式
        for pattern in ignore_files:
            if file_path.match(pattern):
                return True

        # 检查目录模式
        for part in file_path.parts:
            for pattern in ignore_dirs:
                if part == pattern or part.startswith(pattern):
                    return True

        return False

    def _detect_project_type(self, _project_path: Path, file_info: Dict[str, Any]) -> str:
        """检测项目类型"""
        scores = {}

        for proj_type, patterns in self.project_patterns.items():
            score = 0

            # 检查特征文件
            for file_name in patterns["files"]:
                if any(file_name in f for f in file_info["files"]):
                    score += 3

            # 检查目录结构
            for dir_name in patterns["directories"]:
                if any(dir_name in d for d in file_info["directory_structure"]):
                    score += 2

            # 检查文件扩展名
            for ext in patterns["extensions"]:
                if ext in file_info["file_distribution"]:
                    score += file_info["file_distribution"][ext]

            scores[proj_type] = score

        if not scores:
            return "unknown"

        return max(scores, key=scores.get)

    def _detect_framework(self, project_path: Path, file_info: Dict[str, Any], _project_type: str) -> str:
        """检测主要框架"""
        scores = {}

        # 读取几个关键文件的内容来检测框架
        key_files = ["requirements.txt", "package.json", "go.mod", "Cargo.toml", "pom.xml"]
        file_contents = []

        for file_name in key_files:
            file_path = project_path / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        file_contents.append(content)
                except (IOError, OSError, UnicodeDecodeError):
                    continue

        # 也检查一些源代码文件
        source_files = [f for f in file_info["files"] if
                        any(f.endswith(ext) for ext in [".py", ".js", ".go", ".rs", ".java"])][:5]
        for file_name in source_files:
            file_path = project_path / file_name
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()[:2000]  # 只读前2000字符
                    file_contents.append(content)
            except (IOError, OSError, UnicodeDecodeError):
                continue

        all_content = " ".join(file_contents)

        # 检测框架
        for framework, patterns in self.framework_patterns.items():
            score = 0
            for pattern in patterns:
                score += all_content.count(pattern.lower())
            scores[framework] = score

        if not scores:
            return "custom"

        best_framework = max(scores, key=scores.get)
        return best_framework if scores[best_framework] > 0 else "custom"

    @staticmethod
    def _identify_modules(project_path: Path, file_info: Dict[str, Any], project_type: str) -> List[str]:
        """🧠 AI驱动的智能模块识别 - 基于语义理解和业务逻辑"""
        
        # 📦 第一步：识别实际Python包（包含__init__.py的目录）
        real_packages = []
        for directory in file_info["directory_structure"]:
            dir_path = project_path / directory
            if (dir_path / "__init__.py").exists():
                # 提取包名（去除路径前缀）
                package_name = directory.split("/")[-1]
                if package_name not in ["__pycache__", ".pytest_cache"]:
                    real_packages.append(package_name)
        
        # 直接返回实际包结构
        return [pkg for pkg in real_packages if pkg != "root"]

    @staticmethod
    def _assess_complexity(file_info: Dict[str, Any]) -> str:
        """评估代码复杂度"""
        file_count = len(file_info["files"])
        dir_count = len(file_info["directory_structure"])

        if file_count < 10 and dir_count < 5:
            return "simple"
        elif file_count < 50 and dir_count < 15:
            return "medium"
        else:
            return "complex"

    @staticmethod
    def _identify_key_files(_project_path: Path, file_info: Dict[str, Any], project_type: str) -> List[str]:
        """识别关键文件"""
        key_files = []

        # 系统文件排除列表
        system_files = {'.DS_Store', 'Thumbs.db', '.gitignore', '.gitkeep'}
        system_patterns = {'*.log', '*.tmp', '*.temp'}

        # 项目类型特定的关键文件
        type_specific = {
            "python": ["main.py", "app.py", "__init__.py", "models.py", "views.py", "settings.py"],
            "javascript": ["index.js", "app.js", "server.js", "main.js", "package.json"],
            "java": ["Main.java", "Application.java", "Controller.java", "Service.java"],
            "go": ["main.go", "server.go", "handler.go", "service.go"],
            "rust": ["main.rs", "lib.rs", "mod.rs"]
        }

        important_patterns = type_specific.get(project_type, [])

        # 按重要性排序文件
        scored_files = []

        for file_name in file_info["files"]:
            file_lower = file_name.lower()
            file_basename = file_name.split('/')[-1]  # 获取文件名部分
            
            # 排除系统文件
            if file_basename in system_files:
                continue
                
            # 排除匹配系统模式的文件
            if any(file_basename.endswith(pattern.replace('*', '')) for pattern in system_patterns):
                continue
            
            score = 0

            # 主文件得分最高
            if any(pattern.lower() in file_lower for pattern in important_patterns):
                score += 10

            # 根据文件名特征评分
            if "main" in file_lower or "app" in file_lower:
                score += 8
            if "config" in file_lower or "setting" in file_lower:
                score += 6
            if "model" in file_lower or "schema" in file_lower:
                score += 5
            if "controller" in file_lower or "handler" in file_lower:
                score += 5
            if "service" in file_lower or "business" in file_lower:
                score += 4
            if "util" in file_lower or "helper" in file_lower:
                score += 3

            # 根据文件位置评分（根目录或src目录优先）
            if "/" not in file_name or file_name.startswith("src/"):
                score += 2

            scored_files.append((file_name, score))

        # 按分数排序，返回前20个
        scored_files.sort(key=lambda x: x[1], reverse=True)
        return [file_name for file_name, score in scored_files[:20] if score > 0]


    @staticmethod
    def _get_architecture_components(project_type: str) -> List[str]:
        """获取架构组件"""
        base_components = ["system_overview", "tech_stack", "data_flow"]

        type_specific = {
            "python": ["deployment_architecture", "package_structure", "dependency_management"],
            "javascript": ["build_process", "module_system", "runtime_environment"],
            "java": ["class_hierarchy", "spring_configuration", "build_lifecycle"],
            "go": ["package_organization", "concurrency_model", "build_deployment"],
            "rust": ["module_system", "memory_management", "cargo_ecosystem"]
        }

        specific_components = type_specific.get(project_type, ["general_architecture"])
        return base_components + specific_components[:3]  # 最多6个组件

    @staticmethod
    def _estimate_duration(file_count: int, arch_count: int) -> str:
        """估计完成时间"""
        # 假设每个文件3分钟，每个架构组件10分钟
        total_minutes = file_count * 3 + arch_count * 10 + 30  # 加30分钟基础时间

        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:
            return f"{hours} hours {minutes} minutes"
        else:
            return f"{minutes} minutes"


class DocGuideTool:
    """MCP doc_guide 工具类"""

    def __init__(self):
        self.tool_name = "doc_guide"
        self.description = "智能分析项目特征，为AI提供文档生成策略"
        self.analyzer = ProjectAnalyzer()
        self.logger = get_logger(component="DocGuideTool", operation="init")
        self.logger.info("DocGuideTool 初始化完成")
        
        # 响应大小限制配置
        self.MAX_RESPONSE_TOKENS = 20000  # MCP工具响应的最大token数
        self.TOKEN_ESTIMATION_RATIO = 4   # 估算：每4个字符约等于1个token
    
    def _estimate_response_size(self, data: Dict[str, Any]) -> int:
        """估算响应数据的token大小"""
        try:
            import json
            json_str = json.dumps(data, ensure_ascii=False)
            char_count = len(json_str)
            estimated_tokens = char_count // self.TOKEN_ESTIMATION_RATIO
            self.logger.debug("响应大小估算", {
                "char_count": char_count, 
                "estimated_tokens": estimated_tokens,
                "max_tokens": self.MAX_RESPONSE_TOKENS
            })
            return estimated_tokens
        except Exception as e:
            self.logger.warning(f"响应大小估算失败: {e}")
            return 0
    
    def _auto_downgrade_analysis(self, config: Dict[str, Any], file_count: int) -> Dict[str, Any]:
        """根据文件数量自动降级分析配置"""
        original_config = config.copy()
        
        # 基于文件数量的自动降级策略
        if file_count > 1000:
            # 超大项目：最严格过滤
            config["analysis_depth"] = "basic"
            config["focus_areas"] = ["architecture"]
            self.logger.info("检测到超大项目，自动降级到基础分析", {
                "file_count": file_count,
                "new_depth": "basic",
                "new_focus": ["architecture"]
            })
        elif file_count > 500:
            # 大项目：中等过滤
            config["analysis_depth"] = "basic" if config["analysis_depth"] == "comprehensive" else config["analysis_depth"]
            config["focus_areas"] = config["focus_areas"][:2]  # 最多2个关注领域
            self.logger.info("检测到大项目，降级分析深度", {
                "file_count": file_count,
                "new_depth": config["analysis_depth"],
                "new_focus": config["focus_areas"]
            })
        elif file_count > 100:
            # 中等项目：轻度优化
            if config["analysis_depth"] == "comprehensive":
                config["analysis_depth"] = "detailed"
                self.logger.info("中等项目，从comprehensive降级到detailed", {
                    "file_count": file_count
                })
        
        if original_config != config:
            self.logger.info("分析配置已自动调整", {
                "original": original_config,
                "adjusted": config,
                "reason": f"file_count={file_count}"
            })
        
        return config
    
    def _simplify_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """简化响应数据以减少token使用量"""
        simplified = response_data.copy()
        
        try:
            # 简化项目分析数据
            if "project_analysis" in simplified:
                analysis = simplified["project_analysis"]
                
                # 限制关键文件列表长度
                if "key_files" in analysis and len(analysis["key_files"]) > 10:
                    analysis["key_files"] = analysis["key_files"][:10]
                    self.logger.debug("限制key_files到前10个")
                
                # 简化目录结构信息
                if "directory_structure" in analysis and len(analysis["directory_structure"]) > 20:
                    analysis["directory_structure"] = analysis["directory_structure"][:20]
                    self.logger.debug("限制directory_structure到前20个")
                
                # 简化文件分布信息
                if "file_distribution" in analysis:
                    file_dist = analysis["file_distribution"]
                    # 只保留文件数量超过5的扩展名
                    simplified_dist = {k: v for k, v in file_dist.items() if v >= 5}
                    if len(simplified_dist) < len(file_dist):
                        analysis["file_distribution"] = simplified_dist
                        self.logger.debug("简化file_distribution，只保留主要文件类型")
            
            # 简化生成计划
            if "generation_plan" in simplified:
                plan = simplified["generation_plan"]
                
                # 限制文件任务数量
                if "phase_1_files" in plan and len(plan["phase_1_files"]) > 15:
                    plan["phase_1_files"] = plan["phase_1_files"][:15]
                    self.logger.debug("限制phase_1_files到前15个")
            
            self.logger.info("响应数据简化完成")
            return simplified
            
        except Exception as e:
            self.logger.error(f"响应数据简化失败: {e}")
            # 如果简化失败，返回最基本的数据
            return {
                "project_analysis": {
                    "project_type": response_data.get("project_analysis", {}).get("project_type", "unknown"),
                    "main_framework": response_data.get("project_analysis", {}).get("main_framework", "unknown"),
                    "code_complexity": response_data.get("project_analysis", {}).get("code_complexity", "unknown"),
                    "file_count": response_data.get("project_analysis", {}).get("file_count", 0)
                },
                "analysis_file": response_data.get("analysis_file", "")
            }

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
                    "project_type": {
                        "type": "string",
                        "enum": ["auto", "python", "javascript", "java", "go", "rust"],
                        "description": "项目类型，auto为自动检测"
                    },
                    "analysis_depth": {
                        "type": "string",
                        "enum": ["basic", "detailed", "comprehensive"],
                        "description": "分析深度"
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
                            }
                        }
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["architecture", "modules", "files", "project"]
                        },
                        "description": "重点关注的领域"
                    }
                },
                "required": []
            }
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行doc_guide工具"""
        operation_id = self.logger.log_operation_start("execute_doc_guide", 
                                                       project_path=arguments.get("project_path"),
                                                       create_analysis_file=arguments.get("create_analysis_file", True))
        start_time = time.time()
        
        try:
            self.logger.info("开始执行doc_guide工具", {"arguments": arguments, "operation_id": operation_id})
            
            # 参数验证 - 如果没有提供project_path，使用当前工作目录
            project_path = arguments.get("project_path")
            if not project_path:
                project_path = os.getcwd()
                self.logger.info("未提供project_path，使用当前工作目录", {
                    "current_working_directory": project_path
                })
            
            self.logger.debug("验证project_path参数", {"project_path": project_path})
                
            if not os.path.exists(project_path):
                error_msg = f"项目路径不存在: {project_path}"
                self.logger.error(error_msg)
                return self._error_response("Invalid project path")

            # 获取参数
            project_type = arguments.get("project_type", "auto")
            analysis_depth = arguments.get("analysis_depth", "detailed")
            ignore_patterns = arguments.get("ignore_patterns", {})
            focus_areas = arguments.get("focus_areas", ["architecture", "modules", "files", "project"])

            config = {
                "project_type": project_type,
                "analysis_depth": analysis_depth,
                "ignore_patterns": ignore_patterns,
                "focus_areas": focus_areas
            }

            # 首先快速获取文件数量以进行预判
            self.logger.info("预扫描项目文件数量")
            quick_file_info = self.analyzer._get_file_info(Path(project_path), config)
            file_count = len(quick_file_info["files"])
            
            # 根据文件数量自动调整配置
            config = self._auto_downgrade_analysis(config, file_count)

            # 分析项目
            self.logger.info("开始分析项目", {"project_path": project_path, "config": config, "file_count": file_count})
            analysis = self.analyzer.analyze_project(project_path, config)
            self.logger.info("项目分析完成", {"analysis_summary": {
                "project_type": analysis.get("project_type"),
                "file_count": analysis.get("file_count"),
                "complexity": analysis.get("code_complexity")
            }})

            # 生成文档策略
            self.logger.info("开始生成文档策略", {"focus_areas": focus_areas})
            strategy = self.analyzer.generate_documentation_strategy(analysis, focus_areas)
            self.logger.info("文档策略生成完成", {"strategy_summary": {
                "priority_strategy": strategy.get("priority_strategy"),
                "estimated_templates": strategy.get("estimated_templates")
            }})

            # 生成具体计划
            self.logger.info("开始生成具体计划")
            plan = self.analyzer.generate_generation_plan(analysis, strategy)
            self.logger.info("具体计划生成完成")

            # 保存analysis.json到项目.codelens目录
            self.logger.info("开始保存分析结果到.codelens目录")
            analysis_data = {
                "project_analysis": analysis,
                "documentation_strategy": strategy,
                "generation_plan": plan,
                "timestamp": time.time(),
                "version": "1.0"
            }
            
            codelens_dir = Path(project_path) / ".codelens"
            self.logger.debug("创建.codelens目录", {"dir_path": str(codelens_dir)})
            codelens_dir.mkdir(exist_ok=True)
            
            analysis_file = codelens_dir / "analysis.json"
            self.logger.debug("写入分析文件", {"file_path": str(analysis_file)})
            
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            # 准备响应数据
            response_data = {
                "project_analysis": analysis,
                "documentation_strategy": strategy,
                "generation_plan": plan,
                "analysis_file": str(analysis_file)
            }
            
            # 检查响应大小并进行必要的简化
            estimated_size = self._estimate_response_size(response_data)
            if estimated_size > self.MAX_RESPONSE_TOKENS:
                self.logger.warning("响应数据过大，进行简化", {
                    "estimated_tokens": estimated_size,
                    "max_tokens": self.MAX_RESPONSE_TOKENS
                })
                response_data = self._simplify_response(response_data)
                
                # 重新检查简化后的大小
                new_size = self._estimate_response_size(response_data)
                self.logger.info("响应数据已简化", {
                    "original_tokens": estimated_size,
                    "simplified_tokens": new_size,
                    "reduction": estimated_size - new_size
                })

            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_operation_end("execute_doc_guide", operation_id, duration_ms, True,
                                        project_type=analysis['project_type'],
                                        complexity=analysis['code_complexity'],
                                        file_count=analysis['file_count'],
                                        analysis_file=str(analysis_file),
                                        response_tokens=self._estimate_response_size(response_data))

            return self._success_response(response_data)

        except (OSError, IOError, ValueError) as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_operation_end("execute_doc_guide", operation_id, duration_ms, False, error=str(e))
            self.logger.error(f"项目分析失败: {str(e)}", exc_info=e)
            return self._error_response(f"Analysis failed: {str(e)}")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_operation_end("execute_doc_guide", operation_id, duration_ms, False, error=str(e))
            self.logger.error(f"doc_guide工具执行失败: {str(e)}", exc_info=e)
            return self._error_response(f"Tool execution failed: {str(e)}")

    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """成功响应"""
        self.logger.debug("生成成功响应", {"data_keys": list(data.keys()) if data else []})
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


def create_mcp_tool() -> DocGuideTool:
    """创建MCP工具实例"""
    return DocGuideTool()


# 命令行接口，用于测试
def main():
    """命令行测试接口"""

    parser = argparse.ArgumentParser(description="MCP doc_guide tool")
    parser.add_argument("project_path", help="Project path to analyze")
    parser.add_argument("--type", dest="project_type",
                        choices=["auto", "python", "javascript", "java", "go", "rust"],
                        default="auto", help="Project type")
    parser.add_argument("--depth", dest="analysis_depth",
                        choices=["basic", "detailed", "comprehensive"],
                        default="detailed", help="Analysis depth")
    parser.add_argument("--focus", nargs="+",
                        choices=["architecture", "modules", "files", "project"],
                        default=["architecture", "modules", "files", "project"],
                        help="Focus areas")

    args = parser.parse_args()

    # 构建参数
    arguments = {
        "project_path": args.project_path,
        "project_type": args.project_type,
        "analysis_depth": args.analysis_depth,
        "focus_areas": args.focus
    }

    # 执行工具
    tool = create_mcp_tool()
    result = tool.execute(arguments)

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
