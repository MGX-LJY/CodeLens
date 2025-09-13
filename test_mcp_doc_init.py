#!/usr/bin/env python3
"""
CodeLens MCP 服务器文档初始化测试脚本
模拟 Claude Code 的完整文档生成流程
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# 导入MCP工具
from src.mcp_tools.doc_scan import DocScanTool
from src.mcp_tools.template_get import TemplateGetTool
from src.mcp_tools.doc_verify import DocVerifyTool

class DocInitTester:
    """文档初始化测试器 - 模拟Claude Code的工作流程"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.docs_path = self.project_path / "docs"
        
        # 初始化MCP工具
        self.doc_scan = DocScanTool()
        self.template_get = TemplateGetTool()
        self.doc_verify = DocVerifyTool()
        
        print(f"🚀 CodeLens MCP 文档初始化测试")
        print(f"📁 项目路径: {self.project_path}")
        print(f"📄 文档目录: {self.docs_path}")
        print("=" * 60)
    
    def step1_scan_project(self) -> Dict[str, Any]:
        """步骤1: 扫描项目获取完整信息"""
        print("\n📊 步骤1: 扫描项目文件...")
        
        arguments = {
            "project_path": str(self.project_path),
            "include_content": True,
            "config": {
                "file_extensions": [".py", ".md", ".txt", ".json"],
                "max_file_size": 50000,
                "exclude_patterns": ["__pycache__", ".git", "node_modules"]
            }
        }
        
        result = self.doc_scan.execute(arguments)
        
        if result.get("success"):
            scan_data = result["data"]["scan_result"]
            print(f"   ✅ 扫描成功!")
            print(f"   📁 发现文件: {len(scan_data['files'])} 个")
            print(f"   📊 总大小: {scan_data['statistics']['total_size']} 字节")
            print(f"   🏗️ 主要文件: {scan_data['project_info']['main_files']}")
            
            # 显示文件类型分布
            file_types = scan_data['statistics'].get('file_types', {})
            print(f"   📋 文件类型: {file_types}")
            
            return scan_data
        else:
            print(f"   ❌ 扫描失败: {result.get('error')}")
            return {}
    
    def step2_get_templates(self) -> Dict[str, Dict]:
        """步骤2: 获取所有文档模板"""
        print("\n📝 步骤2: 获取文档模板...")
        
        templates = {}
        template_types = ["file_summary", "module_analysis", "architecture", "project_readme"]
        
        for template_type in template_types:
            result = self.template_get.execute({
                "template_name": template_type,
                "format": "with_metadata"
            })
            
            if result.get("success"):
                templates[template_type] = result["data"]
                print(f"   ✅ {template_type}: {result['data']['metadata']['description']}")
            else:
                print(f"   ❌ {template_type}: 获取失败")
        
        print(f"   📝 共获取 {len(templates)} 个模板")
        return templates
    
    def step3_verify_initial_state(self) -> Dict[str, Any]:
        """步骤3: 验证初始文档状态"""
        print("\n🔍 步骤3: 验证初始文档状态...")
        
        result = self.doc_verify.execute({
            "project_path": str(self.project_path),
            "verification_type": "full_status"
        })
        
        if result.get("success"):
            verify_data = result["data"]["verification_result"]
            print(f"   📊 当前状态: {verify_data['overall_status']}")
            print(f"   📁 docs目录存在: {verify_data['docs_directory_exists']}")
            print(f"   💯 完成度: {verify_data['generation_progress']['completion_percentage']}%")
            
            recommendations = result["data"].get("recommendations", [])
            if recommendations:
                print(f"   💡 建议: {', '.join(recommendations)}")
            
            return verify_data
        else:
            print(f"   ❌ 验证失败: {result.get('error')}")
            return {}
    
    def step4_create_docs_structure(self):
        """步骤4: 创建docs目录结构"""
        print("\n🏗️ 步骤4: 创建文档目录结构...")
        
        # 创建标准的docs目录结构
        dirs_to_create = [
            "docs",
            "docs/architecture",
            "docs/architecture/diagrams", 
            "docs/modules",
            "docs/modules/connections",
            "docs/modules/modules",
            "docs/files",
            "docs/files/summaries",
            "docs/project",
            "docs/project/versions"
        ]
        
        for dir_path in dirs_to_create:
            full_path = self.project_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"   📁 创建目录: {dir_path}")
        
        print(f"   ✅ 文档目录结构创建完成")
    
    def step5_generate_project_readme(self, scan_data: Dict, templates: Dict):
        """步骤5: 生成项目README (模拟Claude Code)"""
        print("\n📄 步骤5: 生成项目README...")
        
        if "project_readme" not in templates:
            print("   ❌ 项目README模板不可用")
            return
        
        template_content = templates["project_readme"]["content"]
        
        # 模拟Claude Code分析项目并填充模板
        project_name = scan_data.get("project_info", {}).get("name", "Unknown Project")
        
        # 分析技术栈
        tech_stack = self._analyze_tech_stack(scan_data)
        
        # 分析核心功能
        core_features = self._analyze_core_features(scan_data)
        
        # 填充模板
        readme_content = template_content.format(
            project_name=project_name,
            project_overview=f"{project_name} 是一个基于Python的微信自动化系统，用于文件下载、上传和积分管理。",
            core_features=core_features,
            quick_start="1. 安装依赖: `pip install -r requirements.txt`\n2. 配置文件: 编辑 `config.json`\n3. 运行程序: `python app.py`",
            project_status="🔄 活跃开发中 - v2.3.0",
            tech_architecture=tech_stack,
            usage_examples="参见 docs/project/examples/ 目录下的示例",
            roadmap="参见 docs/project/roadmap.md",
            contribution_guide="欢迎提交Issue和Pull Request",
            license="MIT License"
        )
        
        # 写入文件
        readme_path = self.project_path / "docs" / "project" / "README.md"
        readme_path.write_text(readme_content, encoding='utf-8')
        
        print(f"   ✅ 项目README已生成: {readme_path}")
        print(f"   📄 内容长度: {len(readme_content)} 字符")
    
    def step6_generate_architecture_overview(self, scan_data: Dict, templates: Dict):
        """步骤6: 生成架构概述 (模拟Claude Code)"""
        print("\n🏗️ 步骤6: 生成架构概述...")
        
        if "architecture" not in templates:
            print("   ❌ 架构模板不可用")
            return
        
        template_content = templates["architecture"]["content"]
        
        # 分析项目架构
        components = self._analyze_components(scan_data)
        data_flow = self._analyze_data_flow(scan_data)
        
        # 填充模板
        architecture_content = template_content.format(
            project_overview="微信自动化系统采用模块化架构，包含消息监听、文件下载、上传管理和积分系统等核心组件。",
            tech_stack=self._analyze_tech_stack(scan_data),
            architecture_pattern="事件驱动架构 + 生产者消费者模式",
            core_components=components,
            data_flow=data_flow,
            system_boundaries="- 支持微信消息监听和文件操作\n- 集成多浏览器实例进行并发下载\n- SQLite数据库存储积分和日志",
            deployment_architecture="单机部署，支持多进程和多线程并发处理"
        )
        
        # 写入文件
        arch_path = self.project_path / "docs" / "architecture" / "overview.md"
        arch_path.write_text(architecture_content, encoding='utf-8')
        
        print(f"   ✅ 架构概述已生成: {arch_path}")
        print(f"   📄 内容长度: {len(architecture_content)} 字符")
    
    def step7_generate_file_summaries(self, scan_data: Dict, templates: Dict):
        """步骤7: 生成文件摘要 (模拟Claude Code)"""
        print("\n📄 步骤7: 生成文件摘要...")
        
        if "file_summary" not in templates:
            print("   ❌ 文件摘要模板不可用")
            return
        
        template_content = templates["file_summary"]["content"]
        
        # 选择重要文件生成摘要
        important_files = []
        for file_info in scan_data.get("files", []):
            if (file_info.get("content_available") and 
                file_info.get("size", 0) > 1000 and
                file_info.get("extension") == ".py"):
                important_files.append(file_info)
        
        # 限制处理文件数量
        important_files = important_files[:5]
        
        summaries_dir = self.project_path / "docs" / "files" / "summaries"
        generated_count = 0
        
        for file_info in important_files:
            try:
                # 分析文件内容
                content = file_info.get("content", "")
                filename = file_info.get("name", "unknown.py")
                
                # 简单的代码分析
                imports = self._extract_imports(content)
                functions = self._extract_functions(content)
                classes = self._extract_classes(content)
                
                # 填充模板
                summary_content = template_content.format(
                    filename=filename,
                    function_overview=f"该文件包含 {len(functions)} 个函数和 {len(classes)} 个类，主要负责相关业务逻辑处理。",
                    class_definitions="\n".join([f"- **{cls}**: 核心业务类" for cls in classes[:3]]),
                    function_definitions="\n".join([f"- `{func}()`: 业务处理函数" for func in functions[:5]]),
                    constants="配置相关常量和默认值",
                    imports="\n".join([f"- `{imp}`: {imp}模块" for imp in imports[:5]]),
                    exports="主要导出类和函数",
                    algorithms="业务逻辑算法和数据处理流程",
                    notes="该文件是系统的重要组成部分，负责核心功能实现。"
                )
                
                # 写入文件
                summary_filename = filename.replace('.py', '.py.md')
                summary_path = summaries_dir / summary_filename
                summary_path.write_text(summary_content, encoding='utf-8')
                
                generated_count += 1
                print(f"   ✅ {filename}: 摘要已生成")
                
            except Exception as e:
                print(f"   ❌ {filename}: 生成失败 - {e}")
        
        print(f"   📝 共生成 {generated_count} 个文件摘要")
    
    def step8_verify_final_state(self):
        """步骤8: 验证最终文档状态"""
        print("\n🔍 步骤8: 验证最终文档状态...")
        
        result = self.doc_verify.execute({
            "project_path": str(self.project_path),
            "verification_type": "full_status"
        })
        
        if result.get("success"):
            verify_data = result["data"]["verification_result"]
            print(f"   📊 最终状态: {verify_data['overall_status']}")
            print(f"   📁 docs目录存在: {verify_data['docs_directory_exists']}")
            print(f"   💯 完成度: {verify_data['generation_progress']['completion_percentage']}%")
            
            # 显示统计信息
            total_expected = verify_data['generation_progress']['total_expected']
            total_existing = verify_data['generation_progress']['total_existing']
            print(f"   📈 文档文件: {total_existing}/{total_expected}")
            
            return verify_data
        else:
            print(f"   ❌ 验证失败: {result.get('error')}")
            return {}
    
    def _analyze_tech_stack(self, scan_data: Dict) -> str:
        """分析技术栈"""
        requirements_content = ""
        for file_info in scan_data.get("files", []):
            if file_info.get("name") == "requirements.txt":
                requirements_content = file_info.get("content", "")
                break
        
        if requirements_content:
            deps = [line.split(">=")[0].split("~=")[0].split("==")[0] 
                   for line in requirements_content.strip().split("\n") 
                   if line.strip() and not line.startswith("#")]
            return f"**核心技术栈**:\n- Python 3.7+\n- 主要依赖: {', '.join(deps[:6])}"
        else:
            return "**核心技术栈**:\n- Python 3.7+\n- 微信自动化相关库"
    
    def _analyze_core_features(self, scan_data: Dict) -> str:
        """分析核心功能"""
        return """**核心功能**:
- 🤖 微信消息自动监听和处理
- 📥 智能文件下载管理
- 📤 自动文件上传到指定群组
- 💰 积分系统和下载记录管理
- 🔧 多浏览器实例并发处理
- 📊 下载统计和日志记录"""
    
    def _analyze_components(self, scan_data: Dict) -> str:
        """分析核心组件"""
        return """**核心组件**:
- **WxAutoHandler**: 微信消息监听和处理
- **AutoDownloadManager**: 下载任务管理和分配
- **Uploader**: 文件上传和积分管理
- **PointManager**: 积分系统和数据库管理
- **ErrorHandler**: 错误处理和通知
- **ConfigManager**: 配置管理和热更新"""
    
    def _analyze_data_flow(self, scan_data: Dict) -> str:
        """分析数据流"""
        return """**数据流设计**:
1. 消息监听 → URL提取 → 积分验证
2. 下载任务 → 队列管理 → 浏览器实例分配
3. 文件下载 → 上传处理 → 积分扣除
4. 日志记录 → 统计分析 → 状态报告"""
    
    def _extract_imports(self, content: str) -> list:
        """提取import语句"""
        imports = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                module = line.split()[1].split('.')[0]
                if module not in imports:
                    imports.append(module)
        return imports
    
    def _extract_functions(self, content: str) -> list:
        """提取函数定义"""
        functions = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('def ') and '(' in line:
                func_name = line.split('def ')[1].split('(')[0].strip()
                if not func_name.startswith('_'):  # 忽略私有函数
                    functions.append(func_name)
        return functions
    
    def _extract_classes(self, content: str) -> list:
        """提取类定义"""
        classes = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('class ') and ':' in line:
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes.append(class_name)
        return classes
    
    def run_full_test(self):
        """运行完整的文档初始化测试"""
        start_time = time.time()
        
        try:
            # 步骤1: 扫描项目
            scan_data = self.step1_scan_project()
            if not scan_data:
                return False
            
            # 步骤2: 获取模板
            templates = self.step2_get_templates()
            if not templates:
                return False
            
            # 步骤3: 验证初始状态
            initial_state = self.step3_verify_initial_state()
            
            # 步骤4: 创建目录结构
            self.step4_create_docs_structure()
            
            # 步骤5-7: 生成文档内容
            self.step5_generate_project_readme(scan_data, templates)
            self.step6_generate_architecture_overview(scan_data, templates)
            self.step7_generate_file_summaries(scan_data, templates)
            
            # 步骤8: 验证最终状态
            final_state = self.step8_verify_final_state()
            
            # 总结
            elapsed_time = time.time() - start_time
            print(f"\n🎉 文档初始化测试完成!")
            print(f"⏱️ 耗时: {elapsed_time:.2f} 秒")
            print(f"📁 文档目录: {self.docs_path}")
            
            if final_state.get('docs_directory_exists'):
                completion = final_state['generation_progress']['completion_percentage']
                print(f"💯 完成度: {completion}%")
                
                if completion > 0:
                    print("✅ 文档初始化成功!")
                    return True
            
            return False
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python test_mcp_doc_init.py <project_path>")
        print("示例: python test_mcp_doc_init.py /path/to/wechat-automation-project")
        sys.exit(1)
    
    project_path = sys.argv[1]
    
    if not os.path.exists(project_path):
        print(f"❌ 项目路径不存在: {project_path}")
        sys.exit(1)
    
    tester = DocInitTester(project_path)
    success = tester.run_full_test()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()