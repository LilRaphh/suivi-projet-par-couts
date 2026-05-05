from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, Set


def working_day_to_date(project_start: date, working_day: int) -> date:
    """Convert a working-day offset from project_start to a calendar date."""
    if working_day == 0:
        return project_start
    current = project_start
    count = 0
    while count < working_day:
        current += timedelta(days=1)
        if current.weekday() < 5:   # Mon-Fri
            count += 1
    return current


def compute_schedule(
    tasks: List[dict],
    project_start: date,
    durations: Dict[int, int],
    lags: Dict[int, int] | None = None,
) -> Dict[int, dict]:
    """
    ASAP scheduling via recursive topological resolution.
    Returns {task_id: {es_day, ef_day, es: date, ef: date}}
    """
    task_by_id = {t["id"]: t for t in tasks}
    schedule: Dict[int, dict] = {}
    resolving: Set[int] = set()

    def resolve(tid: int) -> None:
        if tid in schedule:
            return
        if tid in resolving:
            raise ValueError(f"Dependency cycle detected at task {tid}")
        resolving.add(tid)
        t = task_by_id[tid]
        for dep in t["deps"]:
            resolve(dep)
        dur = durations.get(tid, t["duration"])
        es_day = max((schedule[dep]["ef_day"] for dep in t["deps"]), default=0)
        if lags:
            es_day += lags.get(tid, 0)
        ef_day = es_day + dur
        schedule[tid] = {
            "es_day": es_day,
            "ef_day": ef_day,
            "es": working_day_to_date(project_start, es_day),
            "ef": working_day_to_date(project_start, ef_day),
        }
        resolving.discard(tid)

    for t in tasks:
        resolve(t["id"])
    return schedule


def compute_critical_path(
    tasks: List[dict],
    schedule: Dict[int, dict],
) -> Set[int]:
    """
    Standard CPM backward pass.
    Returns the set of task IDs on the critical path (total float == 0).
    """
    task_by_id = {t["id"]: t for t in tasks}
    project_end = max(s["ef_day"] for s in schedule.values())

    # Build successor map
    successors: Dict[int, List[int]] = {t["id"]: [] for t in tasks}
    for t in tasks:
        for dep in t["deps"]:
            successors[dep].append(t["id"])

    # Backward pass: LF[j] = min(LS[k] for successors k), project_end if no successors
    lf: Dict[int, int] = {}
    for t in sorted(tasks, key=lambda x: schedule[x["id"]]["ef_day"], reverse=True):
        tid = t["id"]
        dur = schedule[tid]["ef_day"] - schedule[tid]["es_day"]
        if not successors[tid]:
            lf[tid] = project_end
        else:
            lf[tid] = min(lf[s] - (schedule[s]["ef_day"] - schedule[s]["es_day"]) for s in successors[tid])

    critical: Set[int] = set()
    for t in tasks:
        tid = t["id"]
        dur = schedule[tid]["ef_day"] - schedule[tid]["es_day"]
        ls = lf[tid] - dur
        total_float = ls - schedule[tid]["es_day"]
        if total_float == 0:
            critical.add(tid)
    return critical


def resource_workload(tasks: List[dict], schedule: Dict[int, dict], durations: Dict[int, int], resources_map: Dict[int, str]) -> Dict[str, int]:
    """Total working days per resource."""
    workload: Dict[str, int] = {}
    for t in tasks:
        res = resources_map[t["id"]]
        workload[res] = workload.get(res, 0) + durations.get(t["id"], t["duration"])
    return workload
