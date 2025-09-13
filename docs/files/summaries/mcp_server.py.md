# 文件摘要：mcp_server.py

## 功能概述

CodeLens v0.6.1.5 MCP协议服务器的核心实现，为Claude Code提供智能任务引擎驱动的5阶段文档生成系统。该服务器集成16个核心模板和完整的任务管理流程，统一管理6个MCP工具，实现了标准的JSON-RPC通信协议，专为AI协作和任务自动化优化设计。

## 主要组件

### 类定义
- **CodeLensMCPServer**: MCP服务器主类，实现完整的MCP协议支持

### 函数定义
- `get_server_info()`: 获取服务器元信息
- `list_tools()`: 列出所有可用的MCP工具
- `execute_tool()`: 执行指定的MCP工具
- `handle_request()`: 处理MCP JSON-RPC请求
- `main()`: 服务器主入口，支持多种运行模式

### 重要常量和配置
- 服务器版本: v0.6.1.5 (智能任务引擎5阶段文档生成系统)
- 支持的MCP方法: initialize, tools/list, tools/call
- 集成的工具: doc_scan, template_get, doc_guide, task_init, task_execute, task_status (6个MCP工具)
- 模板系统: 16个核心模板，四层文档架构
- 模板分布: 架构层(6个) + 模块层(6个) + 文件层(1个) + 项目层(3个)
- 任务引擎: 5个执行阶段，15种任务类型，支持依赖管理和状态跟踪

## 依赖关系

### 导入的模块
- `sys, json, time, traceback`: 基础系统、时间处理和错误处理
- `typing`: 类型注解支持
- `src.mcp_tools.*`: 6个MCP工具模块 (doc_scan, template_get, doc_guide, task_init, task_execute, task_status)
- `src.logging`: 日志系统 (含DummyLogger备用实现)

### 对外接口
- **MCP协议接口**: 标准JSON-RPC over stdin/stdout
- **测试接口**: 命令行测试模式
- **信息查询**: 服务器信息和工具列表

## 关键算法和逻辑

### MCP协议实现
- **请求路由**: 根据method字段路由到对应处理器
- **工具管理**: 统一管理和调用所有MCP工具
- **错误处理**: 完整的异常捕获和JSON格式错误响应
- **状态管理**: 无状态设计，每次请求独立处理

### 通信协议
- **输入**: JSON-RPC请求 via stdin
- **输出**: JSON响应 via stdout
- **格式**: 标准MCP协议格式

### 运行模式
- **MCP模式**: 标准协议模式，用于Claude Code集成
- **测试模式**: `python mcp_server.py test /path` 智能任务引擎5阶段系统功能验证
  - 📊 16个核心模板系统展示
  - 🎯 四层架构模板分布统计 (6+6+1+3)
  - 🚀 智能任务引擎系统测试 (5阶段，15任务类型)
  - 🔍 项目分析和任务计划生成
  - 📈 任务状态监控和进度跟踪
  - ✅ 完整6工具链功能验证
- **信息模式**: `python mcp_server.py info` 查看详细服务器信息

## 实际性能表现

### CodeLens项目自测结果
- **扫描性能**: 22个文件，<0.05秒完成
- **模板加载**: 16个核心模板，<0.02秒加载
- **四层架构**: architecture(6) + module(6) + file(1) + project(3)
- **任务引擎**: 5阶段任务执行，15种任务类型支持
- **依赖管理**: 智能任务依赖解析和状态跟踪
- **内存使用**: 轻量级，无状态设计
- **响应时间**: 毫秒级响应
- **稳定性**: 完整错误处理，生产就绪

### 集成测试覆盖
- ✅ 所有6个MCP工具正常工作 (doc_scan, template_get, doc_guide, task_init, task_execute, task_status)
- ✅ JSON-RPC协议完整实现
- ✅ 错误处理和异常恢复
- ✅ 智能任务引擎5阶段执行验证
- ✅ 任务依赖管理和状态跟踪测试
- ✅ Claude Code配置模板验证

## 备注

mcp_server.py是CodeLens v0.6.1.5的核心组件，已演进为智能任务引擎驱动的5阶段文档生成系统。从早期版本的静态模板系统发展为集成16个核心模板和完整任务管理流程的动态系统。通过6个专业MCP工具和标准化的JSON-RPC协议实现，为Claude Code提供了智能化的项目分析、任务规划和文档生成体验，真正实现了"智能协作助手"与"内容生成者"的深度集成。