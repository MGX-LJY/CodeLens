# src/mcp_tools/project_overview.py

## File Overview
**Path**: `src/mcp_tools/project_overview.py`  
**Type**: MCP Tool Implementation  
**Purpose**: Documentation discovery and AI reading prompt generation tool that scans project documentation folders and creates prioritized reading lists

## Primary Functionality

### Core Purpose
Scans project `docs` folder structure to identify available documentation files and generates intelligent reading prompts for AI systems. Focuses specifically on project-level and architecture documentation to provide comprehensive project understanding.

### Key Components

#### ProjectOverviewTool Class
**Purpose**: Main MCP tool implementation for documentation scanning
**Key Methods**:
- `execute()`: Main execution method with parameter validation and error handling
- `_generate_file_list_prompt()`: Scans documentation directories and creates reading prompts
- `_success_response()` / `_error_response()`: Standardized response formatting

## Key Features

### Documentation Discovery
- **Project Documentation**: Scans `docs/project` directory for project-level documentation
- **Architecture Documentation**: Scans `docs/architecture` directory for system design documentation  
- **Recursive Scanning**: Uses `rglob("*.md")` to find all Markdown files in subdirectories
- **File Prioritization**: Sorts files with README files prioritized first

### AI Prompt Generation
- **Reading Order**: Creates ordered list of documentation files for systematic reading
- **Contextual Prompts**: Generates prompts that include project name and file count
- **Completion Instructions**: Includes instructions for summarizing core functionality and architecture

### Path Management
- **Flexible Input**: Accepts optional project_path parameter
- **Current Directory Fallback**: Uses current working directory if no path provided
- **Path Validation**: Verifies project path exists and is a valid directory
- **Relative Path Display**: Shows file paths relative to project root

## Technical Implementation

### Dependencies
- **Standard Library**: `sys`, `os`, `json`, `pathlib`, `typing`
- **Project Modules**: `src.logging` for comprehensive operation tracking

### File Scanning Logic
```python
# Target directories
docs/project/     # Project-level documentation
docs/architecture/  # System architecture documentation

# File selection criteria
*.md files only   # Markdown documentation files
Recursive search  # Includes subdirectories
README priority   # README files listed first
```

### Error Handling
- **Path Validation**: Comprehensive checking of project directory existence
- **Graceful Degradation**: Returns informative messages when no documentation found
- **Exception Management**: Catches and logs all exceptions with context

## Integration Points

### MCP Protocol Integration
- **Tool Definition**: Provides complete MCP tool schema with optional parameters
- **Standardized Response**: Returns structured JSON responses with success/error status
- **Parameter Flexibility**: Supports optional project_path parameter

### CodeLens Ecosystem Integration
- **Documentation Structure**: Aligns with CodeLens 3-layer documentation architecture
- **Workflow Integration**: Supports documentation discovery phase of CodeLens workflow
- **Logging Integration**: Uses centralized logging system for operation tracking

## Usage Examples

### Command Line Usage
```bash
python src/mcp_tools/project_overview.py /path/to/project
```

### MCP Tool Usage
```python
tool = ProjectOverviewTool()
result = tool.execute({"project_path": "/path/to/project"})
```

### Expected Output Example
```json
{
  "success": true,
  "tool": "project_overview", 
  "data": {
    "prompt": "请按顺序阅读以下3个项目文档文件，了解MyProject项目：\n\n- docs/project/README.md\n- docs/architecture/system_design.md\n- docs/project/changelog.md\n\n阅读完成后，请总结项目的核心功能和架构特点。",
    "message": "已生成项目 MyProject 的文档阅读提示词"
  }
}
```

## Design Patterns

### Scanner Pattern
- **Directory Traversal**: Systematic scanning of documentation directories
- **File Collection**: Gathering files based on type and location criteria
- **Result Aggregation**: Combining results from multiple directory scans

### Template Method Pattern
- **Execution Framework**: Standard execution flow with customizable scanning logic
- **Response Formatting**: Consistent response structure across all operations
- **Error Handling**: Standardized error response generation

### Strategy Pattern
- **File Prioritization**: Configurable sorting strategy for file ordering
- **Prompt Generation**: Flexible prompt template system
- **Directory Selection**: Configurable target directory scanning

## Performance Characteristics

### Lightweight Operation
- **Fast Scanning**: Simple file system traversal with minimal processing
- **Memory Efficient**: Processes file paths without loading file contents
- **Quick Response**: Typically completes in milliseconds

### Scalability Considerations
- **Large Document Sets**: Efficiently handles projects with many documentation files
- **Deep Directory Structures**: Recursive scanning handles nested documentation
- **Path Resolution**: Efficient relative path calculation

## Error Scenarios and Handling

### Common Error Cases
1. **Missing Project Path**: Returns clear error with path validation failure
2. **No Documentation Found**: Returns informative message about missing docs directories
3. **Permission Issues**: Handles file access errors gracefully
4. **Invalid Directory**: Validates that project path is actually a directory

### Recovery Mechanisms
- **Graceful No-Content**: Provides helpful message when no documentation exists
- **Path Validation**: Clear error messages for path-related issues
- **Exception Logging**: Comprehensive error tracking with stack traces

## Documentation Structure Alignment

### CodeLens Documentation Architecture
- **Project Layer**: Scans `docs/project/` for project-level documentation
- **Architecture Layer**: Scans `docs/architecture/` for system design documentation
- **Strategic Focus**: Targets high-level documentation for project understanding

### File Type Support
- **Markdown Focus**: Specifically targets `.md` files for documentation
- **Recursive Discovery**: Finds documentation in subdirectories
- **Comprehensive Coverage**: Includes all markdown files in target directories

## Output Format and Structure

### Prompt Generation Logic
1. **Header Generation**: Creates descriptive prompt header with file count and project name
2. **File Listing**: Lists files in priority order with relative paths
3. **Instructions**: Includes completion instructions for AI systems
4. **Formatting**: Uses clear markdown-style formatting for readability

### Priority System
- **README First**: README files appear at the top of the reading list
- **Alphabetical Secondary**: Non-README files sorted alphabetically
- **Path Consistency**: All paths shown relative to project root

## Future Enhancement Opportunities

### Content Analysis
- **File Size Consideration**: Potential for ordering based on file size or importance
- **Content Scanning**: Could analyze file headers for additional prioritization
- **Cross-References**: Potential for detecting and highlighting file relationships

### Advanced Prompting
- **Template Customization**: Support for different prompt templates
- **Context Enhancement**: Addition of project metadata to prompts
- **Multi-Language Support**: Support for documentation in multiple languages

### Integration Expansion
- **Additional Directories**: Support for scanning other documentation directories
- **File Type Expansion**: Support for other documentation formats (PDF, HTML, etc.)
- **Metadata Integration**: Integration with project configuration for enhanced context

## Maintenance and Documentation

### Code Quality
- **Clear Structure**: Well-organized class with focused responsibilities
- **Comprehensive Logging**: Detailed operation tracking and error reporting
- **Consistent Naming**: Clear, descriptive method and variable names

### Testing Support
- **Command Line Interface**: Built-in CLI for standalone testing
- **Factory Pattern**: Clean tool instantiation for testing
- **Error Simulation**: Comprehensive error handling for testing scenarios