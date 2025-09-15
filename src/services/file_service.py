"""
文件服务：负责扫描和读取项目源代码文件
为Claude Code提供结构化的文件信息
"""
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

# 导入日志系统
try:
    from ..logging import get_logger
except ImportError:
    # 如果日志系统不可用，创建一个空日志器
    class DummyLogger:
        def debug(self, msg, context=None): pass

        def info(self, msg, context=None): pass

        def warning(self, msg, context=None): pass

        def error(self, msg, context=None, exc_info=None): pass

        def log_operation_start(self, *args, **kwargs): return "dummy"

        def log_operation_end(self, op, op_id, **ctx): pass


    get_logger = lambda **kwargs: DummyLogger()


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
            '*.egg-info',
            '.DS_Store',
            'Thumbs.db',
            '*.log',
            '.gitignore',
            '.gitkeep',
            '.pytest_cache',
            '.coverage',
            '*.tmp',
            '*.temp'
        ]

        # 初始化日志器
        self.logger = get_logger(component="FileService", operation="default")

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

    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件元数据信息"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None

            stat = path.stat()
            return {
                'path': str(path),
                'name': path.name,
                'size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'extension': path.suffix if path.is_file() else None
            }
        except Exception as e:
            print(f"Error getting metadata for {file_path}: {e}")
            return None

    def get_directory_tree(self, project_path: str, max_depth: int = 3) -> Dict[str, Any]:
        """获取优化的目录树结构，专为Claude Code设计"""
        project_path = Path(project_path)

        def _build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return None

            # 获取基本信息
            node = {
                'name': path.name,
                'path': str(path),
                'type': 'directory' if path.is_dir() else 'file',
                'depth': current_depth
            }

            # 添加元数据
            if path.exists():
                try:
                    stat = path.stat()
                    node['size'] = stat.st_size
                    node['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                except:
                    pass

            # 如果是目录，添加子节点
            if path.is_dir() and current_depth < max_depth:
                children = []
                try:
                    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                    for item in items:
                        if self._should_exclude(item, self.default_excludes):
                            continue

                        child = _build_tree(item, current_depth + 1)
                        if child:
                            children.append(child)

                    node['children'] = children
                    node['children_count'] = len(children)
                except PermissionError:
                    node['children'] = []
                    node['children_count'] = 0

            return node

        return _build_tree(project_path)

    def get_project_files_info(self, project_path: str, include_content: bool = True,
                               extensions: List[str] = None, exclude_patterns: List[str] = None,
                               max_file_size: int = 50000) -> Dict[str, Any]:
        """获取项目文件的完整信息，为Claude Code提供结构化数据"""

        # 开始操作日志记录
        start_time = time.time()
        operation_id = self.logger.log_operation_start("get_project_files_info",
                                                       project_path=project_path,
                                                       include_content=include_content,
                                                       max_file_size=max_file_size)

        try:
            # 获取项目基础信息
            self.logger.debug("获取项目基础信息", {"project_path": project_path})
            project_info = self.get_project_info(project_path)

            # 扫描源代码文件
            self.logger.debug("扫描项目源代码文件", {
                "extensions": extensions or self.default_extensions,
                "exclude_patterns": exclude_patterns or self.default_excludes
            })
            source_files = self.scan_source_files(project_path, extensions, exclude_patterns)

            self.logger.info("文件扫描完成", {
                "found_files": len(source_files),
                "project_path": project_path
            })

            # 构建文件信息列表
            files_info = []
            for file_path in source_files:
                file_info = {
                    'path': file_path,
                    'relative_path': self.get_relative_path(file_path, project_path)
                }

                # 添加文件元数据
                metadata = self.get_file_metadata(file_path)
                if metadata:
                    file_info.update(metadata)

                # 添加文件内容（如果需要）
                if include_content:
                    content = self.read_file_safe(file_path, max_file_size)
                    file_info['content'] = content
                    file_info['content_available'] = content is not None

                files_info.append(file_info)

            # 获取目录树
            directory_tree = self.get_directory_tree(project_path)

            # 统计信息
            statistics = {
                'total_files': len(files_info),
                'total_size': sum(f.get('size', 0) for f in files_info),
                'file_types': {},
                'largest_file': None,
                'newest_file': None
            }

            # 统计文件类型
            for file_info in files_info:
                ext = file_info.get('extension', 'no_extension')
                statistics['file_types'][ext] = statistics['file_types'].get(ext, 0) + 1

            # 找到最大和最新的文件
            if files_info:
                statistics['largest_file'] = max(files_info, key=lambda f: f.get('size', 0))
                statistics['newest_file'] = max(files_info, key=lambda f: f.get('modified_time', ''))

            result = {
                'project_info': project_info,
                'files': files_info,
                'directory_tree': directory_tree,
                'statistics': statistics,
                'scan_config': {
                    'extensions': extensions or self.default_extensions,
                    'exclude_patterns': exclude_patterns or self.default_excludes,
                    'max_file_size': max_file_size,
                    'include_content': include_content
                }
            }

            # 记录操作成功完成
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_operation_end("get_project_files_info", operation_id,
                                          duration_ms=duration_ms, success=True,
                                          total_files=statistics['total_files'],
                                          total_size=statistics['total_size'])

            return result

        except Exception as e:
            # 记录操作失败
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_operation_end("get_project_files_info", operation_id,
                                          duration_ms=duration_ms, success=False,
                                          error=str(e))
            self.logger.error("项目文件信息获取失败", {
                "project_path": project_path,
                "error": str(e)
            }, exc_info=e)
            raise
