import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from src.aitechpioneer.domain.models import FileType, TaskStatus, UploadTask


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, UploadTask] = {}
        self._lock = asyncio.Lock()

    async def create_task(
        self,
        file_name: str,
        file_type: FileType,
        display_name: Optional[str] = None,
    ) -> UploadTask:
        async with self._lock:
            task = UploadTask.create(file_name, file_type, display_name)
            self.tasks[task.task_id] = task
            return task

    async def get_task(self, task_id: str) -> Optional[UploadTask]:
        async with self._lock:
            return self.tasks.get(task_id)

    async def update_task(
        self,
        task_id: str,
        status: TaskStatus,
        progress: int = 0,
        error_message: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> Optional[UploadTask]:
        async with self._lock:
            task = self.tasks.get(task_id)
            if task:
                task.update_status(status, progress, error_message)
                if document_id:
                    task.set_document_id(document_id)
            return task

    async def get_all_tasks(self) -> List[UploadTask]:
        async with self._lock:
            return list(self.tasks.values())

    async def delete_task(self, task_id: str) -> bool:
        async with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
            return False

    async def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        async with self._lock:
            now = datetime.utcnow()
            to_delete = []
            for task_id, task in self.tasks.items():
                age = now - task.created_at
                if age.total_seconds() > max_age_hours * 3600:
                    to_delete.append(task_id)

            for task_id in to_delete:
                del self.tasks[task_id]

            return len(to_delete)

    async def retry_task(self, task_id: str) -> Optional[UploadTask]:
        async with self._lock:
            task = self.tasks.get(task_id)
            if task:
                task.update_status(TaskStatus.PENDING, progress=0, error_message=None)
            return task


task_manager = TaskManager()
