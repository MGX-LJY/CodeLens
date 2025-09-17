# src/mcp_tools/doc_sync.py - 智能文档同步工具

## 文件概述
CodeLens的MCP智能文档同步工具，合并了doc_update_init和doc_update功能，自动检测项目状态并执行初始化或更新检测，记录完整变更历史。

## 导入模块
```python
import sys, os, json, hashlib
from pathlib import Path
from datetime import datetime
from src.logging import get_logger
```

## 全局变量
- `project_root`: 项目根目录路径

## 核心常量
- **工具名称**: "doc_sync"
- **支持模式**: auto, init, update, status
- **文件变更类型**: modified, added, deleted

## 类汇总表

| 类名 | 功能 | 关键方法 | 特性 |
|------|------|----------|------|
| `DocSyncTool` | 智能文档同步工具类 | `execute()`, `_detect_mode()` | 四模式智能检测 |

## 详细功能分析

### DocSyncTool类核心功能

#### MCP工具定义
```python
def get_tool_definition(self) -> Dict[str, Any]:
    return {
        "name": "doc_sync",
        "description": "智能文档同步工具 - 自动检测并处理项目文件变更",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "项目根路径"},
                "mode": {"enum": ["auto", "init", "update", "status"]},
                "record_changes": {"type": "boolean", "description": "是否记录变更历史"}
            }
        }
    }
```

#### 智能模式检测
```python
def _detect_mode(self, project_path: Path) -> str:
    """智能检测应该执行的模式"""
    fingerprint_file = project_path / ".codelens" / "project_fingerprint.json"
    return "init" if not fingerprint_file.exists() else "update"
```

## 四种工作模式

### 1. auto模式（智能检测）
- 自动检测项目状态
- 无指纹文件 → 执行init
- 有指纹文件 → 执行update
- **推荐使用模式**

### 2. init模式（强制初始化）
- 重新扫描整个项目
- 生成新的项目指纹
- 创建完整的文件记录
- 适用于首次使用或重新开始

### 3. update模式（强制更新）
- 基于现有指纹检测变更
- 比较文件hash值
- 识别新增、修改、删除文件
- 适用于日常开发同步

### 4. status模式（状态查看）
- 显示当前项目状态
- 指纹文件信息
- 最近变更历史
- 不执行实际同步操作

## 数据流分析

### 初始化流程
```
项目路径 → 文件扫描 → Hash计算 → 指纹生成 → 保存到.codelens/project_fingerprint.json
```

### 更新检测流程
```
读取旧指纹 → 重新扫描 → Hash对比 → 变更分类 → 记录变更历史 → 更新指纹
```

### 变更记录流程
```
检测到变更 → 生成变更ID → 记录到change_history.json → 返回变更统计
```

## 文件结构管理

### .codelens目录结构
```
.codelens/
├── project_fingerprint.json    # 项目文件指纹
├── change_history.json         # 变更历史记录
└── [其他配置文件]
```

### 项目指纹格式
```json
{
  "project_path": "/path/to/project",
  "scan_time": "2025-01-01T10:00:00",
  "total_files": 50,
  "files": {
    "src/main.py": {
      "hash": "abc123...",
      "size": 1024,
      "modified": "2025-01-01T09:00:00"
    }
  }
}
```

### 变更历史格式
```json
{
  "change_1234567890": {
    "timestamp": "2025-01-01T10:00:00",
    "type": "update",
    "files_count": 50,
    "changes": {
      "modified": ["src/main.py", "src/config.py"],
      "added": ["src/new_feature.py"],
      "deleted": ["src/old_module.py"]
    },
    "summary": "检测到6个文件变更：修改2，新增1，删除1"
  }
}
```

## 错误处理机制

### 路径验证
```python
if not project_path.exists():
    return self._error_response(f"Project path does not exist: {project_path}")

if not project_path.is_dir():
    return self._error_response(f"Project path is not a directory: {project_path}")
```

### 文件操作异常处理
- JSON读写异常捕获
- Hash计算失败处理
- 目录创建权限检查
- 编码问题处理（跳过二进制文件）

## 性能优化考虑

### 文件过滤策略
- 排除.git目录
- 排除__pycache__目录
- 排除二进制文件
- 支持.gitignore规则

### Hash计算优化
- 使用SHA256 hash算法
- 流式读取大文件
- 跳过无法读取的文件

## 日志集成

### 详细操作日志
```python
self.logger.info("开始doc_sync操作", {"arguments": arguments})
self.logger.info("智能检测模式: update")
self.logger.info("扫描完成，共检测到 50 个代码文件")
self.logger.info("更新检测完成，变更统计: 修改6, 新增4, 删除2")
```

### 错误日志记录
```python
self.logger.warning("跳过文件 /path/file: 'utf-8' codec can't decode")
self.logger.error("执行失败", exc_info=e)
```

## 使用示例

### 基本使用
```python
# 智能检测模式
doc_sync_tool.execute({"project_path": "/path/to/project", "mode": "auto"})

# 强制初始化
doc_sync_tool.execute({"project_path": "/path/to/project", "mode": "init"})

# 查看状态
doc_sync_tool.execute({"project_path": "/path/to/project", "mode": "status"})
```

### 返回结果格式
```json
{
  "success": true,
  "tool": "doc_sync",
  "data": {
    "operation": "update",
    "has_changes": true,
    "files_count": 50,
    "changes": {
      "modified": ["src/main.py"],
      "added": ["src/new.py"],
      "deleted": ["src/old.py"]
    },
    "suggestion": "检测到文件变化，建议更新相关文档..."
  }
}
```

## 扩展性评估
**高扩展性**:
- 可插拔的文件过滤器
- 灵活的Hash算法选择
- 可配置的变更记录格式
- 支持自定义忽略规则

## 代码质量评估
**优秀**:
- 清晰的模式分离
- 完善的错误处理
- 详细的日志记录
- 标准的MCP接口实现

## 文档完整性
**完整**: 包含详细的工具描述、参数说明和使用示例

## 注意事项
- 需要读写权限在项目目录创建.codelens文件夹
- 大型项目首次扫描可能耗时较长
- 变更历史文件会随时间增长，建议定期清理
- UTF-8编码问题会导致某些文件被跳过
- **与doc_update系列工具功能重叠，建议统一使用doc_sync**