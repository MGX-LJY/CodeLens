# CodeLens 数据流设计

## 智能化协作工作流

### Claude Code 与 CodeLens 协作流程
CodeLens通过7个MCP工具与Claude Code协作，提供完整的文档生成支持：

## MCP工具协作流程

### 阶段1: 项目分析 (doc_guide)
```
Claude Code → doc_guide → ProjectAnalyzer
     ↓
项目路径 → 智能扫描 → 项目类型检测 → 框架识别
     ↓
分析结果 + 文档策略 + 生成计划 → JSON响应 → Claude Code
```

### 阶段2: 任务规划 (task_init)
```
Claude Code → task_init → TaskPlanGenerator
     ↓
分析数据 → 任务生成 → 依赖图构建 → 优先级排序
     ↓
23+任务计划 + 执行策略 → JSON响应 → Claude Code
```

### 阶段3: 任务执行 (task_execute)
```
Claude Code → task_execute → TaskExecutor
     ↓
任务ID → 上下文构建 → 模板获取 → 执行管理
     ↓
执行结果 + 状态更新 → JSON响应 → Claude Code
```

### 阶段4: 进度监控 (task_status)
```
Claude Code → task_status → StateTracker
     ↓
状态查询 → 进度分析 → 健康检查 → 建议生成
     ↓
状态报告 + 执行建议 → JSON响应 → Claude Code
```

### 阶段5: 数据支持服务

#### 5.1 智能文件扫描 (doc_scan)
```
Claude Code → doc_scan → FileService
     ↓
项目路径 → 智能过滤 → 元数据提取 → 目录树生成
     ↓
结构化数据 → JSON响应 → Claude Code
```

#### 5.2 模板获取 (template_get)
```
Claude Code → template_get → TemplateService
     ↓
模板查询 → 层级定位 → 模板加载
     ↓ 
架构层/模块层/文件层/项目层模板
     ↓
模板内容 + 元数据 → JSON响应 → Claude Code
```

#### 5.3 文档验证 (doc_verify)
```
Claude Code → doc_verify → ValidationService
     ↓
目录检查 → 文件存在性验证 → 状态分析
     ↓
验证报告 → JSON响应 → Claude Code
```

## 5阶段文档生成工作流

### Phase 1: 项目扫描分析 (phase_1_scan)
```
任务类型: SCAN (1个任务)
TaskManager → 项目扫描任务 → FileService → 项目结构分析
     ↓
项目信息 → 文件列表 → 统计数据 → 任务状态更新(COMPLETED)
```

### Phase 2: 文件层文档生成 (phase_2_files)  
```
任务类型: FILE_SUMMARY (1-50个任务)
TaskManager → 文件任务调度 → 依赖验证(Phase 1) → 优先级排序
     ↓
高优先级文件(main.py, app.py等) → 模板匹配 → 文档生成
     ↓
普通/低优先级文件 → 批量处理 → 状态跟踪 → 100%完成检查
```

### Phase 3: 模块层架构分析 (phase_3_modules)
```
任务类型: MODULE_* (6-20个任务)  
依赖检查(Phase 2 100%完成) → 模块任务生成
     ↓
MODULE_ANALYSIS → MODULE_RELATIONS → DEPENDENCY_GRAPH
     ↓
重要模块详细任务: MODULE_README + MODULE_API + MODULE_FLOW
     ↓
模块关系构建 → 架构设计基础 → 阶段完成验证
```

### Phase 4: 架构层文档生成 (phase_4_architecture)
```
任务类型: ARCHITECTURE/TECH_STACK/DATA_FLOW + 图表任务 (6个任务)
依赖检查(Phase 3 100%完成) → 架构任务并发执行
     ↓
系统架构设计 + 技术栈分析 + 数据流设计
     ↓
架构图表生成: SYSTEM_ARCHITECTURE + COMPONENT_DIAGRAM + DEPLOYMENT_DIAGRAM  
     ↓
架构文档完整性验证 → 项目技术全貌构建
```

### Phase 5: 项目层总结文档 (phase_5_project)
```
任务类型: PROJECT_README (1个任务)
依赖检查(Phase 4 100%完成) → 项目总结任务
     ↓
整合所有阶段成果 → 项目README生成 → 文档完整性验证
     ↓
项目文档生成完成 → 全流程状态更新(COMPLETED)
```

## 详细数据流程

### 任务引擎流程

#### TaskManager流程
1. **输入**: 任务定义、依赖关系、优先级
2. **处理**: 任务创建 → 状态跟踪 → 调度管理
3. **输出**: 任务状态、执行队列、进度报告

#### PhaseController流程
1. **输入**: 阶段定义、完成条件
2. **处理**: 阶段验证 → 依赖检查 → 进度门控
3. **输出**: 阶段状态、转换权限、执行建议

#### StateTracker流程
1. **输入**: 状态变更、事件记录
2. **处理**: 状态持久化 → 历史追踪 → 性能监控
3. **输出**: 状态快照、执行历史、健康报告

### 核心服务流程

#### 智能文件服务流程
1. **输入**: 项目路径、过滤配置
2. **处理**: 智能扫描 → 项目类型检测 → 元数据提取
3. **输出**: 过滤后文件列表、项目信息、统计数据

#### 模板服务流程
1. **输入**: 模板名称、查询类型
2. **处理**: 模板查找 → 内容加载 → 格式化
3. **输出**: 模板内容、元数据、变量列表

#### 验证服务流程
1. **输入**: 项目路径、验证类型
2. **处理**: 目录检查 → 状态分析 → 建议生成
3. **输出**: 验证状态、完成度报告

## 数据格式规范
- **输入格式**: JSON参数配置
- **输出格式**: JSON结构化响应
- **模板格式**: Markdown模板文件
- **状态存储**: JSON持久化文件
- **元数据**: 文件信息、模板属性、验证状态、任务状态

## 性能考量

### 智能化优化
- **智能文件过滤**: 项目类型感知，大幅减少无关文件处理
- **依赖图优化**: 智能任务调度，避免重复执行
- **阶段控制**: 严格阶段依赖，确保执行效率

### 系统性能
- **高效扫描**: pathlib + glob优化文件处理
- **按需加载**: 模板和数据按需获取  
- **状态持久化**: 支持中断恢复，提升长时间任务执行稳定性
- **并发安全**: 无状态设计，支持多任务并发执行

### 监控与优化
- **实时监控**: 毫秒级状态检查响应
- **性能指标**: 详细的执行时间和资源使用统计
- **健康检查**: 自动检测系统健康状态和执行异常