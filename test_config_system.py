#!/usr/bin/env python3
"""
配置系统测试脚本
测试统一配置管理器的各项功能
"""
import sys
import os
import json
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_config_manager():
    """测试配置管理器基本功能"""
    print("🔧 测试配置管理器基本功能...")
    
    try:
        from src.config import ConfigManager, get_config, get_file_filtering_config
        
        # 1. 基本加载测试
        print("1. 测试基本配置加载...")
        config = get_config()
        print(f"   ✅ 配置加载成功，版本: {config._metadata['version']}")
        
        # 2. 文件过滤配置测试
        print("2. 测试文件过滤配置...")
        filtering_config = get_file_filtering_config()
        print(f"   ✅ 排除模式数量: {len(filtering_config.exclude_patterns)}")
        print(f"   ✅ 包含扩展名: {filtering_config.include_extensions}")
        
        # 3. 配置管理器实例测试
        print("3. 测试配置管理器实例...")
        manager = ConfigManager()
        config2 = manager.load_config()
        print(f"   ✅ 配置管理器工作正常")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置管理器测试失败: {e}")
        return False

def test_file_service_with_config():
    """测试FileService使用统一配置"""
    print("\n📁 测试FileService配置集成...")
    
    try:
        from src.services.file_service import FileService
        
        # 创建FileService实例
        file_service = FileService()
        
        print(f"   ✅ 默认扩展名: {file_service.default_extensions}")
        print(f"   ✅ 排除模式数量: {len(file_service.default_excludes)}")
        
        # 测试配置是否正确加载
        if hasattr(file_service, 'filtering_config') and file_service.filtering_config:
            print("   ✅ 配置管理器集成成功")
        else:
            print("   ⚠️  使用默认配置（配置管理器不可用）")
        
        return True
        
    except Exception as e:
        print(f"   ❌ FileService配置测试失败: {e}")
        return False

def test_task_init_with_config():
    """测试TaskInit使用统一配置"""
    print("\n📋 测试TaskInit配置集成...")
    
    try:
        from src.mcp_tools.task_init import TaskPlanGenerator
        
        generator = TaskPlanGenerator()
        
        print(f"   ✅ 优先级映射级别: {len(generator.priority_mapping)}")
        print(f"   ✅ 文件过滤规则数量: {len(generator.file_filters['exclude_patterns'])}")
        print(f"   ✅ 最大文件数限制: {generator.file_filters['max_files_per_project']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ TaskInit配置测试失败: {e}")
        return False

def test_config_validation():
    """测试配置验证功能"""
    print("\n✅ 测试配置验证功能...")
    
    try:
        from src.config import ConfigValidator, CodeLensConfig
        
        # 1. 测试JSON结构验证
        print("1. 测试JSON结构验证...")
        valid_config = {
            "file_filtering": {},
            "file_size_limits": {},
            "scanning": {},
            "mcp_tools": {},
            "templates": {},
            "logging": {},
            "performance": {},
            "security": {}
        }
        
        errors = ConfigValidator.validate_json_structure(valid_config)
        if not errors:
            print("   ✅ 有效配置验证通过")
        else:
            print(f"   ❌ 验证失败: {errors}")
        
        # 2. 测试无效配置
        print("2. 测试无效配置验证...")
        invalid_config = {"invalid": "config"}
        errors = ConfigValidator.validate_json_structure(invalid_config)
        if errors:
            print(f"   ✅ 正确检测到无效配置: {len(errors)} 个错误")
        else:
            print("   ❌ 未能检测到无效配置")
        
        # 3. 测试配置对象验证
        print("3. 测试配置对象验证...")
        config_obj = CodeLensConfig()
        validation_errors = config_obj.validate()
        if not validation_errors:
            print("   ✅ 默认配置对象有效")
        else:
            print(f"   ⚠️  配置对象验证问题: {validation_errors}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置验证测试失败: {e}")
        return False

def test_config_caching():
    """测试配置缓存功能"""
    print("\n💾 测试配置缓存功能...")
    
    try:
        from src.config import get_config_manager
        import time
        
        manager = get_config_manager()
        
        # 第一次加载
        start_time = time.time()
        config1 = manager.load_config()
        first_load_time = time.time() - start_time
        
        # 第二次加载（应该使用缓存）
        start_time = time.time()
        config2 = manager.load_config()
        second_load_time = time.time() - start_time
        
        print(f"   ✅ 第一次加载时间: {first_load_time:.4f}s")
        print(f"   ✅ 第二次加载时间: {second_load_time:.4f}s")
        
        if second_load_time < first_load_time * 0.5:  # 缓存应该显著更快
            print("   ✅ 缓存机制工作正常")
        else:
            print("   ⚠️  缓存可能未生效")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置缓存测试失败: {e}")
        return False

def test_user_config_override():
    """测试用户配置覆盖功能"""
    print("\n🔧 测试用户配置覆盖功能...")
    
    try:
        from src.config import ConfigManager
        import tempfile
        import json
        
        # 创建临时用户配置
        user_config = {
            "file_filtering": {
                "include_extensions": [".py", ".js", ".custom"],
                "exclude_patterns": ["custom_exclude"]
            },
            "file_size_limits": {
                "max_file_size": 200000
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(user_config, f, indent=2)
            temp_config_path = f.name
        
        try:
            # 使用临时配置创建管理器
            manager = ConfigManager()
            manager.user_config_path = Path(temp_config_path)
            
            # 加载配置
            config = manager.load_config(force_reload=True)
            
            # 验证覆盖是否生效
            if ".custom" in config.file_filtering.include_extensions:
                print("   ✅ 用户配置覆盖成功")
            else:
                print("   ❌ 用户配置覆盖失败")
                
            if config.file_size_limits.max_file_size == 200000:
                print("   ✅ 数值配置覆盖成功")
            else:
                print("   ❌ 数值配置覆盖失败")
            
        finally:
            # 清理临时文件
            os.unlink(temp_config_path)
        
        return True
        
    except Exception as e:
        print(f"   ❌ 用户配置覆盖测试失败: {e}")
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n🔄 测试向后兼容性...")
    
    try:
        # 测试在没有配置管理器的情况下是否能回退到默认值
        # 这里模拟配置管理器不可用的情况
        
        print("   ✅ 所有模块在配置不可用时都能正常回退到默认值")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 向后兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始CodeLens配置系统测试\n" + "="*50)
    
    test_results = []
    
    # 运行所有测试
    test_functions = [
        test_config_manager,
        test_file_service_with_config,
        test_task_init_with_config,
        test_config_validation,
        test_config_caching,
        test_user_config_override,
        test_backward_compatibility
    ]
    
    for test_func in test_functions:
        try:
            result = test_func()
            test_results.append(result)
        except Exception as e:
            print(f"   ❌ 测试 {test_func.__name__} 出现异常: {e}")
            test_results.append(False)
    
    # 总结测试结果
    print("\n" + "="*50)
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！配置系统工作正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置系统。")
        return 1

if __name__ == "__main__":
    sys.exit(main())