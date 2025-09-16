"""
配置管理器：统一管理CodeLens所有配置项
提供配置加载、验证、缓存和访问的统一接口
"""
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from threading import Lock
import copy

from .config_schema import (
    CodeLensConfig, ConfigValidator, 
    FileFilteringConfig, FileSizeLimitsConfig, ScanningConfig,
    MCPToolsConfig, LogLevel
)

try:
    from ..logging import get_logger
except ImportError:
    # 如果日志系统不可用，创建一个空日志器
    class DummyLogger:
        def debug(self, msg, context=None): pass
        def info(self, msg, context=None): pass
        def warning(self, msg, context=None): pass
        def error(self, msg, context=None, exc_info=None): pass
        def log_operation_start(self, *args, **kwargs): return "dummy"
        def log_operation_end(self, op, op_id, **ctx): pass
    
    get_logger = lambda **kwargs: DummyLogger()


class ConfigManager:
    """
    配置管理器 - CodeLens统一配置管理中心
    
    功能：
    1. 配置文件加载和保存
    2. 配置验证和合并
    3. 配置缓存和热重载
    4. 为各个模块提供配置访问接口
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        """单例模式确保全局唯一配置管理器"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self.logger = get_logger(component="ConfigManager", operation="init")
        
        # 确定配置文件路径
        if config_path:
            self.config_path = Path(config_path)
        else:
            # 默认路径：当前模块目录下的default_config.json
            current_dir = Path(__file__).parent
            self.config_path = current_dir / "default_config.json"
        
        # 用户自定义配置路径
        self.user_config_path = Path.cwd() / ".codelens" / "config.json"
        
        # 配置缓存
        self._config_cache: Optional[CodeLensConfig] = None
        self._raw_config_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: float = 0
        self._cache_ttl: float = 300  # 5分钟缓存
        
        # 配置文件监控
        self._last_modified: Dict[str, float] = {}
        
        self.logger.info("ConfigManager 初始化完成", {
            "default_config_path": str(self.config_path),
            "user_config_path": str(self.user_config_path),
            "cache_ttl": self._cache_ttl
        })
        
        self._initialized = True
    
    def load_config(self, force_reload: bool = False) -> CodeLensConfig:
        """
        加载配置，支持缓存和热重载
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            配置对象
        """
        operation_id = self.logger.log_operation_start("load_config", force_reload=force_reload)
        
        try:
            # 检查是否需要重新加载
            if not force_reload and self._is_cache_valid():
                self.logger.debug("使用缓存配置")
                return self._config_cache
            
            self.logger.info("加载配置文件")
            
            # 加载默认配置
            default_config = self._load_config_file(self.config_path)
            self.logger.debug("默认配置加载完成", {"keys": len(default_config)})
            
            # 加载用户配置（如果存在）
            user_config = {}
            if self.user_config_path.exists():
                user_config = self._load_config_file(self.user_config_path)
                self.logger.debug("用户配置加载完成", {"keys": len(user_config)})
            
            # 合并配置
            merged_config = self._merge_configs(default_config, user_config)
            
            # 验证配置
            validation_errors = self._validate_config(merged_config)
            if validation_errors:
                self.logger.warning("配置验证发现问题", {"errors": validation_errors})
                # 可以选择是否在验证失败时抛出异常
                # for error in validation_errors:
                #     self.logger.error(f"配置验证错误: {error}")
            
            # 创建配置对象
            config_obj = self._create_config_object(merged_config)
            
            # 更新缓存
            self._config_cache = config_obj
            self._raw_config_cache = merged_config
            self._cache_timestamp = time.time()
            self._update_file_timestamps()
            
            self.logger.log_operation_end("load_config", operation_id, 
                                        config_sections=len(merged_config),
                                        validation_errors=len(validation_errors))
            
            return config_obj
            
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}", exc_info=True)
            self.logger.log_operation_end("load_config", operation_id, success=False, error=str(e))
            
            # 返回默认配置作为后备
            if self._config_cache:
                self.logger.warning("使用缓存配置作为后备")
                return self._config_cache
            else:
                self.logger.warning("使用内置默认配置作为后备")
                return CodeLensConfig()
    
    def get_config(self) -> CodeLensConfig:
        """获取当前配置（优先使用缓存）"""
        return self.load_config(force_reload=False)
    
    def reload_config(self) -> CodeLensConfig:
        """强制重新加载配置"""
        self.logger.info("强制重新加载配置")
        return self.load_config(force_reload=True)
    
    def save_user_config(self, config: Union[CodeLensConfig, Dict[str, Any]]) -> bool:
        """
        保存用户自定义配置
        
        Args:
            config: 配置对象或字典
            
        Returns:
            是否保存成功
        """
        operation_id = self.logger.log_operation_start("save_user_config")
        
        try:
            # 确保用户配置目录存在
            self.user_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换配置为字典
            if isinstance(config, CodeLensConfig):
                config_dict = config.to_dict()
            else:
                config_dict = config
            
            # 验证配置
            validation_errors = self._validate_config(config_dict)
            if validation_errors:
                self.logger.error("用户配置验证失败", {"errors": validation_errors})
                return False
            
            # 保存配置文件
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info("用户配置保存成功", {"path": str(self.user_config_path)})
            
            # 清除缓存，强制下次重新加载
            self._invalidate_cache()
            
            self.logger.log_operation_end("save_user_config", operation_id, success=True)
            return True
            
        except Exception as e:
            self.logger.error(f"用户配置保存失败: {e}", exc_info=True)
            self.logger.log_operation_end("save_user_config", operation_id, success=False, error=str(e))
            return False
    
    def get_file_filtering_config(self) -> FileFilteringConfig:
        """获取文件过滤配置"""
        return self.get_config().file_filtering
    
    def get_file_size_limits_config(self) -> FileSizeLimitsConfig:
        """获取文件大小限制配置"""
        return self.get_config().file_size_limits
    
    def get_scanning_config(self) -> ScanningConfig:
        """获取扫描配置"""
        return self.get_config().scanning
    
    def get_mcp_tools_config(self) -> MCPToolsConfig:
        """获取MCP工具配置"""
        return self.get_config().mcp_tools
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """获取特定工具的配置"""
        mcp_config = self.get_mcp_tools_config()
        return getattr(mcp_config, tool_name, {})
    
    def update_config_section(self, section: str, updates: Dict[str, Any]) -> bool:
        """
        更新配置的特定部分
        
        Args:
            section: 配置节名称
            updates: 要更新的配置项
            
        Returns:
            是否更新成功
        """
        try:
            current_config = self._raw_config_cache or {}
            
            if section not in current_config:
                current_config[section] = {}
            
            # 深度合并更新
            current_config[section] = self._deep_merge(current_config[section], updates)
            
            # 保存更新后的配置
            return self.save_user_config(current_config)
            
        except Exception as e:
            self.logger.error(f"配置节更新失败: {e}", exc_info=True)
            return False
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self._config_cache:
            return False
        
        # 检查缓存时间
        if time.time() - self._cache_timestamp > self._cache_ttl:
            return False
        
        # 检查文件修改时间
        for file_path in [self.config_path, self.user_config_path]:
            if file_path.exists():
                current_mtime = file_path.stat().st_mtime
                cached_mtime = self._last_modified.get(str(file_path), 0)
                if current_mtime > cached_mtime:
                    return False
        
        return True
    
    def _invalidate_cache(self):
        """使缓存失效"""
        self._config_cache = None
        self._raw_config_cache = None
        self._cache_timestamp = 0
        self._last_modified.clear()
    
    def _update_file_timestamps(self):
        """更新文件时间戳记录"""
        for file_path in [self.config_path, self.user_config_path]:
            if file_path.exists():
                self._last_modified[str(file_path)] = file_path.stat().st_mtime
    
    def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """加载单个配置文件"""
        if not file_path.exists():
            self.logger.warning(f"配置文件不存在: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.debug(f"配置文件加载成功: {file_path}")
            return config
            
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件JSON解析失败 {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"配置文件读取失败 {file_path}: {e}")
            raise
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """合并默认配置和用户配置"""
        if not user:
            return copy.deepcopy(default)
        
        return self._deep_merge(copy.deepcopy(default), user)
    
    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并两个字典"""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        
        return result
    
    def _validate_config(self, config: Dict[str, Any]) -> List[str]:
        """验证配置"""
        errors = []
        
        # JSON结构验证
        errors.extend(ConfigValidator.validate_json_structure(config))
        
        # 文件路径验证
        errors.extend(ConfigValidator.validate_file_paths(config))
        
        # 数值范围验证
        errors.extend(ConfigValidator.validate_numeric_ranges(config))
        
        return errors
    
    def _create_config_object(self, config_dict: Dict[str, Any]) -> CodeLensConfig:
        """从字典创建配置对象"""
        # 简化版本：使用默认配置对象并尝试更新字段
        config = CodeLensConfig()
        
        try:
            # 文件过滤配置
            if "file_filtering" in config_dict:
                ff_data = config_dict["file_filtering"]
                config.file_filtering = FileFilteringConfig(
                    include_extensions=ff_data.get("include_extensions", [".py"]),
                    exclude_patterns=ff_data.get("exclude_patterns", []),
                    exclude_directories=ff_data.get("exclude_directories", []),
                    smart_filtering=ff_data.get("smart_filtering", {})
                )
            
            # 文件大小限制配置
            if "file_size_limits" in config_dict:
                fsl_data = config_dict["file_size_limits"]
                
                # 分片配置
                chunking_data = fsl_data.get("chunking", {})
                from .config_schema import ChunkingConfig
                chunking_config = ChunkingConfig(
                    enabled=chunking_data.get("enabled", True),
                    max_chunk_size=chunking_data.get("max_chunk_size", 2000),
                    min_chunk_size=chunking_data.get("min_chunk_size", 100),
                    overlap_size=chunking_data.get("overlap_size", 50)
                )
                
                config.file_size_limits = FileSizeLimitsConfig(
                    min_file_size=fsl_data.get("min_file_size", 50),
                    max_file_size=fsl_data.get("max_file_size", 122880),
                    large_file_threshold=fsl_data.get("large_file_threshold", 50000),
                    chunking=chunking_config
                )
            
            # 扫描配置
            if "scanning" in config_dict:
                scan_data = config_dict["scanning"]
                config.scanning = ScanningConfig(
                    max_depth=scan_data.get("max_depth", 6),
                    follow_symlinks=scan_data.get("follow_symlinks", False),
                    include_hidden_files=scan_data.get("include_hidden_files", False)
                )
            
            # MCP工具配置
            if "mcp_tools" in config_dict:
                mcp_data = config_dict["mcp_tools"]
                config.mcp_tools = MCPToolsConfig(
                    # 这里可以添加具体的MCP工具配置映射
                )
            
            # 验证最终配置对象
            validation_errors = config.validate()
            if validation_errors:
                self.logger.warning("配置对象验证失败", {"errors": validation_errors})
            
        except Exception as e:
            self.logger.error(f"配置对象创建失败: {e}", exc_info=True)
            # 返回默认配置作为后备
            config = CodeLensConfig()
        
        return config


# 全局配置管理器实例
_global_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager


def get_config() -> CodeLensConfig:
    """快捷方式：获取当前配置"""
    return get_config_manager().get_config()


def get_file_filtering_config() -> FileFilteringConfig:
    """快捷方式：获取文件过滤配置"""
    return get_config_manager().get_file_filtering_config()


def get_file_size_limits_config() -> FileSizeLimitsConfig:
    """快捷方式：获取文件大小限制配置"""
    return get_config_manager().get_file_size_limits_config()


def get_tool_config(tool_name: str) -> Dict[str, Any]:
    """快捷方式：获取工具配置"""
    return get_config_manager().get_tool_config(tool_name)


# 配置常量导出（向后兼容）
class ConfigConstants:
    """配置常量类，提供向后兼容的常量访问"""
    
    @property
    def DEFAULT_EXCLUDE_PATTERNS(self) -> List[str]:
        return get_file_filtering_config().exclude_patterns
    
    @property
    def DEFAULT_EXCLUDE_DIRECTORIES(self) -> List[str]:
        return get_file_filtering_config().exclude_directories
    
    @property
    def DEFAULT_INCLUDE_EXTENSIONS(self) -> List[str]:
        return get_file_filtering_config().include_extensions
    
    @property
    def LARGE_FILE_THRESHOLD(self) -> int:
        return get_file_size_limits_config().large_file_threshold
    
    @property
    def MAX_FILE_SIZE(self) -> int:
        return get_file_size_limits_config().max_file_size
    
    @property
    def MIN_FILE_SIZE(self) -> int:
        return get_file_size_limits_config().min_file_size


# 创建全局常量实例
CONFIG_CONSTANTS = ConfigConstants()