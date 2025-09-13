
# CodeLens 模块依赖关系分析

## 整体依赖架构

```
MCP 工具层 (接口层)
├── doc_scan.py ──────────→ FileService
├── template_get.py ──────→ TemplateService
└── doc_verify.py ────────→ ValidationService

服务层 (核心业务)
├── FileService ──────────→ LoggingService
├── TemplateService ──────→ LoggingService
├── ValidationService ────→ LoggingService
└── LoggingService ───────→ [独立模块]

日志系统内部依赖
├── LogManager ───────────→ LogConfig, FileRotator
├── FileRotator ─────────→ LogConfig
└── LogConfig ───────────→ [独立配置模块]
```

## 详细依赖关系

### 1. MCP工具层依赖
- **DocScanTool** → **FileService**: 项目文件扫描和信息提取
- **TemplateGetTool** → **TemplateService**: 模板获取和管理
- **DocVerifyTool** → **ValidationService**: 文档验证和状态检查

### 2. 服务层依赖
- **FileService** → **LoggingService**: 文件操作日志记录和性能监控
- **TemplateService** → **LoggingService**: 模板操作日志记录
- **ValidationService** → **LoggingService**: 验证操作日志记录
- **LoggingService**: 独立服务，无外部业务依赖

### 3. 日志系统内部依赖
- **LogManager** → **LogConfig**: 配置管理和运行时更新
- **LogManager** → **FileRotator**: 文件轮转和压缩
- **FileRotator** → **LogConfig**: 轮转配置获取
- **LogConfig**: 独立配置模块，仅依赖标准库

### 4. 标准库依赖
所有模块都依赖Python标准库：
- `pathlib`: 文件路径操作
- `json`: JSON数据处理
- `datetime`: 时间处理
- `threading`: 并发处理（日志系统）
- `typing`: 类型注解

## 模块独立性分析

### 完全独立模块
- **LogConfig**: 配置管理，无业务依赖
- **TemplateService**: 模板管理，仅依赖日志系统
- **ValidationService**: 文档验证，仅依赖日志系统

### 核心依赖模块
- **LoggingService**: 被所有服务模块依赖
- **FileService**: 被DocScanTool依赖

### 接口层模块
- **MCP工具**: 仅依赖对应的服务模块，相互独立

## 依赖注入模式

### 日志系统注入
```python
class FileService:
    def __init__(self):
        self.logger = get_logger(component="FileService")
```

### 配置依赖注入
```python
class LogManager:
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.rotator = FileRotator(config.file)
```

## 循环依赖分析

### 无循环依赖设计
- **单向依赖**: 所有依赖关系都是单向的
- **分层架构**: 上层依赖下层，避免循环
- **接口隔离**: 通过接口隔离实现解耦

### 依赖方向
```
MCP工具层 → 服务层 → 日志系统 → 标准库
     ↓         ↓         ↓
   无依赖   单向依赖   无外部依赖
```

## 模块替换和扩展性

### 可替换模块
- **LogConfig**: 可替换为其他配置实现
- **FileRotator**: 可替换为其他轮转策略
- **TemplateService**: 可扩展支持更多模板类型

### 扩展点
- **新MCP工具**: 可独立添加新的MCP工具
- **新服务类**: 可添加新的业务服务类
- **新日志处理**: 可扩展日志处理功能

## 测试依赖

### 测试隔离
- **单元测试**: 每个模块可独立测试
- **模块测试**: 服务层可独立于MCP工具测试
- **集成测试**: 完整依赖链的集成测试

### Mock策略
- **日志系统Mock**: 测试时可使用DummyLogger
- **文件系统Mock**: 可Mock文件操作
- **配置Mock**: 可Mock配置加载

## 部署依赖

### 运行时依赖
- **Python 3.9+**: 最低版本要求
- **标准库**: 无第三方依赖
- **文件系统权限**: 读写权限要求

### 可选依赖
- **配置文件**: JSON配置文件（可选）
- **日志目录**: 日志文件存储目录
- **环境变量**: CODELENS_LOG_CONFIG（可选）

## 版本兼容性

### 向后兼容
- **API稳定性**: 公开接口保持向后兼容
- **配置兼容**: 配置文件格式向后兼容
- **模块接口**: 模块间接口保持稳定

### 升级路径
- **渐进升级**: 可单独升级各个模块
- **配置迁移**: 自动处理配置格式升级
- **数据迁移**: 日志格式向后兼容

---

**模块关系总结**: CodeLens采用分层架构设计，模块间依赖关系清晰，支持独立测试和部署。日志系统作为横切关注点，为所有业务模块提供可观测性能力。
