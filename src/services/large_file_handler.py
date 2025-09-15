"""
大文件分片处理系统
实现基于AST的智能代码分片，支持多种编程语言的语义完整性保持
"""
import ast
import hashlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Iterator, Union
import logging

# 尝试导入可选依赖
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 导入日志系统
try:
    from ..logging import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda **kwargs: logging.getLogger(__name__)


class ChunkType(Enum):
    """分片类型枚举"""
    CLASS = "class"
    FUNCTION = "function"
    MODULE = "module"
    MIXED = "mixed"
    IMPORT = "import"
    COMMENT = "comment"


class ChunkPriority(Enum):
    """分片优先级"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class SplitStrategy(Enum):
    """分片策略"""
    BY_CLASS = "by_class"
    BY_FUNCTION = "by_function"
    BY_SIZE = "by_size"
    BY_COMPLEXITY = "by_complexity"
    SEMANTIC = "semantic"


@dataclass
class CodeChunk:
    """代码分片数据类"""
    id: str
    content: str
    chunk_type: ChunkType
    language: str
    start_line: int
    end_line: int
    file_path: str
    priority: ChunkPriority = ChunkPriority.NORMAL
    dependencies: Set[str] = field(default_factory=set)
    definitions: Set[str] = field(default_factory=set)
    references: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    complexity_score: float = 0.0
    size_bytes: int = 0
    
    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
        self.size_bytes = len(self.content.encode('utf-8'))
    
    def _generate_id(self) -> str:
        """生成唯一的分片ID"""
        content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:8]
        return f"{self.chunk_type.value}_{self.start_line}_{content_hash}"


@dataclass
class ChunkingResult:
    """分片处理结果"""
    chunks: List[CodeChunk]
    processing_method: str
    success: bool
    total_chunks: int = 0
    total_size: int = 0
    processing_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.total_chunks = len(self.chunks)
        self.total_size = sum(chunk.size_bytes for chunk in self.chunks)


@dataclass 
class DependencyRelation:
    """依赖关系定义"""
    source_chunk_id: str
    target_chunk_id: str
    relation_type: str  # "inheritance", "call", "reference", "import"
    strength: float = 1.0  # 依赖强度 0.0-1.0


class BaseChunker(ABC):
    """基础分片器抽象类"""
    
    def __init__(self, max_chunk_size: int = 2000, min_chunk_size: int = 100):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.logger = get_logger(component=self.__class__.__name__)
    
    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """检查是否支持指定语言"""
        pass
    
    @abstractmethod
    def chunk_code(self, content: str, file_path: str) -> ChunkingResult:
        """分片代码"""
        pass
    
    @abstractmethod
    def analyze_dependencies(self, chunks: List[CodeChunk]) -> List[DependencyRelation]:
        """分析分片间依赖关系"""
        pass
    
    def calculate_complexity_score(self, content: str) -> float:
        """计算代码复杂度评分"""
        # 基础复杂度计算，子类可重写
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        complexity = len(non_empty_lines)
        
        # 简单的关键字权重
        keywords_weights = {
            'if': 1.2, 'elif': 1.1, 'else': 1.0,
            'for': 1.5, 'while': 1.5, 'try': 1.3,
            'except': 1.3, 'finally': 1.1,
            'class': 2.0, 'def': 1.8
        }
        
        for keyword, weight in keywords_weights.items():
            complexity += content.count(keyword) * weight
        
        return complexity


class PythonChunker(BaseChunker):
    """Python代码分片器"""
    
    def __init__(self, max_chunk_size: int = 2000, min_chunk_size: int = 100):
        super().__init__(max_chunk_size, min_chunk_size)
        self.import_statements = []
        self.global_variables = set()
    
    def supports_language(self, language: str) -> bool:
        return language.lower() in ['python', 'py']
    
    def chunk_code(self, content: str, file_path: str) -> ChunkingResult:
        """
        Python代码分片策略：
        1. 首先按类分片
        2. 如果类太大，按类内方法分片
        3. 保持导入语句和全局变量的完整性
        """
        start_time = time.time()
        
        try:
            # 解析AST
            tree = ast.parse(content)
            chunks = []
            
            # 1. 提取模块级导入和全局变量
            module_chunk = self._extract_module_level_content(content, tree, file_path)
            if module_chunk:
                chunks.append(module_chunk)
            
            # 2. 按类分片
            class_chunks = self._chunk_by_classes(content, tree, file_path)
            chunks.extend(class_chunks)
            
            # 3. 处理模块级函数
            function_chunks = self._chunk_module_functions(content, tree, file_path)
            chunks.extend(function_chunks)
            
            # 4. 处理剩余代码
            remaining_chunk = self._handle_remaining_code(content, tree, chunks, file_path)
            if remaining_chunk:
                chunks.append(remaining_chunk)
            
            # 5. 分析并设置依赖关系
            dependencies = self.analyze_dependencies(chunks)
            self._apply_dependencies_to_chunks(chunks, dependencies)
            
            processing_time = time.time() - start_time
            
            return ChunkingResult(
                chunks=chunks,
                processing_method="python_ast_semantic",
                success=True,
                processing_time=processing_time
            )
            
        except SyntaxError as e:
            # 语法错误时降级到基于行的分片
            self.logger.warning(f"Syntax error in {file_path}, falling back to line-based chunking: {e}")
            return self._fallback_line_based_chunking(content, file_path, start_time)
        
        except Exception as e:
            self.logger.error(f"Error chunking Python file {file_path}: {e}")
            return ChunkingResult(
                chunks=[],
                processing_method="failed",
                success=False,
                processing_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    def _extract_module_level_content(self, content: str, tree: ast.AST, file_path: str) -> Optional[CodeChunk]:
        """提取模块级内容（导入、全局变量、模块文档字符串）"""
        lines = content.split('\n')
        module_lines = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # 导入语句
                start_line = node.lineno - 1
                end_line = getattr(node, 'end_lineno', node.lineno) - 1
                module_lines.extend(range(start_line, end_line + 1))
            
            elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                # 全局变量赋值
                if node.lineno <= 50:  # 只考虑文件开头的全局变量
                    start_line = node.lineno - 1
                    end_line = getattr(node, 'end_lineno', node.lineno) - 1
                    module_lines.extend(range(start_line, end_line + 1))
                    self.global_variables.add(node.targets[0].id)
        
        # 添加模块文档字符串
        if (isinstance(tree, ast.Module) and tree.body and 
            isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, ast.Constant)):
            module_lines.extend(range(0, tree.body[0].end_lineno))
        
        if module_lines:
            module_lines = sorted(set(module_lines))
            content_lines = [lines[i] for i in module_lines if i < len(lines)]
            
            if content_lines:
                return CodeChunk(
                    id="",
                    content='\n'.join(content_lines),
                    chunk_type=ChunkType.MODULE,
                    language="python",
                    start_line=min(module_lines) + 1,
                    end_line=max(module_lines) + 1,
                    file_path=file_path,
                    priority=ChunkPriority.HIGH,
                    metadata={
                        'description': 'Module-level imports and global variables',
                        'contains_imports': True
                    }
                )
        
        return None
    
    def _chunk_by_classes(self, content: str, tree: ast.AST, file_path: str) -> List[CodeChunk]:
        """按类分片"""
        chunks = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                start_line = node.lineno - 1
                end_line = getattr(node, 'end_lineno', node.lineno) - 1
                
                class_content = '\n'.join(lines[start_line:end_line + 1])
                
                # 检查类大小是否超过限制
                if len(class_content) > self.max_chunk_size:
                    # 类太大，按方法分片
                    method_chunks = self._chunk_class_methods(node, lines, file_path)
                    chunks.extend(method_chunks)
                else:
                    # 整个类作为一个分片
                    chunk = CodeChunk(
                        id="",
                        content=class_content,
                        chunk_type=ChunkType.CLASS,
                        language="python",
                        start_line=start_line + 1,
                        end_line=end_line + 1,
                        file_path=file_path,
                        complexity_score=self.calculate_complexity_score(class_content),
                        metadata={
                            'class_name': node.name,
                            'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)],
                            'method_count': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                        }
                    )
                    
                    # 分析类定义和引用
                    chunk.definitions.add(node.name)
                    self._extract_references_from_class(node, chunk)
                    
                    chunks.append(chunk)
        
        return chunks
    
    def _chunk_class_methods(self, class_node: ast.ClassDef, lines: List[str], file_path: str) -> List[CodeChunk]:
        """将大类按方法分片"""
        chunks = []
        
        # 1. 类头部分片（类定义和类变量）
        class_start = class_node.lineno - 1
        first_method_line = None
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                first_method_line = node.lineno - 1
                break
        
        if first_method_line is not None:
            header_content = '\n'.join(lines[class_start:first_method_line])
            header_chunk = CodeChunk(
                id="",
                content=header_content,
                chunk_type=ChunkType.CLASS,
                language="python",
                start_line=class_start + 1,
                end_line=first_method_line,
                file_path=file_path,
                metadata={
                    'class_name': class_node.name,
                    'is_class_header': True,
                    'base_classes': [base.id for base in class_node.bases if isinstance(base, ast.Name)]
                }
            )
            header_chunk.definitions.add(class_node.name)
            chunks.append(header_chunk)
        
        # 2. 每个方法作为独立分片
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_start = node.lineno - 1
                method_end = getattr(node, 'end_lineno', node.lineno) - 1
                
                method_content = '\n'.join(lines[method_start:method_end + 1])
                
                method_chunk = CodeChunk(
                    id="",
                    content=method_content,
                    chunk_type=ChunkType.FUNCTION,
                    language="python",
                    start_line=method_start + 1,
                    end_line=method_end + 1,
                    file_path=file_path,
                    complexity_score=self.calculate_complexity_score(method_content),
                    metadata={
                        'function_name': node.name,
                        'class_name': class_node.name,
                        'is_method': True,
                        'is_private': node.name.startswith('_'),
                        'is_special': node.name.startswith('__') and node.name.endswith('__'),
                        'parameter_count': len(node.args.args)
                    }
                )
                
                # 分析方法定义和引用
                method_chunk.definitions.add(f"{class_node.name}.{node.name}")
                self._extract_references_from_function(node, method_chunk)
                
                chunks.append(method_chunk)
        
        return chunks
    
    def _chunk_module_functions(self, content: str, tree: ast.AST, file_path: str) -> List[CodeChunk]:
        """分片模块级函数"""
        chunks = []
        lines = content.split('\n')
        
        # 只处理模块级的函数定义
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno - 1
                end_line = getattr(node, 'end_lineno', node.lineno) - 1
                
                function_content = '\n'.join(lines[start_line:end_line + 1])
                
                chunk = CodeChunk(
                    id="",
                    content=function_content,
                    chunk_type=ChunkType.FUNCTION,
                    language="python",
                    start_line=start_line + 1,
                    end_line=end_line + 1,
                    file_path=file_path,
                    complexity_score=self.calculate_complexity_score(function_content),
                    metadata={
                        'function_name': node.name,
                        'is_module_function': True,
                        'parameter_count': len(node.args.args),
                        'has_decorators': len(node.decorator_list) > 0
                    }
                )
                
                # 分析函数定义和引用
                chunk.definitions.add(node.name)
                self._extract_references_from_function(node, chunk)
                
                chunks.append(chunk)
        
        return chunks
    
    def _handle_remaining_code(self, content: str, tree: ast.AST, existing_chunks: List[CodeChunk], file_path: str) -> Optional[CodeChunk]:
        """处理未被其他分片包含的剩余代码"""
        lines = content.split('\n')
        covered_lines = set()
        
        # 收集已覆盖的行
        for chunk in existing_chunks:
            covered_lines.update(range(chunk.start_line - 1, chunk.end_line))
        
        # 找到未覆盖的行
        uncovered_lines = []
        for i, line in enumerate(lines):
            if i not in covered_lines and line.strip():
                uncovered_lines.append(i)
        
        if uncovered_lines:
            # 创建剩余代码分片
            uncovered_content_lines = [lines[i] for i in uncovered_lines]
            uncovered_content = '\n'.join(uncovered_content_lines)
            
            return CodeChunk(
                id="",
                content=uncovered_content,
                chunk_type=ChunkType.MIXED,
                language="python",
                start_line=min(uncovered_lines) + 1,
                end_line=max(uncovered_lines) + 1,
                file_path=file_path,
                priority=ChunkPriority.LOW,
                metadata={
                    'description': 'Remaining uncategorized code',
                    'line_count': len(uncovered_lines)
                }
            )
        
        return None
    
    def _extract_references_from_class(self, class_node: ast.ClassDef, chunk: CodeChunk):
        """从类中提取引用"""
        for node in ast.walk(class_node):
            if isinstance(node, ast.Name):
                chunk.references.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    chunk.references.add(f"{node.value.id}.{node.attr}")
    
    def _extract_references_from_function(self, func_node: ast.FunctionDef, chunk: CodeChunk):
        """从函数中提取引用"""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Name):
                chunk.references.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    chunk.references.add(f"{node.value.id}.{node.attr}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    chunk.references.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        chunk.references.add(f"{node.func.value.id}.{node.func.attr}")
    
    def analyze_dependencies(self, chunks: List[CodeChunk]) -> List[DependencyRelation]:
        """分析Python分片间的依赖关系"""
        dependencies = []
        
        # 建立定义到分片的映射
        definition_to_chunk = {}
        for chunk in chunks:
            for definition in chunk.definitions:
                definition_to_chunk[definition] = chunk.id
        
        # 分析引用依赖
        for chunk in chunks:
            for reference in chunk.references:
                # 直接引用
                if reference in definition_to_chunk:
                    target_chunk_id = definition_to_chunk[reference]
                    if target_chunk_id != chunk.id:
                        dependencies.append(DependencyRelation(
                            source_chunk_id=chunk.id,
                            target_chunk_id=target_chunk_id,
                            relation_type="reference",
                            strength=0.8
                        ))
                
                # 类方法引用
                if '.' in reference:
                    class_name = reference.split('.')[0]
                    if class_name in definition_to_chunk:
                        target_chunk_id = definition_to_chunk[class_name]
                        if target_chunk_id != chunk.id:
                            dependencies.append(DependencyRelation(
                                source_chunk_id=chunk.id,
                                target_chunk_id=target_chunk_id,
                                relation_type="method_call",
                                strength=0.9
                            ))
        
        # 分析继承依赖
        for chunk in chunks:
            if chunk.chunk_type == ChunkType.CLASS and 'base_classes' in chunk.metadata:
                for base_class in chunk.metadata['base_classes']:
                    if base_class in definition_to_chunk:
                        target_chunk_id = definition_to_chunk[base_class]
                        if target_chunk_id != chunk.id:
                            dependencies.append(DependencyRelation(
                                source_chunk_id=chunk.id,
                                target_chunk_id=target_chunk_id,
                                relation_type="inheritance",
                                strength=1.0
                            ))
        
        return dependencies
    
    def _apply_dependencies_to_chunks(self, chunks: List[CodeChunk], dependencies: List[DependencyRelation]):
        """将依赖关系应用到分片对象上"""
        chunk_map = {chunk.id: chunk for chunk in chunks}
        
        for dep in dependencies:
            if dep.source_chunk_id in chunk_map:
                source_chunk = chunk_map[dep.source_chunk_id]
                source_chunk.dependencies.add(dep.target_chunk_id)
    
    def _fallback_line_based_chunking(self, content: str, file_path: str, start_time: float) -> ChunkingResult:
        """降级到基于行数的分片策略"""
        lines = content.split('\n')
        chunks = []
        
        chunk_size = min(self.max_chunk_size // 50, 100)  # 每个分片约100行
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            
            if chunk_content.strip():
                chunk = CodeChunk(
                    id=f"line_chunk_{i}_{int(time.time() * 1000000)}",
                    content=chunk_content,
                    chunk_type=ChunkType.MIXED,
                    language="python",
                    start_line=i + 1,
                    end_line=min(i + chunk_size, len(lines)),
                    file_path=file_path,
                    priority=ChunkPriority.LOW,
                    metadata={'fallback_method': 'line_based'}
                )
                chunks.append(chunk)
        
        return ChunkingResult(
            chunks=chunks,
            processing_method="python_line_based_fallback",
            success=True,
            processing_time=time.time() - start_time,
            warnings=["Used fallback line-based chunking due to syntax errors"]
        )


class LargeFileHandler:
    """大文件处理器主类"""
    
    def __init__(self):
        self.logger = get_logger(component="LargeFileHandler")
        self.chunkers = {
            'python': PythonChunker()
        }
        self.processing_stats = {
            'total_files_processed': 0,
            'total_chunks_created': 0,
            'total_processing_time': 0.0
        }
    
    def register_chunker(self, language: str, chunker: BaseChunker):
        """注册新的语言分片器"""
        self.chunkers[language] = chunker
        self.logger.info(f"Registered chunker for language: {language}")
    
    def detect_language(self, file_path: str) -> str:
        """检测文件语言"""
        file_ext = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php'
        }
        
        return language_map.get(file_ext, 'unknown')
    
    def should_chunk_file(self, file_path: str, max_size: int = 50000) -> bool:
        """判断文件是否需要分片处理"""
        try:
            file_size = Path(file_path).stat().st_size
            return file_size > max_size
        except Exception:
            return False
    
    def process_large_file(self, file_path: str, content: str) -> ChunkingResult:
        """处理大文件，返回分片结果"""
        start_time = time.time()
        
        # 检测语言
        language = self.detect_language(file_path)
        
        # 获取对应的分片器
        chunker = self.chunkers.get(language)
        if not chunker:
            self.logger.warning(f"No chunker available for language: {language}")
            return self._fallback_size_based_chunking(content, file_path, start_time)
        
        try:
            result = chunker.chunk_code(content, file_path)
            
            # 更新统计信息
            self.processing_stats['total_files_processed'] += 1
            self.processing_stats['total_chunks_created'] += result.total_chunks
            self.processing_stats['total_processing_time'] += result.processing_time
            
            self.logger.info(
                f"Successfully chunked {file_path}: "
                f"{result.total_chunks} chunks, "
                f"{result.processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing large file {file_path}: {e}")
            return self._fallback_size_based_chunking(content, file_path, start_time)
    
    def _fallback_size_based_chunking(self, content: str, file_path: str, start_time: float) -> ChunkingResult:
        """降级到基于大小的分片策略"""
        chunks = []
        chunk_size = 2000  # 2KB per chunk
        
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i:i + chunk_size]
            
            # 尝试在自然边界处切分
            if i + chunk_size < len(content):
                last_newline = chunk_content.rfind('\n')
                if last_newline > chunk_size * 0.7:  # 至少保留70%的内容
                    chunk_content = chunk_content[:last_newline]
            
            chunk = CodeChunk(
                id=f"size_chunk_{i}_{int(time.time() * 1000000)}",
                content=chunk_content,
                chunk_type=ChunkType.MIXED,
                language=self.detect_language(file_path),
                start_line=content[:i].count('\n') + 1,
                end_line=content[:i + len(chunk_content)].count('\n') + 1,
                file_path=file_path,
                priority=ChunkPriority.LOW,
                metadata={'fallback_method': 'size_based'}
            )
            chunks.append(chunk)
        
        return ChunkingResult(
            chunks=chunks,
            processing_method="size_based_fallback",
            success=True,
            processing_time=time.time() - start_time,
            warnings=["Used fallback size-based chunking"]
        )
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        stats = self.processing_stats.copy()
        
        # 添加平均值计算
        if stats['total_files_processed'] > 0:
            stats['avg_chunks_per_file'] = stats['total_chunks_created'] / stats['total_files_processed']
            stats['avg_processing_time'] = stats['total_processing_time'] / stats['total_files_processed']
        else:
            stats['avg_chunks_per_file'] = 0
            stats['avg_processing_time'] = 0
        
        # 添加支持的语言列表
        stats['supported_languages'] = list(self.chunkers.keys())
        
        return stats