"""
CodeLens 统一配置管理模块

提供：
1. 统一的配置文件格式和验证
2. 配置管理器和缓存机制  
3. 各个工具的配置访问接口
4. 向后兼容的配置常量

使用示例：
    # 简单使用
    from src.config import get_config, get_file_filtering_config
    
    config = get_config()
    file_config = get_file_filtering_config()
    
    # 高级使用
    from src.config import ConfigManager
    
    manager = ConfigManager()
    config = manager.load_config()
    manager.save_user_config(custom_config)
"""

# 导入主要类和函数
from .config_schema import (
    CodeLensConfig,
    FileFilteringConfig, 
    FileSizeLimitsConfig,
    ScanningConfig,
    MCPToolsConfig,
    TemplateConfig,
    LoggingConfig,
    PerformanceConfig,
    SecurityConfig,
    ConfigValidator,
    LogLevel,
    AnalysisDepth
)

from .config_manager import (
    ConfigManager,
    get_config_manager,
    get_config,
    get_file_filtering_config,
    get_file_size_limits_config,
    get_tool_config,
    CONFIG_CONSTANTS
)

# 版本信息
__version__ = "1.0.0"

# 模块级别的便捷函数
def init_config(config_path=None):
    """初始化配置系统"""
    manager = ConfigManager(config_path)
    return manager.load_config()

def reload_config():
    """重新加载配置"""
    return get_config_manager().reload_config()

def save_config(config):
    """保存用户配置"""
    return get_config_manager().save_user_config(config)

def validate_config(config_dict):
    """验证配置"""
    return ConfigValidator.validate_json_structure(config_dict)

# 导出的公共接口
__all__ = [
    # 配置类
    'CodeLensConfig',
    'FileFilteringConfig', 
    'FileSizeLimitsConfig',
    'ScanningConfig',
    'MCPToolsConfig',
    'TemplateConfig',
    'LoggingConfig',
    'PerformanceConfig',
    'SecurityConfig',
    'ConfigValidator',
    'LogLevel',
    'AnalysisDepth',
    
    # 配置管理器
    'ConfigManager',
    'get_config_manager',
    
    # 便捷函数
    'get_config',
    'get_file_filtering_config', 
    'get_file_size_limits_config',
    'get_tool_config',
    'init_config',
    'reload_config',
    'save_config',
    'validate_config',
    
    # 常量
    'CONFIG_CONSTANTS'
]