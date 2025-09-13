"""
验证服务：检查文档生成状态和文件结构
专为Claude Code协作设计，只验证文件存在性
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ValidationService:
    """文档验证服务 - 检查文档生成状态但不读取内容"""
    
    def __init__(self):
        self.expected_structure = {
            'docs': {
                'type': 'directory',
                'required': True,
                'children': {
                    'architecture': {
                        'type': 'directory', 
                        'required': True,
                        'files': ['overview.md', 'tech-stack.md', 'data-flow.md']
                    },
                    'modules': {
                        'type': 'directory',
                        'required': True, 
                        'files': ['overview.md', 'module-relations.md']
                    },
                    'files': {
                        'type': 'directory',
                        'required': True,
                        'children': {
                            'summaries': {
                                'type': 'directory',
                                'required': True
                            }
                        }
                    },
                    'project': {
                        'type': 'directory',
                        'required': False,
                        'files': ['README.md', 'CHANGELOG.md']
                    }
                }
            }
        }
    
    def check_file_exists(self, file_path: str) -> bool:
        """检查单个文件是否存在"""
        try:
            path = Path(file_path)
            return path.exists() and path.is_file()
        except Exception:
            return False
    
    def check_directory_exists(self, dir_path: str) -> bool:
        """检查目录是否存在"""
        try:
            path = Path(dir_path)
            return path.exists() and path.is_dir()
        except Exception:
            return False
    
    def get_directory_files(self, dir_path: str, pattern: str = "*") -> List[Dict[str, Any]]:
        """获取目录下的文件列表（不读取内容）"""
        try:
            path = Path(dir_path)
            if not path.exists() or not path.is_dir():
                return []
            
            files = []
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        files.append({
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'extension': file_path.suffix
                        })
                    except:
                        files.append({
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': None,
                            'modified': None,
                            'extension': file_path.suffix
                        })
            
            return sorted(files, key=lambda x: x['name'])
        except Exception:
            return []
    
    def check_directory_structure(self, base_path: str, 
                                expected_structure: Optional[Dict] = None) -> Dict[str, Any]:
        """检查目录结构是否符合预期"""
        if expected_structure is None:
            expected_structure = self.expected_structure
        
        base_path = Path(base_path)
        results = {
            'base_path': str(base_path),
            'structure_valid': True,
            'missing_items': [],
            'existing_items': [],
            'extra_items': [],
            'validation_details': {}
        }
        
        def _check_structure(current_path: Path, structure: Dict, path_key: str = ""):
            for item_name, item_config in structure.items():
                item_path = current_path / item_name
                item_key = f"{path_key}/{item_name}" if path_key else item_name
                
                item_result = {
                    'name': item_name,
                    'path': str(item_path),
                    'type': item_config.get('type', 'unknown'),
                    'required': item_config.get('required', False),
                    'exists': False,
                    'details': {}
                }
                
                if item_path.exists():
                    item_result['exists'] = True
                    results['existing_items'].append(item_key)
                    
                    # 检查文件类型是否匹配
                    expected_type = item_config.get('type', 'unknown')
                    if expected_type == 'directory' and not item_path.is_dir():
                        item_result['details']['type_mismatch'] = f"Expected directory, found file"
                        results['structure_valid'] = False
                    elif expected_type == 'file' and not item_path.is_file():
                        item_result['details']['type_mismatch'] = f"Expected file, found directory"
                        results['structure_valid'] = False
                    
                    # 如果是目录，检查子项目
                    if item_path.is_dir() and 'children' in item_config:
                        _check_structure(item_path, item_config['children'], item_key)
                    
                    # 如果有指定文件列表，检查这些文件
                    if item_path.is_dir() and 'files' in item_config:
                        for file_name in item_config['files']:
                            file_path = item_path / file_name
                            if file_path.exists():
                                results['existing_items'].append(f"{item_key}/{file_name}")
                            else:
                                results['missing_items'].append(f"{item_key}/{file_name}")
                                if item_config.get('required', False):
                                    results['structure_valid'] = False
                else:
                    if item_config.get('required', False):
                        results['missing_items'].append(item_key)
                        results['structure_valid'] = False
                
                results['validation_details'][item_key] = item_result
        
        _check_structure(base_path, expected_structure)
        return results
    
    def get_missing_files(self, project_path: str, expected_files: List[str]) -> List[str]:
        """获取缺失的文件列表"""
        missing = []
        base_path = Path(project_path)
        
        for file_path in expected_files:
            full_path = base_path / file_path
            if not self.check_file_exists(str(full_path)):
                missing.append(file_path)
        
        return missing
    
    def get_generation_status(self, project_path: str) -> Dict[str, Any]:
        """获取文档生成状态的完整报告"""
        project_path = Path(project_path)
        docs_path = project_path / "docs"
        
        # 基本状态检查
        status = {
            'project_path': str(project_path),
            'docs_directory_exists': self.check_directory_exists(str(docs_path)),
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'generation_progress': {
                'total_expected': 0,
                'total_existing': 0,
                'completion_percentage': 0
            },
            'structure_validation': {},
            'layer_status': {},
            'file_statistics': {}
        }
        
        # 检查目录结构
        structure_result = self.check_directory_structure(str(project_path))
        status['structure_validation'] = structure_result
        
        if not status['docs_directory_exists']:
            status['overall_status'] = 'not_initialized'
            return status
        
        # 检查各层级状态
        layers = {
            'architecture': docs_path / 'architecture',
            'modules': docs_path / 'modules', 
            'files': docs_path / 'files',
            'project': docs_path / 'project'
        }
        
        total_expected = 0
        total_existing = 0
        
        for layer_name, layer_path in layers.items():
            layer_files = self.get_directory_files(str(layer_path), "*.md")
            layer_exists = self.check_directory_exists(str(layer_path))
            
            # 估算每层预期的文件数量
            expected_count = {
                'architecture': 3,  # overview.md, tech-stack.md, data-flow.md
                'modules': 2,       # overview.md, module-relations.md
                'files': 1,         # 至少有summaries子目录
                'project': 2        # README.md, CHANGELOG.md
            }.get(layer_name, 1)
            
            total_expected += expected_count
            existing_count = len(layer_files) if layer_exists else 0
            total_existing += min(existing_count, expected_count)
            
            status['layer_status'][layer_name] = {
                'exists': layer_exists,
                'file_count': existing_count,
                'expected_count': expected_count,
                'files': layer_files,
                'completion': min(existing_count / expected_count, 1.0) if expected_count > 0 else 0
            }
        
        # 计算总体进度
        status['generation_progress'] = {
            'total_expected': total_expected,
            'total_existing': total_existing,
            'completion_percentage': round((total_existing / total_expected * 100), 2) if total_expected > 0 else 0
        }
        
        # 确定总体状态
        completion_pct = status['generation_progress']['completion_percentage']
        if completion_pct == 0:
            status['overall_status'] = 'not_started'
        elif completion_pct < 30:
            status['overall_status'] = 'minimal'
        elif completion_pct < 70:
            status['overall_status'] = 'partial'
        elif completion_pct < 95:
            status['overall_status'] = 'mostly_complete'
        else:
            status['overall_status'] = 'complete'
        
        # 文件统计
        all_files = []
        for layer_files in [layer['files'] for layer in status['layer_status'].values()]:
            all_files.extend(layer_files)
        
        if all_files:
            total_size = sum(f.get('size', 0) for f in all_files if f.get('size'))
            status['file_statistics'] = {
                'total_files': len(all_files),
                'total_size': total_size,
                'average_size': round(total_size / len(all_files), 2) if len(all_files) > 0 else 0,
                'latest_modified': max(f.get('modified', '') for f in all_files if f.get('modified'))
            }
        
        return status
    
    def validate_expected_structure(self, project_path: str, 
                                  custom_structure: Optional[Dict] = None) -> Dict[str, Any]:
        """验证项目是否具有预期的文档结构"""
        structure = custom_structure or self.expected_structure
        return self.check_directory_structure(project_path, structure)
    
    def get_validation_summary(self, project_path: str) -> Dict[str, Any]:
        """获取验证结果摘要"""
        status = self.get_generation_status(project_path)
        
        return {
            'project_path': project_path,
            'validation_timestamp': datetime.now().isoformat(),
            'summary': {
                'overall_status': status['overall_status'],
                'completion_percentage': status['generation_progress']['completion_percentage'],
                'docs_initialized': status['docs_directory_exists'],
                'structure_valid': status['structure_validation']['structure_valid'],
                'total_files': status.get('file_statistics', {}).get('total_files', 0)
            },
            'recommendations': self._generate_recommendations(status)
        }
    
    def _generate_recommendations(self, status: Dict[str, Any]) -> List[str]:
        """根据验证状态生成建议"""
        recommendations = []
        
        if not status['docs_directory_exists']:
            recommendations.append("需要初始化docs目录结构")
            return recommendations
        
        completion = status['generation_progress']['completion_percentage']
        
        if completion < 30:
            recommendations.append("建议先完成架构层文档的生成")
        elif completion < 70:
            recommendations.append("继续完善模块层和文件层文档")
        elif completion < 95:
            recommendations.append("补充缺失的文档文件")
        else:
            recommendations.append("文档结构完整，可以进行内容质量检查")
        
        # 检查各层级状态
        for layer, info in status.get('layer_status', {}).items():
            if not info['exists']:
                recommendations.append(f"需要创建{layer}层级目录")
            elif info['completion'] < 0.5:
                recommendations.append(f"{layer}层级文档不完整，建议补充")
        
        return recommendations