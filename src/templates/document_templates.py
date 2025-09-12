"""
文档模板服务：提供标准化的文档模板
"""


class DocumentTemplates:
    """文档模板集合"""
    
    # 文件摘要模板
    FILE_SUMMARY_TEMPLATE = """# 文件摘要：{filename}

## 功能概述
{function_overview}

## 主要组件

### 类定义
{class_definitions}

### 函数定义
{function_definitions}

### 重要常量和配置
{constants}

## 依赖关系

### 导入的模块
{imports}

### 对外接口
{exports}

## 关键算法和逻辑
{algorithms}

## 备注
{notes}
"""

    # 模块分析模板
    MODULE_ANALYSIS_TEMPLATE = """# 模块总览

## 识别的功能模块
{identified_modules}

## 模块详细信息

{module_details}

## 模块关系图谱
{module_relations}

## 核心接口汇总
{core_interfaces}
"""

    # 架构文档模板
    ARCHITECTURE_TEMPLATE = """# 系统架构概述

## 项目概况
{project_overview}

## 技术栈分析
{tech_stack}

## 架构模式
{architecture_pattern}

## 核心组件
{core_components}

## 数据流设计
{data_flow}

## 系统边界和约束
{system_boundaries}

## 部署架构
{deployment_architecture}
"""

    # AI提示词模板
    PROMPTS = {
        'file_analysis': """
请分析以下Python源代码文件，生成详细的文件摘要：

文件路径：{file_path}
文件内容：
```python
{file_content}
```

请按照以下要求分析：

1. **功能概述**：这个文件的主要作用和功能是什么？
2. **类定义**：列出所有类，简要说明每个类的作用和主要方法
3. **函数定义**：列出重要的函数，说明其功能和参数
4. **重要常量和配置**：识别重要的常量、配置项、全局变量
5. **导入的模块**：分析import语句，说明依赖了哪些外部模块
6. **对外接口**：这个文件对外提供了哪些接口（类、函数、常量）
7. **关键算法和逻辑**：如果有复杂的算法或业务逻辑，请简要说明
8. **备注**：其他值得注意的信息

请用清晰、简洁的语言描述，避免冗余。
""",
        
        'module_analysis': """
请基于以下文件摘要和项目结构，识别和分析项目的功能模块：

项目结构：
{directory_structure}

文件摘要列表：
{file_summaries}

请按照以下要求分析：

1. **识别功能模块**：根据文件的功能和目录结构，识别出项目包含哪些主要的功能模块
2. **模块归类**：将每个文件归类到相应的功能模块中
3. **模块职责**：说明每个模块的核心职责和功能
4. **模块接口**：识别模块之间的接口和调用关系
5. **依赖关系**：分析模块之间的依赖关系，哪些模块依赖哪些模块
6. **核心流程**：如果能识别出主要的业务流程，请说明模块是如何协作的

请以模块为单位组织信息，每个模块包含：模块名称、包含的文件、核心功能、对外接口、依赖关系。
""",
        
        'architecture_analysis': """
请基于以下模块分析和项目信息，生成项目的整体架构文档：

项目基础信息：
{project_info}

模块分析结果：
{module_analysis}

请按照以下要求分析：

1. **项目概况**：基于分析结果，总结项目的整体功能和目标
2. **技术栈分析**：根据导入的模块和文件类型，分析项目使用的技术栈
3. **架构模式**：识别项目采用的架构模式（如MVC、分层架构、微服务等）
4. **核心组件**：总结项目的核心组件和它们的作用
5. **数据流设计**：分析主要的数据流向和处理流程
6. **系统边界**：说明系统的边界、输入输出接口
7. **部署架构**：推断项目的部署方式和运行环境

请从软件架构的角度进行分析，关注系统的整体设计和组织方式。
"""
    }


class TemplateService:
    """模板服务类"""
    
    def __init__(self):
        self.templates = DocumentTemplates()
    
    def get_file_summary_template(self) -> str:
        """获取文件摘要模板"""
        return self.templates.FILE_SUMMARY_TEMPLATE
    
    def get_module_analysis_template(self) -> str:
        """获取模块分析模板"""
        return self.templates.MODULE_ANALYSIS_TEMPLATE
    
    def get_architecture_template(self) -> str:
        """获取架构文档模板"""
        return self.templates.ARCHITECTURE_TEMPLATE
    
    def get_prompt(self, prompt_name: str) -> str:
        """获取AI提示词模板"""
        return self.templates.PROMPTS.get(prompt_name, "")
    
    def build_file_analysis_prompt(self, file_path: str, file_content: str) -> str:
        """构建文件分析提示词"""
        prompt_template = self.get_prompt('file_analysis')
        return prompt_template.format(
            file_path=file_path,
            file_content=file_content[:10000]  # 限制长度避免token过多
        )
    
    def build_module_analysis_prompt(self, directory_structure: str, file_summaries: str) -> str:
        """构建模块分析提示词"""
        prompt_template = self.get_prompt('module_analysis')
        return prompt_template.format(
            directory_structure=directory_structure,
            file_summaries=file_summaries
        )
    
    def build_architecture_analysis_prompt(self, project_info: str, module_analysis: str) -> str:
        """构建架构分析提示词"""
        prompt_template = self.get_prompt('architecture_analysis')
        return prompt_template.format(
            project_info=project_info,
            module_analysis=module_analysis
        )
    
    def format_file_summary(self, **kwargs) -> str:
        """格式化文件摘要"""
        template = self.get_file_summary_template()
        return template.format(**kwargs)
    
    def format_module_analysis(self, **kwargs) -> str:
        """格式化模块分析"""
        template = self.get_module_analysis_template()
        return template.format(**kwargs)
    
    def format_architecture_doc(self, **kwargs) -> str:
        """格式化架构文档"""
        template = self.get_architecture_template()
        return template.format(**kwargs)