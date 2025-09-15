"""
模块重载器 - 安全地重新加载Python模块
"""

import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Set, Dict, List, Optional, Any
import traceback
from collections import defaultdict

from src.logging import get_logger

class DependencyTracker:
    """模块依赖关系追踪器"""
    
    def __init__(self):
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.logger = get_logger("DependencyTracker", "dependency_analysis")
    
    def track_module(self, module_name: str):
        """追踪模块的依赖关系"""
        if module_name not in sys.modules:
            return
        
        module = sys.modules[module_name]
        if not hasattr(module, '__file__') or not module.__file__:
            return
        
        # 清除旧的依赖关系
        self.clear_dependencies(module_name)
        
        # 分析新的依赖关系
        for name, obj in sys.modules.items():
            if name == module_name:
                continue
            
            if hasattr(obj, '__file__') and obj.__file__:
                if self._is_dependent(module, obj):
                    self.dependencies[module_name].add(name)
                    self.reverse_dependencies[name].add(module_name)
    
    def clear_dependencies(self, module_name: str):
        """清除模块的依赖关系记录"""
        # 清除正向依赖
        for dep in self.dependencies.get(module_name, set()):
            self.reverse_dependencies[dep].discard(module_name)
        self.dependencies[module_name] = set()
        
        # 清除反向依赖
        for rdep in self.reverse_dependencies.get(module_name, set()):
            self.dependencies[rdep].discard(module_name)
        self.reverse_dependencies[module_name] = set()
    
    def _is_dependent(self, module1: Any, module2: Any) -> bool:
        """检查module1是否依赖module2"""
        try:
            if not hasattr(module1, '__file__') or not hasattr(module2, '__file__'):
                return False
            
            file1 = Path(module1.__file__ or '')
            file2 = Path(module2.__file__ or '')
            
            # 检查是否在同一个包内
            if file1.parent == file2.parent:
                return True
            
            # 检查是否是子包关系
            if str(file2.parent) in str(file1.parent):
                return True
            
            return False
        except Exception:
            return False
    
    def get_reload_order(self, module_name: str) -> List[str]:
        """获取重载顺序（依赖的模块先重载）"""
        order = []
        visited = set()
        
        def dfs(name: str):
            if name in visited:
                return
            visited.add(name)
            
            # 先处理依赖
            for dep in self.dependencies.get(name, set()):
                if dep in sys.modules:
                    dfs(dep)
            
            order.append(name)
        
        dfs(module_name)
        return order

class ModuleReloader:
    """模块重载器"""
    
    def __init__(self):
        self.dependency_tracker = DependencyTracker()
        self.logger = get_logger("ModuleReloader", "module_reload")
        self.project_root = Path(__file__).parent.parent.parent
        self.reloadable_prefixes = [
            'src.mcp_tools',
            'src.services', 
            'src.task_engine',
            'src.templates',
            'src.logging'
        ]
    
    def is_reloadable(self, module_name: str) -> bool:
        """检查模块是否可以重载"""
        # 排除系统模块和特殊模块
        if module_name.startswith('__') or module_name in [
            '__main__', '__mp_main__', '_frozen_importlib', '_imp', 
            'sys', 'builtins', 'importlib', 'types', 'threading',
            'asyncio', 'json', 'os', 'pathlib'
        ]:
            return False
        
        # 排除第三方库模块
        if any(module_name.startswith(prefix) for prefix in [
            'mcp.', 'watchdog.', 'concurrent.', '_frozen', '_thread'
        ]):
            return False
        
        # 排除只是包名的模块（如 'src', 'src.mcp_tools'）
        if module_name in ['src', 'src.mcp_tools', 'src.services', 'src.task_engine', 'src.templates', 'src.logging', 'src.hot_reload']:
            return False
        
        # 排除没有具体文件的模块
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if not hasattr(module, '__file__') or not module.__file__:
                return False
            if not module.__file__.endswith('.py'):
                return False
        
        # 只重载项目内的模块
        if any(module_name.startswith(prefix) for prefix in self.reloadable_prefixes):
            return True
        
        # 检查是否是项目文件
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, '__file__') and module.__file__:
                module_path = Path(module.__file__)
                try:
                    module_path.relative_to(self.project_root)
                    return True
                except ValueError:
                    pass
        
        return False
    
    def file_path_to_module_name(self, file_path: str) -> Optional[str]:
        """将文件路径转换为模块名"""
        try:
            file_path = Path(file_path).resolve()
            rel_path = file_path.relative_to(self.project_root)
            
            # 移除.py扩展名
            if rel_path.suffix == '.py':
                rel_path = rel_path.with_suffix('')
            
            # 转换为模块名
            module_name = str(rel_path).replace('/', '.').replace('\\', '.')
            
            # 处理__init__.py
            if module_name.endswith('.__init__'):
                module_name = module_name[:-9]
            
            return module_name
        except (ValueError, OSError) as e:
            self.logger.warning(f"无法将文件路径转换为模块名: {file_path}, 错误: {e}")
            return None
    
    def reload_module_by_path(self, file_path: str) -> bool:
        """根据文件路径重载模块"""
        module_name = self.file_path_to_module_name(file_path)
        if not module_name:
            return False
        
        return self.reload_module(module_name)
    
    def reload_module(self, module_name: str) -> bool:
        """重载指定模块"""
        if not self.is_reloadable(module_name):
            self.logger.debug(f"模块不可重载: {module_name}")
            return False
        
        if module_name not in sys.modules:
            self.logger.debug(f"模块未加载: {module_name}")
            return False
        
        try:
            # 追踪依赖关系
            self.dependency_tracker.track_module(module_name)
            
            # 获取重载顺序
            reload_order = self.dependency_tracker.get_reload_order(module_name)
            
            # 过滤不可重载的模块
            filtered_order = [mod for mod in reload_order if self.is_reloadable(mod)]
            
            self.logger.info(f"重载模块链: {' -> '.join(filtered_order)}")
            
            # 按顺序重载模块
            success = True
            for mod_name in filtered_order:
                if not self._reload_single_module(mod_name):
                    success = False
                    break
            
            return success
            
        except Exception as e:
            self.logger.error(f"重载模块失败: {module_name}, 错误: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _reload_single_module(self, module_name: str) -> bool:
        """重载单个模块"""
        try:
            # 再次检查模块是否可重载
            if not self.is_reloadable(module_name):
                self.logger.debug(f"跳过不可重载模块: {module_name}")
                return True
            
            if module_name not in sys.modules:
                return True
            
            module = sys.modules[module_name]
            
            # 保存模块的重要属性
            old_file = getattr(module, '__file__', None)
            old_name = getattr(module, '__name__', module_name)
            
            self.logger.info(f"重载模块: {module_name}")
            
            # 执行重载
            reloaded_module = importlib.reload(module)
            
            # 验证重载是否成功
            if reloaded_module is not module:
                self.logger.warning(f"重载后模块对象发生变化: {module_name}")
            
            # 更新sys.modules（通常reload会自动更新，但确保一致性）
            sys.modules[module_name] = reloaded_module
            
            self.logger.info(f"✅ 模块重载成功: {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 模块重载失败: {module_name}, 错误: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def get_loaded_project_modules(self) -> List[str]:
        """获取已加载的项目模块列表"""
        modules = []
        for module_name in sys.modules:
            if self.is_reloadable(module_name):
                # 只包含具体的Python文件模块，排除包模块
                module = sys.modules[module_name]
                if hasattr(module, '__file__') and module.__file__ and module.__file__.endswith('.py'):
                    modules.append(module_name)
        return sorted(modules)
    
    def clear_module_cache(self, module_name: str):
        """清除模块缓存"""
        try:
            # 清除__pycache__中的.pyc文件
            if module_name in sys.modules:
                module = sys.modules[module_name]
                if hasattr(module, '__file__') and module.__file__:
                    module_path = Path(module.__file__)
                    cache_dir = module_path.parent / '__pycache__'
                    if cache_dir.exists():
                        pattern = module_path.stem + '*.pyc'
                        for cache_file in cache_dir.glob(pattern):
                            try:
                                cache_file.unlink()
                                self.logger.debug(f"清除缓存文件: {cache_file}")
                            except OSError:
                                pass
            
            # 清除依赖关系记录
            self.dependency_tracker.clear_dependencies(module_name)
            
        except Exception as e:
            self.logger.warning(f"清除模块缓存时出错: {module_name}, 错误: {e}")
    
    def reload_all_project_modules(self) -> Dict[str, bool]:
        """重载所有项目模块"""
        modules = self.get_loaded_project_modules()
        results = {}
        
        self.logger.info(f"重载所有项目模块，共 {len(modules)} 个")
        
        for module_name in modules:
            results[module_name] = self.reload_module(module_name)
        
        success_count = sum(1 for result in results.values() if result)
        self.logger.info(f"重载完成: {success_count}/{len(modules)} 成功")
        
        return results