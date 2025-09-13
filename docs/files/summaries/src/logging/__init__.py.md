# 文件摘要：src/logging/__init__.py

## 功能概述
日志系统统一导出模块，为CodeLens项目提供企业级日志管理功能的统一接口。作为日志系统的入口点，提供简化的API供其他模块使用。

## 主要组件

### 导出的核心类
- **LogManager**: 统一日志管理器，支持结构化JSON日志
- **FileRotator**: 文件轮转器，支持按大小/时间轮转和gzip压缩  
- **LogConfig**: 配置管理器，支持JSON配置文件和运行时更新

### 导出的主要函数
- `get_logger()`: 获取日志器实例的便捷函数
- `initialize_logging()`: 初始化日志系统的便捷函数

## 依赖关系

### 内部模块导入
- `.manager.LogManager`: 核心日志管理器
- `.rotator.FileRotator`: 文件轮转组件
- `.config.LogConfig`: 配置管理组件

### 对外接口
- **统一入口**: 为CodeLens其他模块提供统一的日志接口
- **简化API**: 隐藏内部实现复杂性，提供简洁易用的接口
- **版本兼容**: 保证日志系统API的向后兼容性

## 关键特性

### 统一导出策略
- **模块级接口**: 通过`__all__`定义明确的导出接口
- **便捷函数**: 提供快速获取日志器和初始化的方法
- **文档字符串**: 完整的模块级文档说明

### 设计模式
- **门面模式**: 为复杂的日志子系统提供简化接口
- **单例模式**: 确保全局日志配置的一致性
- **工厂模式**: 通过工厂函数创建合适的日志器实例

## 使用示例

### 基础使用
```python
from src.logging import get_logger

# 获取组件专用日志器
logger = get_logger(component="MyService")
logger.info("服务启动", {"port": 8080})
```

### 初始化配置
```python
from src.logging import initialize_logging

# 使用配置文件初始化
initialize_logging("logging_config.json")
```

## 备注
作为CodeLens v0.3.0的核心新功能，日志系统提供了企业级的可观测性能力。该模块确保了日志功能的易用性和一致性，是项目可维护性的重要保障。