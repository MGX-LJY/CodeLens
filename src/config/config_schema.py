"""
配置文件验证模式和数据类型定义
定义了所有配置项的数据结构、验证规则和默认值
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import json
from pathlib import Path


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AnalysisDepth(Enum):
    """分析深度枚举"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


@dataclass
class FileFilteringConfig:
    """文件过滤配置"""
    include_extensions: List[str] = field(default_factory=lambda: [".py"])
    exclude_patterns: List[str] = field(default_factory=list)
    exclude_directories: List[str] = field(default_factory=list)
    smart_filtering: Dict[str, Any] = field(default_factory=dict)
    
    def should_include_file(self, file_path: str) -> bool:
        """判断文件是否应该被包含"""
        file_path_lower = file_path.lower()
        
        # 检查扩展名
        if self.include_extensions:
            if not any(file_path_lower.endswith(ext) for ext in self.include_extensions):
                return False
        
        # 检查排除模式
        for pattern in self.exclude_patterns:
            if pattern.lower() in file_path_lower:
                return False
        
        # 检查排除目录
        for exclude_dir in self.exclude_directories:
            if exclude_dir.lower() in file_path_lower:
                return False
        
        return True


@dataclass
class ChunkingConfig:
    """文件分片配置"""
    enabled: bool = True
    max_chunk_size: int = 2000
    min_chunk_size: int = 100
    overlap_size: int = 50
    
    def validate(self) -> bool:
        """验证分片配置的有效性"""
        if self.max_chunk_size <= self.min_chunk_size:
            return False
        if self.overlap_size >= self.min_chunk_size:
            return False
        return True


@dataclass
class FileSizeLimitsConfig:
    """文件大小限制配置"""
    min_file_size: int = 50
    max_file_size: int = 122880  # 120KB
    large_file_threshold: int = 50000  # 50KB
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    
    def should_chunk_file(self, file_size: int) -> bool:
        """判断文件是否需要分片"""
        return self.chunking.enabled and file_size > self.large_file_threshold
    
    def can_process_file(self, file_size: int) -> bool:
        """判断文件是否可以处理"""
        return self.min_file_size <= file_size <= self.max_file_size


@dataclass
class ParallelProcessingConfig:
    """并行处理配置"""
    enabled: bool = True
    max_workers: int = 4


@dataclass
class ScanningConfig:
    """扫描配置"""
    max_depth: int = 6
    follow_symlinks: bool = False
    include_hidden_files: bool = False
    parallel_processing: ParallelProcessingConfig = field(default_factory=ParallelProcessingConfig)
    content_analysis: Dict[str, bool] = field(default_factory=lambda: {
        "detect_framework": True,
        "extract_dependencies": True,
        "analyze_complexity": True
    })


@dataclass
class MCPToolConfig:
    """MCP工具配置基类"""
    pass


@dataclass
class DocScanConfig(MCPToolConfig):
    """doc_scan工具配置"""
    default_include_content: bool = False
    cache_results: bool = True
    cache_ttl: int = 3600
    max_response_size: int = 25000


@dataclass
class DocGuideConfig(MCPToolConfig):
    """doc_guide工具配置"""
    analysis_depth: AnalysisDepth = AnalysisDepth.COMPREHENSIVE
    generate_suggestions: bool = True
    focus_areas: List[str] = field(default_factory=lambda: ["architecture", "modules", "files", "project"])


@dataclass
class TaskInitConfig(MCPToolConfig):
    """task_init工具配置"""
    auto_filter_files: bool = True
    max_tasks_per_phase: int = 50
    dependency_resolution: bool = True
    template_validation: bool = True


@dataclass
class TaskExecuteConfig(MCPToolConfig):
    """task_execute工具配置"""
    enable_chunking: bool = True
    context_enhancement: bool = True
    template_caching: bool = True
    progress_tracking: bool = True


@dataclass
class MCPToolsConfig:
    """MCP工具集配置"""
    doc_scan: DocScanConfig = field(default_factory=DocScanConfig)
    doc_guide: DocGuideConfig = field(default_factory=DocGuideConfig)
    task_init: TaskInitConfig = field(default_factory=TaskInitConfig)
    task_execute: TaskExecuteConfig = field(default_factory=TaskExecuteConfig)


@dataclass
class TemplateConfig:
    """模板配置"""
    validation: Dict[str, bool] = field(default_factory=lambda: {
        "strict_mode": True,
        "required_variables": True,
        "type_checking": True
    })
    formatting: Dict[str, Any] = field(default_factory=lambda: {
        "markdown_style": "github",
        "code_highlighting": True,
        "table_formatting": True
    })


@dataclass
class LoggingConfig:
    """日志配置"""
    level: LogLevel = LogLevel.INFO
    format: str = "detailed"
    file_logging: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "max_file_size": "10MB",
        "backup_count": 5
    })
    operation_tracking: Dict[str, bool] = field(default_factory=lambda: {
        "enabled": True,
        "track_performance": True,
        "detailed_context": True
    })


@dataclass
class PerformanceConfig:
    """性能配置"""
    memory_limits: Dict[str, str] = field(default_factory=lambda: {
        "max_file_cache_size": "100MB",
        "max_template_cache_size": "50MB"
    })
    timeouts: Dict[str, int] = field(default_factory=lambda: {
        "file_scan": 30,
        "analysis": 60,
        "template_render": 10
    })
    optimization: Dict[str, bool] = field(default_factory=lambda: {
        "lazy_loading": True,
        "incremental_analysis": True,
        "result_caching": True
    })


@dataclass
class SecurityConfig:
    """安全配置"""
    path_validation: Dict[str, Any] = field(default_factory=lambda: {
        "allow_absolute_paths": True,
        "restrict_parent_access": True,
        "blocked_paths": ["/etc", "/usr", "/var", "/root"]
    })
    content_filtering: Dict[str, Any] = field(default_factory=lambda: {
        "scan_for_secrets": True,
        "blocked_patterns": ["password", "api_key", "secret", "token"],
        "safe_content_only": False
    })


@dataclass
class CodeLensConfig:
    """CodeLens 主配置类"""
    # 元数据
    _metadata: Dict[str, str] = field(default_factory=lambda: {
        "version": "1.0.0",
        "description": "CodeLens 统一配置",
        "last_updated": "2025-09-16"
    })
    
    # 核心配置模块
    file_filtering: FileFilteringConfig = field(default_factory=FileFilteringConfig)
    file_size_limits: FileSizeLimitsConfig = field(default_factory=FileSizeLimitsConfig)
    scanning: ScanningConfig = field(default_factory=ScanningConfig)
    mcp_tools: MCPToolsConfig = field(default_factory=MCPToolsConfig)
    templates: TemplateConfig = field(default_factory=TemplateConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    def validate(self) -> List[str]:
        """验证配置的有效性，返回错误列表"""
        errors = []
        
        # 验证文件大小配置
        if not self.file_size_limits.chunking.validate():
            errors.append("Invalid chunking configuration: max_chunk_size must be > min_chunk_size")
        
        # 验证扫描深度
        if self.scanning.max_depth <= 0:
            errors.append("Invalid scanning configuration: max_depth must be > 0")
        
        # 验证并行处理配置
        if self.scanning.parallel_processing.max_workers <= 0:
            errors.append("Invalid parallel processing: max_workers must be > 0")
        
        # 验证MCP工具配置
        if self.mcp_tools.task_init.max_tasks_per_phase <= 0:
            errors.append("Invalid task_init configuration: max_tasks_per_phase must be > 0")
        
        if self.mcp_tools.doc_scan.cache_ttl < 0:
            errors.append("Invalid doc_scan configuration: cache_ttl must be >= 0")
        
        return errors
    
    def is_valid(self) -> bool:
        """检查配置是否有效"""
        return len(self.validate()) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        def convert_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                result = {}
                for field_name, field_def in obj.__dataclass_fields__.items():
                    value = getattr(obj, field_name)
                    result[field_name] = convert_dataclass(value)
                return result
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, (list, tuple)):
                return [convert_dataclass(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_dataclass(v) for k, v in obj.items()}
            else:
                return obj
        
        return convert_dataclass(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeLensConfig':
        """从字典创建配置对象"""
        # 这里可以实现更复杂的反序列化逻辑
        # 为了简化，暂时使用默认值并更新部分字段
        config = cls()
        
        # 这里可以添加更详细的字段映射逻辑
        # 现在先返回默认配置
        return config


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_json_structure(config_data: Dict[str, Any]) -> List[str]:
        """验证JSON配置结构"""
        errors = []
        required_sections = [
            "file_filtering", "file_size_limits", "scanning", 
            "mcp_tools", "templates", "logging", "performance", "security"
        ]
        
        for section in required_sections:
            if section not in config_data:
                errors.append(f"Missing required section: {section}")
        
        return errors
    
    @staticmethod
    def validate_file_paths(config_data: Dict[str, Any]) -> List[str]:
        """验证文件路径相关配置"""
        errors = []
        
        # 验证排除路径格式
        if "file_filtering" in config_data:
            filtering = config_data["file_filtering"]
            
            if "exclude_patterns" in filtering:
                for pattern in filtering["exclude_patterns"]:
                    if not isinstance(pattern, str):
                        errors.append(f"Invalid exclude pattern type: {type(pattern)}")
        
        return errors
    
    @staticmethod
    def validate_numeric_ranges(config_data: Dict[str, Any]) -> List[str]:
        """验证数值范围"""
        errors = []
        
        # 验证文件大小配置
        if "file_size_limits" in config_data:
            limits = config_data["file_size_limits"]
            
            min_size = limits.get("min_file_size", 0)
            max_size = limits.get("max_file_size", float('inf'))
            threshold = limits.get("large_file_threshold", 0)
            
            if min_size >= max_size:
                errors.append("min_file_size must be < max_file_size")
            
            if threshold > max_size:
                errors.append("large_file_threshold must be <= max_file_size")
        
        return errors