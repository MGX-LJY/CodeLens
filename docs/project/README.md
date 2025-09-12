# CodeLens - 文档驱动的MCP服务器

## 项目概述

CodeLens 是一个基于MCP（Model Context Protocol）的文档驱动代码理解系统。通过AI生成的三层文档体系，为代码项目提供结构化的文档，避免直接读取大量源代码造成的上下文浪费。

## 核心特性

- **三层文档架构**：文件层 → 模块层 → 架构层，从具体到抽象的渐进分析
- **AI驱动生成**：使用AI理解代码并生成结构化文档  
- **模板化输出**：标准化的文档格式，便于AI理解和使用
- **当前状态分析**：将当前代码状态视为V1.0，无需了解项目历史

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt  # 暂未实现，当前为开发版本
```

### 2. 生成项目文档

```bash
python src/mcp_tools/doc_init.py /path/to/your/project
```

### 3. 查看生成的文档

文档将生成在项目的 `docs/` 目录下：
- `docs/architecture/` - 系统架构文档
- `docs/modules/` - 模块分析文档  
- `docs/files/` - 文件摘要文档

## 项目状态

**当前版本**: MVP v0.1.0

**已实现功能**:
- ✅ 文件扫描和读取服务
- ✅ 模板化文档生成系统
- ✅ Mock AI 服务（用于测试）
- ✅ 三层文档生成流程
- ✅ MCP doc_init 工具
- ✅ 基础错误处理

**正在开发**:
- 🔄 真实AI服务集成
- 🔄 更好的项目过滤规则
- 🔄 多语言支持

## 技术架构

### 核心组件
- **FileService**: 项目文件扫描和读取
- **TemplateService**: 文档模板管理
- **AIService**: AI内容生成服务
- **ThreeLayerDocGenerator**: 三层文档生成器
- **DocInitTool**: MCP工具接口

### 生成流程
1. **文件层**: 逐个分析源代码文件，生成功能摘要
2. **模块层**: 基于文件摘要识别功能模块和依赖关系
3. **架构层**: 基于模块分析生成系统整体架构文档

## 使用示例

生成的文档结构示例：

```
docs/
├── architecture/
│   ├── overview.md              # 系统架构概述
│   ├── tech-stack.md           # 技术栈分析
│   └── data-flow.md            # 数据流设计
├── modules/
│   ├── overview.md             # 模块总览
│   └── module-relations.md     # 模块关系图
└── files/
    └── summaries/              # 文件摘要
        └── src/
            ├── main.py.md
            └── utils.py.md
```

## 开发路线图

### Phase 1: MVP完善 (当前)
- 改进文件过滤机制
- 集成真实AI服务
- 测试更多项目类型

### Phase 2: 功能扩展
- 支持TypeScript/JavaScript项目
- 增加配置文件支持
- 实现增量更新

### Phase 3: 产品化
- Web界面
- API服务
- 插件系统

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交改动
4. 发起Pull Request

## 许可证

[MIT License](LICENSE)