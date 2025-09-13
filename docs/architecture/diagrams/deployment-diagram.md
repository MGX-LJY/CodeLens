
# CodeLens 部署架构图

## 部署拓扑

```
┌─────────────────────────────────────────────────────────────┐
│                        开发环境                             │
├─────────────────────────────────────────────────────────────┤
│                      Claude Code                           │
│                   (MCP 客户端)                             │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP 协议调用
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      本地主机                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              CodeLens MCP 服务器                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  MCP 工具层                                            │ │
│  │  ├── doc_scan.py                                      │ │
│  │  ├── template_get.py                                  │ │
│  │  └── doc_verify.py                                    │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  服务层                                                │ │
│  │  ├── FileService                                      │ │
│  │  ├── TemplateService                                  │ │
│  │  ├── ValidationService                                │ │
│  │  └── LoggingService                                   │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      文件系统                              │
│  ├── 项目源代码目录                                         │
│  ├── 文档输出目录 (/docs)                                  │
│  ├── 日志文件目录 (/logs)                                  │
│  │   ├── codelens.log                                     │
│  │   ├── codelens.log.1.gz                                │
│  │   └── codelens.log.2.gz                                │
│  └── 配置文件                                              │
│      └── logging_config.json                              │
└─────────────────────────────────────────────────────────────┘
```

## 部署方式

### 1. **命令行部署** - 直接工具调用
```bash
# 项目文件扫描
python src/mcp_tools/doc_scan.py /path/to/project

# 模板获取
python src/mcp_tools/template_get.py --list-all

# 文档验证
python src/mcp_tools/doc_verify.py /path/to/project
```

### 2. **MCP 协议部署** - Claude Code 集成
```json
{
  "mcpServers": {
    "codelens": {
      "command": "python",
      "args": ["/path/to/codelens/src/mcp_tools/doc_scan.py"],
      "env": {
        "CODELENS_LOG_CONFIG": "logging_config.json"
      }
    }
  }
}
```

### 3. **配置化部署** - 企业级日志
```bash
# 使用自定义日志配置
export CODELENS_LOG_CONFIG=/path/to/custom_logging_config.json
python src/mcp_tools/doc_scan.py /project/path

# 生产环境部署
python -c "
from src.logging import initialize_logging
initialize_logging('production_logging_config.json')
# 然后运行 MCP 工具
"
```

## 运行环境要求

### **系统要求**
- **Python 版本**: Python 3.9+ (推荐 3.11+)
- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **内存**: 最小 256MB，推荐 512MB
- **磁盘空间**: 50MB (代码) + 可配置日志空间

### **权限要求**
- **文件读取权限**: 需要访问目标项目目录
- **文件写入权限**: 日志文件目录写入权限
- **网络权限**: 不需要网络访问（纯本地操作）

### **依赖要求**
- **零外部依赖**: 仅使用 Python 标准库
- **模块化设计**: 各组件可独立部署

## 日志系统部署

### **日志文件结构**
```
/logs/
├── codelens.log              # 当前日志文件
├── codelens.log.1.gz         # 轮转压缩日志
├── codelens.log.2.gz         # 历史压缩日志
└── statistics/               # 统计信息 (可选)
    ├── operation_stats.json
    └── performance_metrics.json
```

### **配置文件部署**
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
  "features": {
    "async_write": true,
    "operation_tracking": true,
    "context_manager": true
  }
}
```

## 性能优化部署

### **开发环境**
- 启用控制台日志便于调试
- 降低日志级别为 DEBUG
- 禁用异步写入便于实时查看

### **生产环境**
- 禁用控制台日志减少开销
- 设置 INFO 或 WARNING 级别
- 启用异步写入提升性能
- 配置合理的日志轮转策略

### **高负载环境**
- 增大日志文件大小限制
- 减少备份文件数量
- 启用文件压缩节省空间
- 监控磁盘使用情况

## 监控和维护

### **日志监控**
```bash
# 查看实时日志
tail -f logs/codelens.log

# 检查日志统计
python -c "
from src.logging import get_logger
logger = get_logger()
print(logger.get_statistics())
"
```

### **性能监控**
- 操作耗时统计
- 文件处理数量追踪
- 内存使用监控
- 磁盘空间检查
