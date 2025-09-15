# CodeLens AI工具设计方案 V2.0

## 概述

基于实用性原则，重新设计两个核心AI辅助工具：

1. **project_overview工具** - 简单直接的项目文档阅读器
2. **doc_update_init + doc_update工具** - 基于文件指纹的智能文档更新检测系统

## 1. project_overview工具设计

### 1.1 设计原则
- **简单直接**：不做复杂的结构化处理，直接读取文件内容
- **完整覆盖**：读取docs/architecture和docs/project文件夹的所有文件
- **AI友好**：提供清晰的文件组织和提示词

### 1.2 实现方案

#### 方案A：直接文件内容输出
```python
class ProjectOverviewCore:
    def read_project_docs(self, project_path):
        """直接读取并返回所有项目文档内容"""
        result = {
            "architecture_docs": {},
            "project_docs": {},
            "reading_guide": self._generate_reading_guide()
        }
        
        # 读取architecture文件夹
        arch_path = Path(project_path) / "docs" / "architecture"
        for file_path in arch_path.rglob("*.md"):
            relative_path = file_path.relative_to(arch_path)
            result["architecture_docs"][str(relative_path)] = file_path.read_text(encoding='utf-8')
        
        # 读取project文件夹  
        project_path = Path(project_path) / "docs" / "project"
        for file_path in project_path.rglob("*.md"):
            relative_path = file_path.relative_to(project_path)
            result["project_docs"][str(relative_path)] = file_path.read_text(encoding='utf-8')
            
        return result

    def _generate_reading_guide(self):
        """生成AI阅读指南"""
        return """
        # CodeLens项目文档阅读指南
        
        ## 阅读顺序建议：
        1. **项目概述** - 先读 project/README.md 了解整体概况
        2. **系统架构** - 读 architecture/overview.md 理解五层架构
        3. **技术栈** - 读 architecture/tech-stack.md 了解技术选型  
        4. **数据流** - 读 architecture/data-flow.md 理解工作流程
        5. **组件关系** - 读 architecture/diagrams/ 了解组件详情
        
        ## 重点关注：
        - CodeLens是智能化任务驱动MCP服务器
        - 五层架构：MCP接口层、任务引擎层、热重载系统层、服务层、基础设施层
        - 7个专业MCP工具 + 5阶段工作流程
        - 支持14种任务类型和16个核心模板
        - 具备完整的热重载系统
        """
```

#### 方案B：AI提示词方式
```python
def generate_ai_prompt(self, project_path):
    """生成让AI自主读取文档的提示词"""
    docs_structure = self._scan_docs_structure(project_path)
    project_name = Path(project_path).name
    
    prompt = f"""
请按以下顺序阅读这个项目的文档，全面了解项目信息：

## 必读文档列表：

### 项目核心文档：
{self._format_file_list(docs_structure['project'])}

### 架构设计文档：  
{self._format_file_list(docs_structure['architecture'])}

## 通用阅读指导：
1. **项目概览**：先从README.md开始，理解项目的整体定位和核心功能
2. **架构理解**：阅读architecture文件夹中的文档，重点关注：
   - overview.md: 系统架构概述
   - tech-stack.md: 技术栈和依赖
   - data-flow.md: 数据流和工作流程
   - diagrams/: 架构图和组件关系
3. **项目详情**：阅读project文件夹中的其他文档了解具体特性

## 阅读重点：
- 项目的核心定位和价值主张
- 技术架构和设计理念  
- 主要功能特性和使用方法
- 部署和集成方式

请你现在开始按顺序阅读这些文件，阅读完成后总结你对"{project_name}"项目的理解。
"""
    return prompt
```

### 1.3 MCP工具配置

```python
def get_tool_definition(self):
    return {
        "name": "project_overview",
        "description": "通用项目文档阅读工具，快速让AI了解任何项目的docs/architecture和docs/project文件夹内容",
        "inputSchema": {
            "type": "object", 
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "项目根路径（任何包含docs/architecture和docs/project文件夹的项目）"
                },
                "mode": {
                    "type": "string",
                    "enum": ["direct", "prompt"],
                    "description": "direct: 直接返回所有文档内容, prompt: 生成AI阅读提示词",
                    "default": "direct"
                },
                "include_subdirs": {
                    "type": "boolean",
                    "description": "是否包含子目录中的文档",
                    "default": true
                }
            },
            "required": ["project_path"]
        }
    }
```

## 2. doc_update系统设计

### 2.1 核心思路

建立**文件指纹缓存系统**：
- `doc_update_init`: 建立项目文件的初始"指纹基点"
- `doc_update`: 对比指纹变化，提供更新建议，然后**更新指纹基点**为新的对比基准

**工作流程**：
1. **第一次 init**：建立初始指纹基点
2. **第二次 update**：检测变化 → 提供更新建议 → 清除旧指纹 → 建立新指纹基点  
3. **第三次 update**：基于新基点检测变化 → 提供更新建议 → 再次更新指纹基点
4. **持续循环**：每次update都会更新指纹基点，确保下次对比的准确性

### 2.2 文件指纹系统

#### 2.2.1 指纹数据结构

```python
# .codelens/doc_fingerprints.json
{
    "created_at": "2025-09-15T10:30:00Z",
    "last_updated": "2025-09-15T15:45:00Z", 
    "source_files": {
        "src/mcp_tools/doc_guide.py": {
            "hash": "abc123...",
            "size": 15420,
            "modified_time": "2025-09-15T15:30:00Z",
            "related_docs": [
                "docs/files/summaries/src/mcp_tools/doc_guide.py.md",
                "docs/architecture/overview.md",
                "docs/project/README.md"
            ],
            "doc_sections": [
                "README.md:MCP接口层",
                "overview.md:7个专业工具"
            ]
        },
        "mcp_server.py": {
            "hash": "def456...",
            "size": 8900,
            "modified_time": "2025-09-15T14:20:00Z", 
            "related_docs": [
                "docs/files/summaries/mcp_server.py.md",
                "docs/architecture/overview.md",
                "docs/project/README.md"
            ],
            "doc_sections": [
                "README.md:MCP服务器部署",
                "README.md:热重载支持"
            ]
        }
    },
    "docs_files": {
        "docs/architecture/overview.md": {
            "hash": "ghi789...",
            "size": 12000,
            "modified_time": "2025-09-15T10:00:00Z"
        }
    },
    "mapping_rules": {
        "src/mcp_tools/*.py": "docs/files/summaries/src/mcp_tools/{filename}.md",
        "src/task_engine/*.py": "docs/files/summaries/src/task_engine/{filename}.md",
        "src/hot_reload/*.py": "docs/files/summaries/src/hot_reload/{filename}.md"
    }
}
```

### 2.3 doc_update_init工具

#### 核心功能
```python
class DocUpdateInitCore:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.fingerprint_file = self.project_path / ".codelens" / "doc_fingerprints.json"
        
    def initialize_fingerprints(self):
        """初始化文件指纹缓存"""
        fingerprints = {
            "created_at": datetime.now().isoformat(),
            "source_files": {},
            "docs_files": {}, 
            "mapping_rules": self._build_mapping_rules()
        }
        
        # 扫描源码文件
        for source_file in self._get_source_files():
            fingerprints["source_files"][str(source_file)] = {
                "hash": self._calculate_file_hash(source_file),
                "size": source_file.stat().st_size,
                "modified_time": datetime.fromtimestamp(source_file.stat().st_mtime).isoformat(),
                "related_docs": self._find_related_docs(source_file),
                "doc_sections": self._find_doc_sections(source_file)
            }
        
        # 扫描文档文件
        for doc_file in self._get_docs_files():
            fingerprints["docs_files"][str(doc_file)] = {
                "hash": self._calculate_file_hash(doc_file),
                "size": doc_file.stat().st_size, 
                "modified_time": datetime.fromtimestamp(doc_file.stat().st_mtime).isoformat()
            }
            
        self._save_fingerprints(fingerprints)
        return fingerprints

    def _build_mapping_rules(self):
        """构建源码文件到文档文件的映射规则"""
        return {
            # MCP工具映射
            "src/mcp_tools/*.py": "docs/files/summaries/src/mcp_tools/{filename}.md",
            # 任务引擎映射  
            "src/task_engine/*.py": "docs/files/summaries/src/task_engine/{filename}.md",
            # 热重载系统映射
            "src/hot_reload/*.py": "docs/files/summaries/src/hot_reload/{filename}.md", 
            # 服务层映射
            "src/services/*.py": "docs/files/summaries/src/services/{filename}.md",
            # 核心文件映射
            "mcp_server.py": "docs/files/summaries/mcp_server.py.md"
        }

    def _find_related_docs(self, source_file):
        """找到与源码文件相关的文档文件"""
        related = []
        
        # 1. 直接对应的文件文档
        file_doc = self._get_file_doc_path(source_file)
        if file_doc and file_doc.exists():
            related.append(str(file_doc))
        
        # 2. 架构文档（重要文件会影响架构文档）
        if self._is_important_file(source_file):
            related.extend([
                "docs/architecture/overview.md",
                "docs/architecture/tech-stack.md"
            ])
        
        # 3. README文档（MCP工具会影响README）
        if "mcp_tools" in str(source_file) or source_file.name == "mcp_server.py":
            related.append("docs/project/README.md")
            
        return related

    def _find_doc_sections(self, source_file):
        """找到源码文件在文档中对应的章节"""
        sections = []
        
        # 分析文件特征，确定会影响哪些文档章节
        if "mcp_tools" in str(source_file):
            sections.extend([
                "README.md:MCP接口层", 
                "README.md:7个专业MCP工具",
                "overview.md:MCP接口层"
            ])
        
        if source_file.name == "task_manager.py":
            sections.extend([
                "README.md:Task Engine智能任务管理",
                "overview.md:任务引擎层"
            ])
            
        return sections
```

### 2.4 doc_update工具

#### 核心功能
```python
class DocUpdateCore:
    def detect_and_update_changes(self):
        """检测文件变化并更新指纹基点"""
        # 第1步：检测变化
        current_fingerprints = self._scan_current_files()
        cached_fingerprints = self._load_cached_fingerprints()
        
        changes = {
            "modified_files": [],
            "new_files": [],
            "deleted_files": [],
            "affected_docs": set()
        }
        
        # 检测修改的文件
        for file_path, current_info in current_fingerprints.items():
            if file_path in cached_fingerprints:
                cached_info = cached_fingerprints[file_path]
                if current_info["hash"] != cached_info["hash"]:
                    changes["modified_files"].append({
                        "file": file_path,
                        "change_type": "modified",
                        "related_docs": cached_info.get("related_docs", []),
                        "doc_sections": cached_info.get("doc_sections", [])
                    })
                    # 收集受影响的文档
                    changes["affected_docs"].update(cached_info.get("related_docs", []))
            else:
                # 新文件
                changes["new_files"].append({
                    "file": file_path,
                    "change_type": "new", 
                    "suggested_docs": self._suggest_docs_for_new_file(file_path)
                })
        
        # 检测删除的文件
        for file_path in cached_fingerprints:
            if file_path not in current_fingerprints:
                changes["deleted_files"].append({
                    "file": file_path,
                    "change_type": "deleted",
                    "related_docs": cached_fingerprints[file_path].get("related_docs", [])
                })
        
        # 第2步：生成更新建议
        suggestions = self.generate_update_suggestions(changes)
        
        # 第3步：更新指纹基点（关键步骤）
        self._update_fingerprint_baseline(current_fingerprints)
        
        return {
            "changes": changes,
            "suggestions": suggestions,
            "baseline_updated": True,
            "message": "检测完成，指纹基点已更新为当前状态"
        }

    def _update_fingerprint_baseline(self, current_fingerprints):
        """更新指纹基点为当前文件状态"""
        # 重新扫描并建立完整的新指纹数据
        new_fingerprints = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "source_files": {},
            "docs_files": {},
            "mapping_rules": self._build_mapping_rules()
        }
        
        # 为所有当前文件建立新的指纹基点
        for source_file in self._get_source_files():
            new_fingerprints["source_files"][str(source_file)] = {
                "hash": self._calculate_file_hash(source_file),
                "size": source_file.stat().st_size,
                "modified_time": datetime.fromtimestamp(source_file.stat().st_mtime).isoformat(),
                "related_docs": self._find_related_docs(source_file),
                "doc_sections": self._find_doc_sections(source_file)
            }
        
        for doc_file in self._get_docs_files():
            new_fingerprints["docs_files"][str(doc_file)] = {
                "hash": self._calculate_file_hash(doc_file),
                "size": doc_file.stat().st_size,
                "modified_time": datetime.fromtimestamp(doc_file.stat().st_mtime).isoformat()
            }
        
        # 保存新的指纹基点
        self._save_fingerprints(new_fingerprints)
        
        self.logger.info(f"指纹基点已更新，下次update将基于当前状态进行对比")

    def generate_update_suggestions(self, changes):
        """生成更新建议"""
        suggestions = {
            "critical_updates": [],    # 必须更新的
            "recommended_updates": [], # 建议更新的
            "optional_updates": []     # 可选更新的
        }
        
        affected_docs = {}
        
        # 分析受影响的文档
        for doc_path in changes["affected_docs"]:
            if doc_path not in affected_docs:
                affected_docs[doc_path] = {
                    "priority": self._calculate_doc_priority(doc_path),
                    "reasons": [],
                    "suggested_actions": []
                }
            
        # 为每个受影响的文档生成具体建议
        for modified_file in changes["modified_files"]:
            file_path = modified_file["file"]
            
            # 文件级文档更新（最重要）
            for doc_path in modified_file["related_docs"]:
                if "docs/files/" in doc_path:
                    suggestions["critical_updates"].append({
                        "doc_path": doc_path,
                        "reason": f"源文件 {file_path} 已修改",
                        "action": "重新分析文件并更新文档内容",
                        "priority": "high"
                    })
                    
            # 架构文档更新
            if any("architecture" in doc for doc in modified_file["related_docs"]):
                suggestions["recommended_updates"].append({
                    "doc_path": "docs/architecture/overview.md",
                    "reason": f"核心文件 {file_path} 发生变化，可能影响架构描述", 
                    "action": "检查并更新相关架构描述",
                    "priority": "medium"
                })
            
            # README文档更新
            if "README.md" in str(modified_file["related_docs"]):
                for section in modified_file["doc_sections"]:
                    suggestions["recommended_updates"].append({
                        "doc_path": "docs/project/README.md",
                        "reason": f"文件 {file_path} 变化可能影响 {section}",
                        "action": f"检查并更新 {section} 章节",
                        "priority": "medium"
                    })
        
        return suggestions

    def _calculate_doc_priority(self, doc_path):
        """计算文档更新优先级"""
        if "docs/files/" in doc_path:
            return "high"    # 文件级文档最重要
        elif "README.md" in doc_path:
            return "medium"  # README文档中等重要
        elif "architecture" in doc_path:
            return "medium"  # 架构文档中等重要  
        else:
            return "low"     # 其他文档较低重要
```

### 2.5 使用流程

#### 第一次：初始化基点
```bash
# 1. 项目开发到一定阶段，建立文档更新检测的初始基点
python src/mcp_tools/doc_update_init.py /path/to/project

# 生成指纹基点文件：.codelens/doc_fingerprints.json
# 记录所有源码和文档文件的初始状态
```

#### 第二次：检测并更新基点
```bash  
# 2. 修改了源码后，检测需要更新的文档
python src/mcp_tools/doc_update.py /path/to/project

# 输出示例：
# 检测到变化：
# - src/mcp_tools/task_execute.py (已修改)
# - src/hot_reload/file_watcher.py (已修改) 
# - src/mcp_tools/new_tool.py (新文件)
#
# 需要更新的文档：
# 【必须更新】
# - docs/files/summaries/src/mcp_tools/task_execute.py.md (源文件已修改)
# - docs/files/summaries/src/hot_reload/file_watcher.py.md (源文件已修改)
# 
# 【建议更新】  
# - docs/project/README.md (MCP工具章节，新增工具new_tool.py)
# - docs/architecture/overview.md (热重载系统章节，file_watcher.py变化)
#
# ✅ 检测完成，指纹基点已更新为当前状态
```

#### 第三次及以后：持续检测
```bash
# 3. 再次修改源码后，基于新基点检测变化
python src/mcp_tools/doc_update.py /path/to/project

# 只会检测基于上次update后的新变化
# 不会重复提示上次已经检测过的变化
# 每次检测完都会更新指纹基点

# 工作流程：
# 第2次检测基点 → 第3次检测 → 第3次检测基点 → 第4次检测 → 第4次检测基点...
```

#### 工作原理说明
```
时间线示例：
─────────────────────────────────────────────────────────
T1: init          建立初始基点A
T2: 修改代码1      
T3: update        检测(基于基点A) → 建立新基点B  
T4: 修改代码2      
T5: update        检测(基于基点B) → 建立新基点C
T6: 修改代码3      
T7: update        检测(基于基点C) → 建立新基点D
...

每次update都是增量检测，基于上一次的状态对比
```

### 2.6 MCP工具配置

```python
# doc_update_init工具
def get_tool_definition(self):
    return {
        "name": "doc_update_init", 
        "description": "初始化文档更新检测系统，建立文件指纹缓存",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "项目根路径"},
                "force_rebuild": {
                    "type": "boolean", 
                    "description": "是否强制重建指纹缓存",
                    "default": false
                }
            },
            "required": ["project_path"]
        }
    }

# doc_update工具  
def get_tool_definition(self):
    return {
        "name": "doc_update",
        "description": "基于指纹对比的增量文档更新检测工具，检测完成后自动更新指纹基点",
        "inputSchema": {
            "type": "object", 
            "properties": {
                "project_path": {"type": "string", "description": "项目根路径"},
                "show_details": {
                    "type": "boolean",
                    "description": "是否显示详细的变化信息和文件列表",
                    "default": true
                },
                "priority_filter": {
                    "type": "array",
                    "items": {
                        "type": "string", 
                        "enum": ["critical", "recommended", "optional"]
                    },
                    "description": "只显示指定优先级的更新建议",
                    "default": ["critical", "recommended", "optional"]
                }
            },
            "required": ["project_path"]
        }
    }
```

## 3. 实现优先级

### 阶段1：快速验证 (1-2天)
- ✅ **project_overview工具** - 实现direct模式，直接读取文档内容
- ✅ **doc_update_init工具** - 基础的指纹缓存建立

### 阶段2：核心功能 (3-5天)  
- 🔄 **doc_update工具** - 变化检测和更新建议
- 🔄 **智能映射规则** - 完善源码文件到文档文件的映射关系
- 🔄 **files文档精确更新** - 重点优化files文档的更新检测准确性

### 阶段3：体验优化 (2-3天)
- 🔜 **project_overview提示词模式** - 实现prompt模式
- 🔜 **doc_update细节优化** - 更精确的章节级别更新建议  
- 🔜 **集成测试** - 与现有工具链的完整集成

## 4. 核心价值

### project_overview工具
- **通用性强**：适用于任何包含docs/architecture和docs/project结构的项目
- **简单高效**：一次调用让AI完整理解项目，无需复杂处理
- **灵活选择**：支持直接内容输出和AI提示词两种模式
- **零配置**：无需项目特定配置，开箱即用

### doc_update系统  
- **增量检测**：每次检测后更新指纹基点，避免重复提示已处理的变化
- **精确映射**：基于文件指纹和智能映射规则，准确识别代码变化
- **三级建议**：必须更新(files文档)、建议更新(架构/README)、可选更新
- **files文档重点优化**：一对一精确映射，确保源码文件对应的文档更新建议最准确
- **持续可用**：指纹基点滚动更新，支持长期持续的开发过程

### 工作流程优势
```
传统方式：修改代码 → 手动记忆需要更新的文档 → 容易遗漏

新方式：修改代码 → doc_update检测 → 精确的更新建议列表 → 指纹基点自动更新
```

### 解决的核心痛点
1. **"改了代码不知道更新啥文档"** ✅ - 精确告诉你需要更新什么，为什么要更新
2. **"不想重复看已经处理的变化"** ✅ - 指纹基点滚动更新，只显示新变化
3. **"files文档要做得准确"** ✅ - 一对一映射，源码变了直接告诉你对应文档
4. **"项目文档理解效率低"** ✅ - 一次调用理解完整项目架构和文档

这个V2.0方案真正做到了"简单直接、精确有效"，特别是doc_update的指纹基点滚动更新机制，完美解决了持续开发过程中的文档同步问题！