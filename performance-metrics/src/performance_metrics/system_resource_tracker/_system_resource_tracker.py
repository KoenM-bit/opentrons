"""System resource tracker."""

import logging
import typing
import psutil
import fnmatch

from pathlib import Path
from ..util import format_command, get_timing_function
from ..data_shapes import ProcessResourceUsageSnapshot, MetricsMetadata
from ..metrics_store import MetricsStore

_timing_function = get_timing_function()

logger = logging.getLogger(__name__)


class _SystemResourceTracker:
    """Tracks system resource usage."""

    def __init__(
        self,
        storage_dir: Path,
        process_filters: typing.Tuple[str, ...],
        refresh_interval: int,
        should_track: bool,
    ) -> None:
        """Initialize the tracker."""
        self.storage_dir = storage_dir
        self.process_filters = process_filters
        self.refresh_interval = refresh_interval
        self.should_track = should_track
        self.processes: typing.List[
            psutil.Process
        ]  # intentionally not public as process.kill can be called
        self._store = MetricsStore[ProcessResourceUsageSnapshot](
            MetricsMetadata(
                name="system_resource_data",
                storage_dir=self.storage_dir,
                headers=ProcessResourceUsageSnapshot.headers(),
            )
        )
        self._store.setup()
        self.refresh_processes()

    def refresh_processes(self) -> None:
        """Filter processes by their command line path with globbing support."""
        processes = []
        for process in psutil.process_iter(attrs=["cmdline"]):
            try:
                process_cmdline: typing.List[str] | None = process.info.get("cmdline")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

            if not process_cmdline:
                continue

            formatted_cmdline: str = format_command(process_cmdline)

            if not formatted_cmdline:
                continue

            if any(
                fnmatch.fnmatch(formatted_cmdline, pattern)
                for pattern in self.process_filters
            ):
                processes.append(process)

        self.processes = processes

    @property
    def snapshots(self) -> typing.List[ProcessResourceUsageSnapshot]:
        """Get snapshots."""
        snapshots: typing.List[ProcessResourceUsageSnapshot] = []
        for process in self.processes:
            with process.oneshot():
                cpu_time = process.cpu_times()
                snapshots.append(
                    ProcessResourceUsageSnapshot(
                        query_time=_timing_function(),
                        command=format_command(process.cmdline()),
                        running_since=process.create_time(),
                        system_cpu_time=cpu_time.system,
                        user_cpu_time=cpu_time.user,
                        memory_percent=process.memory_percent(),
                    )
                )

        return snapshots

    def get_and_store_system_data_snapshots(self) -> None:
        """Get and store system data snapshots."""
        if self.should_track:
            self.refresh_processes()
            self._store.add_all(self.snapshots)
            self._store.store()
