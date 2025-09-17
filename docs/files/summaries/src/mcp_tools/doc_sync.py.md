# doc_sync.py - 智能文档同步工具

## 文件概述

**路径**: `src/mcp_tools/doc_sync.py`  
**类型**: MCP工具实现  
**主要功能**: 统一的智能文档同步工具，合并了doc_update_init和doc_update的功能

## 设计理念

这是一个**统一的文档同步工具**，解决了原有两个独立工具的分离问题：
- **智能检测**: 自动判断执行初始化还是更新检测
- **完整追踪**: 记录每次操作的详细变更历史
- **操作友好**: 提供多种操作模式适应不同场景

## 核心类

### DocSyncTool
```python
class DocSyncTool:
    """MCP doc_sync 统一工具类 - 智能文档同步"""
```

**关键属性**:
- `tool_name`: "doc_sync"
- `description`: "智能文档同步工具 - 自动检测并处理项目文件变更"
- `logger`: 组件日志记录器

## 主要功能

### 1. 智能模式检测
```python
def _detect_mode(self, project_path: Path) -> str:
    """智能检测应该使用init还是update模式"""
```

**检测逻辑**:
- 检查 `file_fingerprints.json` 是否存在
- 验证指纹文件的有效性和完整性
- 文件不存在或损坏 → 返回 "init"
- 文件有效且包含数据 → 返回 "update"

### 2. 初始化操作
```python
def _execute_init(self, project_path: Path, record_changes: bool = True) -> Dict[str, Any]:
    """执行初始化操作"""
```

**功能**:
- 扫描项目代码文件（排除文档和临时文件）
- 计算每个文件的MD5哈希值
- 创建指纹基点文件 `file_fingerprints.json`
- 记录初始化操作到变更历史

### 3. 更新检测操作
```python
def _execute_update(self, project_path: Path, record_changes: bool = True) -> Dict[str, Any]:
    """执行更新检测操作"""
```

**功能**:
- 加载历史指纹数据
- 重新扫描当前项目状态
- 对比变化：修改、新增、删除的文件
- 生成详细的更新建议
- 更新指纹文件和变更历史

### 4. 状态查询
```python
def _get_status(self, project_path: Path) -> Dict[str, Any]:
    """获取当前状态信息"""
```

**返回信息**:
- 项目路径和基本状态
- 指纹文件创建/更新时间
- 跟踪的文件数量
- 历史记录统计信息
- 最近操作详情

## 操作模式

### 参数说明
```python
"inputSchema": {
    "properties": {
        "project_path": {
            "type": "string",
            "description": "项目根路径（可选，默认使用当前工作目录）"
        },
        "mode": {
            "enum": ["auto", "init", "update", "status"],
            "description": "操作模式"
        },
        "record_changes": {
            "type": "boolean", 
            "description": "是否记录变更历史（默认true）"
        }
    }
}
```

### 模式详解

**auto模式（推荐）**:
- 智能检测项目状态
- 自动选择初始化或更新操作
- 适合日常使用

**init模式**:
- 强制执行初始化
- 重建指纹基点
- 用于首次设置或重置

**update模式**:
- 强制执行更新检测
- 要求已有有效指纹文件
- 用于明确的变更检测

**status模式**:
- 查看项目同步状态
- 不执行任何修改操作
- 用于状态监控

## 文件扫描策略

### 包含的文件类型
```python
code_extensions = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yaml', '.yml',
    '.toml', '.cfg', '.ini', '.conf', '.sh', '.bat', '.ps1',
    '.html', '.css', '.scss', '.less', '.vue', '.go', '.rs',
    '.java', '.kt', '.cpp', '.c', '.h', '.hpp', '.cs', '.php',
    '.rb', '.swift', '.dart', '.sql', '.r', '.m', '.scala'
}
```

### 排除策略
**忽略目录**:
- `.git`, `__pycache__`, `node_modules`
- `.idea`, `.vscode`, `venv`, `env`
- `docs`, `.codelens`

**忽略文件扩展名**:
- 文档文件: `.md`, `.txt`, `.rst`, `.pdf`
- 临时文件: `.log`, `.tmp`, `.cache`, `.bak`
- 编译文件: `.pyc`, `.pyo`, `.pyd`

## 变更记录系统

### 数据结构

**change_history.json**:
```json
{
  "created_at": "2025-09-17T15:22:08.897994",
  "last_updated": "2025-09-17T15:23:10.874232", 
  "total_operations": 4,
  "history": [
    {
      "id": "change_1758093728897",
      "timestamp": "2025-09-17T15:22:08.897970",
      "operation": "init",
      "files_count": 48,
      "summary": "初始化项目指纹基点，记录48个代码文件"
    },
    {
      "id": "change_1758093790874", 
      "operation": "update",
      "has_changes": true,
      "files_count": 49,
      "changes": {
        "modified": ["file1.py"],
        "added": ["file2.py"],
        "deleted": ["file3.py"]
      },
      "summary": "检测到变更：修改1个文件"
    }
  ]
}
```

**last_change.json**:
- 保存最近一次变更的详细信息
- 便于快速查看最新状态

### 记录内容
- **操作类型**: init, update
- **时间戳**: 精确到毫秒
- **文件统计**: 总数、变更详情
- **变更分类**: 修改、新增、删除
- **操作摘要**: 人类可读的描述

## 更新建议生成

### 建议格式
```markdown
📝 检测到以下文件变化，建议更新相关文档：

🔄 **已修改的文件：**
- src/mcp_tools/doc_sync.py

✨ **新增的文件：**  
- src/new_feature.py

🗑️ **已删除的文件：**
- src/deprecated.py

💡 **建议操作：**
1. 检查并更新这些文件对应的文档内容
2. 更新项目README中的相关说明  
3. 如有架构变更，请更新架构文档
```

## 使用示例

### 命令行使用
```bash
# 智能模式（推荐）
python src/mcp_tools/doc_sync.py . --mode auto

# 查看状态
python src/mcp_tools/doc_sync.py . --mode status

# 强制初始化
python src/mcp_tools/doc_sync.py . --mode init

# 禁用变更记录
python src/mcp_tools/doc_sync.py . --mode auto --no-record
```

### MCP工具调用
```python
# 通过MCP服务器调用
result = await call_tool("doc_sync", {
    "project_path": "/path/to/project",
    "mode": "auto",
    "record_changes": True
})
```

## 技术特性

### 性能优化
- **增量扫描**: 只处理代码文件，跳过文档和临时文件
- **高效哈希**: 使用MD5算法快速计算文件指纹
- **批量处理**: 一次性扫描所有文件，减少I/O操作

### 可靠性
- **原子操作**: 文件写入使用原子操作，避免数据损坏
- **错误处理**: 全面的异常捕获和日志记录
- **数据验证**: 检查指纹文件的完整性和有效性

### 扩展性
- **模块化设计**: 各功能模块独立，便于维护和扩展
- **配置灵活**: 支持多种操作模式和参数配置
- **日志完整**: 详细的操作日志，便于调试和监控

## 与旧工具的对比

| 特性 | doc_sync.py | doc_update_init.py + doc_update.py |
|------|-------------|-------------------------------------|
| 工具数量 | 1个统一工具 | 2个独立工具 |
| 智能检测 | ✅ 自动判断init/update | ❌ 需要手动选择 |
| 变更记录 | ✅ 完整历史追踪 | ❌ 无历史记录 |
| 状态查询 | ✅ 详细状态信息 | ❌ 无状态查询 |
| 操作模式 | 4种模式 | 固定功能 |
| 用户体验 | 🌟 统一简洁 | 😐 需要记忆两个工具 |

## 总结

doc_sync.py是CodeLens项目中文档同步功能的**集大成者**，它不仅合并了原有两个工具的功能，还增加了智能检测、完整的变更追踪和状态管理能力。这个工具体现了"做一件事并做好"的Unix哲学，为项目文档维护提供了强大而易用的解决方案。