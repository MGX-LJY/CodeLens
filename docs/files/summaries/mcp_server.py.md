# mcp_server.py - CodeLens MCP服务器主文件

## 函数概述
这是CodeLens项目的MCP服务器主入口文件，负责创建和管理MCP服务器实例，提供热重载功能，并协调所有MCP工具的注册与调用。

## 导入模块
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
```

## 全局变量
- `server`: MCP服务器实例
- `hot_reload_manager`: 热重载管理器全局实例
- `codelens_tools`: 工具实例字典

## 核心常量
- **服务器名称**: "codelens"
- **工具数量**: 12个（文档模式8个 + 创造模式4个）

## 函数汇总表

| 函数名 | 功能 | 返回类型 | 关键参数 |
|-------|------|----------|----------|
| `create_tool_instances()` | 创建所有工具实例 | Dict | 无 |
| `setup_hot_reload()` | 设置热重载功能 | None | 无 |
| `on_module_reloaded()` | 模块重载回调 | None | reload_event |
| `refresh_tool_instances()` | 刷新工具实例 | None | 无 |
| `convert_tool_definition()` | 转换工具定义为MCP格式 | Tool | tool_def |
| `list_tools()` | 列出所有可用工具 | list[Tool] | 无 |
| `call_tool()` | 调用指定工具 | Sequence[TextContent] | name, arguments |
| `main()` | 主入口函数 | None | 无 |

## 详细功能分析

### 工具管理系统
该文件管理两类工具：
- **文档模式工具**: 传统的文档生成工具（init_tools, doc_guide, task_init等）
- **创造模式工具**: 新增的功能创建工具（create_guide, create_requirement等）

### 热重载功能
```python
def setup_hot_reload():
    """设置热重载功能"""
    # 支持环境变量控制: CODELENS_HOT_RELOAD
    # 自动注册工具实例和重载回调
    # 0.5秒防抖，2秒批量重载窗口
```

### 命令行模式支持
- **test模式**: `python mcp_server.py test [project_path]`
- **info模式**: `python mcp_server.py info`
- **reload模式**: `python mcp_server.py reload`

### MCP协议实现
实现标准MCP协议的关键装饰器：
- `@server.list_tools()`: 工具列表接口
- `@server.call_tool()`: 工具调用接口

## 数据流分析

### 工具调用流程
```
客户端请求 → call_tool() → 获取工具实例 → tool_instance.execute() → 返回结果
```

### 热重载流程
```
文件变化 → HotReloadManager → on_module_reloaded → refresh_tool_instances → 更新工具注册
```

## 错误处理机制
- 工具执行异常捕获和格式化
- 热重载失败回退机制
- 文件路径验证和错误提示

## 性能优化考虑
- 工具实例缓存和复用
- 异步服务器运行
- 批量热重载减少频繁更新

## 扩展性评估
**高扩展性**:
- 新工具只需添加到`create_tool_instances()`
- 热重载自动支持新模块
- MCP协议标准化接口

## 代码质量评估
**优秀**:
- 清晰的模块分离
- 完善的错误处理
- 良好的日志记录
- 标准化的MCP实现

## 文档完整性
**完整**: 包含详细的docstring和类型注解，工具定义清晰

## 注意事项
- 需要正确设置PYTHONPATH以导入src模块
- 热重载功能依赖watchdog库
- MCP协议要求特定的输入输出格式