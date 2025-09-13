# 文件摘要：src/logging/config.py

## 功能概述
日志系统配置管理模块，提供灵活的JSON配置文件支持和运行时配置更新能力。使用dataclass模式定义配置结构，确保类型安全和数据完整性。

## 主要组件

### 数据类定义
- **FileConfig**: 文件日志配置
  - `enabled`: 是否启用文件日志
  - `path`: 日志文件路径
  - `max_size_mb`: 文件大小限制(MB)
  - `backup_count`: 备份文件数量
  - `rotation`: 轮转策略("size"/"time"/"both")

- **ConsoleConfig**: 控制台日志配置
  - `enabled`: 是否启用控制台输出
  - `level`: 控制台日志级别

- **RetentionConfig**: 日志保留策略配置
  - `max_age_days`: 最大保留天数
  - `max_total_size_mb`: 总大小限制(MB)
  - `cleanup_on_start`: 启动时清理旧日志

- **FeatureConfig**: 功能特性配置
  - `async_write`: 异步写入开关
  - `operation_tracking`: 操作追踪开关
  - `context_manager`: 上下文管理开关

- **LoggingConfig**: 主配置类
  - `level`: 全局日志级别
  - `file`: 文件配置
  - `console`: 控制台配置
  - `retention`: 保留策略配置
  - `features`: 功能特性配置

### 核心类
- **LogConfig**: 配置管理器类
  - `load_config()`: 从JSON文件加载配置
  - `save_config()`: 保存配置到JSON文件
  - `update_config()`: 运行时更新配置
  - `get_config()`: 获取当前配置
  - `validate_config()`: 配置验证

## 依赖关系

### 标准库导入
- `dataclasses`: 用于定义配置数据结构
- `json`: JSON配置文件解析
- `pathlib.Path`: 文件路径操作
- `os`: 环境变量访问
- `typing`: 类型注解支持

### 环境变量支持
- `CODELENS_LOG_CONFIG`: 日志配置文件路径

## 关键算法和逻辑

### 配置加载策略
1. **环境变量优先**: 检查CODELENS_LOG_CONFIG环境变量
2. **默认配置**: 使用内置的合理默认配置
3. **配置验证**: 加载后验证配置完整性和合理性
4. **错误恢复**: 配置错误时回退到默认配置

### 运行时更新机制
- **增量更新**: 支持部分配置项更新
- **类型安全**: 通过dataclass确保配置项类型正确
- **即时生效**: 配置更新后立即应用到日志系统
- **回滚支持**: 更新失败时自动回滚到前一配置

### 配置验证逻辑
- **路径有效性**: 验证日志文件路径可写性
- **数值范围**: 检查文件大小、备份数量等数值合理性
- **枚举值**: 验证轮转策略、日志级别等枚举值
- **依赖关系**: 检查配置项之间的依赖关系

## 配置示例

### 默认配置
```json
{
  "level": "INFO",
  "file": {
    "enabled": true,
    "path": "logs/codelens.log",
    "max_size_mb": 10,
    "backup_count": 5,
    "rotation": "size"
  },
  "console": {
    "enabled": false,
    "level": "WARNING"
  },
  "retention": {
    "max_age_days": 30,
    "max_total_size_mb": 100,
    "cleanup_on_start": true
  },
  "features": {
    "async_write": true,
    "operation_tracking": true,
    "context_manager": true
  }
}
```

### 生产环境配置
```json
{
  "level": "WARNING",
  "file": {
    "enabled": true,
    "path": "/var/log/codelens/codelens.log",
    "max_size_mb": 50,
    "backup_count": 10,
    "rotation": "both"
  },
  "console": {
    "enabled": false
  },
  "features": {
    "async_write": true,
    "operation_tracking": true
  }
}
```

## 设计特点

### 类型安全
- **Dataclass模式**: 利用Python dataclass提供类型检查
- **Optional类型**: 合理使用Optional类型处理可选配置
- **类型转换**: 自动处理JSON到Python对象的类型转换

### 扩展性
- **模块化配置**: 每个功能模块有独立的配置类
- **向后兼容**: 新增配置项不影响现有配置文件
- **默认值策略**: 缺失配置项自动使用合理默认值

### 可维护性
- **清晰结构**: 配置层次清晰，易于理解和维护
- **文档完整**: 每个配置项都有详细注释说明
- **错误处理**: 完善的错误处理和异常恢复机制

## 备注
LogConfig是CodeLens日志系统的配置核心，为系统提供了灵活可靠的配置管理能力。通过JSON配置文件和运行时更新，确保了日志系统的可配置性和动态调整能力。