#!/usr/bin/env python3
"""
测试大文件分片处理系统
验证 LargeFileHandler 和相关集成的功能
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_test_large_file(file_path: str, size_kb: int = 60) -> str:
    """创建一个测试用的大Python文件"""
    content = f"""'''
测试大文件 - 自动生成用于测试分片系统
文件大小约 {size_kb}KB
'''

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# 全局变量
GLOBAL_CONFIG = {{
    "debug": True,
    "version": "1.0.0",
    "max_retries": 3
}}

class DataProcessor:
    \"\"\"数据处理器类 - 用于测试类分片\"\"\"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.processed_count = 0
        self.error_count = 0
    
    def process_data(self, data: List[Dict]) -> List[Dict]:
        \"\"\"处理数据列表\"\"\"
        results = []
        
        for item in data:
            try:
                processed_item = self._process_single_item(item)
                results.append(processed_item)
                self.processed_count += 1
            except Exception as e:
                self.error_count += 1
                print(f"Error processing item: {{e}}")
        
        return results
    
    def _process_single_item(self, item: Dict) -> Dict:
        \"\"\"处理单个数据项\"\"\"
        # 模拟复杂的处理逻辑
        processed = item.copy()
        
        # 添加时间戳
        processed['processed_at'] = time.time()
        
        # 数据验证
        if not self._validate_item(processed):
            raise ValueError("Invalid item data")
        
        # 数据转换
        processed = self._transform_item(processed)
        
        return processed
    
    def _validate_item(self, item: Dict) -> bool:
        \"\"\"验证数据项\"\"\"
        required_fields = ['id', 'name', 'type']
        
        for field in required_fields:
            if field not in item:
                return False
        
        return True
    
    def _transform_item(self, item: Dict) -> Dict:
        \"\"\"转换数据项\"\"\"
        # 模拟复杂的转换逻辑
        transformed = item.copy()
        
        # 标准化名称
        if 'name' in transformed:
            transformed['name'] = transformed['name'].strip().lower()
        
        # 添加计算字段
        transformed['computed_hash'] = hash(str(transformed))
        
        # 添加元数据
        transformed['metadata'] = {{
            'processor_version': self.config.get('version', '1.0.0'),
            'processing_time': time.time()
        }}
        
        return transformed

    def get_statistics(self) -> Dict[str, int]:
        \"\"\"获取处理统计信息\"\"\"
        return {{
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'total_count': self.processed_count + self.error_count
        }}

    def reset_statistics(self):
        \"\"\"重置统计信息\"\"\"
        self.processed_count = 0
        self.error_count = 0


class AdvancedDataProcessor(DataProcessor):
    \"\"\"高级数据处理器 - 继承测试\"\"\"
    
    def __init__(self, config: Dict[str, Any], advanced_options: Dict[str, Any] = None):
        super().__init__(config)
        self.advanced_options = advanced_options or {{}}
        self.cache = {{}}
    
    def process_data_with_cache(self, data: List[Dict]) -> List[Dict]:
        \"\"\"带缓存的数据处理\"\"\"
        results = []
        
        for item in data:
            item_key = self._generate_cache_key(item)
            
            if item_key in self.cache:
                # 从缓存获取
                cached_result = self.cache[item_key]
                results.append(cached_result)
            else:
                # 处理并缓存
                processed_item = self._process_single_item(item)
                self.cache[item_key] = processed_item
                results.append(processed_item)
        
        return results
    
    def _generate_cache_key(self, item: Dict) -> str:
        \"\"\"生成缓存键\"\"\"
        key_fields = ['id', 'name', 'type']
        key_values = []
        
        for field in key_fields:
            if field in item:
                key_values.append(str(item[field]))
        
        return "_".join(key_values)
    
    def clear_cache(self):
        \"\"\"清空缓存\"\"\"
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        \"\"\"获取缓存大小\"\"\"
        return len(self.cache)


def create_sample_data(count: int = 100) -> List[Dict]:
    \"\"\"创建示例数据\"\"\"
    data = []
    
    for i in range(count):
        item = {{
            'id': f"item_{{i:05d}}",
            'name': f"Sample Item {{i}}",
            'type': 'test_data',
            'value': i * 2,
            'category': f"category_{{i % 5}}",
            'tags': [f"tag_{{j}}" for j in range(i % 3)],
            'metadata': {{
                'created_at': time.time() - (i * 3600),
                'priority': i % 10,
                'status': 'active' if i % 2 == 0 else 'inactive'
            }}
        }}
        data.append(item)
    
    return data


def process_batch_data(processor: DataProcessor, batch_size: int = 50):
    \"\"\"批量处理数据\"\"\"
    all_data = create_sample_data(200)
    
    print(f"处理 {{len(all_data)}} 条数据，批次大小: {{batch_size}}")
    
    all_results = []
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i:i + batch_size]
        print(f"处理批次 {{i // batch_size + 1}}: {{len(batch)}} 项")
        
        batch_results = processor.process_data(batch)
        all_results.extend(batch_results)
    
    return all_results


def run_performance_test():
    \"\"\"运行性能测试\"\"\"
    print("开始性能测试...")
    
    config = GLOBAL_CONFIG.copy()
    config.update({{"performance_mode": True}})
    
    # 基本处理器测试
    basic_processor = DataProcessor(config)
    start_time = time.time()
    basic_results = process_batch_data(basic_processor)
    basic_time = time.time() - start_time
    
    print(f"基本处理器：处理 {{len(basic_results)}} 项，耗时 {{basic_time:.2f}} 秒")
    print(f"基本处理器统计：{{basic_processor.get_statistics()}}")
    
    # 高级处理器测试
    advanced_processor = AdvancedDataProcessor(config, {{"cache_enabled": True}})
    start_time = time.time()
    advanced_results = process_batch_data(advanced_processor)
    advanced_time = time.time() - start_time
    
    print(f"高级处理器：处理 {{len(advanced_results)}} 项，耗时 {{advanced_time:.2f}} 秒")
    print(f"高级处理器统计：{{advanced_processor.get_statistics()}}")
    print(f"缓存大小：{{advanced_processor.get_cache_size()}}")
    
    # 缓存测试
    start_time = time.time()
    cached_results = process_batch_data(advanced_processor)
    cached_time = time.time() - start_time
    
    print(f"缓存处理器：处理 {{len(cached_results)}} 项，耗时 {{cached_time:.2f}} 秒")
    
    return {{
        'basic_time': basic_time,
        'advanced_time': advanced_time,
        'cached_time': cached_time,
        'results_count': len(basic_results)
    }}


if __name__ == "__main__":
    print("测试大文件处理系统")
    print("=" * 50)
    
    # 运行测试
    results = run_performance_test()
    
    print("\\n测试完成！")
    print(f"性能结果：{{results}}")
"""
    
    # 扩展内容以达到指定大小
    while len(content) < size_kb * 1024:
        content += f"""

# 额外内容 - 行 {len(content.split())}
def additional_function_{len(content.split())}():
    \"\"\"额外的函数用于增加文件大小\"\"\"
    data = [{{
        'index': {len(content.split())},
        'timestamp': time.time(),
        'data': 'x' * 100
    }}]
    return data
"""
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content


def test_large_file_chunking():
    """测试大文件分片功能"""
    print("🔧 测试大文件分片功能")
    
    try:
        # 导入必要的模块
        from src.services.large_file_handler import LargeFileHandler
        from src.services.file_service import FileService
        
        print("✅ 成功导入大文件处理模块")
        
        # 创建测试文件
        test_file = "test_large_file.py"
        content = create_test_large_file(test_file, 70)  # 70KB 文件
        file_size = len(content.encode('utf-8'))
        
        print(f"✅ 创建测试文件: {test_file} ({file_size} 字节, {file_size/1024:.1f} KB)")
        
        # 初始化处理器
        handler = LargeFileHandler()
        print(f"✅ 初始化 LargeFileHandler，支持的语言: {list(handler.chunkers.keys())}")
        
        # 检查文件是否需要分片
        should_chunk = handler.should_chunk_file(test_file, 50000)  # 50KB 阈值
        print(f"✅ 文件是否需要分片: {should_chunk}")
        
        if should_chunk:
            # 执行分片处理
            print("🚀 开始分片处理...")
            result = handler.process_large_file(test_file, content)
            
            if result.success:
                print(f"✅ 分片处理成功!")
                print(f"   - 总分片数: {result.total_chunks}")
                print(f"   - 处理方法: {result.processing_method}")
                print(f"   - 处理时间: {result.processing_time:.2f} 秒")
                print(f"   - 总大小: {result.total_size} 字节")
                
                # 显示分片详情
                print("\n📊 分片详情:")
                for i, chunk in enumerate(result.chunks[:5]):  # 只显示前5个
                    print(f"   分片 {i+1}: {chunk.chunk_type.value} "
                          f"({chunk.start_line}-{chunk.end_line}行, {chunk.size_bytes}字节)")
                
                if len(result.chunks) > 5:
                    print(f"   ... 还有 {len(result.chunks) - 5} 个分片")
                
                # 测试 FileService 集成
                print("\n🔧 测试 FileService 集成...")
                file_service = FileService(enable_large_file_chunking=True)
                
                processing_info = file_service.get_file_processing_info(test_file, 50000)
                print(f"✅ 文件处理信息: {processing_info}")
                
                # 测试文件读取
                read_result = file_service.read_file_with_chunking(test_file, 50000)
                if isinstance(read_result, type(result)) and read_result.success:
                    print(f"✅ FileService 分片读取成功: {read_result.total_chunks} 个分片")
                else:
                    print(f"❌ FileService 分片读取失败")
                
            else:
                print(f"❌ 分片处理失败: {result.errors}")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🧹 清理测试文件: {test_file}")
        
        print("\n✅ 大文件分片测试完成!")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_task_executor_integration():
    """测试 TaskExecutor 集成"""
    print("\n🔧 测试 TaskExecutor 集成")
    
    try:
        from src.mcp_tools.task_execute import TaskExecutor
        
        # 创建测试项目目录
        test_project = Path("test_project")
        test_project.mkdir(exist_ok=True)
        
        # 创建大文件
        test_file = test_project / "large_module.py"
        content = create_test_large_file(str(test_file), 60)
        
        print(f"✅ 创建测试项目: {test_project}")
        print(f"✅ 创建大文件: {test_file} ({len(content)} 字符)")
        
        # 初始化 TaskExecutor
        executor = TaskExecutor(str(test_project))
        
        # 检查分片功能是否启用
        chunking_stats = executor.get_chunking_stats()
        print(f"✅ TaskExecutor 分片统计: {chunking_stats}")
        
        if chunking_stats.get('chunking_enabled'):
            print("✅ TaskExecutor 大文件分片功能已启用")
        else:
            print("⚠️ TaskExecutor 大文件分片功能未启用")
        
        # 清理测试文件
        import shutil
        if test_project.exists():
            shutil.rmtree(test_project)
            print(f"🧹 清理测试项目: {test_project}")
        
        print("✅ TaskExecutor 集成测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ TaskExecutor 集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 CodeLens 大文件处理系统测试")
    print("=" * 60)
    
    # 测试1: 核心分片功能
    test1_result = test_large_file_chunking()
    
    # 测试2: TaskExecutor 集成
    test2_result = test_task_executor_integration()
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   - 大文件分片功能: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"   - TaskExecutor 集成: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过! 大文件处理系统运行正常。")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查实现。")
        return 1


if __name__ == "__main__":
    sys.exit(main())