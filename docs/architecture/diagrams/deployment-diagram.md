
# CodeLens 部署架构图

## 部署拓扑

```
┌─────────────────────────────────────────────────────────────┐
│                        开发环境                             │
├─────────────────────────────────────────────────────────────┤
│                      Claude Code                           │
│                 (智能化文档生成客户端)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP 协议调用 (7个专业工具)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      本地主机                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           CodeLens 智能化任务驱动 MCP 服务器            │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  MCP 工具层 (7个专业工具)                              │ │
│  │  ├── doc_guide.py    (智能项目分析)                   │ │
│  │  ├── task_init.py    (任务计划生成)                   │ │
│  │  ├── task_execute.py (任务执行管理)                   │ │
│  │  ├── task_status.py  (状态监控中心)                   │ │
│  │  ├── doc_scan.py     (项目文件扫描)                   │ │
│  │  ├── template_get.py (模板获取)                       │ │
│  │  └── doc_verify.py   (文档验证)                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  任务引擎层 (Task Engine)                             │ │
│  │  ├── TaskManager     (14种任务类型管理)               │ │
│  │  ├── PhaseController (5阶段严格控制)                  │ │
│  │  └── StateTracker    (状态跟踪监控)                   │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  服务层 (Services)                                    │ │
│  │  ├── FileService     (智能文件分析)                   │ │
│  │  ├── TemplateService (16个核心模板)                   │ │
│  │  └── ValidationService (完整性验证)                   │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      文件系统                              │
│  ├── 项目源代码目录                                         │
│  ├── 文档输出目录 (/docs)                                  │
│  │   ├── architecture/   (架构层文档)                     │
│  │   ├── modules/        (模块层文档)                     │
│  │   ├── files/          (文件层文档)                     │
│  │   └── project/        (项目层文档)                     │
│  └── 任务状态存储 (.codelens/)                             │
│      ├── tasks.json      (任务状态文件)                    │
│      └── execution_history.json (执行历史)                │
└─────────────────────────────────────────────────────────────┘
```

## 部署方式

### 1. **命令行部署** - 直接工具调用
```bash
# 智能项目分析
python src/mcp_tools/doc_guide.py /path/to/project

# 任务计划生成
python src/mcp_tools/task_init.py /path/to/project --analysis-file analysis.json

# 任务执行管理
python src/mcp_tools/task_execute.py /path/to/project --task-id <task_id> --mode execute

# 状态监控检查
python src/mcp_tools/task_status.py /path/to/project --type overall_status

# 项目文件扫描
python src/mcp_tools/doc_scan.py /path/to/project --no-content

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
      "args": ["/path/to/codelens/src/mcp_tools/doc_guide.py"]
    }
  }
}
```

**支持的7个MCP工具**:
- `doc_guide.py`: 智能项目分析
- `task_init.py`: 任务计划生成  
- `task_execute.py`: 任务执行管理
- `task_status.py`: 状态监控中心
- `doc_scan.py`: 项目文件扫描
- `template_get.py`: 模板获取
- `doc_verify.py`: 文档验证

### 3. **智能化工作流部署** - 完整5阶段流程
```bash
# 完整的智能化文档生成工作流
# 1. 项目分析
python src/mcp_tools/doc_guide.py /path/to/project > analysis.json

# 2. 任务规划
python src/mcp_tools/task_init.py /path/to/project --analysis-file analysis.json --create-tasks

# 3. 状态监控
python src/mcp_tools/task_status.py /path/to/project --type current_task

# 4. 任务执行 (循环执行直到完成)
python src/mcp_tools/task_execute.py /path/to/project --task-id <task_id> --mode execute

# 5. 文档验证
python src/mcp_tools/doc_verify.py /path/to/project --type full_status
```

## 运行环境要求

### **系统要求**
- **Python 版本**: Python 3.9+ (推荐 3.11+)
- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **内存**: 最小 256MB，推荐 512MB
- **磁盘空间**: 50MB (代码) + 可变文档空间 + 任务状态存储

### **权限要求**
- **文件读取权限**: 需要访问目标项目目录
- **文件写入权限**: 文档输出目录和.codelens状态目录写入权限
- **网络权限**: 不需要网络访问（纯本地操作）

### **依赖要求**
- **零外部依赖**: 仅使用 Python 标准库
- **模块化设计**: 各组件可独立部署

## 任务状态存储部署

### **状态文件结构**
```
/.codelens/
├── tasks.json               # 主任务状态文件
├── execution_history.json   # 执行历史记录
└── performance_metrics.json # 性能指标统计 (可选)
```

### **任务状态文件格式**
```json
{
  "tasks": {
    "task_id": {
      "id": "task_id",
      "type": "file_summary", 
      "description": "生成app.py文件摘要",
      "phase": "phase_2_files",
      "status": "completed",
      "target_file": "app.py",
      "template": "file_summary",
      "output_path": "docs/files/summaries/app.py.md",
      "dependencies": ["scan_task_id"],
      "priority": "high",
      "created_at": "2025-09-13T10:30:00Z",
      "completed_at": "2025-09-13T10:35:00Z",
      "estimated_time": "3 minutes",
      "metadata": {}
    }
  },
  "metadata": {
    "project_path": "/path/to/project",
    "created_at": "2025-09-13T10:00:00Z",
    "last_updated": "2025-09-13T10:35:00Z"
  }
}
```

## 性能优化部署

### **开发环境**
- 使用task_status工具实时监控任务执行
- 启用详细的错误信息输出
- 保留完整的任务执行历史用于调试

### **生产环境**  
- 配置合理的任务状态文件轮转策略
- 定期清理旧的执行历史记录
- 启用性能指标收集和分析
- 监控.codelens目录磁盘使用情况

### **高负载环境**
- 增大文档输出目录磁盘空间
- 优化任务并发执行策略
- 配置任务状态检查点，支持增量恢复
- 监控内存使用和文件句柄数量

## 监控和维护

### **任务状态监控**
```bash
# 检查总体状态
python src/mcp_tools/task_status.py /path/to/project --type overall_status

# 查看当前任务
python src/mcp_tools/task_status.py /path/to/project --type current_task

# 执行健康检查
python src/mcp_tools/task_status.py /path/to/project --type health_check

# 获取执行建议
python src/mcp_tools/task_status.py /path/to/project --type next_actions
```

### **性能监控**
- 任务执行时间统计
- 阶段完成率追踪  
- 文档生成数量统计
- 系统健康状态检查
- 内存使用和磁盘空间监控

### **维护操作**
```bash
# 清理任务状态
rm -rf .codelens/

# 重新初始化项目
python src/mcp_tools/doc_guide.py /path/to/project
python src/mcp_tools/task_init.py /path/to/project --analysis-file analysis.json

# 状态文件备份
cp .codelens/tasks.json .codelens/tasks.backup.json
```
