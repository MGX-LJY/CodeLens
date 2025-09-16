# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeLens is a Document-Driven MCP (Model Context Protocol) Server designed to collaborate with Claude Code. Instead of autonomously generating documentation, CodeLens provides structured file information, document templates, and validation services that enable Claude Code to efficiently understand and document projects.

**🔥 New Feature: Hot Reload Support**
- Automatically detects code file changes and reloads modules
- Supports watchdog real-time monitoring and polling fallback
- No need to restart server during development, greatly improving development efficiency

## Core Architecture

CodeLens operates as a **Claude Code collaboration assistant** with two main service layers:

### Service Layer
- **FileService**: Project file scanning, metadata extraction, directory tree generation
- **TemplateService**: Document template management and formatting

### MCP Interface Layer
- **doc_scan**: Scans project files and returns structured information
- **doc_guide**: Intelligent project analysis with framework detection and documentation strategy
- **task_init**: Generates complete 4-phase task plans with dependency management
- **task_status**: Real-time task progress monitoring and phase control
- **task_execute**: Advanced task execution engine with template integration
- **init_tools**: One-command project initialization with intelligent workflow

### 3-Layer Documentation Architecture
1. **Architecture Layer** (`/docs/architecture/`) - System overview, tech stack, data flow, deployment diagrams (6 templates)
2. **File Layer** (`/docs/files/`) - Comprehensive file analysis with classes, functions, algorithms (1 unified template)
3. **Project Layer** (`/docs/project/`) - README, changelog, roadmap, project scan reports (3 templates)

**Total: 10 Professional Templates** covering all documentation needs

## Common Development Commands

### Running the MCP Server
```bash
# Start MCP server for development (hot reload enabled by default)
python mcp_server.py  # 🔥 Now supports hot reload

# Disable hot reload
CODELENS_HOT_RELOAD=false python mcp_server.py

# Test MCP server with project scanning
python mcp_server.py test /path/to/project

# Get server information (includes hot reload status)
python mcp_server.py info

# Manually trigger hot reload
python mcp_server.py reload
```

### Testing MCP Tools Individually
```bash
# Test doc_scan tool
python src/mcp_tools/doc_scan.py /path/to/project --no-content


# Test project analysis
python src/mcp_tools/doc_guide.py /path/to/project

# Test task management
python src/mcp_tools/task_init.py /path/to/project
python src/mcp_tools/task_status.py /path/to/project --type current_task
python src/mcp_tools/task_execute.py /path/to/project --task-id <ID>
```

### Template System Testing
```bash
# Run template system tests
python test_template_system_v05.py

```

### Development Workflow
```bash
# Test the complete 4-phase workflow
python src/mcp_tools/init_tools.py /path/to/project  # Initialize workflow
python src/mcp_tools/task_status.py /path/to/project --type phase_overview  # Check progress
python src/mcp_tools/task_execute.py /path/to/project --task-id scan_123456789  # Execute tasks
```

## Tech Stack

- **Primary Language**: Python 3.9+
- **Framework**: MCP (Model Context Protocol) 
- **Task Engine**: Advanced dependency resolution with phase control
- **File Processing**: pathlib, glob for efficient file operations + intelligent large file handling (50KB chunking, 120KB processing limit)
- **Template System**: 10 professional templates with variable validation
- **Persistence**: JSON-based task state management with atomic operations
- **Intelligence**: Framework detection, complexity analysis, smart prioritization
- **Hot Reload**: watchdog file monitoring + importlib module reload, with polling fallback

## Key File Structure

```
/src/
├── services/
│   ├── file_service.py      # Enhanced project file scanning and metadata
│   └── __init__.py
├── templates/
│   ├── document_templates.py # 10 professional templates with validation
│   ├── templates/           # Template layer organization
│   │   ├── architecture_templates.py  # 6 architecture layer templates
│   │   ├── file_templates.py         # 1 comprehensive file template
│   │   └── project_templates.py      # 3 project layer templates
│   └── __init__.py  
├── task_engine/
│   ├── task_manager.py      # Advanced task lifecycle management
│   ├── phase_controller.py  # 4-phase workflow control
│   └── __init__.py
├── mcp_tools/
│   ├── doc_scan.py         # Project scanning MCP tool
│   ├── doc_guide.py        # Intelligent project analysis
│   ├── task_init.py        # Complete task plan generation
│   ├── task_status.py      # Real-time progress monitoring
│   ├── task_execute.py     # Advanced task execution engine
│   ├── init_tools.py       # One-command project initialization
│   └── __init__.py
├── hot_reload/             # 🔥 Hot reload system
│   ├── file_watcher.py     # File watcher (watchdog + polling)
│   ├── module_reloader.py  # Intelligent module reloader
│   ├── hot_reload_manager.py # Hot reload coordination manager
│   └── __init__.py
├── logging/                # Logging system
└── __init__.py
```

## 4-Phase Intelligent Documentation Workflow

### Phase 1: Project Scan and Analysis
```bash
python src/mcp_tools/doc_guide.py /path/to/project
# ✅ Intelligent framework detection (Flask, Django, React, etc.)
# ✅ Complexity analysis and file prioritization  
# ✅ Custom documentation strategy generation
# ✅ Project scanning and file analysis
```

### Phase 2: File-Level Documentation
```bash
python src/mcp_tools/task_execute.py /path/to/project --task-id <FILE_TASK_ID>
# ✅ Detailed file analysis and documentation
# ✅ Function and class documentation
# ✅ Code flow and dependency analysis
```

### Phase 3: Architecture-Level Documentation
```bash
python src/mcp_tools/task_execute.py /path/to/project --task-id <ARCH_TASK_ID>
# ✅ System architecture documentation
# ✅ Tech stack and data flow analysis
# ✅ Component and deployment diagrams
```

### Phase 4: Project-Level Documentation
```bash
python src/mcp_tools/task_execute.py /path/to/project --task-id <PROJECT_TASK_ID>
# ✅ README and project overview
# ✅ Changelog and roadmap generation
# ✅ Final project documentation
```

### One-Command Initialization
```bash
python src/mcp_tools/init_tools.py /path/to/project
# ✅ Complete workflow setup in one command
# ✅ Intelligent project size detection
# ✅ Estimated completion time reporting
```

## Large File Processing Strategy

CodeLens implements intelligent large file handling with a dual-threshold approach:

### File Processing Thresholds
- **Chunking Threshold**: 50KB - Files above this size are automatically chunked for processing
- **Processing Limit**: 120KB - Files above this size are skipped entirely
- **Processing Range**: 50KB-120KB files are handled through intelligent chunking system

### Chunking System Features
- **AST-Based Chunking**: Python files are chunked by classes, methods, and functions
- **Semantic Preservation**: Code semantic integrity maintained across chunks
- **Automatic Fallback**: Line-based chunking when AST parsing fails
- **Dependency Tracking**: Inter-chunk relationships and dependencies tracked

### Configuration
```python
# In task_execute.py and file_service.py
large_file_threshold = 50000    # 50KB - triggers chunking
max_file_size = 122880          # 120KB - processing upper limit

# Usage examples
file_service.read_file_with_chunking(file_path, max_file_size)
file_service.should_chunk_file(file_path, large_file_threshold)
```

### Benefits
- **Enhanced Coverage**: Process files up to 120KB (previously 50KB limit)
- **Maintained Performance**: Chunking prevents memory issues with large files
- **Backward Compatibility**: Existing chunking logic unchanged

## Development Principles

- **Information Provider**: CodeLens provides structured data, Claude Code generates content
- **Template-Driven**: Standardized templates ensure consistent documentation format
- **MCP-Native**: Designed specifically for MCP protocol integration
- **Zero Dependencies**: Core functionality works without external dependencies
- **Intelligent Workflow**: 4-phase automated documentation generation with task management

## Configuration

The MCP server configuration is defined in `claude_code_config.json`:

```json
{
  "mcpServers": {
    "codelens": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": ".",
      "env": {
        "PYTHONPATH": ".",
        "CODELENS_HOT_RELOAD": "true"
      }
    }
  }
}
```

### Hot Reload Configuration

- `CODELENS_HOT_RELOAD=true` - Enable hot reload (default)
- `CODELENS_HOT_RELOAD=false` - Disable hot reload

### How Hot Reload Works

1. **File Monitoring**: watchdog library for real-time monitoring or polling for file changes
2. **Smart Filtering**: Only reload project Python modules, excluding system and third-party libraries
3. **Dependency Resolution**: Automatically analyze module dependencies and reload in correct order
4. **Batch Processing**: Changes within 2-second window are processed in batches to avoid frequent reloads
5. **Tool Updates**: Automatically refresh MCP tool instances after reload

## Logging System

CodeLens includes a comprehensive logging system in `/src/logging/` that provides:
- Operation tracking with start/end timestamps
- Performance monitoring
- Error tracking with context
- Component-based logging

Access logs via the logger:
```python
from src.logging import get_logger
logger = get_logger(component="YourComponent", operation="operation_name")
```

## Template System Usage

### Getting Templates
```python
# Get all 10 templates
templates = service.get_template_list()

# Get templates by layer
arch_templates = service.get_templates_by_layer('architecture')
file_templates = service.get_templates_by_layer('file') 
project_templates = service.get_templates_by_layer('project')

# Get specific template with metadata
result = service.get_template_content('architecture')
```

### Template Layers
- **architecture**: 6 templates for system design documentation
- **file**: 1 comprehensive template for detailed file analysis
- **project**: 3 templates for project-level documentation

Each template includes metadata with variable definitions, file paths, and descriptions for proper usage.

## Task Management

The task engine provides intelligent workflow management:

- **Task Types**: 15 different task types across 4 phases
- **Dependency Resolution**: Automatic dependency chain management
- **Progress Tracking**: Real-time progress monitoring
- **State Persistence**: JSON-based state management
- **Phase Control**: 4-phase workflow with intelligent transitions

Task states: `pending` → `in_progress` → `completed` → `validated`

## Implementation Status

✅ **Production Ready**: All core MCP tools, template system, and task engine are implemented and tested
✅ **Template System**: 10 professional templates covering all documentation layers  
✅ **Task Engine**: Complete dependency resolution and phase control
✅ **Hot Reload System**: Intelligent file monitoring and module reloading, supports real-time development updates
✅ **Recent Fixes**: Scan task template integration, dependency consistency, validation system