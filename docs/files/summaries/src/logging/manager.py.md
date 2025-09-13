# 文件摘要：src/logging/manager.py

## 功能概述
日志系统核心管理器，提供统一的日志管理功能，支持结构化JSON日志、异步写入、操作追踪和性能监控。集成了原本分离的结构化日志功能，成为日志系统的中央控制器。

## 主要组件

### 核心类
- **LogManager**: 统一日志管理器
  - 结构化JSON日志格式化
  - 异步写入队列管理
  - 操作追踪和性能监控
  - 日志级别控制和过滤
  - 文件轮转集成
  - 统计信息收集

### 主要方法

#### 基础日志方法
- `debug()`: 调试级别日志记录
- `info()`: 信息级别日志记录  
- `warning()`: 警告级别日志记录
- `error()`: 错误级别日志记录

#### 高级功能方法
- `log_operation_start()`: 记录操作开始，返回操作ID
- `log_operation_end()`: 记录操作结束，计算耗时
- `set_context()`: 设置日志上下文信息
- `clear_context()`: 清除日志上下文
- `get_statistics()`: 获取日志统计信息

#### 管理方法
- `_write_log()`: 内部日志写入方法
- `_format_log()`: 日志格式化为JSON
- `_background_writer()`: 后台异步写入线程
- `_should_log()`: 日志级别判断
- `shutdown()`: 优雅关闭日志系统

## 依赖关系

### 标准库导入
- `json`: JSON格式化
- `threading`: 线程和锁机制
- `queue.Queue`: 异步写入队列
- `datetime`: 时间戳生成
- `uuid`: 操作ID生成
- `traceback`: 异常堆栈追踪
- `pathlib.Path`: 文件路径操作
- `typing`: 类型注解

### 内部模块依赖
- `.config.LogConfig`: 配置管理器
- `.rotator.FileRotator`: 文件轮转器

## 关键算法和逻辑

### 结构化日志格式
```json
{
  "timestamp": "2025-09-13T10:30:45.123456",
  "level": "INFO",
  "component": "FileService",
  "operation": "get_project_files_info",
  "message": "文件扫描完成",
  "context": {
    "found_files": 25,
    "project_path": "/path/to/project"
  },
  "operation_id": "op_abc123",
  "thread_id": 12345
}
```

### 异步写入机制
1. **主线程**: 日志事件放入队列，立即返回
2. **后台线程**: 持续从队列取出日志并写入文件
3. **缓冲策略**: 批量写入减少磁盘I/O
4. **优雅关闭**: 确保所有日志都被写入再退出

### 操作追踪模式
1. **开始记录**: `log_operation_start()` 生成唯一操作ID
2. **上下文绑定**: 操作期间的所有日志自动关联操作ID
3. **结束记录**: `log_operation_end()` 记录总耗时和结果状态
4. **性能分析**: 自动收集操作耗时统计

### 文件轮转集成
- **自动检查**: 每次写入前检查是否需要轮转
- **无缝切换**: 轮转过程中日志写入不中断
- **压缩处理**: 轮转后自动压缩旧日志文件
- **错误恢复**: 轮转失败时的自动恢复机制

## 性能优化

### 异步写入优势
- **主线程不阻塞**: 日志记录仅需微秒级时间
- **批量处理**: 减少磁盘I/O操作次数
- **缓冲机制**: 智能缓冲提升写入效率
- **背压控制**: 队列满时的背压处理

### 内存管理
- **有界队列**: 防止内存无限增长
- **及时释放**: 日志对象处理后立即释放
- **上下文清理**: 自动清理过期的上下文信息
- **统计优化**: 统计信息采用增量更新

### 错误处理
- **异常隔离**: 日志系统故障不影响主业务
- **自动恢复**: 文件权限、磁盘空间等问题的自动恢复
- **降级机制**: 严重故障时的日志降级策略
- **错误统计**: 记录和统计日志系统自身的错误

## 线程安全

### 同步机制
- **线程锁**: 保护共享状态的线程安全
- **队列同步**: 使用线程安全的Queue进行通信
- **原子操作**: 统计计数器使用原子操作
- **状态保护**: 配置更新时的状态保护

### 并发控制
- **单写线程**: 只有一个后台线程负责写入
- **读写分离**: 读操作不阻塞写操作
- **配置热更新**: 支持并发环境下的配置更新
- **优雅关闭**: 多线程环境下的优雅关闭机制

## 统计监控

### 收集的统计信息
```json
{
  "total_logs": 1234,
  "logs_by_level": {
    "DEBUG": 100,
    "INFO": 800,
    "WARNING": 300,
    "ERROR": 34
  },
  "operations_tracked": 156,
  "avg_operation_time_ms": 25.6,
  "file_rotations": 3,
  "queue_max_size": 50,
  "uptime_seconds": 3600
}
```

### 监控能力
- **实时统计**: 实时更新的日志统计信息
- **性能指标**: 操作耗时、队列状态等性能指标
- **错误统计**: 日志系统自身错误的统计分析
- **趋势分析**: 支持日志趋势和模式分析

## 使用示例

### 基础使用
```python
logger = LogManager(config)
logger.info("服务启动", {"port": 8080})
```

### 操作追踪
```python
op_id = logger.log_operation_start("file_scan", project_path="/path")
# ... 执行业务逻辑 ...
logger.log_operation_end("file_scan", op_id, duration_ms=150, success=True)
```

### 上下文管理
```python
logger.set_context({"user_id": "12345", "session": "abc"})
logger.info("用户操作")  # 自动包含上下文信息
logger.clear_context()
```

## 备注
LogManager是CodeLens日志系统的核心组件，集成了结构化日志、异步写入、操作追踪等企业级功能。通过单一类提供完整的日志管理能力，是系统可观测性的基础设施。