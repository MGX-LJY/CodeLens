"""
状态跟踪器：跟踪任务执行状态和进度变化
"""
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from .task_manager import TaskManager, TaskStatus
from .phase_controller import PhaseController, PhaseStatus


@dataclass
class StateSnapshot:
    """状态快照"""
    timestamp: str
    overall_progress: float
    current_phase: Optional[str]
    phase_states: Dict[str, str]
    task_counts: Dict[str, int]
    active_tasks: List[str]
    recent_completions: List[str]
    errors: List[str]


@dataclass
class TaskEvent:
    """任务事件"""
    timestamp: str
    event_type: str  # created, started, completed, failed, retried
    task_id: str
    task_type: str
    phase: str
    details: Optional[Dict[str, Any]] = None


class StateTracker:
    """状态跟踪器"""
    
    def __init__(self, project_path: str, task_manager: TaskManager, phase_controller: PhaseController):
        self.project_path = Path(project_path)
        self.task_manager = task_manager
        self.phase_controller = phase_controller
        
        # 状态文件路径
        self.state_dir = self.project_path / ".codelens"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.snapshots_file = self.state_dir / "state_snapshots.json"
        self.events_file = self.state_dir / "task_events.json"
        
        # 状态数据
        self.snapshots: List[StateSnapshot] = []
        self.events: List[TaskEvent] = []
        
        # 加载历史数据
        self.load_state()

    def take_snapshot(self) -> StateSnapshot:
        """创建当前状态快照"""
        overview = self.phase_controller.get_all_phases_overview()
        task_summary = self.task_manager.export_tasks_summary()
        
        # 获取最近完成的任务（过去10分钟）
        recent_completions = []
        cutoff_time = datetime.now() - timedelta(minutes=10)
        for task in self.task_manager.tasks.values():
            if (task.status == TaskStatus.COMPLETED and task.completed_at 
                and datetime.fromisoformat(task.completed_at) > cutoff_time):
                recent_completions.append(task.id)
        
        # 获取活跃任务
        active_tasks = [
            task.id for task in self.task_manager.tasks.values()
            if task.status == TaskStatus.IN_PROGRESS
        ]
        
        # 获取错误信息
        errors = []
        for task in self.task_manager.tasks.values():
            if task.status == TaskStatus.FAILED and task.error_message:
                errors.append(f"{task.id}: {task.error_message}")
        
        snapshot = StateSnapshot(
            timestamp=datetime.now().isoformat(),
            overall_progress=overview["overall_progress"],
            current_phase=overview["current_phase"],
            phase_states={
                phase: info["status"] for phase, info in overview["phases"].items()
            },
            task_counts=task_summary["task_summary"],
            active_tasks=active_tasks,
            recent_completions=recent_completions,
            errors=errors[-5:]  # 最近5个错误
        )
        
        self.snapshots.append(snapshot)
        
        # 保持最近100个快照
        if len(self.snapshots) > 100:
            self.snapshots = self.snapshots[-100:]
        
        self.save_state()
        return snapshot

    def record_task_event(self, event_type: str, task_id: str, details: Optional[Dict] = None):
        """记录任务事件"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return
        
        event = TaskEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            task_id=task_id,
            task_type=task.type.value,
            phase=task.phase,
            details=details or {}
        )
        
        self.events.append(event)
        
        # 保持最近1000个事件
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
        
        self.save_state()

    def get_current_status(self) -> Dict[str, Any]:
        """获取当前完整状态"""
        current_snapshot = self.take_snapshot()
        overview = self.phase_controller.get_all_phases_overview()
        
        # 计算执行统计
        execution_stats = self._calculate_execution_stats()
        
        return {
            "snapshot": current_snapshot,
            "phase_overview": overview,
            "execution_statistics": execution_stats,
            "health_check": self._perform_health_check()
        }

    def get_progress_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取进度历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        history = []
        for snapshot in self.snapshots:
            snapshot_time = datetime.fromisoformat(snapshot.timestamp)
            if snapshot_time > cutoff_time:
                history.append({
                    "timestamp": snapshot.timestamp,
                    "progress": snapshot.overall_progress,
                    "current_phase": snapshot.current_phase,
                    "active_tasks_count": len(snapshot.active_tasks),
                    "recent_completions_count": len(snapshot.recent_completions)
                })
        
        return history

    def get_task_timeline(self, task_id: str) -> List[TaskEvent]:
        """获取指定任务的事件时间线"""
        return [event for event in self.events if event.task_id == task_id]

    def get_phase_events(self, phase: str, hours: int = 24) -> List[TaskEvent]:
        """获取指定阶段的事件"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        phase_events = []
        for event in self.events:
            event_time = datetime.fromisoformat(event.timestamp)
            if event.phase == phase and event_time > cutoff_time:
                phase_events.append(event)
        
        return sorted(phase_events, key=lambda e: e.timestamp, reverse=True)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        if not self.events:
            return {"error": "No events recorded"}
        
        # 计算任务完成时间
        completion_times = []
        task_durations = {}
        
        for event in self.events:
            if event.event_type == "started":
                task_durations[event.task_id] = {"started": event.timestamp}
            elif event.event_type == "completed" and event.task_id in task_durations:
                start_time = datetime.fromisoformat(task_durations[event.task_id]["started"])
                end_time = datetime.fromisoformat(event.timestamp)
                duration = (end_time - start_time).total_seconds()
                completion_times.append(duration)
        
        # 计算统计信息
        if completion_times:
            avg_duration = sum(completion_times) / len(completion_times)
            min_duration = min(completion_times)
            max_duration = max(completion_times)
        else:
            avg_duration = min_duration = max_duration = 0
        
        # 计算每小时完成率
        hourly_completions = self._calculate_hourly_completions()
        
        return {
            "average_task_duration_seconds": round(avg_duration, 2),
            "min_task_duration_seconds": round(min_duration, 2),
            "max_task_duration_seconds": round(max_duration, 2),
            "total_completed_tasks": len(completion_times),
            "hourly_completion_rate": hourly_completions,
            "active_session_duration": self._get_session_duration()
        }

    def _calculate_execution_stats(self) -> Dict[str, Any]:
        """计算执行统计信息"""
        # 今日统计
        today = datetime.now().date()
        today_events = [
            e for e in self.events 
            if datetime.fromisoformat(e.timestamp).date() == today
        ]
        
        today_completions = len([e for e in today_events if e.event_type == "completed"])
        today_failures = len([e for e in today_events if e.event_type == "failed"])
        
        # 阶段统计
        phase_stats = {}
        for phase_name in ["phase_1_files", 
                          "phase_2_architecture", "phase_3_project"]:
            phase_events = [e for e in self.events if e.phase == phase_name]
            phase_stats[phase_name] = {
                "total_events": len(phase_events),
                "completions": len([e for e in phase_events if e.event_type == "completed"]),
                "failures": len([e for e in phase_events if e.event_type == "failed"])
            }
        
        return {
            "today_completions": today_completions,
            "today_failures": today_failures,
            "total_events": len(self.events),
            "phase_statistics": phase_stats,
            "success_rate": self._calculate_success_rate()
        }

    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        completed = len([e for e in self.events if e.event_type == "completed"])
        failed = len([e for e in self.events if e.event_type == "failed"])
        total = completed + failed
        
        if total == 0:
            return 100.0
        
        return round((completed / total) * 100, 2)

    def _calculate_hourly_completions(self) -> List[Dict[str, Any]]:
        """计算每小时完成数"""
        hourly_data = {}
        
        for event in self.events:
            if event.event_type == "completed":
                hour_key = datetime.fromisoformat(event.timestamp).strftime("%Y-%m-%d %H:00")
                hourly_data[hour_key] = hourly_data.get(hour_key, 0) + 1
        
        return [
            {"hour": hour, "completions": count}
            for hour, count in sorted(hourly_data.items())
        ]

    def _get_session_duration(self) -> str:
        """获取会话持续时间"""
        if not self.events:
            return "0 minutes"
        
        first_event = min(self.events, key=lambda e: e.timestamp)
        session_start = datetime.fromisoformat(first_event.timestamp)
        duration = datetime.now() - session_start
        
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours} hours {minutes} minutes"
        else:
            return f"{minutes} minutes"


    def _perform_health_check(self) -> Dict[str, Any]:
        """执行健康检查"""
        health = {
            "overall_health": "good",
            "issues": [],
            "warnings": []
        }
        
        # 检查失败率
        success_rate = self._calculate_success_rate()
        if success_rate < 80:
            health["issues"].append(f"任务成功率较低: {success_rate}%")
            health["overall_health"] = "poor"
        elif success_rate < 90:
            health["warnings"].append(f"任务成功率需要关注: {success_rate}%")
            if health["overall_health"] == "good":
                health["overall_health"] = "warning"
        
        # 检查长时间运行的任务
        for task in self.task_manager.tasks.values():
            if task.status == TaskStatus.IN_PROGRESS and task.started_at:
                start_time = datetime.fromisoformat(task.started_at)
                duration = datetime.now() - start_time
                if duration.total_seconds() > 1800:  # 30分钟
                    health["warnings"].append(f"任务 {task.id} 运行时间过长")
                    if health["overall_health"] == "good":
                        health["overall_health"] = "warning"
        
        # 检查是否有进展
        if len(self.snapshots) >= 2:
            recent_progress = self.snapshots[-1].overall_progress
            old_progress = self.snapshots[-2].overall_progress
            if recent_progress == old_progress:
                health["warnings"].append("最近没有进展")
                if health["overall_health"] == "good":
                    health["overall_health"] = "warning"
        
        return health

    def load_state(self):
        """加载状态数据"""
        try:
            # 加载快照
            if self.snapshots_file.exists():
                with open(self.snapshots_file, 'r', encoding='utf-8') as f:
                    snapshots_data = json.load(f)
                    self.snapshots = [
                        StateSnapshot(**data) for data in snapshots_data
                    ]
            
            # 加载事件
            if self.events_file.exists():
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    events_data = json.load(f)
                    self.events = [
                        TaskEvent(**data) for data in events_data
                    ]
        except Exception as e:
            print(f"Error loading state: {e}")
            self.snapshots = []
            self.events = []

    def save_state(self):
        """保存状态数据"""
        try:
            # 保存快照
            with open(self.snapshots_file, 'w', encoding='utf-8') as f:
                snapshots_data = [asdict(snapshot) for snapshot in self.snapshots]
                json.dump(snapshots_data, f, indent=2, ensure_ascii=False)
            
            # 保存事件
            with open(self.events_file, 'w', encoding='utf-8') as f:
                events_data = [asdict(event) for event in self.events]
                json.dump(events_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving state: {e}")

    def export_summary_report(self) -> Dict[str, Any]:
        """导出摘要报告"""
        current_status = self.get_current_status()
        performance = self.get_performance_metrics()
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "overall_progress": current_status["snapshot"].overall_progress,
            "current_phase": current_status["snapshot"].current_phase,
            "health_status": current_status["health_check"]["overall_health"],
            "performance_metrics": performance,
            "phase_summary": current_status["phase_overview"]["phases"]
        }