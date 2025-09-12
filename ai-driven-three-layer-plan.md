# AI驱动的三层文档生成方案

## 核心思路

### 简化原则
- **只分析当前状态**：不需要了解项目历史和进展
- **当前版本即V1.0**：把现在看到的代码当作完整的V1.0版本
- **三层生成顺序**：第三层（File Layer）→ 第二层（Module Layer）→ 第一层（Architecture Layer）
- **纯模板驱动**：我们只提供文件读取和模板服务，AI负责内容生成

### 为什么从第三层开始
- **跳过项目层**：项目层需要了解业务背景和历史，复杂且不必要
- **从具体开始**：先理解每个文件做什么，再抽象出模块和架构
- **信息自下而上流动**：文件信息→模块信息→架构信息

## 三层生成流程

### 第三层：文件文档（File Layer）
**目标**：为每个源代码文件生成摘要文档

**实现流程**：
```python
def generate_file_layer(project_path):
    # 1. 扫描所有源代码文件
    source_files = scan_python_files(project_path)
    
    # 2. 逐个文件分析和生成
    for file_path in source_files:
        file_content = read_file(file_path)
        
        # 3. 使用模板调用AI生成文件摘要
        prompt = build_file_analysis_prompt(file_path, file_content)
        summary = ai_generate_with_template(prompt, FILE_SUMMARY_TEMPLATE)
        
        # 4. 写入文件摘要
        write_file_summary(file_path, summary)
```

**文件摘要模板**：
```markdown
# 文件摘要：{filename}

## 功能概述
{AI生成：这个文件的主要功能和作用}

## 主要组件
### 类定义
{AI生成：列出所有类及其作用}

### 函数定义  
{AI生成：列出所有重要函数及其作用}

### 重要常量
{AI生成：列出重要常量和配置}

## 依赖关系
### 导入的模块
{AI生成：分析import语句，说明依赖}

### 被其他文件引用
{AI生成：如果能推断出被引用情况}

## 关键算法
{AI生成：如果有复杂算法，进行说明}
```

### 第二层：模块文档（Module Layer）
**目标**：基于文件摘要，识别和归纳功能模块

**实现流程**：
```python
def generate_module_layer(project_path):
    # 1. 读取所有已生成的文件摘要
    file_summaries = read_all_file_summaries()
    directory_structure = scan_directory_structure(project_path)
    
    # 2. 调用AI识别模块
    prompt = build_module_analysis_prompt(file_summaries, directory_structure)
    module_analysis = ai_generate_with_template(prompt, MODULE_ANALYSIS_TEMPLATE)
    
    # 3. 生成模块文档
    write_module_docs(module_analysis)
```

**模块分析提示词模板**：
```
基于以下文件摘要和目录结构，请识别项目中的功能模块：

目录结构：
{directory_structure}

文件摘要：
{file_summaries}

请分析并生成：
1. 项目包含哪些主要功能模块？
2. 每个模块包含哪些文件？
3. 模块之间有什么依赖关系？
4. 每个模块的核心接口是什么？
```

**模块文档模板**：
```markdown
# 模块总览

## 识别的模块
{AI生成：列出所有识别的功能模块}

## 模块详情
{AI为每个模块生成详细说明}

## 模块关系图
{AI生成：模块间的依赖关系文本描述}
```

### 第一层：架构文档（Architecture Layer）
**目标**：基于模块分析，生成整体架构文档

**实现流程**：
```python
def generate_architecture_layer(project_path):
    # 1. 读取模块分析结果
    module_docs = read_module_layer_docs()
    
    # 2. 读取项目基础信息（可选）
    basic_info = {
        'project_name': get_project_name(project_path),
        'main_files': identify_main_files(project_path),
        'config_files': scan_config_files(project_path)
    }
    
    # 3. 调用AI生成架构文档
    prompt = build_architecture_analysis_prompt(module_docs, basic_info)
    architecture_docs = ai_generate_with_template(prompt, ARCHITECTURE_TEMPLATE)
    
    # 4. 写入架构文档
    write_architecture_docs(architecture_docs)
```

**架构文档模板**：
```markdown
# 系统架构概述

## 项目概况
{AI生成：基于分析的项目整体描述}

## 技术栈
{AI生成：从imports和文件类型推断技术栈}

## 架构模式
{AI生成：识别的架构模式，如MVC、分层架构等}

## 核心组件
{AI生成：基于模块分析的核心组件说明}

## 数据流
{AI生成：主要的数据流向和处理流程}

## 部署结构
{AI生成：推断的部署和运行方式}
```

## 服务架构

### 1. 核心服务类
```python
class ThreeLayerDocGenerator:
    def __init__(self):
        self.file_service = FileService()
        self.template_service = TemplateService()
        self.ai_service = AIService()
    
    def generate_docs(self, project_path):
        """按顺序生成三层文档"""
        print("开始生成三层文档...")
        
        # Step 1: 生成文件层文档
        self._generate_file_layer(project_path)
        print("✓ 文件层文档生成完成")
        
        # Step 2: 生成模块层文档
        self._generate_module_layer(project_path)
        print("✓ 模块层文档生成完成")
        
        # Step 3: 生成架构层文档
        self._generate_architecture_layer(project_path)
        print("✓ 架构层文档生成完成")
        
        print("三层文档生成完成！")
```

### 2. 文件服务
```python
class FileService:
    def scan_python_files(self, project_path):
        """扫描Python源代码文件"""
        return glob.glob(f"{project_path}/**/*.py", recursive=True)
    
    def read_file_safe(self, file_path):
        """安全读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    def get_relative_path(self, file_path, project_path):
        """获取相对路径"""
        return os.path.relpath(file_path, project_path)
```

### 3. 模板服务
```python
class TemplateService:
    def __init__(self):
        self.templates = {
            'file_summary': FILE_SUMMARY_TEMPLATE,
            'module_analysis': MODULE_ANALYSIS_TEMPLATE,
            'architecture': ARCHITECTURE_TEMPLATE
        }
    
    def get_template(self, template_name):
        return self.templates.get(template_name)
    
    def build_prompt(self, template_name, **kwargs):
        template = self.get_template(template_name)
        return template.format(**kwargs)
```

### 4. AI服务
```python
class AIService:
    def generate_with_claude(self, prompt):
        """调用Claude生成内容"""
        # 实际的AI调用实现
        pass
    
    def batch_generate(self, prompts):
        """批量生成，提高效率"""
        pass
```

## MCP工具实现

```python
{
  "name": "doc_init",
  "description": "生成项目的三层文档结构",
  "parameters": {
    "project_path": {
      "type": "string",
      "description": "要分析的项目路径"
    },
    "output_path": {
      "type": "string", 
      "description": "文档输出路径，默认为项目下的docs目录"
    },
    "config": {
      "type": "object",
      "properties": {
        "file_extensions": {
          "type": "array",
          "default": [".py"],
          "description": "要分析的文件扩展名"
        },
        "exclude_patterns": {
          "type": "array", 
          "default": ["__pycache__", ".git", "node_modules", ".idea"],
          "description": "排除的目录或文件模式"
        },
        "max_file_size": {
          "type": "number",
          "default": 50000,
          "description": "单个文件最大字符数限制"
        }
      }
    }
  }
}
```

## 应用到目标项目

### kbxy-monsters-pro项目生成流程
```
1. 文件层：分析每个.py文件（monster.py, player.py, game.py等）
   → 生成每个文件的功能摘要

2. 模块层：基于文件摘要识别模块
   → 怪物系统模块、玩家系统模块、游戏引擎模块等

3. 架构层：基于模块分析生成整体架构
   → 游戏架构模式、数据流、技术栈说明
```

### wechat-automation-project项目生成流程  
```
1. 文件层：分析自动化脚本文件
   → 每个脚本的功能和API调用说明

2. 模块层：基于脚本功能识别模块
   → 消息处理模块、任务调度模块、API交互模块等

3. 架构层：基于模块分析生成架构
   → 自动化系统架构、工作流程、技术实现方案
```

## 优势总结

1. **简单直接**：不需要复杂的代码分析，只需要AI理解能力
2. **无历史包袱**：不需要了解项目历史，当前状态即完整版本
3. **渐进抽象**：从具体文件到抽象架构，符合认知规律
4. **易于实现**：主要是文件读写和AI调用，技术难度低
5. **效果可期**：AI直接理解代码，生成的文档质量有保障

## 实现计划

### Day 1: 基础服务
- 文件扫描和读取服务
- 模板系统
- 基础的AI调用服务

### Day 2: 文件层生成
- 实现文件摘要生成
- 在两个目标项目上测试

### Day 3: 模块层和架构层
- 实现模块识别和架构生成
- 完整流程测试和优化