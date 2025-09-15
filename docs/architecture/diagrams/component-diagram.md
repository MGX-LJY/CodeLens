
# CodeLens 组件关系图

## 组件层次结构

```mermaid
graph TD
    subgraph "客户端层"
        CC[Claude Code<br/>智能化文档生成]
    end
    
    subgraph "MCP接口层 - 7个工具"
        subgraph "工作流控制工具"
            IT[init_tools<br/>InitTools]
            TC[task_complete<br/>TaskCompleteTool]
        end
        
        subgraph "项目分析工具"
            DG[doc_guide<br/>DocGuideTool]
            DS[doc_scan<br/>DocScanTool]
        end
        
        subgraph "任务管理工具"
            TI[task_init<br/>TaskInitTool]
            TE[task_execute<br/>TaskExecuteTool]
            TS[task_status<br/>TaskStatusTool]
        end
    end
    
    subgraph "任务引擎层"
        TM[TaskManager<br/>任务生命周期]
        PC[PhaseController<br/>阶段流程控制]
        ST[StateTracker<br/>状态跟踪监控]
        SA[调度算法<br/>智能调度引擎]
    end
    
    subgraph "热重载系统层"
        HRM[HotReloadManager<br/>热重载管理器]
        FW[FileWatcher<br/>文件监控组件]
        MR[ModuleReloader<br/>模块重载组件]
        SC[系统协调<br/>事件协调器]
    end
    
    subgraph "服务层"
        FS[FileService<br/>智能文件服务]
        TmS[TemplateService<br/>模板管理]
        VS[ValidationService<br/>验证服务]
    end
    
    subgraph "基础层"
        FileSys[文件系统<br/>Python pathlib<br/>智能过滤]
        Templates[模板资源<br/>10个核心模板<br/>三层架构模板]
        Storage[状态存储<br/>JSON持久化文件<br/>.codelens/tasks.json]
    end
    
    CC -->|MCP协议通信| IT
    CC -->|MCP协议通信| DG
    CC -->|MCP协议通信| TI
    CC -->|MCP协议通信| TE
    CC -->|MCP协议通信| TS
    CC -->|MCP协议通信| TC
    CC -->|MCP协议通信| DS
    
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
    PC --> ST
    
    TM --> HRM
    PC --> HRM
    ST --> HRM
    SA --> HRM
    
    HRM --> FW
    HRM --> MR
    HRM --> SC
    
    HRM --> FS
    HRM --> TmS
    HRM --> VS
    
    FS --> FileSys
    TmS --> Templates
    VS --> Storage
    
    style CC fill:#e3f2fd
    style TM fill:#fff3e0
    style HRM fill:#fce4ec
    style FS fill:#e8f5e8
```

## 详细组件说明

### 1. **MCP 工具组件** - 对外接口层 (7个专业工具)
- **InitTools**: 工作流指导工具，提供标准5阶段操作步骤指导
- **DocGuideTool**: 智能项目分析器，自动识别项目类型、框架和生成文档策略
- **TaskInitTool**: 任务计划生成器，基于分析结果创建5阶段执行计划
- **TaskExecuteTool**: 任务执行管理器，提供模板、上下文和执行指导
- **TaskStatusTool**: 状态监控中心，实时进度跟踪和健康诊断
- **TaskCompleteTool**: 任务完成工具，标记任务完成并验证输出质量
- **DocScanTool**: 项目文件扫描工具，智能过滤和结构化数据提取

### 2. **任务引擎组件** - 智能化任务驱动核心
- **TaskManager**: 智能任务管理器，支持核心任务类型、依赖关系和优先级调度
- **PhaseController**: 5阶段严格控制器，确保100%完成率的阶段转换
- **StateTracker**: 实时状态跟踪，支持执行历史、性能监控和健康检查
- **调度算法**: 基于依赖关系的DAG调度和优先级算法

### 3. **热重载系统组件** - 开发时实时更新支持
- **HotReloadManager**: 热重载协调管理器，统一管理文件监控和模块重载流程
- **FileWatcher**: 文件监控组件，支持watchdog实时监控和轮询备用方案
- **ModuleReloader**: 模块重载组件，安全重载Python模块，支持依赖分析
- **系统协调**: 事件调度、状态同步、降级处理和性能优化

### 4. **服务组件** - 核心业务逻辑
- **FileService**: 智能文件分析服务，项目类型检测、框架识别和智能过滤
- **TemplateService**: 模板管理服务，10个核心模板统一管理，三层架构支持
- **ValidationService**: 验证服务，文档结构验证、完整性检查和多种验证模式

### 5. **基础组件** - 底层支撑
- **文件系统接口**: 基于 pathlib 的智能文件操作和过滤
- **模板资源**: 10个核心模板，三层架构(Architecture/File/Project)支持
- **状态存储**: JSON持久化文件系统，支持任务状态和执行历史保存

## 组件依赖关系

```mermaid
graph TD
    subgraph "MCP工具依赖链"
        IT3[InitTools] --> GUIDE[纯指导工具<br/>无依赖]
        
        DG3[DocGuideTool] --> FS2[FileService]
        DG3 --> PA[ProjectAnalyzer]
        
        TI3[TaskInitTool] --> TM2[TaskManager]
        TI3 --> TPG[TaskPlanGenerator]
        
        TE3[TaskExecuteTool] --> TM3[TaskManager]
        TE3 --> TEX[TaskExecutor]
        TE3 --> TmS2[TemplateService]
        
        TS3[TaskStatusTool] --> TM4[TaskManager]
        TS3 --> PC2[PhaseController]
        TS3 --> ST2[StateTracker]
        
        TC3[TaskCompleteTool] --> TM5[TaskManager]
        TC3 --> VS2[ValidationService]
        
        DS3[DocScanTool] --> FS3[FileService]
        
        HRM2[HotReloadManager] --> FW2[FileWatcher]
        HRM2 --> MR2[ModuleReloader]
    end
    
    subgraph "任务引擎内部关系"
        TMCore[TaskManager] <--> PCCore[PhaseController]
        PCCore <--> STCore[StateTracker]
        STCore <--> TMCore
        
        TMCore --> DEP[依赖图管理]
        PCCore --> PHASE[阶段控制逻辑]
        STCore --> PERSIST[状态持久化存储]
        
        DEP --> PRIORITY[优先级调度]
        PHASE --> COMPLETE[100%完成验证]
        PERSIST --> MONITOR[性能监控分析]
    end
    
    style IT3 fill:#e1f5fe
    style DG3 fill:#e8f5e8
    style TI3 fill:#fff8e1
    style TE3 fill:#fce4ec
    style TS3 fill:#e0f2f1
    style TC3 fill:#f1f8e9
    style DS3 fill:#e8eaf6
    style TMCore fill:#fff3e0
    style PCCore fill:#e8f5e8
    style STCore fill:#e0f2f1
```

### 依赖说明
- **MCP 工具** → **任务引擎/服务层**: MCP工具依赖任务引擎和对应服务组件
- **任务引擎组件** → **相互协作**: TaskManager、PhaseController、StateTracker紧密协作
- **任务引擎** → **服务层**: 任务引擎调用FileService、TemplateService、ValidationService
- **服务间无依赖**: FileService、TemplateService、ValidationService 相互独立
- **状态持久化**: 任务状态保存到JSON文件，支持中断恢复

## 数据流组件

### 智能化协作处理流
```mermaid
graph LR
    A[Claude Code 请求] --> B[MCP 工具<br/>7个专业工具]
    B --> C[参数验证]
    C --> D[任务引擎调用]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#e8f5e8
```

### 任务引擎处理流  
```mermaid
graph LR
    A[任务引擎调用] --> B[TaskManager]
    A --> C[PhaseController]
    A --> D[StateTracker]
    
    B --> E[服务层调用]
    C --> E
    D --> E
    
    E --> F[智能分析执行]
    
    style A fill:#e1f5fe
    style E fill:#fff3e0
    style F fill:#c8e6c9
```

### 服务层处理流
```mermaid
graph LR
    A[服务层调用] --> B[FileService]
    A --> C[TemplateService]
    A --> D[ValidationService]
    
    B --> E[业务逻辑]
    C --> E
    D --> E
    
    E --> F[数据处理]
    
    style A fill:#e1f5fe
    style E fill:#fff3e0
    style F fill:#c8e6c9
```

### 输出处理流
```mermaid
graph LR
    A[数据处理] --> B[结果生成]
    B --> C[JSON 格式化]
    C --> D[MCP 响应]
    D --> E[Claude Code]
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style C fill:#fce4ec
    style D fill:#e0f2f1
    style E fill:#c8e6c9
```

### 状态持久化流
```mermaid
graph LR
    A[任务状态变更] --> B[StateTracker]
    B --> C[JSON持久化]
    C --> D[.codelens/tasks.json]
    D --> E[中断恢复支持]
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style C fill:#fce4ec
    style D fill:#e0f2f1
    style E fill:#c8e6c9
```
