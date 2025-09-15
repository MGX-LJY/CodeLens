# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeLens is a Document-Driven MCP (Model Context Protocol) Server designed to collaborate with Claude Code. Instead of autonomously generating documentation, CodeLens provides structured file information, document templates, and validation services that enable Claude Code to efficiently understand and document projects.

## Current State

This repository has been **successfully refactored** from an AI-driven documentation generator to a Claude Code collaboration assistant. The core MCP tools are implemented, tested, and **production-ready** with intelligent task management system.

## Core Architecture

CodeLens operates as a **Claude Code collaboration assistant** with two main service layers:

### Service Layer
- **FileService**: Project file scanning, metadata extraction, directory tree generation
- **TemplateService**: Document template management and formatting

### MCP Interface Layer
- **doc_scan**: Scans project files and returns structured information
- **template_get**: Provides document templates for various documentation levels
- **doc_guide**: Intelligent project analysis with framework detection and documentation strategy
- **task_init**: Generates complete 5-phase task plans with dependency management
- **task_status**: Real-time task progress monitoring and phase control
- **task_execute**: Advanced task execution engine with template integration
- **init_tools**: One-command project initialization with intelligent workflow

### 4-Layer Documentation Architecture
1. **Architecture Layer** (`/docs/architecture/`) - System overview, tech stack, data flow, deployment diagrams (6 templates)
2. **Module Layer** (`/docs/modules/`) - Module functionality, API docs, business flows, dependencies (6 templates)  
3. **File Layer** (`/docs/files/`) - Comprehensive file analysis with classes, functions, algorithms (1 unified template)
4. **Project Layer** (`/docs/project/`) - README, changelog, roadmap, project scan reports (4 templates)

**Total: 17 Professional Templates** covering all documentation needs

## Tech Stack

- **Primary Language**: Python 3.9+
- **Framework**: MCP (Model Context Protocol)
- **Task Engine**: Advanced dependency resolution with phase control
- **File Processing**: pathlib, glob for efficient file operations
- **Template System**: 17 professional templates with variable validation
- **Persistence**: JSON-based task state management with atomic operations
- **Intelligence**: Framework detection, complexity analysis, smart prioritization

## 🚀 5-Phase Intelligent Documentation Workflow

CodeLens provides a **complete automated workflow** for large-scale project documentation:

### Phase 1: Project Analysis
```bash
python src/mcp_tools/doc_guide.py /path/to/project
# ✅ Intelligent framework detection (Flask, Django, React, etc.)
# ✅ Complexity analysis and file prioritization  
# ✅ Custom documentation strategy generation
```

### Phase 2: Task Planning
```bash
python src/mcp_tools/task_init.py /path/to/project --analysis-file .codelens/analysis.json --create-tasks
# ✅ Generates 20-100+ tasks based on project size
# ✅ Smart dependency graph with proper sequencing
# ✅ Estimated completion time calculation
```

### Phase 3: Progress Monitoring
```bash
python src/mcp_tools/task_status.py /path/to/project --type current_task
# ✅ Real-time progress tracking
# ✅ Phase completion validation
# ✅ Dependency satisfaction checking
```

### Phase 4: Documentation Generation
```bash
python src/mcp_tools/task_execute.py /path/to/project --task-id <TASK_ID>
# ✅ Template-driven content generation
# ✅ Automatic output directory creation
# ✅ Quality validation and error handling
```

### Phase 5: One-Command Initialization
```bash
python src/mcp_tools/init_tools.py /path/to/project
# ✅ Complete workflow setup in one command
# ✅ Intelligent project size detection
# ✅ Estimated completion time reporting
```

## MCP Tools Reference

### doc_scan
**Purpose**: Scan project files and return structured information
```python
# Command line usage
python src/mcp_tools/doc_scan.py /path/to/project --no-content

# MCP parameters
{
  "project_path": "/path/to/project",
  "include_content": true,
  "config": {
    "file_extensions": [".py"],
    "max_file_size": 50000
  }
}
```

### template_get  
**Purpose**: Retrieve document templates
```python
# Get all 17 templates
python src/mcp_tools/template_get.py --list-all

# Get specific template with metadata
python src/mcp_tools/template_get.py --template project_scan_summary
```

### task_status
**Purpose**: Monitor documentation progress
```python
# Check current task
python src/mcp_tools/task_status.py /path/to/project --type current_task

# Get phase overview
python src/mcp_tools/task_status.py /path/to/project --type phase_overview
```

### task_execute
**Purpose**: Execute documentation tasks
```python
# Execute specific task
python src/mcp_tools/task_execute.py /path/to/project --task-id scan_123456789

# Complete task
python src/mcp_tools/task_execute.py /path/to/project --task-id scan_123456789 --mode complete
```



## Key Principles

- **Information Provider**: CodeLens provides structured data, Claude Code generates content
- **Template-Driven**: Standardized templates ensure consistent documentation format
- **MCP-Native**: Designed specifically for MCP protocol integration

## 🎯 Implementation Status (Updated 2025-09)

✅ **Completed & Production Ready**:
- **FileService**: Enhanced metadata extraction, directory tree generation, framework detection
- **TemplateService**: 17 professional templates covering all documentation layers
- **TaskEngine**: Complete dependency resolution, phase control, atomic state management
- **7 MCP Tools**: doc_scan, template_get, doc_guide, task_init, task_status, task_execute, init_tools
- **Intelligent Workflow**: 5-phase automated documentation generation
- **Recent Fixes**: Scan task template integration, dependency ID consistency, template validation

🧪 **Successfully Tested**:
- WeChat automation project (453 files) - Generated 40 tasks across 5 phases
- Task dependency resolution working correctly
- Template system producing real documentation output
- All critical bugs from initial implementation resolved

## File Structure (Updated)

```
/src/
├── services/
│   ├── file_service.py      # Enhanced project file scanning and metadata
│   └── __init__.py
├── templates/
│   ├── document_templates.py # 17 professional templates with validation
│   ├── templates/           # Template layer organization
│   │   ├── architecture_templates.py  # 6 architecture layer templates
│   │   ├── module_templates.py       # 6 module layer templates  
│   │   ├── file_templates.py         # 1 comprehensive file template
│   │   └── project_templates.py      # 4 project layer templates
│   └── __init__.py  
├── task_engine/
│   ├── task_manager.py      # Advanced task lifecycle management
│   ├── phase_controller.py  # 5-phase workflow control
│   └── __init__.py
├── mcp_tools/
│   ├── doc_scan.py         # Project scanning MCP tool
│   ├── template_get.py     # Template retrieval MCP tool
│   ├── doc_guide.py        # 🆕 Intelligent project analysis
│   ├── task_init.py        # 🆕 Complete task plan generation
│   ├── task_status.py      # 🆕 Real-time progress monitoring
│   ├── task_execute.py     # 🆕 Advanced task execution engine
│   ├── init_tools.py       # 🆕 One-command project initialization
│   └── __init__.py
└── __init__.py
/docs/                      # Generated documentation structure
```

## 🛠️ Development Guidelines

### For Large Projects (50+ files)

**Workflow:**
1. **Initialize**: `python src/mcp_tools/init_tools.py /path/to/project`
2. **Monitor Progress**: `python src/mcp_tools/task_status.py /path/to/project --type current_task`  
3. **Execute Tasks**: `python src/mcp_tools/task_execute.py /path/to/project --task-id <ID>`
4. **Repeat**: Continue executing tasks until all phases complete

### For Small Projects (< 50 files)

**Quick Workflow:**
1. **Analyze**: `python src/mcp_tools/doc_guide.py /path/to/project`
2. **Plan**: `python src/mcp_tools/task_init.py /path/to/project --analysis-file .codelens/analysis.json`
3. **Generate**: Use Claude Code with templates from `template_get`

### Template System Usage

```python
# Get specific template with full metadata
python src/mcp_tools/template_get.py --template project_scan_summary --metadata

# List templates by layer
python src/mcp_tools/template_get.py --layer architecture
python src/mcp_tools/template_get.py --layer module
python src/mcp_tools/template_get.py --layer file
python src/mcp_tools/template_get.py --layer project
```

## 🚨 Critical Fixes Applied (2025-09)

- **Scan Task Empty Implementation**: Fixed scan tasks to generate actual project reports using `project_scan_summary` template
- **Dependency ID Mismatch**: Resolved task dependency chain issues with consistent ID generation
- **Template Integration**: All 17 templates properly integrated with task execution engine
- **Task Validation**: Added comprehensive output validation and quality checks

## 每次都要记得把想法生成在文档中