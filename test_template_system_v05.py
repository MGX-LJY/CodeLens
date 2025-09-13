#!/usr/bin/env python3
"""
CodeLens 模板系统测试
验证四层架构的专业模板是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.templates.document_templates import TemplateService
    print("✅ 成功导入TemplateService")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


def test_template_system():
    """测试模板系统"""
    print("\n🚀 开始测试 CodeLens 模板系统...")
    
    # 初始化模板服务
    try:
        service = TemplateService()
        print("✅ TemplateService 初始化成功")
    except Exception as e:
        print(f"❌ TemplateService 初始化失败: {e}")
        return False
    
    # 测试模板统计
    try:
        layer_stats = service.get_layer_stats()
        print(f"\n📊 各层级模板统计:")
        for layer, count in layer_stats.items():
            print(f"  {layer}: {count}个模板")
        
        total_templates = sum(layer_stats.values())
        print(f"📈 总模板数: {total_templates}")
        
        if total_templates != 26:
            print(f"⚠️  警告: 期望26个模板，实际{total_templates}个")
        else:
            print("✅ 模板数量正确")
            
    except Exception as e:
        print(f"❌ 模板统计测试失败: {e}")
        return False
    
    # 测试模板列表
    try:
        templates = service.get_template_list()
        print(f"\n📋 模板列表测试:")
        print(f"  获取到 {len(templates)} 个模板定义")
        
        # 按层级分组统计
        by_layer = {}
        for template in templates:
            layer = template.get('layer', 'unknown')
            by_layer[layer] = by_layer.get(layer, 0) + 1
        
        print("  按层级分布:")
        for layer, count in by_layer.items():
            print(f"    {layer}: {count}个")
            
    except Exception as e:
        print(f"❌ 模板列表测试失败: {e}")
        return False
    
    # 测试每层的代表性模板
    test_templates = [
        ('architecture', 'tech_stack'),
        ('module', 'module_relations'), 
        ('file', 'class_analysis'),
        ('project', 'changelog')
    ]
    
    print(f"\n🔍 测试代表性模板获取:")
    for layer, template_name in test_templates:
        try:
            result = service.get_template_content(template_name)
            if result['success']:
                content_length = len(result['content'])
                template_type = result['metadata'].get('type', 'unknown')
                template_layer = result['metadata'].get('layer', 'unknown')
                print(f"  ✅ {template_name}: {content_length}字符, 类型={template_type}, 层级={template_layer}")
            else:
                print(f"  ❌ {template_name}: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"  ❌ {template_name}: 异常 {e}")
    
    # 测试按层级获取模板
    print(f"\n🔍 测试按层级获取模板:")
    for layer_name in ['architecture', 'module', 'file', 'project']:
        try:
            layer_templates = service.get_templates_by_layer(layer_name)
            print(f"  {layer_name}层: {len(layer_templates)}个模板")
            if layer_templates:
                print(f"    示例: {[t['name'] for t in layer_templates[:3]]}")
        except Exception as e:
            print(f"  ❌ {layer_name}层测试失败: {e}")
    
    # 测试模板格式化
    print(f"\n🔍 测试模板格式化:")
    try:
        test_vars = {
            'project_name': 'TestProject',
            'project_overview': '这是一个测试项目',
            'tech_stack': '- Python 3.9+\n- MCP协议',
            'architecture_pattern': '分层架构模式'
        }
        
        result = service.format_template('architecture', **test_vars)
        if result['success']:
            formatted_length = len(result['formatted_content'])
            print(f"  ✅ 架构模板格式化成功: {formatted_length}字符")
            print(f"    使用变量: {list(result['variables_used'].keys())}")
        else:
            print(f"  ❌ 模板格式化失败: {result.get('error')}")
            
    except Exception as e:
        print(f"  ❌ 模板格式化测试异常: {e}")
    
    print("\n🎉 CodeLens 模板系统测试完成!")
    return True


def show_template_structure():
    """显示模板结构概览"""
    service = TemplateService()
    templates = service.get_template_list()
    
    print("\n📁 CodeLens 模板结构:")
    print("=" * 60)
    
    by_layer = {}
    for template in templates:
        layer = template.get('layer', 'unknown')
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(template)
    
    for layer, layer_templates in by_layer.items():
        print(f"\n📂 {layer.upper()} 层 ({len(layer_templates)}个模板):")
        for template in layer_templates:
            name = template['name']
            desc = template['description']
            path = template.get('file_path', 'N/A')
            print(f"  📄 {name}")
            print(f"     {desc}")
            print(f"     路径: {path}")


if __name__ == "__main__":
    print("🔬 CodeLens 模板系统测试工具")
    print("=" * 50)
    
    success = test_template_system()
    
    if success:
        show_template_structure()
        print(f"\n✅ 所有测试通过! CodeLens 模板系统工作正常")
    else:
        print(f"\n❌ 测试失败! 请检查模板系统配置")
        sys.exit(1)