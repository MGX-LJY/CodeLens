# 文件摘要：src/logging/rotator.py

## 功能概述
日志文件轮转器，提供智能的文件轮转和压缩功能。支持按文件大小、时间间隔或混合策略进行轮转，轮转后自动gzip压缩节省磁盘空间，确保日志文件的高效管理。

## 主要组件

### 核心类
- **FileRotator**: 文件轮转管理器
  - 多种轮转策略支持
  - 自动gzip压缩
  - 备份文件管理
  - 磁盘空间监控
  - 文件权限处理

### 主要方法

#### 轮转检查和执行
- `should_rotate()`: 检查是否需要轮转
- `rotate_file()`: 执行文件轮转操作
- `_rotate_by_size()`: 按大小轮转
- `_rotate_by_time()`: 按时间轮转
- `_rotate_by_both()`: 混合轮转策略

#### 文件管理
- `_compress_file()`: 压缩备份文件
- `_cleanup_old_files()`: 清理过期备份文件
- `_get_backup_files()`: 获取备份文件列表
- `_ensure_directory()`: 确保目录存在

#### 状态和监控
- `get_rotation_stats()`: 获取轮转统计信息
- `_check_disk_space()`: 检查磁盘空间
- `_update_last_rotation()`: 更新最后轮转时间

## 依赖关系

### 标准库导入
- `pathlib.Path`: 文件路径操作
- `gzip`: 文件压缩功能
- `shutil`: 文件操作工具
- `time`: 时间处理
- `datetime`: 日期时间操作
- `glob`: 文件模式匹配
- `os`: 系统级操作
- `typing`: 类型注解

### 配置依赖
- `FileConfig`: 文件配置信息
- `RetentionConfig`: 保留策略配置

## 关键算法和逻辑

### 轮转策略算法

#### 按大小轮转 (size)
```python
current_size = log_file.stat().st_size
max_size_bytes = config.max_size_mb * 1024 * 1024
if current_size >= max_size_bytes:
    return True
```

#### 按时间轮转 (time)
```python
last_rotation = get_last_rotation_time()
current_time = datetime.now()
if (current_time - last_rotation).days >= 1:
    return True
```

#### 混合轮转 (both)
```python
return _rotate_by_size() or _rotate_by_time()
```

### 文件轮转流程
1. **轮转检查**: 根据策略判断是否需要轮转
2. **文件重命名**: 当前日志文件重命名为备份文件
3. **压缩处理**: 使用gzip压缩备份文件
4. **清理维护**: 删除超出保留策略的旧文件
5. **状态更新**: 更新轮转统计和时间记录

### 备份文件命名规则
```
原文件: codelens.log
备份文件: codelens.log.1.gz, codelens.log.2.gz, ...
最新备份: 数字越小越新
```

### 压缩算法
```python
def _compress_file(self, file_path: Path) -> None:
    with open(file_path, 'rb') as f_in:
        with gzip.open(f"{file_path}.gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    file_path.unlink()  # 删除原文件
```

## 轮转策略详解

### 按大小轮转 (Size-based)
- **触发条件**: 文件大小超过配置的max_size_mb
- **适用场景**: 日志量大但时间不敏感的应用
- **优势**: 确保单个日志文件不会过大
- **配置**: `"rotation": "size"`

### 按时间轮转 (Time-based)
- **触发条件**: 距离上次轮转超过24小时
- **适用场景**: 需要按日归档的应用
- **优势**: 便于按日期查找和分析日志
- **配置**: `"rotation": "time"`

### 混合轮转 (Both)
- **触发条件**: 满足大小或时间条件之一
- **适用场景**: 生产环境的综合日志管理
- **优势**: 灵活性最高，适应不同日志负载
- **配置**: `"rotation": "both"`

## 压缩和存储优化

### Gzip压缩特性
- **压缩比**: 通常可达到70-90%的压缩率
- **速度**: 快速压缩，不阻塞主业务
- **兼容性**: 标准gzip格式，工具支持广泛
- **透明性**: 自动压缩，用户无感知

### 磁盘空间管理
- **备份数量控制**: `backup_count`限制备份文件数量
- **总空间限制**: `max_total_size_mb`控制日志总占用空间
- **老化清理**: `max_age_days`自动删除过期日志
- **空间监控**: 实时监控磁盘空间使用情况

## 错误处理和恢复

### 常见错误场景
1. **磁盘空间不足**: 暂停轮转，记录错误日志
2. **文件权限问题**: 尝试修复权限或降级处理
3. **压缩失败**: 保留原文件，记录压缩错误
4. **目录不存在**: 自动创建必要的目录结构

### 错误恢复机制
- **重试机制**: 临时失败时的自动重试
- **降级模式**: 压缩失败时保留未压缩文件
- **状态保护**: 确保轮转过程中的状态一致性
- **错误上报**: 向日志管理器报告轮转错误

## 性能优化

### I/O优化
- **流式处理**: 使用流式压缩减少内存占用
- **批量操作**: 批量处理多个文件操作
- **异步清理**: 后台异步执行清理任务
- **缓存状态**: 缓存文件状态减少系统调用

### 内存管理
- **分块压缩**: 大文件分块压缩避免内存溢出
- **及时释放**: 操作完成后立即释放资源
- **状态最小化**: 保持最小必要的状态信息
- **对象复用**: 复用临时对象减少创建开销

## 监控和统计

### 轮转统计信息
```json
{
  "total_rotations": 15,
  "last_rotation_time": "2025-09-13T10:30:00",
  "compression_ratio": 0.82,
  "backup_files_count": 5,
  "total_compressed_size_mb": 45.6,
  "disk_usage_percentage": 12.3
}
```

### 监控指标
- **轮转频率**: 单位时间内的轮转次数
- **压缩效率**: 压缩前后的大小比较
- **磁盘使用**: 日志文件的磁盘占用情况
- **操作耗时**: 轮转和压缩操作的耗时统计

## 配置示例

### 基础配置
```json
{
  "max_size_mb": 10,
  "backup_count": 5,
  "rotation": "size"
}
```

### 生产环境配置
```json
{
  "max_size_mb": 50,
  "backup_count": 10,
  "rotation": "both",
  "max_age_days": 30,
  "max_total_size_mb": 500
}
```

## 文件系统兼容性

### 支持的文件系统
- **本地文件系统**: NTFS, ext4, APFS等主流文件系统
- **网络存储**: NFS, SMB等网络文件系统
- **云存储**: 支持挂载的云存储文件系统
- **容器存储**: Docker volume, Kubernetes PV等

### 跨平台支持
- **Windows**: 完整支持Windows文件系统特性
- **Linux**: 优化的Linux文件操作性能
- **macOS**: 原生支持macOS文件系统
- **权限处理**: 自动处理不同平台的权限差异

## 备注
FileRotator是CodeLens日志系统的重要组件，提供了企业级的文件轮转和存储管理能力。通过智能的轮转策略和高效的压缩算法，确保了日志文件的高效存储和管理，是系统可观测性基础设施的关键部分。