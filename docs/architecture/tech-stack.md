
# CodeLens 技术栈

## 核心技术

### 编程语言
- **Python 3.9+**: 主要开发语言
- **类型系统**: 使用typing模块提供完整类型注解

### 架构模式
- **MCP协议**: Model Context Protocol 标准协议实现
- **服务分层**: FileService、TemplateService、ValidationService、LoggingService
- **模块化设计**: 各组件独立可测试
- **无状态设计**: 每次调用独立执行

### 日志系统技术栈
- **LogManager**: 统一日志管理器，支持结构化JSON日志
- **FileRotator**: 文件轮转器，支持按大小/时间轮转和gzip压缩
- **LogConfig**: 配置管理器，支持JSON配置文件和运行时更新
- **异步写入**: 后台线程处理，不阻塞主业务流程
- **监控统计**: 操作追踪、性能分析、磁盘使用监控

### 数据格式
- **JSON**: 结构化数据交换格式
- **Markdown**: 文档模板格式
- **ISO 8601**: 时间戳标准格式

### 文件系统操作
- **pathlib**: 现代Python路径操作
- **glob**: 文件模式匹配
- **os**: 系统级操作接口
- **datetime**: 时间处理

### 依赖策略
- **零外部依赖**: 仅使用Python标准库
- **轻量级设计**: 最小化资源占用
- **跨平台兼容**: 支持Windows、macOS、Linux

## 关键设计原则

### 性能优化
- **异步日志写入**: 后台线程处理，主线程无阻塞
- **文件缓冲**: 批量写入减少磁盘I/O
- **延迟格式化**: 只在需要时格式化日志消息
- **级别过滤**: 早期过滤不需要的日志级别

### 可靠性保证
- **异常处理**: 完整的错误捕获和恢复机制
- **优雅降级**: DummyLogger确保系统在日志故障时正常运行
- **文件权限检查**: 确保日志文件可写性
- **磁盘空间监控**: 防止日志文件耗尽磁盘空间

### 可观测性
- **结构化日志**: JSON格式便于解析和分析
- **操作追踪**: 完整的调用链路记录
- **性能监控**: 耗时统计、文件处理统计
- **统计报告**: 日志级别分布、组件活跃度统计

### 配置管理
- **JSON配置**: 人类可读的配置格式
- **运行时更新**: 支持配置热重载
- **默认配置**: 提供合理的开箱即用配置
- **环境变量**: 支持环境变量覆盖配置

## 版本兼容性

### Python版本支持
- **最低要求**: Python 3.9
- **推荐版本**: Python 3.11+
- **测试覆盖**: 3.9, 3.10, 3.11, 3.12

### 操作系统支持
- **Windows**: Windows 10+
- **macOS**: macOS 10.15+
- **Linux**: Ubuntu 20.04+, CentOS 8+

## 部署架构

### 本地开发
```bash
# 直接运行
python src/mcp_tools/doc_scan.py

# 配置日志
export CODELENS_LOG_CONFIG=logging_config.json
python src/mcp_tools/doc_scan.py
```

### 生产部署
```bash
# 使用配置文件
python -c "
from src.logging import initialize_logging
initialize_logging('production_logging_config.json')
"
```

### 容器化（未来计划）
- **Docker**: 容器化部署支持
- **Kubernetes**: 云原生部署选项
