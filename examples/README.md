# CodeLens 配置系统示例

本目录包含 CodeLens 统一配置系统的使用示例和配置模板。

## 文件结构

```
examples/
├── README.md                          # 本文件
├── config_usage_examples.py           # 配置使用示例脚本
└── config_examples/                   # 配置文件示例
    ├── development_config.json        # 开发环境配置
    ├── production_config.json         # 生产环境配置
    └── large_project_config.json      # 大型项目配置
```

## 快速开始

### 运行配置使用示例

```bash
cd /Users/martinezdavid/Documents/MG/code/CodeLens
python examples/config_usage_examples.py
```

这个脚本演示了：
- 基本配置API使用
- FileService 配置集成
- TaskInit 配置集成
- 自定义配置创建
- 配置验证功能
- 性能监控
- 环境特定配置

### 使用配置模板

1. **开发环境** (`development_config.json`)
   - 支持更多文件类型
   - 详细的调试日志
   - 更大的文件处理限制
   - 适合本地开发

2. **生产环境** (`production_config.json`)
   - 严格的文件过滤
   - 优化的性能设置
   - 安全性增强
   - 适合生产部署

3. **大型项目** (`large_project_config.json`)
   - 极严格的文件过滤
   - 最小化的文件处理
   - 优化的内存使用
   - 适合大型代码库

### 创建自定义配置

1. 在项目根目录创建 `.codelens/config.json`
2. 复制合适的模板作为起点
3. 根据需要修改配置项
4. 验证配置有效性

示例：
```bash
mkdir -p .codelens
cp examples/config_examples/development_config.json .codelens/config.json
# 编辑 .codelens/config.json 根据需要修改
```

## 配置项说明

### 主要配置节

- **file_filtering**: 文件过滤规则
- **file_size_limits**: 文件大小限制
- **scanning**: 扫描行为配置
- **mcp_tools**: MCP工具特定配置
- **logging**: 日志配置
- **performance**: 性能优化配置
- **security**: 安全相关配置

### 智能过滤

配置支持智能文件过滤：
- 按文件重要性优先级排序
- 自动排除测试文件和临时文件
- 可配置的文件数量限制
- 文件大小阈值控制

## 最佳实践

1. **环境分离**: 为不同环境使用不同的配置文件
2. **渐进式配置**: 从默认配置开始，逐步添加自定义选项
3. **验证配置**: 使用内置验证器检查配置有效性
4. **性能监控**: 定期检查配置对性能的影响
5. **文档记录**: 记录自定义配置的原因和用途

## 故障排除

如果遇到配置问题：

1. **检查配置语法**: 确保JSON格式正确
2. **验证数值范围**: 确保数值配置在合理范围内
3. **查看日志**: 启用详细日志查看加载过程
4. **使用默认配置**: 删除自定义配置测试是否是配置问题
5. **运行测试**: 使用 `test_config_system.py` 验证系统状态

## 更多信息

- 完整配置指南: [docs/configuration_guide.md](../docs/configuration_guide.md)
- 配置系统测试: [test_config_system.py](../test_config_system.py)
- 默认配置文件: [src/config/default_config.json](../src/config/default_config.json)

---

*如有问题或建议，请查看项目文档或提交Issue。*