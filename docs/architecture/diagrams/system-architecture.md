
# CodeLens 系统架构图

## 整体架构

```mermaid
graph TD
    subgraph "客户端层"
        CC[Claude Code<br/>智能化文档生成客户端]
    end
    
    subgraph "MCP接口层 - 7个专业工具"
        IT[init_tools<br/>工作流指导]
        DG[doc_guide<br/>智能项目分析]
        TI[task_init<br/>任务计划生成]
        TE[task_execute<br/>任务执行管理]
        TS[task_status<br/>状态监控中心]
        TC[task_complete<br/>任务完成工具]
        DS[doc_scan<br/>项目文件扫描]
    end
    
    subgraph "任务引擎层 - Task Engine"
        TM[TaskManager<br/>14种任务管理]
        PC[PhaseController<br/>5阶段严格控制]
        ST[StateTracker<br/>状态跟踪监控]
        SA[智能调度算法<br/>依赖图+优先级]
    end
    
    subgraph "热重载系统层 - Hot Reload"
        HRM[HotReloadManager<br/>协调管理器]
        FW[FileWatcher<br/>文件监控]
        MR[ModuleReloader<br/>模块重载]
        DA[依赖分析<br/>防抖动机制]
    end
    
    subgraph "服务层 - Services"
        FS[FileService<br/>智能文件分析<br/>项目类型检测]
        TmS[TemplateService<br/>16个核心模板<br/>四层架构支持]
        VS[ValidationService<br/>完整性验证<br/>多种验证模式]
    end
    
    subgraph "基础设施层"
        FileSys[文件系统<br/>pathlib/glob<br/>智能过滤]
        Templates[模板资源<br/>Markdown<br/>16个模板]
        Storage[状态存储<br/>JSON持久化文件<br/>.codelens/tasks.json]
    end
    
    CC -->|MCP协议调用| IT
    CC -->|MCP协议调用| DG
    CC -->|MCP协议调用| TI
    CC -->|MCP协议调用| TE
    CC -->|MCP协议调用| TS
    CC -->|MCP协议调用| TC
    CC -->|MCP协议调用| DS
    
    IT --> TM
    DG --> TM
    TI --> TM
    TE --> TM
    TS --> TM
    TC --> TM
    DS --> TM
    
    TM --> PC
    TM --> ST
    TM --> SA
    
    PC --> HRM
    ST --> HRM
    SA --> HRM
    
    HRM --> FW
    HRM --> MR
    HRM --> DA
    
    FW --> FS
    MR --> TmS
    DA --> VS
    
    FS --> FileSys
    TmS --> Templates
    VS --> Storage
    
    style CC fill:#e3f2fd
    style TM fill:#fff3e0
    style HRM fill:#fce4ec
    style FS fill:#e8f5e8
```

## 详细组件架构

### MCP 接口层 (7个专业工具)

```mermaid
graph TB
    subgraph "MCP Tools Layer - 7个专业工具"
        subgraph "工作流管理工具"
            IT2[init_tools.py<br/>• 工作流指导<br/>• 5阶段操作步骤<br/>• 完整工作流程<br/>• 标准化指导]
            TC2[task_complete.py<br/>• 任务完成标记<br/>• 质量验证<br/>• 完成确认<br/>• 输出检查]
        end
        
        subgraph "项目分析工具"
            DG2[doc_guide.py<br/>• 智能项目分析<br/>• 项目类型检测<br/>• 框架识别<br/>• 文档策略生成]
            DS2[doc_scan.py<br/>• 项目文件扫描<br/>• 智能过滤<br/>• 元数据提取<br/>• 目录树生成]
        end
        
        subgraph "任务管理工具"
            TI2[task_init.py<br/>• 任务计划生成<br/>• 5阶段规划<br/>• 依赖图构建<br/>• 优先级排序]
            TE2[task_execute.py<br/>• 任务执行管理<br/>• 上下文构建<br/>• 模板集成<br/>• 3种执行模式]
            TS2[task_status.py<br/>• 状态监控<br/>• 进度跟踪<br/>• 健康诊断<br/>• 执行建议]
        end
    end
    
    style IT2 fill:#e1f5fe
    style DG2 fill:#e8f5e8
    style TI2 fill:#fff8e1
    style TE2 fill:#fce4ec
    style TS2 fill:#e0f2f1
    style TC2 fill:#f1f8e9
    style DS2 fill:#e8eaf6
```

### 任务引擎层架构

```mermaid
graph LR
    subgraph "Task Engine Layer"
        subgraph "核心管理器"
            TM3[TaskManager<br/>• 任务创建管理<br/>• 14种任务类型<br/>• 依赖关系验证<br/>• 状态持久化]
        end
        
        subgraph "控制器"
            PC3[PhaseController<br/>• 5阶段控制<br/>• 100%完成率<br/>• 阶段转换门控<br/>• 健康检查]
        end
        
        subgraph "跟踪器"
            ST3[StateTracker<br/>• 状态跟踪<br/>• 执行历史<br/>• 性能监控<br/>• 异常检测]
        end
        
        subgraph "调度算法"
            SA3[智能调度算法<br/>• DAG依赖图<br/>• 优先级算法<br/>• 智能调度<br/>• 并发安全]
        end
    end
    
    TM3 <--> PC3
    PC3 <--> ST3
    ST3 <--> SA3
    SA3 <--> TM3
    
    style TM3 fill:#fff3e0
    style PC3 fill:#e8f5e8
    style ST3 fill:#e0f2f1
    style SA3 fill:#f3e5f5
```

### 热重载系统层架构

```mermaid
graph TD
    subgraph "Hot Reload System Layer"
        subgraph "管理器"
            HRM3[HotReloadManager<br/>• 热重载协调<br/>• 工具实例管理<br/>• 回调管理<br/>• 生命周期控制]
        end
        
        subgraph "监控器"
            FW3[FileWatcher<br/>• 双模式监控<br/>• watchdog优先<br/>• 轮询备用<br/>• 防抖动处理]
        end
        
        subgraph "重载器"
            MR3[ModuleReloader<br/>• 智能重载<br/>• 依赖分析<br/>• 安全重载<br/>• 缓存清理]
        end
        
        subgraph "协调器"
            SC[系统协调<br/>• 事件调度<br/>• 状态同步<br/>• 降级处理<br/>• 性能优化]
        end
    end
    
    HRM3 --> FW3
    HRM3 --> MR3
    HRM3 --> SC
    FW3 --> MR3
    MR3 --> SC
    SC --> HRM3
    
    style HRM3 fill:#fce4ec
    style FW3 fill:#e8f5e8
    style MR3 fill:#fff3e0
    style SC fill:#e1f5fe
```

**14种支持任务类型**:
- **Phase 1**: SCAN (项目扫描)
- **Phase 2**: FILE_SUMMARY (文件摘要) 
- **Phase 3**: MODULE_ANALYSIS, MODULE_RELATIONS, DEPENDENCY_GRAPH, MODULE_README, MODULE_API, MODULE_FLOW
- **Phase 4**: ARCHITECTURE, TECH_STACK, DATA_FLOW, SYSTEM_ARCHITECTURE, COMPONENT_DIAGRAM, DEPLOYMENT_DIAGRAM
- **Phase 5**: PROJECT_README (项目README)

### 服务层架构

```mermaid
graph LR
    subgraph "Services Layer"
        subgraph "文件服务"
            FS3[FileService<br/>• 智能文件扫描<br/>• 项目类型检测<br/>• 框架识别<br/>• 元数据提取<br/>• 目录树构建]
        end
        
        subgraph "模板服务"
            TS3[TemplateService<br/>• 16个核心模板<br/>• 四层架构支持<br/>• 智能查询系统<br/>• 模板格式化<br/>• 变量管理]
        end
        
        subgraph "验证服务"
            VS3[ValidationService<br/>• 文档结构验证<br/>• 完整性检查<br/>• 改进建议<br/>• 多种验证模式<br/>• 状态报告]
        end
    end
    
    FS3 -.-> TS3
    TS3 -.-> VS3
    VS3 -.-> FS3
    
    style FS3 fill:#e8f5e8
    style TS3 fill:#fff8e1
    style VS3 fill:#e0f2f1
```

## 智能化协作数据流

```mermaid
graph TD
    A[Claude Code 请求] --> B[MCP 工具接收<br/>7个专业工具]
    B --> C[参数验证处理]
    C --> D[任务引擎调用]
    
    D --> TM4[TaskManager]
    D --> PC4[PhaseController]
    D --> ST4[StateTracker]
    
    TM4 --> E[服务层处理]
    PC4 --> E
    ST4 --> E
    
    E --> FS4[FileService]
    E --> TS4[TemplateService]
    E --> VS4[ValidationService]
    
    FS4 --> F[智能分析执行]
    TS4 --> F
    VS4 --> F
    
    F --> G1[项目分析]
    F --> G2[任务生成]
    F --> G3[状态跟踪]
    
    G1 --> H[结果格式化]
    G2 --> H
    G3 --> H
    
    H --> I[JSON结构化响应]
    I --> J[Claude Code 接收完整响应数据]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style J fill:#c8e6c9
```

## 5阶段文档生成流程

```mermaid
graph LR
    subgraph "Phase 1: 项目扫描"
        P1[1个SCAN任务<br/>项目结构分析<br/>文件过滤优化]
    end
    
    subgraph "Phase 2: 文件层文档"
        P2[1-50个FILE_SUMMARY任务<br/>详细文件分析<br/>代码结构文档]
    end
    
    subgraph "Phase 3: 模块层架构"
        P3[6-20个MODULE_*任务<br/>模块关系分析<br/>API设计文档]
    end
    
    subgraph "Phase 4: 架构层设计"
        P4[6个ARCHITECTURE任务<br/>系统架构设计<br/>技术栈文档]
    end
    
    subgraph "Phase 5: 项目层总结"
        P5[1个PROJECT_README任务<br/>项目综合文档<br/>使用指南]
    end
    
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    
    P5 --> CHECK[100%完成检查]
    CHECK --> VERIFY[最终文档验证]
    
    style P1 fill:#e1f5fe
    style P2 fill:#e8f5e8
    style P3 fill:#fff8e1
    style P4 fill:#fce4ec
    style P5 fill:#e0f2f1
    style CHECK fill:#fff3e0
    style VERIFY fill:#c8e6c9
```

## 技术栈架构

```mermaid
graph TB
    subgraph "Application Layer"
        APP[Python 3.9+ / MCP Protocol<br/>智能化任务驱动架构<br/>7个专业MCP工具]
    end
    
    subgraph "Framework Layer"
        FRAME[pathlib / glob / json / threading<br/>核心Python标准库<br/>零外部依赖设计]
    end
    
    subgraph "System Layer"  
        SYS[File System / OS Resources<br/>跨平台兼容支持<br/>智能权限管理]
    end
    
    APP --> FRAME
    FRAME --> SYS
    
    style APP fill:#e3f2fd
    style FRAME fill:#fff8e1
    style SYS fill:#e8f5e8
```

这是一个专为 Claude Code 协作设计的智能化任务驱动 MCP 服务器，采用五层分层架构，具有完整的任务引擎、热重载系统、智能项目分析和5阶段严格控制能力。
