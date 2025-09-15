# CodeLens 数据流设计

## 整体协作流程图

### Claude Code 与 CodeLens 5阶段协作流程

```mermaid
graph TD
    A[Claude Code 启动文档生成] --> B[init_tools: 获取工作流指导]
    B --> C[doc_guide: 智能项目分析]
    C --> D[task_init: 生成5阶段任务计划]
    D --> E[task_status: 检查当前任务状态]
    
    E --> F{是否有待执行任务?}
    F -->|是| G[task_execute: 执行当前任务]
    F -->|否| H[所有任务已完成]
    
    G --> I[task_complete: 标记任务完成]
    I --> J[task_status: 检查下一个任务]
    J --> F
    
    H --> K[文档生成完成]
    
    style A fill:#e1f5fe
    style K fill:#c8e6c9
    style F fill:#fff3e0
```

## MCP工具数据流程图

### 7个核心MCP工具协作流程

```mermaid
graph LR
    subgraph "Claude Code 客户端"
        CC[Claude Code]
    end
    
    subgraph "CodeLens MCP服务器"
        subgraph "MCP工具层"
            IT[init_tools<br/>工作流指导]
            DG[doc_guide<br/>项目分析]
            TI[task_init<br/>任务计划]
            TE[task_execute<br/>任务执行]
            TS[task_status<br/>状态监控]
            TC[task_complete<br/>任务完成]
            DS[doc_scan<br/>文件扫描]
        end
        
        subgraph "引擎和服务层"
            TM[TaskManager<br/>任务管理]
            PC[PhaseController<br/>阶段控制]
            ST[StateTracker<br/>状态跟踪]
            FS[FileService<br/>文件服务]
            TS2[TemplateService<br/>模板服务]
            HR[HotReloadManager<br/>热重载]
        end
    end
    
    CC --> IT
    CC --> DG
    CC --> TI
    CC --> TE
    CC --> TS
    CC --> TC
    CC --> DS
    
    DG --> FS
    TI --> TM
    TE --> TM
    TE --> TS2
    TS --> ST
    TC --> TM
    DS --> FS
    
    TM --> PC
    PC --> ST
    
    style CC fill:#e3f2fd
    style IT fill:#f3e5f5
    style DG fill:#e8f5e8
    style TI fill:#fff8e1
    style TE fill:#fce4ec
    style TS fill:#e0f2f1
    style TC fill:#f1f8e9
    style DS fill:#e8eaf6
```

## 5阶段文档生成工作流

### 完整任务执行流程图

```mermaid
graph TD
    subgraph "Phase 1: 项目分析"
        P1A[SCAN任务启动] --> P1B[项目结构扫描]
        P1B --> P1C[项目类型检测]
        P1C --> P1D[框架识别]
        P1D --> P1E[生成分析报告]
        P1E --> P1F[Phase 1 完成]
    end
    
    subgraph "Phase 2: 任务计划"
        P2A[基于分析结果] --> P2B[生成5阶段任务]
        P2B --> P2C[构建依赖关系图]
        P2C --> P2D[设置任务优先级]
        P2D --> P2E[创建执行计划]
        P2E --> P2F[Phase 2 完成]
    end
    
    subgraph "Phase 3: 文件层文档"
        P3A[FILE_SUMMARY任务] --> P3B[高优先级文件]
        P3A --> P3C[普通文件]
        P3A --> P3D[低优先级文件]
        P3B --> P3E[生成文件文档]
        P3C --> P3E
        P3D --> P3E
        P3E --> P3F{所有文件完成?}
        P3F -->|否| P3A
        P3F -->|是| P3G[Phase 3 完成]
    end
    
    subgraph "Phase 4: 架构层文档"
        P4A[ARCHITECTURE任务] --> P4B[系统架构分析]
        P4B --> P4C[技术栈文档]
        P4C --> P4D[数据流设计]
        P4D --> P4E[组件关系图]
        P4E --> P4F[部署架构图]
        P4F --> P4G[Phase 4 完成]
    end
    
    subgraph "Phase 5: 项目层文档"
        P5A[PROJECT_README任务] --> P5B[整合所有成果]
        P5B --> P5C[生成项目文档]
        P5C --> P5D[更新变更日志]
        P5D --> P5E[制定路线图]
        P5E --> P5F[Phase 5 完成]
    end
    
    P1F --> P2A
    P2F --> P3A
    P3G --> P4A
    P4G --> P5A
    P5F --> END[文档生成完成]
    
    style P1F fill:#c8e6c9
    style P2F fill:#c8e6c9
    style P3G fill:#c8e6c9
    style P4G fill:#c8e6c9
    style P5F fill:#c8e6c9
    style END fill:#4caf50,color:#fff
```

## 任务引擎内部流程图

### TaskManager + PhaseController + StateTracker 协作

```mermaid
graph TB
    subgraph "任务创建和调度"
        A[任务请求] --> B[TaskManager.create_task]
        B --> C[验证任务参数]
        C --> D[检查依赖关系]
        D --> E[分配任务ID]
        E --> F[设置任务优先级]
        F --> G[加入任务队列]
    end
    
    subgraph "阶段控制"
        G --> H[PhaseController.check_phase]
        H --> I{当前阶段允许执行?}
        I -->|否| J[阻塞任务]
        I -->|是| K[允许执行]
        J --> L[等待阶段条件]
        L --> H
    end
    
    subgraph "任务执行"
        K --> M[TaskManager.execute_task]
        M --> N[更新任务状态为IN_PROGRESS]
        N --> O[StateTracker记录开始时间]
        O --> P[执行具体任务逻辑]
        P --> Q{执行成功?}
        Q -->|是| R[标记COMPLETED]
        Q -->|否| S[标记FAILED]
    end
    
    subgraph "状态跟踪和持久化"
        R --> T[StateTracker记录完成]
        S --> U[StateTracker记录失败]
        T --> V[更新执行历史]
        U --> V
        V --> W[持久化到tasks.json]
        W --> X[性能指标统计]
        X --> Y[健康检查更新]
    end
    
    subgraph "阶段转换检查"
        Y --> Z[PhaseController.check_phase_completion]
        Z --> AA{当前阶段100%完成?}
        AA -->|是| BB[转换到下一阶段]
        AA -->|否| CC[继续当前阶段]
        BB --> DD[更新阶段状态]
        CC --> END1[等待更多任务]
        DD --> END2[阶段转换完成]
    end
    
    style A fill:#e1f5fe
    style P fill:#fff3e0
    style R fill:#c8e6c9
    style S fill:#ffcdd2
    style BB fill:#81c784
```

## 热重载系统流程图

### 开发时实时代码更新流程

```mermaid
graph TD
    subgraph "文件监控"
        A[代码文件修改] --> B[FileWatcher检测变化]
        B --> C{watchdog可用?}
        C -->|是| D[watchdog实时监控]
        C -->|否| E[轮询模式监控]
        D --> F[文件变化事件]
        E --> F
    end
    
    subgraph "事件处理"
        F --> G[防抖动处理]
        G --> H{是.py文件?}
        H -->|否| I[忽略事件]
        H -->|是| J[触发重载事件]
    end
    
    subgraph "模块重载"
        J --> K[ModuleReloader分析]
        K --> L[检查模块可重载性]
        L --> M{可以重载?}
        M -->|否| N[记录日志跳过]
        M -->|是| O[分析模块依赖]
        O --> P[计算重载顺序]
        P --> Q[逐个重载模块]
    end
    
    subgraph "工具更新"
        Q --> R{重载成功?}
        R -->|否| S[记录错误]
        R -->|是| T[更新工具实例]
        T --> U[刷新MCP工具]
        U --> V[通知重载成功]
        S --> W[降级处理]
    end
    
    subgraph "服务继续"
        V --> X[MCP服务器继续运行]
        W --> X
        X --> Y[无需重启开发体验]
    end
    
    style A fill:#e3f2fd
    style F fill:#fff3e0
    style Q fill:#fce4ec
    style V fill:#c8e6c9
    style S fill:#ffcdd2
    style Y fill:#4caf50,color:#fff
```

## MCP工具详细数据流

### init_tools 工作流指导

```mermaid
graph LR
    A[Claude Code请求] --> B[init_tools.execute]
    B --> C[验证project_path]
    C --> D[分析项目规模]
    D --> E[生成5阶段指导]
    E --> F[返回操作步骤]
    F --> G[Claude Code获得指导]
    
    style A fill:#e3f2fd
    style G fill:#c8e6c9
```

### doc_guide 项目分析流程

```mermaid
graph TD
    A[项目路径输入] --> B[ProjectAnalyzer启动]
    B --> C[扫描项目文件]
    C --> D[检测项目类型]
    D --> E{Python项目?}
    E -->|是| F[Python特征分析]
    E -->|否| G[其他语言检测]
    F --> H[框架识别]
    G --> H
    H --> I[复杂度评估]
    I --> J[生成文档策略]
    J --> K[返回分析结果]
    
    style A fill:#e1f5fe
    style K fill:#c8e6c9
```

### task_execute 任务执行流程

```mermaid
graph TD
    A[任务执行请求] --> B[获取任务信息]
    B --> C[验证任务状态]
    C --> D{任务可执行?}
    D -->|否| E[返回错误信息]
    D -->|是| F[获取执行上下文]
    F --> G[加载文档模板]
    G --> H[构建任务指导]
    H --> I[返回执行指导]
    I --> J[Claude Code生成文档]
    J --> K[task_complete标记完成]
    
    style A fill:#e1f5fe
    style I fill:#fff3e0
    style K fill:#c8e6c9
```

## 数据格式和接口规范

### JSON数据流格式

```mermaid
graph LR
    subgraph "输入格式"
        A[MCP Request<br/>JSON]
        A --> A1[project_path: string]
        A --> A2[task_id: string]
        A --> A3[parameters: object]
    end
    
    subgraph "处理格式"
        B[内部数据<br/>JSON]
        B --> B1[任务状态]
        B --> B2[执行历史]
        B --> B3[性能指标]
    end
    
    subgraph "输出格式"
        C[MCP Response<br/>JSON]
        C --> C1[success: boolean]
        C --> C2[data: object]
        C --> C3[error: string]
    end
    
    A --> B
    B --> C
    
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#c8e6c9
```

### 状态持久化流程

```mermaid
graph TD
    A[状态变更事件] --> B[StateTracker接收]
    B --> C[生成状态快照]
    C --> D[更新执行历史]
    D --> E[计算性能指标]
    E --> F[写入tasks.json]
    F --> G[原子操作保证]
    G --> H[支持中断恢复]
    
    style A fill:#e1f5fe
    style H fill:#c8e6c9
```

## 性能优化流程

### 智能文件过滤流程

```mermaid
graph TD
    A[项目路径输入] --> B[项目类型检测]
    B --> C[应用类型特定过滤]
    C --> D[排除无关目录]
    D --> E[大小和扩展名过滤]
    E --> F[智能优先级排序]
    F --> G[返回过滤结果]
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
```

### 任务调度优化流程

```mermaid
graph LR
    A[任务队列] --> B[依赖图分析]
    B --> C[优先级计算]
    C --> D[智能调度]
    D --> E[并发安全执行]
    E --> F[性能监控]
    F --> G[调度优化]
    G --> B
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
```

这套流程图设计提供了CodeLens系统完整的数据流可视化，涵盖了从Claude Code协作到内部任务引擎处理的所有关键流程，让整个系统的工作机制一目了然。