# CodeLens 重构思路文档

## 需求变更分析

### 当前架构（需要重构）
```
CodeLens = AI驱动的文档生成器
├── FileService (文件扫描读取)
├── TemplateService (模板管理)  
├── AIService (AI内容生成) ❌ 需删除
├── ThreeLayerDocGenerator (三层生成器) ❌ 需删除
└── DocInitTool (完整文档生成) ❌ 需重构
```

### 新需求架构（Claude Code协作）
```
CodeLens = Claude Code的MCP助手服务器
├── FileService (文件信息提供)
├── TemplateService (模板资源提供)
├── ValidationService (文档验证) ✅ 新增
└── MCP Tools (信息提供+验证) ✅ 重构
    ├── doc_scan (扫描项目文件信息)
    ├── template_get (获取文档模板)
    └── doc_verify (验证文档生成状态)
```

## 核心理念转变

### 原理念：自主生成
- **角色**：AI文档生成器
- **职责**：完整的文档生成流程
- **输出**：直接生成最终文档

### 新理念：协作助手  
- **角色**：Claude Code的信息提供者
- **职责**：提供文件信息、模板资源、验证状态
- **输出**：结构化数据供Claude Code使用

## 新架构详细设计

### 1. FileService (文件信息服务)
**功能调整**：
- 保留：`scan_source_files()` - 扫描项目文件
- 保留：`read_file_safe()` - 读取文件内容  
- 保留：`get_project_info()` - 项目基础信息
- 新增：`get_file_metadata()` - 获取文件元数据（大小、修改时间等）
- 新增：`get_directory_tree()` - 获取目录树结构

**返回格式**：
```json
{
  "project_info": {...},
  "files": [
    {
      "path": "src/main.py",
      "content": "...",
      "metadata": {...}
    }
  ],
  "directory_tree": {...}
}
```

### 2. TemplateService (模板资源服务)
**功能调整**：
- 保留：所有文档模板定义
- 删除：AI提示词构建（不再需要）
- 新增：`get_template_list()` - 获取可用模板列表
- 新增：`get_template_content()` - 按需获取具体模板

**模板类型**：
```json
{
  "templates": {
    "file_summary": "文件摘要模板",
    "module_overview": "模块概览模板", 
    "architecture_overview": "架构概览模板",
    "project_readme": "项目README模板"
  }
}
```

### 3. ValidationService (新增 - 文档验证服务)
**核心功能**：
```python
class ValidationService:
    def check_file_exists(self, file_path: str) -> bool
    def check_directory_structure(self, base_path: str) -> dict
    def get_missing_files(self, expected_files: list) -> list
    def get_generation_status(self, project_path: str) -> dict
```

**验证范围**：
- 检查docs/目录结构是否存在
- 检查各层级文档文件是否已生成
- 统计生成进度（已生成/总需生成）
- **不读取内容**：只检查文件存在性

### 4. MCP工具重构

#### A. doc_scan (替代原doc_init)
**功能**：扫描项目并返回文件信息
```json
{
  "name": "doc_scan",
  "description": "扫描项目文件并返回结构化信息供Claude Code使用",
  "parameters": {
    "project_path": "string",
    "include_content": "boolean"
  }
}
```

#### B. template_get (新增)
**功能**：获取指定类型的文档模板
```json
{
  "name": "template_get", 
  "description": "获取指定类型的文档模板",
  "parameters": {
    "template_type": "string",
    "format": "string"
  }
}
```

#### C. doc_verify (新增)
**功能**：验证文档生成状态
```json
{
  "name": "doc_verify",
  "description": "检查项目文档生成状态", 
  "parameters": {
    "project_path": "string",
    "expected_structure": "object"
  }
}
```

## 工作流程对比

### 原流程（AI自主生成）
1. MCP调用 doc_init
2. 扫描文件 → AI分析 → 生成文档
3. 返回"文档已生成"

### 新流程（Claude Code协作）
1. Claude Code调用 doc_scan → 获取项目文件信息
2. Claude Code调用 template_get → 获取文档模板  
3. **Claude Code自己分析文件并生成文档**
4. Claude Code调用 doc_verify → 验证生成状态

## 需要删除的组件

### 1. AIService相关
- `src/services/ai_service.py`
- `MockAIService`类
- `create_ai_service()`工厂函数
- 所有AI调用相关代码

### 2. 文档生成器相关  
- `src/doc_generator.py`
- `ThreeLayerDocGenerator`类
- `generate_project_docs()`方法
- 三层生成流程代码

### 3. AI提示词相关
- `TemplateService`中的提示词构建方法
- `build_*_prompt()`系列方法

## 保留并增强的组件

### 1. FileService
- 增强文件元数据获取
- 添加目录树生成
- 优化文件扫描性能

### 2. TemplateService  
- 保留所有文档模板
- 增加模板查询接口
- 支持动态模板获取

### 3. MCP工具框架
- 保留MCP协议适配
- 重构工具定义
- 增加新的MCP工具

## 优势分析

### 1. 职责更清晰
- CodeLens专注于**信息提供**
- Claude Code专注于**内容生成**
- 各自发挥专长

### 2. 更灵活的生成
- Claude Code可以根据具体需求调整生成策略
- 不受固定三层模式限制
- 支持增量和定制化生成

### 3. 更好的集成
- 标准MCP协议，易于集成
- 减少依赖，提高稳定性
- 便于测试和维护

## 实施计划

### Phase 1: 核心重构
1. 删除AIService和文档生成器
2. 增强FileService和TemplateService
3. 实现ValidationService

### Phase 2: MCP工具重构
1. 重构doc_init为doc_scan
2. 实现template_get工具
3. 实现doc_verify工具

### Phase 3: 测试验证
1. 与Claude Code集成测试
2. 验证各MCP工具功能
3. 性能优化

---

**关键确认点**：
1. 是否删除所有AI相关功能？
2. MCP工具分拆为三个是否合适？
3. ValidationService只检查文件存在性是否满足需求？
4. 还需要其他信息提供功能吗？