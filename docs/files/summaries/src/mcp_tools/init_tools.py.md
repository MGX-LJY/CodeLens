# src/mcp_tools/init_tools.py

## File Overview
**Path**: `src/mcp_tools/init_tools.py`  
**Type**: MCP Tool Implementation  
**Purpose**: CodeLens workflow initialization and guidance tool that provides standard 5-phase documentation generation workflow instructions

## Primary Functionality

### Core Purpose
Pure guidance tool that provides standardized CodeLens 5-phase workflow operation steps. Does not execute actual operations - only provides detailed instructions and project analysis for guiding users through the complete documentation generation process.

### Key Components

#### InitToolsCore Class
**Purpose**: Core workflow guidance generator
**Key Methods**:
- `get_workflow_guidance()`: Generates complete 5-phase workflow instructions
- `_get_project_info()`: Analyzes project scale and estimates completion time
- `_get_workflow_phases()`: Defines the 5 standard phases
- `_get_detailed_steps()`: Provides step-by-step execution instructions
- `_get_execution_tips()`: Offers workflow execution guidance
- `_get_workflow_features()`: Describes system capabilities

#### InitTools Class (MCP Wrapper)
**Purpose**: MCP tool interface wrapper
**Key Methods**:
- `get_tool_definition()`: Provides MCP tool schema definition
- `execute()`: Executes initialization guidance generation

## Key Features

### 5-Phase Workflow Definition
1. **Phase 1**: 智能项目分析 (doc_guide) - Project structure and type analysis
2. **Phase 2**: 任务计划生成 (task_init) - Complete task list creation
3. **Phase 3**: 状态监控检查 (task_status) - Current task information retrieval
4. **Phase 4**: 任务循环执行 (task_execute) - Iterative documentation generation
5. **Phase 5**: 文档验证确认 (doc_verify) - Final result validation

### Project Analysis Capabilities
- **File Scanning**: Counts total files and Python files
- **Scale Assessment**: Categorizes projects as small (<20 files), medium (<100 files), or large (100+ files)
- **Time Estimation**: Provides completion time estimates based on project size
- **Directory Validation**: Ensures project path exists and is accessible

### Workflow Features
- **智能分析**: Automatic project type, framework, and module structure identification
- **任务管理**: 40+ task types with intelligent dependency management and 5-phase flow control
- **模板系统**: 16 document templates with four-layer documentation architecture (file→module→architecture→project)
- **状态跟踪**: Real-time progress monitoring, complete execution history, interrupt recovery support
- **质量保证**: Template-driven generation, structured output, completeness validation

## Technical Implementation

### Dependencies
- **Standard Library**: `sys`, `json`, `argparse`, `pathlib`, `datetime`, `typing`
- **Project Modules**: `src.logging` for operation tracking and debugging

### Error Handling
- **Path Validation**: Checks project path existence and directory status
- **Graceful Degradation**: Returns structured error responses with solutions
- **Logging Integration**: Comprehensive operation tracking with start/end logging

### Configuration Management
- **Default Behavior**: Uses current working directory if no project_path provided
- **Flexible Input**: Accepts optional project_path parameter
- **Project Path Resolution**: Converts relative paths to absolute paths

## Integration Points

### MCP Protocol Integration
- **Tool Definition**: Provides complete MCP tool schema with input validation
- **Standardized Response**: Returns structured JSON responses with success/error status
- **Parameter Handling**: Supports optional project_path parameter

### CodeLens Ecosystem Integration
- **Command Generation**: Provides exact command syntax for each workflow phase
- **File Path Integration**: Uses project-relative paths in all generated commands
- **Dependency Awareness**: References correct tool dependencies and execution order

## Usage Examples

### Command Line Usage
```bash
python src/mcp_tools/init_tools.py /path/to/project
```

### MCP Tool Usage
```python
tool = InitTools()
result = tool.execute({"project_path": "/path/to/project"})
```

### Expected Output Structure
```json
{
  "success": true,
  "tool": "init_tools",
  "timestamp": "2024-01-01T12:00:00",
  "project_path": "/path/to/project",
  "guidance": {
    "workflow_name": "CodeLens 5阶段智能文档生成工作流",
    "description": "标准化文档生成流程，确保高质量输出",
    "project_info": {...},
    "phases": [...],
    "detailed_steps": {...},
    "execution_tips": [...],
    "workflow_features": {...}
  }
}
```

## Design Patterns

### Information Provider Pattern
- **Pure Guidance**: Provides instructions without executing operations
- **Structured Information**: Returns organized, actionable guidance
- **Template-Based**: Uses consistent response structure

### Factory Pattern
- **Tool Creation**: `create_mcp_tool()` factory function
- **Instance Management**: Clean separation of core logic and MCP wrapper

### Command Pattern
- **Step Definition**: Each workflow step includes specific command syntax
- **Execution Order**: Clear dependency chain and execution sequence
- **Parameterization**: Dynamic path and parameter insertion

## Performance Characteristics

### Lightweight Operation
- **Fast Execution**: No heavy file processing, only basic project scanning
- **Minimal Memory**: Simple data structures for workflow definition
- **Quick Response**: Typically completes in under 1 second

### Scalability
- **Project Size Handling**: Adapts recommendations based on project scale
- **Time Estimation**: Provides realistic completion time estimates
- **Resource Awareness**: Considers project complexity in guidance

## Error Scenarios and Handling

### Common Error Cases
1. **Invalid Project Path**: Returns clear error message with solution guidance
2. **Permission Issues**: Handles file access errors gracefully
3. **Missing Dependencies**: Provides fallback behavior with dummy logger

### Recovery Mechanisms
- **Graceful Degradation**: Continues operation even with partial failures
- **Clear Error Messages**: Provides actionable error information
- **Structured Error Response**: Maintains consistent response format

## Documentation and Maintenance

### Code Organization
- **Clear Separation**: Core logic separated from MCP interface
- **Comprehensive Documentation**: Extensive inline documentation and examples
- **Consistent Naming**: Clear, descriptive method and variable names

### Logging Integration
- **Operation Tracking**: Logs all major operations with context
- **Performance Monitoring**: Tracks operation start/end times
- **Error Tracking**: Comprehensive error logging with stack traces

## Future Considerations

### Enhancement Opportunities
- **Interactive Mode**: Potential for step-by-step interactive guidance
- **Custom Workflows**: Support for project-specific workflow variations
- **Integration Hooks**: Potential for pre/post-step custom actions

### Extensibility Points
- **Phase Customization**: Framework for adding custom workflow phases
- **Template Extension**: Support for custom workflow templates
- **Tool Integration**: Framework for integrating additional tools