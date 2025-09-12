#!/usr/bin/env python3
"""
生成四层文档架构的空白文件结构
根据 doc-driven-mcp-requirements.md 规范创建完整的文档目录和空白文件
"""

import os
from pathlib import Path

def create_file(filepath):
    """创建空白文件"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    Path(filepath).touch()
    print(f"Created: {filepath}")

def main():
    base_dir = Path(__file__).parent / "docs"
    
    # 四层文档架构结构定义
    doc_structure = {
        # 第一层：架构文档（Architecture Layer）
        "architecture": [
            "overview.md",
            "tech-stack.md", 
            "data-flow.md",
            "diagrams/system-architecture.md",
            "diagrams/component-diagram.md",
            "diagrams/deployment-diagram.md"
        ],
        
        # 第二层：模块文档（Module Layer）
        "modules": [
            "overview.md",
            "module-relations.md",
            "modules/auth/README.md",
            "modules/auth/api.md",
            "modules/auth/flow.md",
            "modules/database/README.md",
            "modules/database/schema.md", 
            "modules/database/queries.md",
            "connections/auth-database.md",
            "connections/api-services.md"
        ],
        
        # 第三层：文件文档（File Layer）
        "files": [
            "summaries/src/main.py.md",
            "summaries/src/utils.py.md",
            "summaries/tests/test_main.py.md"
        ],
        
        # 第四层：项目文档（Project Layer）
        "project": [
            "README.md",
            "CHANGELOG.md",
            "versions/v1.0.0.md",
            "versions/v1.1.0.md", 
            "versions/current.md",
            "roadmap.md",
            "decisions/ADR-001.md",
            "decisions/ADR-002.md"
        ]
    }
    
    print("正在生成四层文档架构...")
    print("=" * 50)
    
    # 创建所有文件
    for layer, files in doc_structure.items():
        print(f"\n创建 {layer} 层:")
        print("-" * 30)
        
        for file_path in files:
            full_path = base_dir / layer / file_path
            create_file(full_path)
    
    print("\n" + "=" * 50)
    print("四层文档架构生成完成!")
    print(f"总共创建了 {sum(len(files) for files in doc_structure.values())} 个文件")
    print("\n文档结构预览:")
    
    # 显示生成的目录结构
    def show_tree(directory, prefix="", is_last=True):
        if not directory.exists():
            return
            
        items = sorted([item for item in directory.iterdir() if not item.name.startswith('.')])
        
        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1
            current_prefix = "└── " if is_last_item else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir():
                next_prefix = prefix + ("    " if is_last_item else "│   ")
                show_tree(item, next_prefix, is_last_item)
    
    if base_dir.exists():
        print(f"\n{base_dir.name}/")
        show_tree(base_dir)

if __name__ == "__main__":
    main()