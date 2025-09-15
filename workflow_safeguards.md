# 工作流程安全防护方案

## 方案2：分步验证工作流

### 当前问题工作流:
```
task_execute → (跳过实际生成) → --mode complete → 标记完成 ❌
```

### 改进工作流:
```
1. task_execute → 获取模板和上下文
2. 验证目标文件存在性
3. 读取文件内容/生成内容  
4. 根据模板生成文档
5. Write工具保存文档
6. 验证保存结果
7. --mode complete (仅在验证通过后)
```

## 方案3：行为引导改进

### A. 强制检查点
在关键步骤增加强制验证:
- 每5个任务完成后，强制检查产出文件
- 每个阶段完成后，运行质量检查
- 提供"取样验证"功能

### B. 反馈机制改进
```python
# 每次完成任务后显示实际产出信息
def show_completion_summary(task_id: str):
    task = get_task(task_id)
    output_path = task.output_path
    
    if Path(output_path).exists():
        file_size = Path(output_path).stat().st_size
        line_count = len(Path(output_path).read_text().splitlines())
        print(f"✅ {task_id}: 生成 {line_count} 行文档 ({file_size} bytes)")
    else:
        print(f"❌ {task_id}: 输出文件不存在!")
```

## 方案4：设计模式改进

### A. 策略模式 - 不同任务类型不同验证策略
```python
class ValidationStrategy:
    def validate(self, task, output_path): pass

class FileAnalysisValidation(ValidationStrategy):
    def validate(self, task, output_path):
        # 检查是否包含函数分析、类分析等

class ArchitectureValidation(ValidationStrategy):  
    def validate(self, task, output_path):
        # 检查是否包含系统架构图、技术栈等
```

### B. 装饰器模式 - 自动验证
```python
@validate_output
def complete_task(task_id, success=True):
    # 装饰器自动验证输出
    pass
```

## 方案5：系统级防护

### A. 配置强制验证模式
```json
{
  "strict_validation": true,
  "require_content_verification": true,
  "min_doc_length": 500,
  "forbid_placeholders": true
}
```

### B. 审计日志
记录所有"可疑"的快速完成:
- 完成时间过短的任务  
- 输出文件过小的任务
- 批量完成的任务

## 实施建议

1. **短期** - 立即实施验证器
2. **中期** - 改进工作流程引导  
3. **长期** - 重构工具设计，移除危险的逃逸通道

这样可以从多个层面防止类似问题再次发生。