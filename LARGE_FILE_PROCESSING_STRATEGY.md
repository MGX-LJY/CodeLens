# 🚀 大文件处理解决方案

## 问题
处理大型代码文件（5000+行）时面临的问题：
- 内存不足，一次性加载大文件导致崩溃
- 处理时间过长，用户体验差
- 生成文档质量差，结构混乱

## 解决方案

### 1. 智能分块
**核心思路**: 按代码结构智能切分，不破坏逻辑

```python
def smart_split_file(content: str, max_lines=1500):
    """智能分块：按类和函数边界切分"""
    chunks = []
    lines = content.splitlines()
    current_chunk = []
    
    for i, line in enumerate(lines):
        current_chunk.append(line)
        
        # 检测分块点：类定义或函数定义
        if (line.strip().startswith(('class ', 'def ')) and 
            len(current_chunk) > 500):
            chunks.append('\n'.join(current_chunk[:-1]))
            current_chunk = [line]
        
        # 强制分块：防止块过大
        elif len(current_chunk) >= max_lines:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks
```

### 2. 任务分解
**核心思路**: 将大文件分解为多个子任务，利用现有任务系统

```python
def create_large_file_tasks(file_path, project_path):
    """为大文件创建子任务"""
    
    # 1. 读取文件内容并分块
    with open(file_path, 'r') as f:
        content = f.read()
    
    chunks = smart_split_file(content)
    
    # 2. 为每个块创建文件分析任务
    chunk_tasks = []
    for i, chunk in enumerate(chunks):
        # 保存块内容到临时文件
        chunk_file = f"{file_path}.chunk_{i}.tmp"
        with open(chunk_file, 'w') as f:
            f.write(chunk)
        
        # 创建任务
        task = {
            'id': f"large_file_chunk_{hash(file_path)}_{i}",
            'type': 'file_summary',
            'status': 'pending',
            'file_path': chunk_file,
            'chunk_id': i,
            'total_chunks': len(chunks),
            'original_file': file_path
        }
        chunk_tasks.append(task)
    
    # 3. 创建合并任务
    merge_task = {
        'id': f"large_file_merge_{hash(file_path)}",
        'type': 'large_file_merge', 
        'status': 'pending',
        'depends_on': [task['id'] for task in chunk_tasks],
        'original_file': file_path,
        'chunk_tasks': [task['id'] for task in chunk_tasks]
    }
    
    return chunk_tasks + [merge_task]
```

### 3. 顺序处理
**核心思路**: Claude按顺序处理每个块，最后合并结果

```python
def process_large_file_chunk(chunk_task):
    """处理大文件的单个块"""
    
    # 读取块内容
    with open(chunk_task['file_path'], 'r') as f:
        chunk_content = f.read()
    
    # 生成块的文档
    doc_fragment = analyze_and_document_chunk(
        chunk_content, 
        chunk_task['chunk_id'],
        chunk_task['total_chunks'],
        chunk_task['original_file']
    )
    
    # 保存块文档
    chunk_doc_path = f"{chunk_task['original_file']}.chunk_{chunk_task['chunk_id']}.md"
    with open(chunk_doc_path, 'w') as f:
        f.write(doc_fragment)
    
    # 清理临时文件
    os.remove(chunk_task['file_path'])
    
    return {
        'chunk_id': chunk_task['chunk_id'],
        'doc_path': chunk_doc_path,
        'lines_processed': len(chunk_content.splitlines())
    }

def merge_large_file_docs(merge_task):
    """合并大文件的所有块文档"""
    
    # 收集所有块的文档
    chunk_docs = []
    for chunk_task_id in merge_task['chunk_tasks']:
        # 找到对应的块文档文件
        chunk_id = extract_chunk_id(chunk_task_id)
        chunk_doc_path = f"{merge_task['original_file']}.chunk_{chunk_id}.md"
        
        if os.path.exists(chunk_doc_path):
            with open(chunk_doc_path, 'r') as f:
                chunk_docs.append({
                    'id': chunk_id,
                    'content': f.read()
                })
    
    # 按顺序排列并合并
    chunk_docs.sort(key=lambda x: x['id'])
    
    final_doc = generate_file_header(merge_task['original_file'])
    final_doc += "\n## 文件分析\n\n"
    
    for doc in chunk_docs:
        final_doc += f"### 代码块 {doc['id'] + 1}\n\n"
        final_doc += doc['content']
        final_doc += "\n\n"
    
    # 保存最终文档
    final_doc_path = get_file_doc_path(merge_task['original_file'])
    with open(final_doc_path, 'w') as f:
        f.write(final_doc)
    
    # 清理临时块文档
    for doc in chunk_docs:
        chunk_doc_path = f"{merge_task['original_file']}.chunk_{doc['id']}.md"
        if os.path.exists(chunk_doc_path):
            os.remove(chunk_doc_path)
    
    return final_doc_path
```

## 集成到现有任务系统

### 修改任务初始化 (task_init.py)
检测大文件时自动创建子任务：

```python
def handle_large_file_in_task_init(file_path, project_path):
    """在任务初始化时处理大文件"""
    
    if is_large_file(file_path, threshold=5000):
        # 创建大文件子任务
        chunk_tasks = create_large_file_tasks(file_path, project_path) 
        
        # 将子任务添加到任务列表
        for task in chunk_tasks:
            task_manager.add_task(task)
        
        print(f"大文件 {file_path} 已分解为 {len(chunk_tasks)-1} 个子任务")
        return True
    
    return False  # 不是大文件，正常处理

def is_large_file(file_path, threshold=5000):
    """检测是否为大文件"""
    try:
        with open(file_path, 'r') as f:
            line_count = sum(1 for _ in f)
        return line_count > threshold
    except:
        return False
```

### 修改任务执行 (task_execute.py)
添加大文件任务类型处理：

```python
def execute_task_by_type(task):
    """根据任务类型执行任务"""
    
    if task['type'] == 'file_summary':
        # 检查是否为大文件块任务
        if 'chunk_id' in task:
            return process_large_file_chunk(task)
        else:
            return process_normal_file_summary(task)
    
    elif task['type'] == 'large_file_merge':
        return merge_large_file_docs(task)
    
    # ... 其他任务类型
```

### 修改文件服务 (file_service.py)
添加分块器功能：

```python
class FileService:
    def __init__(self):
        # ... 现有代码
        self.large_file_threshold = 5000
    
    def read_file_safe(self, file_path: str, max_size: int = 50000) -> Optional[str]:
        """增强的安全文件读取，支持大文件处理"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return None

            # 检查文件大小和行数
            file_size = file_path.stat().st_size
            if file_size > max_size:
                # 检查是否为大文件（按行数）
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                
                if line_count > self.large_file_threshold:
                    print(f"检测到大文件 {file_path} ({line_count} 行)，建议使用大文件处理流程")
                    return "LARGE_FILE_DETECTED"  # 特殊标记
                else:
                    print(f"警告: 文件 {file_path} 过大 ({file_size} 字节)，跳过")
                    return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件错误 {file_path}: {e}")
            return None
```

## 实际处理流程

**正常文件 (<5000行)**:
```
文件扫描 → 直接处理 → 生成文档
```

**大文件 (≥5000行)**:
```
文件扫描 → 检测大文件 → 智能分块 → 创建子任务
    ↓
块任务1 → Claude处理 → 块文档1
块任务2 → Claude处理 → 块文档2  
块任务N → Claude处理 → 块文档N
    ↓
合并任务 → 整合所有块 → 最终文档
```

## 关键优势

1. **内存安全**: 分块处理，避免内存溢出
2. **任务兼容**: 完全融入现有任务系统  
3. **结构完整**: 智能分块，保持代码逻辑
4. **渐进反馈**: 按块处理，实时显示进度

## 适配现有系统

**无需修改**:
- 模板系统继续使用
- MCP接口保持不变
- 任务状态管理不变

**最小修改**:
- `task_init.py`: 添加大文件检测逻辑
- `task_execute.py`: 增加两种新任务类型处理
- `file_service.py`: 增强文件读取功能

## 下一步实施

1. **第一步**: 在 `file_service.py` 添加 `is_large_file()` 检测
2. **第二步**: 在 `task_init.py` 添加大文件任务分解逻辑  
3. **第三步**: 在 `task_execute.py` 添加块任务和合并任务处理
4. **第四步**: 测试并优化分块大小和处理逻辑