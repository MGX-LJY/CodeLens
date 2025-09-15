"""
FileRotator - 文件轮转器

为CodeLens日志系统提供日志文件的创建、轮转和清理功能，
支持按大小或时间进行文件轮转，自动创建日志目录，
历史文件清理和文件压缩。
"""

import datetime
import gzip
import os
import shutil
from pathlib import Path
from typing import List

from .config import LogConfig


class FileRotator:
    """文件轮转器
    
    职责：
    - 管理日志文件的创建、轮转和清理
    - 按大小或时间进行文件轮转
    - 自动创建日志目录
    - 历史文件清理
    - 文件命名和压缩
    """

    def __init__(self, config: LogConfig):
        """初始化文件轮转器
        
        Args:
            config: 日志配置对象
        """
        self.config = config
        self.log_path = config.get_absolute_file_path()
        self.log_dir = self.log_path.parent
        self.log_name = self.log_path.stem
        self.log_ext = self.log_path.suffix

        # 确保日志目录存在
        self._ensure_log_directory()

    def _ensure_log_directory(self) -> None:
        """确保日志目录存在"""
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def should_rotate(self) -> bool:
        """检查是否需要轮转文件
        
        Returns:
            是否需要轮转
        """
        if not self.log_path.exists():
            return False

        file_config = self.config.get_config().file

        if file_config.rotation == "size":
            return self._should_rotate_by_size()
        elif file_config.rotation == "time":
            return self._should_rotate_by_time()
        elif file_config.rotation == "lines":
            return self._should_rotate_by_lines()

        return False

    def _should_rotate_by_size(self) -> bool:
        """检查是否需要按大小轮转
        
        Returns:
            是否需要轮转
        """
        if not self.log_path.exists():
            return False

        file_config = self.config.get_config().file
        max_size_bytes = file_config.max_size_mb * 1024 * 1024
        current_size = self.log_path.stat().st_size

        return current_size >= max_size_bytes

    def _should_rotate_by_time(self) -> bool:
        """检查是否需要按时间轮转
        
        Returns:
            是否需要轮转
        """
        if not self.log_path.exists():
            return False

        # 获取文件的最后修改时间
        file_mtime = datetime.datetime.fromtimestamp(self.log_path.stat().st_mtime)
        current_date = datetime.datetime.now().date()
        file_date = file_mtime.date()

        # 如果文件不是今天创建的，需要轮转
        return file_date < current_date

    def _should_rotate_by_lines(self) -> bool:
        """检查是否需要按行数轮转
        
        Returns:
            是否需要轮转
        """
        if not self.log_path.exists():
            return False

        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            return line_count >= 1000
        except Exception:
            return False

    def rotate_file(self) -> bool:
        """执行文件轮转
        
        Returns:
            轮转是否成功
        """
        if not self.log_path.exists():
            return True

        try:
            file_config = self.config.get_config().file
            
            if file_config.rotation == "lines":
                # 对于行数轮转，直接清空文件
                with open(self.log_path, 'w', encoding='utf-8') as f:
                    f.write('')
            else:
                # 对于大小和时间轮转，使用备份机制
                # 移动现有的备份文件
                self._shift_backup_files()

                # 将当前文件重命名为.1
                backup_path = self._get_backup_path(1)
                shutil.move(str(self.log_path), str(backup_path))

                # 压缩备份文件（如果启用）
                if self.config.get_config().retention.compress:
                    self._compress_file(backup_path)

                # 清理过期文件
                self._cleanup_old_files()

            return True

        except Exception as e:
            print(f"Error during file rotation: {e}")
            return False

    def _shift_backup_files(self) -> None:
        """移动现有的备份文件"""
        file_config = self.config.get_config().file

        # 从最大编号开始，向后移动备份文件
        for i in range(file_config.backup_count, 0, -1):
            current_backup = self._get_backup_path(i)
            next_backup = self._get_backup_path(i + 1)

            if current_backup.exists():
                if i >= file_config.backup_count:
                    # 删除超出保留数量的文件
                    current_backup.unlink()
                else:
                    # 移动到下一个编号
                    shutil.move(str(current_backup), str(next_backup))

    def _get_backup_path(self, index: int) -> Path:
        """获取备份文件路径
        
        Args:
            index: 备份文件索引
            
        Returns:
            备份文件路径
        """
        return self.log_dir / f"{self.log_name}{self.log_ext}.{index}"

    def _compress_file(self, file_path: Path) -> None:
        """压缩文件
        
        Args:
            file_path: 要压缩的文件路径
        """
        if not file_path.exists():
            return

        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')

        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # 删除原文件
            file_path.unlink()

        except Exception as e:
            print(f"Error compressing file {file_path}: {e}")

    def _cleanup_old_files(self) -> None:
        """清理过期的日志文件"""
        retention_config = self.config.get_config().retention
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_config.days)

        # 清理主日志目录中的过期文件
        self._cleanup_directory(self.log_dir, cutoff_date)

    def _cleanup_directory(self, directory: Path, cutoff_date: datetime.datetime) -> None:
        """清理指定目录中的过期文件
        
        Args:
            directory: 要清理的目录
            cutoff_date: 截止日期
        """
        try:
            for file_path in directory.iterdir():
                if file_path.is_file() and self._is_log_file(file_path):
                    file_mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        file_path.unlink()
                        print(f"Cleaned up old log file: {file_path}")
        except Exception as e:
            print(f"Error cleaning up directory {directory}: {e}")

    def _is_log_file(self, file_path: Path) -> bool:
        """检查文件是否是日志文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否是日志文件
        """
        name = file_path.name
        # 检查是否是当前项目的日志文件
        return (name.startswith(self.log_name) and
                (name.endswith('.log') or name.endswith('.log.gz') or
                 '.log.' in name))

    def get_current_file_size(self) -> int:
        """获取当前日志文件大小（字节）
        
        Returns:
            文件大小
        """
        if self.log_path.exists():
            return self.log_path.stat().st_size
        return 0

    def get_current_file_size_mb(self) -> float:
        """获取当前日志文件大小（MB）
        
        Returns:
            文件大小（MB）
        """
        return self.get_current_file_size() / (1024 * 1024)



    def get_backup_files(self) -> List[Path]:
        """获取所有备份文件列表
        
        Returns:
            备份文件路径列表
        """
        backup_files = []

        # 获取编号备份文件
        file_config = self.config.get_config().file
        for i in range(1, file_config.backup_count + 1):
            backup_path = self._get_backup_path(i)
            compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')

            if backup_path.exists():
                backup_files.append(backup_path)
            elif compressed_path.exists():
                backup_files.append(compressed_path)

        return backup_files

    def get_disk_usage(self) -> dict:
        """获取日志文件的磁盘使用情况
        
        Returns:
            磁盘使用情况字典
        """
        total_size = 0
        file_count = 0

        # 当前文件
        if self.log_path.exists():
            total_size += self.log_path.stat().st_size
            file_count += 1

        # 备份文件
        for backup_file in self.get_backup_files():
            total_size += backup_file.stat().st_size
            file_count += 1

        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "file_count": file_count,
            "current_file_size_mb": self.get_current_file_size_mb()
        }

    def ensure_writable(self) -> bool:
        """确保日志文件可写
        
        Returns:
            文件是否可写
        """
        try:
            # 如果文件不存在，尝试创建
            if not self.log_path.exists():
                self.log_path.touch()

            # 检查写权限
            return os.access(self.log_path, os.W_OK)

        except Exception:
            return False
