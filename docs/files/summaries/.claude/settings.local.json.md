# .claude/settings.local.json - Claude Code权限配置

## 文件概述
Claude Code的本地权限配置文件，定义了允许、拒绝和需要询问的工具权限。

## 配置结构
```json
{
  "permissions": {
    "allow": [/* 允许的工具和命令 */],
    "deny": [/* 拒绝的工具和命令 */],
    "ask": [/* 需要询问的工具和命令 */]
  }
}
```

## 权限类别分析

### 文件系统操作权限
- `mcp__filesystem__*`: 文件系统MCP工具套件
  - `directory_tree`: 目录树查看
  - `read_text_file`: 文本文件读取
  - `write_file`: 文件写入
  - `edit_file`: 文件编辑
  - `list_directory*`: 目录列表查看
  - `create_directory`: 目录创建
  - `move_file`: 文件移动

### 文件读取权限
特定路径的读取权限：
- `/Users/martinezdavid/Documents/MG/**`: MG目录完全读取权限
- `/Users/martinezdavid/Documents/MG/code/wechat-automation-project/**`: 微信自动化项目权限
- `/tmp/**`: 临时文件权限

### Bash命令权限
允许的Bash命令模式：
- `Bash(rm:*)`: 删除命令
- `Bash(python:*)`: Python执行
- `Bash(find:*)`: 文件查找
- `Bash(grep:*)`: 文本搜索
- `Bash(chmod:*)`: 权限修改
- `Bash(sed:*)`: 文本编辑
- `Bash(cat:*)`: 文件查看
- `Bash(pkill:*)`: 进程终止
- `Bash(kill:*)`: 进程终止

### 特定Python环境权限
- `/usr/bin/python3:*`: 系统Python
- `/Users/martinezdavid/.virtualenvs/CodeLens/bin/python3:*`: CodeLens虚拟环境
- `claude mcp:*`: Claude MCP命令

### CodeLens MCP工具权限
核心工具权限：
- `mcp__codelens__init_tools`: 工具初始化
- `mcp__codelens__doc_guide`: 文档指导
- `mcp__codelens__task_*`: 任务管理套件
- `mcp__codelens__doc_sync`: 文档同步

### 创造模式工具权限
新增的创造模式权限：
- `mcp__codelens__create_guide`: 创造模式指导
- `mcp__codelens__create_requirement`: 需求创建

### 批量任务权限
特定的批量处理命令：
```bash
for i in {2..19}; do echo "Processing task file_summary_*_$i"; done
for i in {3..19}; do python src/mcp_tools/task_execute.py ... ; done
```

## 安全考虑

### 允许的操作
- 文件系统的基本CRUD操作
- Python脚本执行（限制在特定环境）
- CodeLens工具的完整访问
- 特定项目目录的读写权限

### 风险控制
- 路径权限限制在特定目录
- 系统命令有模式限制
- 没有网络访问权限
- 没有系统配置修改权限

## 配置更新历史

### 最近更新
- 增加创造模式工具权限
- 添加新的文件系统操作权限
- 扩展Python环境支持

### 权限数量统计
- **总权限数**: 约50个
- **文件系统权限**: 8个
- **Bash命令权限**: 15个
- **CodeLens工具权限**: 10个
- **路径权限**: 5个

## 维护建议

### 定期审查
- 检查未使用的权限
- 验证路径权限的必要性
- 更新过期的命令模式

### 安全最佳实践
- 最小权限原则
- 定期清理临时权限
- 监控权限使用情况

## 注意事项
- 权限更改需要重启Claude Code
- 路径必须使用绝对路径
- 通配符模式需要谨慎使用
- deny和ask列表当前为空，表示没有明确拒绝或需要询问的权限