#!/usr/bin/env python3
"""
CodeLens 配置系统使用示例
演示各种配置场景和API用法
"""
import sys
import os
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def example_basic_usage():
    """基本配置使用示例"""
    print("📋 基本配置使用示例")
    print("-" * 40)
    
    try:
        from src.config import get_config, get_file_filtering_config, get_tool_config
        
        # 1. 获取完整配置
        config = get_config()
        print(f"✅ 配置版本: {config._metadata['version']}")
        print(f"✅ 支持的文件扩展名: {config.file_filtering.include_extensions}")
        
        # 2. 获取特定配置节
        filtering_config = get_file_filtering_config()
        print(f"✅ 排除模式数量: {len(filtering_config.exclude_patterns)}")
        
        # 3. 获取工具配置
        
        # 4. 测试文件过滤
        test_files = ["main.py", "__pycache__/test.pyc", "node_modules/lib.js", "src/model.py"]
        for file_path in test_files:
            should_include = filtering_config.should_include_file(file_path)
            status = "✅ 包含" if should_include else "❌ 排除"
            print(f"   {status}: {file_path}")
        
    except Exception as e:
        print(f"❌ 基本配置示例失败: {e}")
    
    print()

def example_file_service_integration():
    """FileService 配置集成示例"""
    print("📁 FileService 配置集成示例")
    print("-" * 40)
    
    try:
        from src.services.file_service import FileService
        
        # 创建FileService实例（会自动加载配置）
        file_service = FileService()
        
        print(f"✅ 默认扩展名: {file_service.default_extensions}")
        print(f"✅ 排除模式数量: {len(file_service.default_excludes)}")
        
        # 检查配置来源
        if hasattr(file_service, 'filtering_config') and file_service.filtering_config:
            print("✅ 使用统一配置管理器")
        else:
            print("⚠️  使用默认配置（向后兼容）")
        
        # 测试大文件处理配置
        if file_service.enable_large_file_chunking:
            print("✅ 大文件分片处理已启用")
        else:
            print("❌ 大文件分片处理未启用")
        
    except Exception as e:
        print(f"❌ FileService 集成示例失败: {e}")
    
    print()

def example_custom_config():
    """自定义配置示例"""
    print("🔧 自定义配置示例")
    print("-" * 40)
    
    try:
        from src.config import ConfigManager
        import tempfile
        
        # 创建自定义配置
        custom_config = {
            "file_filtering": {
                "include_extensions": [".py", ".js", ".custom"],
                "exclude_patterns": ["my_custom_exclude"],
                "smart_filtering": {
                    "max_files_per_project": 30
                }
            },
            "file_size_limits": {
                "max_file_size": 150000,
                "large_file_threshold": 60000
            }
        }
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(custom_config, f, indent=2)
            temp_config_path = f.name
        
        try:
            # 使用自定义配置
            manager = ConfigManager()
            manager.user_config_path = Path(temp_config_path)
            
            config = manager.load_config(force_reload=True)
            
            print(f"✅ 自定义扩展名: {config.file_filtering.include_extensions}")
            print(f"✅ 自定义最大文件大小: {config.file_size_limits.max_file_size}")
            print(f"✅ 自定义最大文件数: {config.file_filtering.smart_filtering.get('max_files_per_project', 'N/A')}")
            
        finally:
            # 清理临时文件
            os.unlink(temp_config_path)
        
    except Exception as e:
        print(f"❌ 自定义配置示例失败: {e}")
    
    print()

def example_config_validation():
    """配置验证示例"""
    print("✅ 配置验证示例")
    print("-" * 40)
    
    try:
        from src.config import ConfigValidator, CodeLensConfig
        
        # 1. 验证有效配置
        valid_config = {
            "file_filtering": {"include_extensions": [".py"]},
            "file_size_limits": {"min_file_size": 50, "max_file_size": 100000},
            "scanning": {},
            "mcp_tools": {},
            "templates": {},
            "logging": {},
            "performance": {},
            "security": {}
        }
        
        errors = ConfigValidator.validate_json_structure(valid_config)
        if not errors:
            print("✅ 有效配置验证通过")
        else:
            print(f"❌ 验证失败: {errors}")
        
        # 2. 验证无效配置
        invalid_config = {
            "file_size_limits": {
                "min_file_size": 1000,
                "max_file_size": 500  # 错误：min > max
            }
        }
        
        range_errors = ConfigValidator.validate_numeric_ranges(invalid_config)
        if range_errors:
            print(f"✅ 正确检测到数值范围错误: {range_errors}")
        
        # 3. 验证配置对象
        config_obj = CodeLensConfig()
        validation_errors = config_obj.validate()
        if not validation_errors:
            print("✅ 默认配置对象验证通过")
        else:
            print(f"⚠️  配置对象验证问题: {validation_errors}")
        
    except Exception as e:
        print(f"❌ 配置验证示例失败: {e}")
    
    print()

def example_performance_monitoring():
    """性能监控示例"""
    print("🚀 性能监控示例")
    print("-" * 40)
    
    try:
        from src.config import get_config_manager
        import time
        
        manager = get_config_manager()
        
        # 测试配置加载性能
        times = []
        for i in range(5):
            start = time.time()
            config = manager.load_config()
            end = time.time()
            times.append(end - start)
            print(f"   第{i+1}次加载: {(end-start)*1000:.2f}ms")
        
        avg_time = sum(times) / len(times)
        print(f"✅ 平均加载时间: {avg_time*1000:.2f}ms")
        
        # 检查缓存效果
        if times[1] < times[0] * 0.8:
            print("✅ 缓存机制工作良好")
        else:
            print("⚠️  缓存可能需要优化")
        
    except Exception as e:
        print(f"❌ 性能监控示例失败: {e}")
    
    print()

def example_task_init_integration():
    """TaskInit 配置集成示例"""
    print("📋 TaskInit 配置集成示例")
    print("-" * 40)
    
    try:
        from src.mcp_tools.task_init import TaskPlanGenerator
        
        generator = TaskPlanGenerator()
        
        print(f"✅ 优先级映射: {list(generator.priority_mapping.keys())}")
        print(f"✅ 高优先级文件: {generator.priority_mapping['high']}")
        print(f"✅ 排除模式数量: {len(generator.file_filters['exclude_patterns'])}")
        print(f"✅ 最大文件数限制: {generator.file_filters['max_files_per_project']}")
        print(f"✅ 最小文件大小: {generator.file_filters['min_file_size']} bytes")
        
        # 测试文件重要性评分
        test_files = ["main.py", "utils.py", "test_helper.py", "config.py"]
        for file_path in test_files:
            # 这里可以调用内部方法测试文件评分逻辑
            print(f"   📄 {file_path}")
        
    except Exception as e:
        print(f"❌ TaskInit 集成示例失败: {e}")
    
    print()

def example_environment_specific_configs():
    """环境特定配置示例"""
    print("🌍 环境特定配置示例")
    print("-" * 40)
    
    config_examples = {
        "development": "examples/config_examples/development_config.json",
        "production": "examples/config_examples/production_config.json", 
        "large_project": "examples/config_examples/large_project_config.json"
    }
    
    for env, config_path in config_examples.items():
        full_path = Path(__file__).parent.parent / config_path
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                metadata = config_data.get('_metadata', {})
                file_filtering = config_data.get('file_filtering', {})
                
                print(f"📝 {env.upper()} 环境:")
                print(f"   描述: {metadata.get('description', 'N/A')}")
                print(f"   最大文件数: {file_filtering.get('smart_filtering', {}).get('max_files_per_project', 'N/A')}")
                print(f"   支持扩展名: {len(file_filtering.get('include_extensions', []))}")
                
            except Exception as e:
                print(f"❌ 读取 {env} 配置失败: {e}")
        else:
            print(f"⚠️  {env} 配置文件不存在: {full_path}")
    
    print()

def main():
    """主函数：运行所有示例"""
    print("🚀 CodeLens 配置系统使用示例")
    print("=" * 50)
    print()
    
    examples = [
        example_basic_usage,
        example_file_service_integration,
        example_task_init_integration,
        example_custom_config,
        example_config_validation,
        example_performance_monitoring,
        example_environment_specific_configs
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ 示例 {example_func.__name__} 执行失败: {e}")
            print()
    
    print("=" * 50)
    print("🎉 所有配置示例执行完成！")
    print("\n💡 更多信息请参考:")
    print("   - 配置指南: docs/configuration_guide.md") 
    print("   - 配置示例: examples/config_examples/")
    print("   - 默认配置: src/config/default_config.json")

if __name__ == "__main__":
    main()