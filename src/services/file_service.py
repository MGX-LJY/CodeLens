"""
文件服务：负责扫描和读取项目源代码文件
"""
import os
import glob
from pathlib import Path
from typing import List, Dict, Optional


class FileService:
    def __init__(self):
        self.default_extensions = ['.py']
        self.default_excludes = [
            '__pycache__',
            '.git',
            'node_modules',
            '.idea',
            '.vscode',
            'venv',
            'env',
            '.env',
            'dist',
            'build',
            '*.egg-info'
        ]
    
    def scan_source_files(self, project_path: str, extensions: List[str] = None, 
                         exclude_patterns: List[str] = None) -> List[str]:
        """扫描项目中的源代码文件"""
        if extensions is None:
            extensions = self.default_extensions
        
        if exclude_patterns is None:
            exclude_patterns = self.default_excludes
        
        source_files = []
        project_path = Path(project_path)
        
        # 扫描指定扩展名的文件
        for ext in extensions:
            pattern = f"**/*{ext}"
            files = list(project_path.glob(pattern))
            source_files.extend(files)
        
        # 过滤排除的文件和目录
        filtered_files = []
        for file_path in source_files:
            if self._should_exclude(file_path, exclude_patterns):
                continue
            filtered_files.append(str(file_path))
        
        return sorted(filtered_files)
    
    def read_file_safe(self, file_path: str, max_size: int = 50000) -> Optional[str]:
        """安全读取文件内容，带大小限制"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return None
                
            # 检查文件大小
            file_size = file_path.stat().st_size
            if file_size > max_size:
                print(f"Warning: File {file_path} is too large ({file_size} bytes), skipping")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def get_relative_path(self, file_path: str, project_path: str) -> str:
        """获取相对于项目根目录的路径"""
        return os.path.relpath(file_path, project_path)
    
    def scan_directory_structure(self, project_path: str, max_depth: int = 3) -> Dict:
        """扫描目录结构，返回层次化的目录信息"""
        project_path = Path(project_path)
        
        def _scan_dir(path: Path, current_depth: int = 0) -> Dict:
            if current_depth > max_depth:
                return {}
            
            structure = {
                'name': path.name,
                'type': 'directory',
                'children': []
            }
            
            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                for item in items:
                    if self._should_exclude(item, self.default_excludes):
                        continue
                    
                    if item.is_dir():
                        child_structure = _scan_dir(item, current_depth + 1)
                        if child_structure:
                            structure['children'].append(child_structure)
                    else:
                        structure['children'].append({
                            'name': item.name,
                            'type': 'file'
                        })
            except PermissionError:
                pass
            
            return structure
        
        return _scan_dir(project_path)
    
    def get_project_info(self, project_path: str) -> Dict:
        """获取项目基础信息"""
        project_path = Path(project_path)
        project_name = project_path.name
        
        # 查找主要文件
        main_files = []
        common_main_files = ['main.py', 'app.py', 'run.py', '__main__.py', 'manage.py']
        
        for main_file in common_main_files:
            main_path = project_path / main_file
            if main_path.exists():
                main_files.append(str(main_path))
        
        # 查找配置文件
        config_files = {}
        config_patterns = {
            'requirements': 'requirements*.txt',
            'setup': 'setup.py',
            'pyproject': 'pyproject.toml',
            'package': 'package.json',
            'dockerfile': 'Dockerfile*',
            'readme': 'README*'
        }
        
        for config_type, pattern in config_patterns.items():
            matches = list(project_path.glob(pattern))
            if matches:
                config_files[config_type] = [str(f) for f in matches]
        
        return {
            'name': project_name,
            'path': str(project_path),
            'main_files': main_files,
            'config_files': config_files
        }
    
    def _should_exclude(self, path: Path, exclude_patterns: List[str]) -> bool:
        """检查路径是否应该被排除"""
        path_str = str(path)
        path_name = path.name
        
        for pattern in exclude_patterns:
            if pattern in path_str or pattern in path_name:
                return True
            
            # 检查是否匹配通配符模式
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(path_name, pattern) or fnmatch.fnmatch(path_str, pattern):
                    return True
        
        return False
    
    def create_file_summary_path(self, file_path: str, project_path: str, docs_path: str) -> str:
        """创建文件摘要的输出路径"""
        relative_path = self.get_relative_path(file_path, project_path)
        summary_path = Path(docs_path) / "files" / "summaries" / f"{relative_path}.md"
        
        # 确保目录存在
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        return str(summary_path)