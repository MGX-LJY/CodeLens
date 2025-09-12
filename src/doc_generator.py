"""
三层文档生成器主类
实现从文件层 -> 模块层 -> 架构层的文档生成流程
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional

from services.file_service import FileService
from services.ai_service import create_ai_service
from templates.document_templates import TemplateService


class ThreeLayerDocGenerator:
    """三层文档生成器"""
    
    def __init__(self, ai_service_type: str = "mock"):
        self.file_service = FileService()
        self.template_service = TemplateService()
        self.ai_service = create_ai_service(ai_service_type)
        
        self.generated_data = {
            'file_summaries': {},
            'module_analysis': {},
            'architecture_doc': {}
        }
    
    def generate_project_docs(self, project_path: str, output_path: str = None, 
                            config: Dict = None) -> bool:
        """生成项目的三层文档"""
        try:
            # 参数处理
            if output_path is None:
                output_path = os.path.join(project_path, "docs")
            
            if config is None:
                config = self._get_default_config()
            
            print(f"开始为项目生成三层文档: {project_path}")
            print(f"输出目录: {output_path}")
            print("=" * 50)
            
            # 第一步：生成文件层文档
            self._generate_file_layer(project_path, output_path, config)
            print("✓ 文件层文档生成完成")
            
            # 第二步：生成模块层文档
            self._generate_module_layer(project_path, output_path, config)
            print("✓ 模块层文档生成完成")
            
            # 第三步：生成架构层文档
            self._generate_architecture_layer(project_path, output_path, config)
            print("✓ 架构层文档生成完成")
            
            # 生成总结报告
            self._generate_summary_report(project_path, output_path)
            print("✓ 生成总结报告")
            
            print("=" * 50)
            print("三层文档生成完成！")
            
            return True
            
        except Exception as e:
            print(f"文档生成失败: {e}")
            return False
    
    def _generate_file_layer(self, project_path: str, output_path: str, config: Dict):
        """生成文件层文档"""
        print("\n--- 第三层：生成文件文档 ---")
        
        # 扫描源代码文件
        source_files = self.file_service.scan_source_files(
            project_path,
            extensions=config.get('file_extensions', ['.py']),
            exclude_patterns=config.get('exclude_patterns', [])
        )
        
        print(f"找到 {len(source_files)} 个源代码文件")
        
        # 为每个文件生成摘要
        file_summaries = {}
        for i, file_path in enumerate(source_files, 1):
            print(f"  处理文件 {i}/{len(source_files)}: {os.path.basename(file_path)}")
            
            # 读取文件内容
            file_content = self.file_service.read_file_safe(
                file_path, 
                max_size=config.get('max_file_size', 50000)
            )
            
            if file_content is None:
                print(f"    跳过文件: {file_path}")
                continue
            
            # 构建AI提示词
            relative_path = self.file_service.get_relative_path(file_path, project_path)
            prompt = self.template_service.build_file_analysis_prompt(relative_path, file_content)
            
            # 调用AI生成摘要
            summary_data = self.ai_service.generate_file_summary(prompt)
            file_summaries[relative_path] = summary_data
            
            # 写入文件摘要
            summary_path = self.file_service.create_file_summary_path(file_path, project_path, output_path)
            formatted_summary = self.template_service.format_file_summary(**summary_data)
            self._write_file(summary_path, formatted_summary)
        
        self.generated_data['file_summaries'] = file_summaries
    
    def _generate_module_layer(self, project_path: str, output_path: str, config: Dict):
        """生成模块层文档"""
        print("\n--- 第二层：生成模块文档 ---")
        
        # 获取项目结构信息
        directory_structure = self.file_service.scan_directory_structure(project_path)
        
        # 准备文件摘要数据
        file_summaries_text = self._format_file_summaries_for_ai()
        directory_structure_text = self._format_directory_structure(directory_structure)
        
        # 构建模块分析提示词
        prompt = self.template_service.build_module_analysis_prompt(
            directory_structure_text, 
            file_summaries_text
        )
        
        # 调用AI生成模块分析
        module_data = self.ai_service.generate_module_analysis(prompt)
        self.generated_data['module_analysis'] = module_data
        
        # 写入模块文档
        module_overview_path = os.path.join(output_path, "modules", "overview.md")
        formatted_module_doc = self.template_service.format_module_analysis(**module_data)
        self._write_file(module_overview_path, formatted_module_doc)
        
        # 写入模块关系图
        module_relations_path = os.path.join(output_path, "modules", "module-relations.md")
        self._write_file(module_relations_path, module_data.get('module_relations', ''))
    
    def _generate_architecture_layer(self, project_path: str, output_path: str, config: Dict):
        """生成架构层文档"""
        print("\n--- 第一层：生成架构文档 ---")
        
        # 获取项目基础信息
        project_info = self.file_service.get_project_info(project_path)
        project_info_text = self._format_project_info(project_info)
        
        # 准备模块分析数据
        module_analysis_text = self._format_module_analysis_for_ai()
        
        # 构建架构分析提示词
        prompt = self.template_service.build_architecture_analysis_prompt(
            project_info_text,
            module_analysis_text
        )
        
        # 调用AI生成架构文档
        arch_data = self.ai_service.generate_architecture_doc(prompt)
        self.generated_data['architecture_doc'] = arch_data
        
        # 写入架构文档
        arch_overview_path = os.path.join(output_path, "architecture", "overview.md")
        formatted_arch_doc = self.template_service.format_architecture_doc(**arch_data)
        self._write_file(arch_overview_path, formatted_arch_doc)
        
        # 写入各个架构子文档
        arch_docs = {
            "tech-stack.md": arch_data.get('tech_stack', ''),
            "data-flow.md": arch_data.get('data_flow', ''),
            "diagrams/system-architecture.md": arch_data.get('project_overview', ''),
            "diagrams/component-diagram.md": arch_data.get('core_components', ''),
            "diagrams/deployment-diagram.md": arch_data.get('deployment_architecture', '')
        }
        
        for filename, content in arch_docs.items():
            file_path = os.path.join(output_path, "architecture", filename)
            self._write_file(file_path, content)
    
    def _generate_summary_report(self, project_path: str, output_path: str):
        """生成总结报告"""
        project_name = os.path.basename(project_path)
        file_count = len(self.generated_data['file_summaries'])
        
        report = f"""# {project_name} 文档生成报告

## 生成统计
- 项目路径: {project_path}
- 分析文件数量: {file_count}
- 生成时间: {self._get_current_time()}

## 生成内容
### 第三层：文件文档
- 生成了 {file_count} 个文件的摘要文档
- 位置: docs/files/summaries/

### 第二层：模块文档  
- 生成了模块总览和关系分析
- 位置: docs/modules/

### 第一层：架构文档
- 生成了系统架构概述和技术分析
- 位置: docs/architecture/

## 使用方法
1. 查看 `docs/architecture/overview.md` 了解整体架构
2. 查看 `docs/modules/overview.md` 了解模块结构
3. 查看 `docs/files/summaries/` 了解具体文件功能

---
*由 CodeLens 三层文档生成器自动生成*
"""
        
        report_path = os.path.join(output_path, "generation-report.md")
        self._write_file(report_path, report)
    
    def _format_file_summaries_for_ai(self) -> str:
        """格式化文件摘要供AI分析使用"""
        summaries = []
        for file_path, summary_data in self.generated_data['file_summaries'].items():
            summary_text = f"""
文件: {file_path}
功能: {summary_data.get('function_overview', '')}
主要类: {summary_data.get('class_definitions', '')}
主要函数: {summary_data.get('function_definitions', '')}
导入模块: {summary_data.get('imports', '')}
"""
            summaries.append(summary_text)
        
        return "\n".join(summaries)
    
    def _format_directory_structure(self, structure: Dict) -> str:
        """格式化目录结构"""
        def format_tree(node, indent=0):
            result = "  " * indent + f"- {node['name']}\n"
            for child in node.get('children', []):
                result += format_tree(child, indent + 1)
            return result
        
        return format_tree(structure)
    
    def _format_project_info(self, project_info: Dict) -> str:
        """格式化项目信息"""
        return f"""
项目名称: {project_info['name']}
项目路径: {project_info['path']}
主要文件: {', '.join(project_info.get('main_files', []))}
配置文件: {project_info.get('config_files', {})}
"""
    
    def _format_module_analysis_for_ai(self) -> str:
        """格式化模块分析数据供AI使用"""
        module_data = self.generated_data['module_analysis']
        return f"""
识别的模块: {module_data.get('identified_modules', '')}
模块详情: {module_data.get('module_details', '')}
模块关系: {module_data.get('module_relations', '')}
"""
    
    def _write_file(self, file_path: str, content: str):
        """写入文件，确保目录存在"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'file_extensions': ['.py'],
            'exclude_patterns': [
                '__pycache__', '.git', 'node_modules', '.idea',
                '.vscode', 'venv', 'env', '.env'
            ],
            'max_file_size': 50000,
            'ai_service_type': 'mock'
        }
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")