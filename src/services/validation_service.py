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
        # 基于16个核心模板系统的预期结构
        self.expected_structure = {
            'docs': {
                'type': 'directory',
                'required': True,
                'children': {
                    'architecture': {
                        'type': 'directory',
                        'required': True,
                        'files': ['overview.md', 'tech-stack.md', 'data-flow.md'],
                        'children': {
                            'diagrams': {
                                'type': 'directory',
                                'required': False,
                                'files': ['system-architecture.md', 'component-diagram.md', 'deployment-diagram.md']
                            }
                        }
                    },
                    'modules': {
                        'type': 'directory',
                        'required': True,
                        'files': ['overview.md', 'module-relations.md', 'dependency-graph.md'],
                        'children': {
                            'connections': {
                                'type': 'directory',
                                'required': False,
                                'files': ['api-services.md', 'auth-database.md']
                            },
                            'modules': {
                                'type': 'directory',
                                'required': False
                            }
                        }
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
                        'files': ['README.md', 'CHANGELOG.md', 'roadmap.md']
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

            # 基于16个核心模板系统的预期文件数量
            expected_count = {
                'architecture': 6,  # 6个架构层模板: overview, tech-stack, data-flow + 3个diagrams
                'modules': 6,  # 6个模块层模板: overview, relations, dependency + connections + modules
                'files': 1,  # 1个文件层综合模板 (summaries目录)
                'project': 3  # 3个项目层模板: README, CHANGELOG, roadmap
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
            recommendations.append("建议先完成架构层文档的生成（6个核心模板）")
        elif completion < 70:
            recommendations.append("继续完善模块层文档（6个模板）和文件层文档（1个综合模板）")
        elif completion < 95:
            recommendations.append("补充缺失的文档文件，完成16个核心模板的生成")
        else:
            recommendations.append("16个核心模板文档结构完整，可以进行内容质量检查")

        # 检查各层级状态
        for layer, info in status.get('layer_status', {}).items():
            if not info['exists']:
                recommendations.append(f"需要创建{layer}层级目录")
            elif info['completion'] < 0.5:
                recommendations.append(f"{layer}层级文档不完整，建议补充")

        return recommendations

    def get_complete_directory_structure(self) -> str:
        """获取使用CodeLens为任意项目生成文档时的标准目录结构"""
        return '''
# CodeLens 16个核心模板系统 - 标准文档目录结构
# 适用于任何使用CodeLens生成文档的项目

任意项目根目录/
├── docs/
│   ├── architecture/                    # 架构层 (6个模板)
│   │   ├── overview.md                  # 项目架构概述
│   │   ├── tech-stack.md               # 技术栈分析  
│   │   ├── data-flow.md                # 数据流设计
│   │   └── diagrams/
│   │       ├── system-architecture.md   # 系统架构图
│   │       ├── component-diagram.md     # 组件关系图
│   │       └── deployment-diagram.md    # 部署架构图
│   │
│   ├── modules/                         # 模块层 (6个模板)
│   │   ├── overview.md                  # 模块总览
│   │   ├── module-relations.md          # 模块关系分析
│   │   ├── dependency-graph.md          # 依赖图谱分析
│   │   ├── connections/                 # 连接关系分析
│   │   │   ├── api-services.md          # API-服务连接关系
│   │   │   ├── auth-database.md         # 认证-数据库连接关系
│   │   │   └── [其他连接关系文档...]
│   │   └── modules/                     # 具体模块文档
│   │       ├── auth/                    # 认证模块
│   │       │   ├── README.md           # 模块主文档
│   │       │   ├── api.md              # API接口文档
│   │       │   └── flow.md             # 业务流程文档
│   │       ├── database/                # 数据库模块
│   │       │   ├── README.md
│   │       │   ├── api.md
│   │       │   └── flow.md
│   │       ├── user-management/         # 用户管理模块
│   │       │   ├── README.md
│   │       │   ├── api.md
│   │       │   └── flow.md
│   │       └── [其他识别的功能模块...]
│   │
│   ├── files/                          # 文件层 (1个综合模板)
│   │   └── summaries/                   # 文件摘要目录
│   │       ├── src/                     # 源码文件摘要 (按项目结构)
│   │       │   ├── main.py.md           # 主程序文件摘要
│   │       │   ├── models/
│   │       │   │   ├── user.py.md       # 用户模型文件摘要
│   │       │   │   ├── auth.py.md       # 认证模型文件摘要
│   │       │   │   └── [其他模型文件摘要...]
│   │       │   ├── controllers/
│   │       │   │   ├── user_controller.py.md
│   │       │   │   ├── auth_controller.py.md
│   │       │   │   └── [其他控制器文件摘要...]
│   │       │   ├── services/
│   │       │   │   ├── user_service.py.md
│   │       │   │   ├── auth_service.py.md
│   │       │   │   └── [其他服务文件摘要...]
│   │       │   ├── utils/
│   │       │   │   ├── database.py.md
│   │       │   │   ├── helpers.py.md
│   │       │   │   └── [其他工具文件摘要...]
│   │       │   └── [按实际项目结构生成...]
│   │       ├── tests/                   # 测试文件摘要
│   │       │   ├── test_user.py.md
│   │       │   ├── test_auth.py.md
│   │       │   └── [其他测试文件摘要...]
│   │       ├── config/                  # 配置文件摘要
│   │       │   ├── database.yml.md
│   │       │   ├── app.json.md
│   │       │   └── [其他配置文件摘要...]
│   │       └── [其他项目文件摘要...]
│   │
│   └── project/                        # 项目层 (3个模板)
│       ├── README.md                   # 项目主文档
│       ├── CHANGELOG.md                # 变更日志
│       ├── roadmap.md                  # 发展路线图
├── [项目实际源码目录结构]
├── README.md                           # 项目根README (可选更新)
└── [其他项目文件...]

## 16个核心模板分布统计
- 📐 Architecture Layer: 6个模板 (37.5%)
  └── 提供系统整体架构视图和技术选型分析
- 🧩 Module Layer: 6个模板 (37.5%)  
  └── 分析功能模块关系和具体模块实现
- 📄 File Layer: 1个综合模板 (6.25%)
  └── 为每个源码文件生成详细摘要文档
- 📊 Project Layer: 3个模板 (18.75%)
  └── 项目管理和对外展示文档
- 📋 Total: 16个核心模板 (100%)

## 文档生成状态等级
- not_initialized: 无docs目录
- not_started: 0% 完成度
- minimal: < 30% 完成度 (< 5个模板)
- partial: 30-70% 完成度 (5-11个模板)  
- mostly_complete: 70-95% 完成度 (11-15个模板)
- complete: >= 95% 完成度 (16个模板)

## 使用说明
这是使用CodeLens为任何项目生成文档时的标准目录结构。
根据项目实际情况，某些目录和文件会动态生成：
- files/summaries/ 会根据项目的实际源码结构生成
- modules/modules/ 会根据识别的功能模块生成
- connections/ 会根据项目的模块连接关系生成
        '''.strip()
