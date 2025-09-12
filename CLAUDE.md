# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeLens is a Document-Driven MCP (Model Context Protocol) Server that enables AI to understand and modify code through a structured five-layer documentation system instead of directly reading source code. This approach minimizes context waste and reduces comprehension errors.

## Current State

This repository is in the **planning/specification stage**. The main specification document `doc-driven-mcp-requirements.md` contains the complete project vision and requirements in Chinese. No source code has been implemented yet.

## Core Architecture

The project centers around a **five-layer documentation system**:

1. **Architecture Layer** (`/docs/architecture/`) - System overview, design patterns, tech stack
2. **Module Layer** (`/docs/modules/`) - Module functionality, interfaces, dependencies  
3. **File Layer** (`/docs/files/`) - File summaries, classes, functions, algorithms
4. **Project Layer** (`/docs/project/`) - README, changelog, version records, ADRs
5. **Context Layer** - Business context, terminology, coding standards

## Planned Tech Stack

- **Primary Language**: Python 3.9+ (with TypeScript support planned)
- **Framework**: Anthropic MCP SDK
- **Parsing**: AST parsers (Python: ast, TypeScript: ts-morph)
- **Documentation**: Markdown + JSON metadata
- **Configuration**: YAML/JSON config files

## Core MCP Tools (To Be Implemented)

- `doc_init` - Initialize the five-layer documentation system
- `doc_query` - Multi-dimensional documentation search and retrieval
- `doc_update` - Update documentation content across all layers
- `code_modify` - Execute code modifications based on documentation understanding

## Development Phases

1. **Phase 1** (2 weeks): MVP with basic 3-layer documentation
2. **Phase 2** (3 weeks): Complete 5-layer system with intelligent querying
3. **Phase 3** (2 weeks): Performance optimization and multi-language support
4. **Phase 4** (1 week): Production-ready release

## Operating Modes

- **Init Mode**: Scan existing projects and generate initial documentation
- **Update Mode**: Monitor code changes and auto-update documentation
- **Query Mode**: Respond to AI queries using documentation layers
- **Modify Mode**: Execute precise code modifications based on AI instructions

## Key Principles

- **Documentation as Interface**: AI interacts with projects through documentation, not direct code reading
- **Layered Understanding**: Each documentation layer provides different granularity of project understanding
- **Version Tracking**: Complete evolution history of both code and documentation
- **Intelligent Modification**: Precise code changes based on comprehensive documentation context

## Development Guidelines

When implementing this project:

1. Start with the three core layers (Architecture, Module, File) before expanding
2. Ensure all MCP tools follow the specification in `doc-driven-mcp-requirements.md`
3. Implement robust AST parsing for accurate code-documentation synchronization
4. Design the documentation format to be both human-readable and machine-parseable
5. Build comprehensive test suites for each MCP tool and operating mode

## File Structure (Planned)

```
/src/mcp_server/          # Main MCP server implementation
/src/parsers/             # Language-specific AST parsers  
/src/documentation/       # Documentation generation and management
/docs/                    # Five-layer documentation system
/tests/                   # Comprehensive test suites
/config/                  # Configuration templates and schemas
```