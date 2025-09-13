# API-服务模块连接关系分析

## 整体依赖架构

```
Claude Code (外部)
    ↓
MCP服务器 (mcp_server.py)
    ↓
MCP工具层 (src/mcp_tools/)
    ├── doc_scan → FileService
    ├── template_get → TemplateServiceV05  
    └── doc_verify → ValidationService
    ↓
服务层 (src/services/)
    ├── FileService (文件信息服务)
    ├── ValidationService (验证服务)
    └── LoggingService (日志服务)
    ↓
模板层 (src/templates/)
    └── TemplateServiceV05 → 16个核心模板
```

## 详细依赖关系

### 1. MCP工具层依赖
- **DocScanTool** → FileService
  - 调用 `get_project_files_info()` 获取完整项目信息
  - 调用 `get_directory_tree()` 生成目录结构
  - 调用 `scan_source_files()` 扫描源码文件

- **TemplateGetTool** → TemplateServiceV05
  - 调用 `get_template_list()` 获取16个模板列表
  - 调用 `get_template_content()` 获取指定模板内容
  - 调用 `get_templates_by_layer()` 按层级查询模板

- **DocVerifyTool** → ValidationService
  - 调用 `get_generation_status()` 获取文档生成状态
  - 调用 `check_directory_structure()` 检查目录结构
  - 调用 `get_validation_summary()` 获取验证摘要

### 2. 服务层依赖
- **TemplateServiceV05** → 模板类依赖
  - ArchitectureTemplates (6个架构层模板)
  - ModuleTemplates (6个模块层模板)  
  - FileTemplates (1个文件层综合模板)
  - ProjectTemplates (3个项目层模板)

### 3. 日志服务依赖
- **所有服务组件** → LoggingService
  - 操作追踪和性能监控
  - 结构化日志记录
  - 文件轮转和异步写入

### 4. 外部API依赖
- **MCP协议服务器** → Claude Code
  - JSON-RPC通信协议
  - 标准MCP工具接口
  - 无状态设计，每次调用独立

## 依赖注入模式

CodeLens采用简单的依赖注入模式：

```python
# MCP工具初始化时注入服务依赖
class DocScanTool:
    def __init__(self):
        self.file_service = FileService()
        self.logger = get_logger(component="DocScan")

class TemplateGetTool:
    def __init__(self):
        self.template_service = TemplateServiceV05()
        self.logger = get_logger(component="TemplateGet")
```

## 循环依赖分析

✅ **无循环依赖**：
- 采用单向依赖设计
- MCP工具层 → 服务层 → 模板层
- 各服务组件相互独立

## 模块替换和扩展性

### 可扩展点
1. **新增MCP工具**: 可添加新的MCP工具调用现有服务
2. **扩展模板系统**: 可在各层级添加新的文档模板
3. **增强服务功能**: 各服务组件可独立扩展功能
4. **日志系统配置**: 支持不同的日志配置和输出格式

### 替换策略
- **服务层替换**: 实现相同接口即可替换任意服务
- **模板系统替换**: 可替换整个模板系统或单个模板
- **日志系统替换**: 支持DummyLogger降级机制

## 测试依赖

- **单元测试**: 各服务组件独立测试
- **集成测试**: MCP工具端到端测试
- **模板验证**: 16个模板的完整性测试

## 部署依赖

- **零外部依赖**: 仅使用Python 3.9+标准库
- **单文件部署**: mcp_server.py可独立运行
- **模块化部署**: 可按需部署特定功能模块

## 版本兼容性

- **Python版本**: 支持Python 3.9+
- **MCP协议**: 遵循标准MCP协议规范
- **向后兼容**: 保持模板别名和接口兼容性