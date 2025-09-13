"""
CodeLens 模板包
四层架构文档模板系统
"""

from .architecture_templates import ArchitectureTemplates
from .module_templates import ModuleTemplates  
from .file_templates import FileTemplates
from .project_templates import ProjectTemplates

__all__ = [
    'ArchitectureTemplates',
    'ModuleTemplates', 
    'FileTemplates',
    'ProjectTemplates'
]