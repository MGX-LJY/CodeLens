# src/logging/manager.py - 日志核心管理器

## 文件概述
CodeLens日志系统的核心管理文件，提供统一的日志管理功能，包括**新优化的易读混合格式**、异步写入、文件轮转协调和上下文信息管理。

## 导入模块
```python
import datetime, json, os, sys, threading, traceback, uuid
from queue import Queue, Empty
from .config import LogConfig
from .rotator import FileRotator
```

## 全局变量
无全局变量，所有状态封装在类中。

## 核心常量
- **日志级别映射**: CRITICAL(50), ERROR(40), WARNING(30), INFO(20), DEBUG(10)
- **时间戳格式**: ISO格式（去除'Z'后缀优化可读性）

## 类汇总表

| 类名 | 功能 | 关键方法 | 特性 |
|------|------|----------|------|
| `LogRecord` | 日志记录对象 | `to_json()`, `to_simple()` | **新混合格式** |
| `AsyncLogWriter` | 异步日志写入器 | `write_async()`, `write_sync()` | 异步队列写入 |
| `LogManager` | 日志核心管理器 | `debug()`, `info()`, `warning()`, `error()`, `critical()` | 统一日志接口 |

## 🔥 重大改进：混合格式日志输出

### 新格式特性
**原紧凑JSON格式**:
```json
{"timestamp":"2025-01-01T10:00:00Z","level":"INFO","component":"Test","message":"Hello","context":{"key":"value"}}
```

**新易读混合格式**:
```
2025-01-01T10:00:00 [INFO] [Test/operation] "Hello" key="value" req_id=abc123
```

### 格式优化详情
1. **时间戳简化**: 去掉'Z'后缀，提升可读性
2. **级别突出**: 用方括号包围级别
3. **组件清晰**: component/operation格式
4. **消息明确**: 双引号包围消息内容
5. **上下文平铺**: key=value格式，智能类型处理
6. **元数据精简**: 只显示关键的req_id

## 详细功能分析

### LogRecord类核心功能

#### to_json()方法 - 新混合格式实现
```python
def to_json(self) -> str:
    """转换为易读的混合格式字符串"""
    # 清理时间戳（去掉'Z'后缀）
    clean_timestamp = self.timestamp.rstrip('Z')
    
    # 基础格式：timestamp [level] [component/operation] "message"
    parts = [clean_timestamp, f"[{self.level}]", f"[{self.component}/{self.operation}]", f'"{self.message}"']
    
    # 智能上下文处理
    if self.context:
        for key, value in self.context.items():
            if isinstance(value, str):
                parts.append(f'{key}="{value}"')  # 字符串加引号
            elif isinstance(value, (int, float, bool)):
                parts.append(f'{key}={value}')    # 数字直接显示
            else:
                parts.append(f'{key}={json.dumps(value, ensure_ascii=False)}')  # 复杂对象JSON化
```

#### 智能异常处理
```python
if self.exc_info:
    error_msg = f"{type(self.exc_info).__name__}: {str(self.exc_info)}"
    parts.append(f'error="{error_msg}"')
```

### AsyncLogWriter类功能

#### 重启清空机制
```python
def _clear_log_file_on_restart(self) -> None:
    """重启时清空日志文件"""
    # 保持文件但清空内容，避免旧日志混淆
```

#### 异步写入队列
- **队列机制**: Queue线程安全队列
- **工作线程**: 独立后台线程处理写入
- **超时处理**: 1秒超时避免阻塞
- **回退机制**: 异步失败时同步写入

### LogManager类核心管理

#### 日志级别控制
```python
def _should_log(self, level: str) -> bool:
    """检查是否应该记录此级别的日志"""
    current_level = self.config.get_log_level_int(self.component)
    record_level = self.LEVEL_MAP.get(level, 20)
    return record_level >= current_level
```

#### 上下文管理
```python
def set_context(self, **context) -> None:
    """设置持久化上下文"""
    self.context.update(context)

def clear_context(self) -> None:
    """清空上下文"""
    self.context.clear()
```

## 数据流分析

### 日志生成流程
```
日志调用 → _log() → 级别检查 → LogRecord创建 → 格式化 → 异步/同步写入 → 文件轮转
```

### 异步写入流程
```
日志记录 → 队列入队 → 后台线程 → 文件写入 → 轮转检查
```

## 性能优化考虑

### 异步写入优势
- 非阻塞日志记录
- 批量文件操作
- 独立工作线程

### 混合格式优势
- 减少JSON解析开销
- 直观的视觉阅读
- 保留结构化信息

## 错误处理机制

### 多层容错
1. **异步失败回退**: 异步写入失败时同步写入
2. **文件操作异常**: 捕获并输出到stderr
3. **轮转失败处理**: 错误记录但不中断日志
4. **队列满处理**: 直接同步写入避免丢失

## 扩展性评估
**高扩展性**:
- 可插拔的格式化器
- 灵活的处理器架构
- 组件级别配置
- 上下文系统支持

## 代码质量评估
**优秀**:
- 清晰的类职责分离
- 完善的异常处理
- 线程安全设计
- **用户体验优化**（新混合格式）

## 使用示例

### 基本日志记录
```python
logger = LogManager(config, "FileService", "scan")
logger.info("文件处理完成", {"count": 25, "size_mb": 1024.5})
# 输出: 2025-01-01T10:00:00 [INFO] [FileService/scan] "文件处理完成" count=25 size_mb=1024.5 req_id=abc123
```

### 异常日志记录
```python
try:
    raise FileNotFoundError("配置文件不存在")
except Exception as e:
    logger.error("配置加载失败", {"path": "/etc/config.json"}, exc_info=e)
# 输出: 2025-01-01T10:00:00 [ERROR] [FileService/scan] "配置加载失败" path="/etc/config.json" error="FileNotFoundError: 配置文件不存在" req_id=abc123
```

## 注意事项
- 异步写入依赖后台线程，需要正确关闭
- 文件轮转会清空当前日志文件
- 上下文信息会在所有日志中持久化
- **新混合格式大幅提升日志可读性**，减少视觉疲劳