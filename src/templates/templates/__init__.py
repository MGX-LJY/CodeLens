"""
CodeLens 模板包
三层架构文档模板系统
"""

from .architecture_templates import ArchitectureTemplates
from .file_templates import FileTemplates
from .project_templates import ProjectTemplates

__all__ = [
    'ArchitectureTemplates',
    'FileTemplates',
    'ProjectTemplates'
]