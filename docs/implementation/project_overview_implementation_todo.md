# Project Overview工具实现TODO

## 概述
实现project_overview工具的提示词模式（方案B），生成让AI自主阅读项目文档的智能提示词。

## 实现计划

### 阶段1：核心功能开发 (预计2-3小时)

#### 1.1 创建简化核心功能
**实现方式**: 直接在MCP工具中实现，无需独立服务类

**TODO任务**：
- [ ] 扫描docs/architecture和docs/project文件夹，获取文件列表
- [ ] 生成简单的文件路径列表提示词
- [ ] 告诉AI需要阅读哪些文件即可

**核心思路**：
```python
def generate_file_list_prompt(project_path):
    """简单扫描并生成文件列表提示词"""
    project_path = Path(project_path)
    files_to_read = []
    
    # 扫描docs/project文件夹
    project_docs = project_path / "docs" / "project"
    if project_docs.exists():
        files_to_read.extend(list(project_docs.rglob("*.md")))
    
    # 扫描docs/architecture文件夹  
    arch_docs = project_path / "docs" / "architecture"
    if arch_docs.exists():
        files_to_read.extend(list(arch_docs.rglob("*.md")))
    
    # 生成简单提示词：告诉AI读哪些文件
    return f"请按顺序阅读以下项目文档文件：\n" + \
           "\n".join([f"- {f.relative_to(project_path)}" for f in files_to_read])
```

#### 1.2 创建简化MCP工具接口
**文件**: `src/mcp_tools/project_overview.py`

**TODO任务**：
- [ ] 创建 `ProjectOverviewTool` 类，继承MCP基类
- [ ] 实现 `get_tool_definition()` 方法 - 定义MCP工具接口
- [ ] 实现 `execute()` 方法 - 扫描文件并生成简单提示词
- [ ] 基本错误处理（目录不存在等）

**简化工具参数**：
```python
{
    "project_path": str,      # 必需：项目根路径
}
```

#### 1.3 集成到MCP服务器
**文件**: `mcp_server.py`

**TODO任务**：
- [ ] 在 `MCPServer` 类中导入 `ProjectOverviewTool`
- [ ] 在 `get_available_tools()` 方法中注册工具
- [ ] 在 `handle_call_tool()` 方法中添加工具处理逻辑
- [ ] 测试MCP服务器集成

## 简化实现（总计1-2小时）

### 核心功能
- 扫描 `docs/project` 和 `docs/architecture` 文件夹
- 返回文件列表的简单提示词
- 告诉AI按顺序阅读这些文件即可

## 简化实现代码示例

### 核心实现函数
```python
def generate_file_list_prompt(project_path):
    """简单扫描并生成文件列表提示词"""
    from pathlib import Path
    
    project_path = Path(project_path)
    files_to_read = []
    
    # 扫描docs/project文件夹
    project_docs = project_path / "docs" / "project"
    if project_docs.exists():
        files_to_read.extend(list(project_docs.rglob("*.md")))
    
    # 扫描docs/architecture文件夹  
    arch_docs = project_path / "docs" / "architecture"
    if arch_docs.exists():
        files_to_read.extend(list(arch_docs.rglob("*.md")))
    
    if not files_to_read:
        return "没有找到项目文档文件（docs/project或docs/architecture目录）"
    
    # 简单排序：README优先
    files_to_read.sort(key=lambda f: (0 if "readme" in f.name.lower() else 1, f.name))
    
    # 生成简单提示词：告诉AI读哪些文件
    prompt = f"请按顺序阅读以下{len(files_to_read)}个项目文档文件：\n\n"
    for f in files_to_read:
        prompt += f"- {f.relative_to(project_path)}\n"
    
    prompt += "\n阅读完成后，请总结项目的核心功能和架构特点。"
    return prompt
```

### MCP工具定义
```python
def get_tool_definition():
    return {
        "name": "project_overview",
        "description": "扫描项目docs文件夹，生成文档阅读提示词",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "项目根路径"
                }
            },
            "required": ["project_path"]
        }
    }
```

## 测试命令
```bash
# 测试CodeLens项目本身
python src/mcp_tools/project_overview.py /Users/martinezdavid/Documents/MG/code/CodeLens
```

## 完成标准
- [ ] 能扫描docs文件夹并列出.md文件
- [ ] 生成简单的文件列表提示词
- [ ] MCP工具集成成功
- [ ] 基本错误处理

## 预计完成时间
**总计：1-2小时**

---

# Doc Update系统简化实现TODO

## 概述
基于文件指纹的简单文档更新检测系统。

## 核心思路
- `doc_update_init`: 扫描项目文件，记录文件hash作为基点
- `doc_update`: 对比文件hash变化，告诉AI哪些文件变了，需要更新对应文档

## 简化实现计划

### 阶段1：doc_update_init工具 (预计30分钟)

#### 核心功能
**文件**: `src/mcp_tools/doc_update_init.py`

**TODO任务**：
- [ ] 扫描项目源码文件（src文件夹下的.py文件）
- [ ] 计算文件hash值
- [ ] 保存到 `.codelens/file_fingerprints.json`

**简化实现**：
```python
def init_file_fingerprints(project_path):
    """扫描项目文件并记录hash基点"""
    from pathlib import Path
    import hashlib
    import json
    from datetime import datetime
    
    project_path = Path(project_path)
    fingerprints = {
        "created_at": datetime.now().isoformat(),
        "files": {}
    }
    
    # 扫描src文件夹下的.py文件
    src_path = project_path / "src"
    if src_path.exists():
        for py_file in src_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                file_hash = hashlib.md5(content.encode()).hexdigest()
                fingerprints["files"][str(py_file.relative_to(project_path))] = {
                    "hash": file_hash,
                    "size": py_file.stat().st_size,
                    "modified_time": datetime.fromtimestamp(py_file.stat().st_mtime).isoformat()
                }
            except Exception as e:
                print(f"跳过文件 {py_file}: {e}")
    
    # 也扫描根目录的主要文件
    for main_file in ["mcp_server.py", "main.py", "app.py"]:
        main_path = project_path / main_file
        if main_path.exists():
            try:
                content = main_path.read_text(encoding='utf-8')
                file_hash = hashlib.md5(content.encode()).hexdigest()
                fingerprints["files"][main_file] = {
                    "hash": file_hash,
                    "size": main_path.stat().st_size,
                    "modified_time": datetime.fromtimestamp(main_path.stat().st_mtime).isoformat()
                }
            except Exception as e:
                print(f"跳过文件 {main_path}: {e}")
    
    # 保存指纹文件
    fingerprints_dir = project_path / ".codelens"
    fingerprints_dir.mkdir(exist_ok=True)
    
    fingerprints_file = fingerprints_dir / "file_fingerprints.json"
    with open(fingerprints_file, 'w', encoding='utf-8') as f:
        json.dump(fingerprints, f, indent=2, ensure_ascii=False)
    
    return f"已记录 {len(fingerprints['files'])} 个文件的指纹基点"
```

### 阶段2：doc_update工具 (预计45分钟)

#### 核心功能
**文件**: `src/mcp_tools/doc_update.py`

**TODO任务**：
- [ ] 重新扫描项目文件并计算hash
- [ ] 对比指纹文件，找出变化的文件
- [ ] 生成简单的更新建议提示词
- [ ] 更新指纹基点

**简化实现**：
```python
def detect_file_changes(project_path):
    """检测文件变化并生成更新建议"""
    from pathlib import Path
    import hashlib
    import json
    from datetime import datetime
    
    project_path = Path(project_path)
    fingerprints_file = project_path / ".codelens" / "file_fingerprints.json"
    
    if not fingerprints_file.exists():
        return "请先运行 doc_update_init 初始化指纹基点"
    
    # 加载旧指纹
    with open(fingerprints_file, 'r', encoding='utf-8') as f:
        old_fingerprints = json.load(f)
    
    # 扫描当前文件状态
    current_files = {}
    src_path = project_path / "src"
    if src_path.exists():
        for py_file in src_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                file_hash = hashlib.md5(content.encode()).hexdigest()
                current_files[str(py_file.relative_to(project_path))] = {
                    "hash": file_hash,
                    "size": py_file.stat().st_size,
                    "modified_time": datetime.fromtimestamp(py_file.stat().st_mtime).isoformat()
                }
            except Exception as e:
                print(f"跳过文件 {py_file}: {e}")
    
    for main_file in ["mcp_server.py", "main.py", "app.py"]:
        main_path = project_path / main_file
        if main_path.exists():
            try:
                content = main_path.read_text(encoding='utf-8')
                file_hash = hashlib.md5(content.encode()).hexdigest()
                current_files[main_file] = {
                    "hash": file_hash,
                    "size": main_path.stat().st_size,
                    "modified_time": datetime.fromtimestamp(main_path.stat().st_mtime).isoformat()
                }
            except Exception as e:
                print(f"跳过文件 {main_path}: {e}")
    
    # 检测变化
    changed_files = []
    new_files = []
    deleted_files = []
    
    old_files = old_fingerprints.get("files", {})
    
    for file_path, current_info in current_files.items():
        if file_path in old_files:
            if current_info["hash"] != old_files[file_path]["hash"]:
                changed_files.append(file_path)
        else:
            new_files.append(file_path)
    
    for file_path in old_files:
        if file_path not in current_files:
            deleted_files.append(file_path)
    
    # 生成更新建议提示词
    if not changed_files and not new_files and not deleted_files:
        suggestion = "没有检测到文件变化，无需更新文档。"
    else:
        suggestion = "检测到以下文件变化，建议更新相关文档：\n\n"
        
        if changed_files:
            suggestion += "📝 已修改的文件：\n"
            for file in changed_files:
                suggestion += f"- {file}\n"
            suggestion += "\n"
        
        if new_files:
            suggestion += "✨ 新增的文件：\n"
            for file in new_files:
                suggestion += f"- {file}\n"
            suggestion += "\n"
        
        if deleted_files:
            suggestion += "🗑️ 已删除的文件：\n"
            for file in deleted_files:
                suggestion += f"- {file}\n"
            suggestion += "\n"
        
        suggestion += "建议检查并更新这些文件对应的文档内容。"
    
    # 更新指纹基点
    new_fingerprints = {
        "created_at": old_fingerprints.get("created_at"),
        "last_updated": datetime.now().isoformat(),
        "files": current_files
    }
    
    with open(fingerprints_file, 'w', encoding='utf-8') as f:
        json.dump(new_fingerprints, f, indent=2, ensure_ascii=False)
    
    suggestion += f"\n✅ 指纹基点已更新，共记录 {len(current_files)} 个文件。"
    
    return suggestion
```

### 阶段3：MCP工具集成 (预计30分钟)

#### TODO任务：
- [ ] 在 `mcp_server.py` 中注册两个新工具
- [ ] 简单测试验证

#### MCP工具定义
```python
# doc_update_init工具
{
    "name": "doc_update_init",
    "description": "初始化项目文件指纹基点，用于后续变化检测",
    "inputSchema": {
        "type": "object",
        "properties": {
            "project_path": {"type": "string", "description": "项目根路径"}
        },
        "required": ["project_path"]
    }
}

# doc_update工具
{
    "name": "doc_update", 
    "description": "检测项目文件变化并生成文档更新建议",
    "inputSchema": {
        "type": "object",
        "properties": {
            "project_path": {"type": "string", "description": "项目根路径"}
        },
        "required": ["project_path"]
    }
}
```

## 使用流程

### 第一次使用
```bash
# 1. 初始化指纹基点
python src/mcp_tools/doc_update_init.py /path/to/project
# 输出：已记录 25 个文件的指纹基点
```

### 后续使用
```bash
# 2. 检测变化
python src/mcp_tools/doc_update.py /path/to/project
# 输出：
# 检测到以下文件变化，建议更新相关文档：
# 📝 已修改的文件：
# - src/mcp_tools/task_execute.py
# - mcp_server.py
# ✅ 指纹基点已更新，共记录 25 个文件。
```

## 完成标准
- [ ] doc_update_init 能正确扫描并记录文件hash
- [ ] doc_update 能检测文件变化并生成建议
- [ ] 指纹文件正确保存到 `.codelens/file_fingerprints.json`
- [ ] 两个MCP工具集成成功

## 预计完成时间
**总计：1.5-2小时**
- doc_update_init工具：30分钟
- doc_update工具：45分钟  
- MCP集成和测试：30分钟