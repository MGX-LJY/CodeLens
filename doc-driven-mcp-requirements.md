# 文档驱动MCP服务器需求文档

## 1. 项目概述

### 1.1 项目背景
开发一个基于MCP（Model Context Protocol）的服务器，通过多层次文档体系驱动AI进行代码修改和项目管理，避免直接读取大量源代码造成的上下文浪费和理解偏差。

### 1.2 核心理念
- **文档即接口**：AI通过文档理解项目，而非直接读取代码/除了细节实现的时候
- **分层管理**：从宏观到微观的五层文档体系
- **版本追踪**：完整记录项目演进历史
- **智能化修改**：基于文档理解进行精准代码修改

## 2. 系统架构

### 2.1 运行模式
- **Init模式**：初始化文档体系，扫描项目生成各层文档
- **Update模式**：监听代码变更，自动更新相关文档
- **Query模式**：响应AI查询，提供文档内容
- **Modify模式**：接收AI指令，执行代码修改

### 2.2 四层文档体系

#### 第一层：架构文档（Architecture Layer）
```
/docs/architecture/
├── overview.md              # 整体架构概述
├── tech-stack.md           # 技术栈说明
├── data-flow.md            # 数据流设计
└── diagrams/               # 架构图
    ├── system-architecture.md
    ├── component-diagram.md
    └── deployment-diagram.md
```

**包含内容**：
- 系统整体架构设计
- 核心设计模式和原则
- 技术选型
- 系统边界和约束
- 部署架构

#### 第二层：模块文档（Module Layer）
```
/docs/modules/
├── overview.md              # 模块总览
├── module-relations.md      # 模块关系图谱
├── modules/                 # 具体模块文档
│   ├── auth/
│   │   ├── README.md       # 认证模块说明
│   │   ├── api.md          # 接口定义
│   │   └── flow.md         # 流程图
│   └── database/
│       ├── README.md       # 数据库模块说明
│       ├── schema.md       # 数据结构
│       └── queries.md      # 查询逻辑
└── connections/            # 模块间连接文档
    ├── auth-database.md    # 认证与数据库连接
    └── api-services.md     # API与服务连接
```

**包含内容**：
- 模块功能定义和职责
- 模块接口规范
- 模块间依赖关系
- 模块内部流程
- 关键函数和类的说明

#### 第三层：文件文档（File Layer）
```
/docs/files/
├── summaries/              # 文件摘要
│   ├── src/
│   │   ├── main.py.md     # main.py的摘要
│   │   └── utils.py.md    # utils.py的摘要
│   └── tests/
│       └── test_main.py.md
```

**包含内容**：
- 文件功能概述
- 主要类和函数列表
- 关键算法说明
- 依赖和被依赖关系
- 重要常量和配置

#### 第四层：项目文档（Project Layer）
```
/docs/project/
├── README.md               # 项目说明
├── CHANGELOG.md            # 版本更新日志
├── versions/               # 版本记录
│   ├── v1.0.0.md
│   ├── v1.1.0.md
│   └── current.md          # 当前版本
├── roadmap.md              # 开发路线图
└── decisions/              # 技术决策记录
    ├── ADR-001.md          # 架构决策记录
    └── ADR-002.md
```

**版本管理规则**：
- 主版本号（x.0.0）：重大架构变更
- 次版本号（0.x.0）：新功能添加
- 修订号（0.0.x）：Bug修复和小改进

**包含内容**：
- 业务背景和目标
- 用户故事和场景
- 领域术语定义
- 编码和文档规范
- AI交互最佳实践

## 3. 核心功能需求

### 3.1 文档生成功能
- **自动扫描**：扫描项目代码，自动生成初始文档
- **智能解析**：识别代码结构、依赖关系、设计模式
- **格式标准化**：统一文档格式，便于AI理解

### 3.2 文档查询功能
- **多维度查询**：支持按层级、模块、文件等维度查询
- **关联查询**：自动返回相关联的文档
- **智能推荐**：根据查询内容推荐相关文档
- **上下文构建**：为AI构建最小必要上下文

### 3.3 代码修改功能
- **修改计划生成**：基于需求生成修改计划
- **影响分析**：评估修改对其他模块的影响
- **自动化执行**：执行代码修改并更新文档
- **回滚机制**：支持修改回滚

### 3.4 版本管理功能
- **自动版本号管理**：根据修改类型自动更新版本
- **变更日志生成**：自动生成CHANGELOG
- **版本对比**：支持不同版本间的差异对比
- **版本回退**：支持回退到指定版本

### 3.5 AI修改流程管理
- **修改意见模板化**：标准化的修改意见文档格式
- **三段式流程**：待执行→已批准→已完成
- **影响评估**：自动分析修改的影响范围
- **审批机制**：支持人工审批或自动审批规则
- **执行追踪**：记录从提议到执行的完整过程
- **历史查询**：可查询所有历史修改意见和执行结果

## 4. MCP工具定义

### 4.1 初始化工具
```typescript
{
  name: "doc_init",
  description: "初始化项目文档体系",
  parameters: {
    project_path: string,
    doc_path: string,
    config?: {
      exclude_patterns?: string[],
      include_tests?: boolean,
      language?: string
    }
  }
}
```

### 4.2 查询工具
```typescript
{
  name: "doc_query",
  description: "查询项目文档",
  parameters: {
    query_type: "architecture" | "module" | "file" | "project" | "context",
    query: string,
    include_related?: boolean,
    max_depth?: number
  }
}
```

### 4.3 更新工具
```typescript
{
  name: "doc_update",
  description: "更新文档内容",
  parameters: {
    doc_path: string,
    changes: {
      type: "add" | "modify" | "delete",
      content: string,
      position?: number
    }[],
    trigger_code_update?: boolean
  }
}
```

### 4.4 代码修改工具
```typescript
{
  name: "code_modify",
  description: "基于文档理解修改代码",
  parameters: {
    modification_plan: {
      target_files: string[],
      changes: ChangeSet[],
      test_requirements?: string[]
    },
    dry_run?: boolean,
    auto_commit?: boolean
  }
}
```

## 5. 技术实现要求

### 5.1 技术栈建议
- **开发语言**：Python 3.9+ 或 TypeScript
- **MCP框架**：基于Anthropic MCP SDK
- **文档解析**：AST解析器（Python: ast, TypeScript: ts-morph）
- **文档格式**：Markdown + JSON
- **版本控制**：Git集成
- **配置管理**：YAML/JSON配置文件

### 5.2 性能要求
- 初始化扫描：< 30秒（中型项目）
- 文档查询响应：< 100ms
- 增量更新：< 5秒
- 内存占用：< 500MB

### 5.3 扩展性要求
- 支持多语言（Python, JavaScript, TypeScript, Java）
- 插件化架构，支持自定义文档生成器
- 支持自定义文档模板
- 支持与其他开发工具集成

## 6. 实施计划

### Phase 1: MVP版本（2周）
- 实现基础文档生成（架构、模块、文件三层）
- 实现简单查询功能
- 支持Python项目

### Phase 2: 核心功能（3周）
- 完善五层文档体系
- 实现智能查询和关联推荐
- 添加代码修改功能
- 集成版本管理

### Phase 3: 优化增强（2周）
- 性能优化
- 多语言支持
- 插件系统
- 文档可视化

### Phase 4: 生产就绪（1周）
- 完善错误处理
- 添加日志系统
- 编写用户文档
- 发布第一个稳定版本

## 7. 成功指标

- **文档覆盖率**：> 95%的代码有对应文档
- **AI理解准确率**：> 90%的修改请求能正确理解
- **修改成功率**：> 85%的代码修改无需人工干预
- **性能达标率**：100%满足性能要求
- **用户满意度**：> 4.5/5.0

## 8. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 文档与代码不同步 | 高 | 实时监听文件变更，自动触发更新 |
| AI理解偏差 | 中 | 提供详细的上下文和示例，持续优化提示词 |
| 性能瓶颈 | 中 | 采用增量更新，缓存常用查询 |
| 多语言支持复杂 | 低 | 先专注Python，逐步扩展 |

## 9. 附录

### 9.1 文档模板示例
（略，可根据需要补充）

### 9.2 配置文件示例
```yaml
# mcp-doc-config.yaml
project:
  name: "MyProject"
  version: "1.0.0"
  language: "python"
  
documentation:
  output_dir: "./docs"
  update_mode: "incremental"
  
  layers:
    architecture:
      enabled: true
      auto_generate_diagrams: true
    
    modules:
      enabled: true
      min_complexity: 5
    
    files:
      enabled: true
      exclude_patterns:
        - "**/__pycache__/**"
        - "**/node_modules/**"
        - "**/.git/**"
    
    project:
      enabled: true
      changelog_format: "keepachangelog"
    
    context:
      enabled: true
      include_business_docs: true

mcp:
  server_name: "doc-driven-mcp"
  port: 8080
  max_context_size: 100000
```

---

*文档版本：1.0.0*  
*最后更新：2025-01-12*