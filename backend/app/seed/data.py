import random
import string
from datetime import datetime, timedelta, timezone

from faker import Faker

PLATE_SIZES = (24, 48, 96, 384)
PLATE_DIMENSIONS = {
    24: (4, 6),
    48: (6, 8),
    96: (8, 12),
    384: (16, 24),
}
PROCESS_DEFINITIONS = (
    {"name": "VALIDATE_INPUTS", "expected_duration_seconds": 120, "sort_order": 1},
    {"name": "FASTQC", "expected_duration_seconds": 300, "sort_order": 2},
    {"name": "TRIM_READS", "expected_duration_seconds": 900, "sort_order": 3},
    {"name": "ALIGN", "expected_duration_seconds": 2400, "sort_order": 4},
    {"name": "MARK_DUPLICATES", "expected_duration_seconds": 900, "sort_order": 5},
    {"name": "BQSR", "expected_duration_seconds": 1800, "sort_order": 6},
    {"name": "COVERAGE_QC", "expected_duration_seconds": 600, "sort_order": 7},
    {"name": "CALL_VARIANTS", "expected_duration_seconds": 3600, "sort_order": 8},
    {
        "name": "JOINT_GENOTYPE",
        "expected_duration_seconds": 1800,
        "sort_order": 9,
        "scope": "run",
    },
    {"name": "VARIANT_QC", "expected_duration_seconds": 600, "sort_order": 10},
    {"name": "FILTER_VARIANTS", "expected_duration_seconds": 900, "sort_order": 11},
    {"name": "ANNOTATE_VARIANTS", "expected_duration_seconds": 1800, "sort_order": 12},
    {"name": "GENERATE_REPORT", "expected_duration_seconds": 300, "sort_order": 13},
)
STATUS_PATTERN = (
    "completed",
    "completed",
    "running",
    "running",
    "running",
    "queued",
    "failed",
    "completed",
    "running",
    "cancelled",
)
SEQUENCERS = ("NovaSeq X", "NextSeq 2000", "NovaSeq 6000")
RESOURCES = {
    "VALIDATE_INPUTS": (1, 2048),
    "FASTQC": (2, 4096),
    "TRIM_READS": (4, 8192),
    "ALIGN": (8, 16384),
    "MARK_DUPLICATES": (4, 12288),
    "BQSR": (4, 12288),
    "COVERAGE_QC": (2, 8192),
    "CALL_VARIANTS": (8, 32768),
    "JOINT_GENOTYPE": (8, 32768),
    "VARIANT_QC": (2, 8192),
    "FILTER_VARIANTS": (4, 8192),
    "ANNOTATE_VARIANTS": (4, 8192),
    "GENERATE_REPORT": (2, 4096),
}
PROCESS_TASK_CODES = {
    "FASTQC": 1,
    "TRIM_READS": 2,
    "ALIGN": 3,
    "VALIDATE_INPUTS": 4,
    "MARK_DUPLICATES": 5,
    "BQSR": 6,
    "COVERAGE_QC": 7,
    "CALL_VARIANTS": 8,
    "JOINT_GENOTYPE": 9,
    "VARIANT_QC": 10,
    "FILTER_VARIANTS": 11,
    "ANNOTATE_VARIANTS": 12,
    "GENERATE_REPORT": 13,
}


def _well_positions(plate_size):
    row_count, column_count = PLATE_DIMENSIONS[plate_size]
    rows = string.ascii_uppercase[:row_count]
    return [f"{row}{column:02d}" for row in rows for column in range(1, column_count + 1)]


def generate_dummy_data(run_count=32, seed_value=42042, now=None):
    if run_count < 0:
        raise ValueError("run_count must be non-negative")
    if seed_value < 0:
        raise ValueError("seed_value must be non-negative")

    rng = random.Random(seed_value)
    fake = Faker("en_US")
    fake.seed_instance(seed_value)
    now = (now or datetime.now(timezone.utc)).replace(microsecond=0)

    plate_offset = rng.randrange(len(PLATE_SIZES))
    plate_sizes = [
        PLATE_SIZES[(index + plate_offset) % len(PLATE_SIZES)]
        for index in range(run_count)
    ]
    status_cycle = list(STATUS_PATTERN)
    rng.shuffle(status_cycle)
    statuses = [status_cycle[index % len(status_cycle)] for index in range(run_count)]

    result = {
        "processes": list(PROCESS_DEFINITIONS),
        "runs": [],
        "samples": [],
        "executions": [],
    }
    running_count = 0

    for run_index, (plate_size, run_status) in enumerate(zip(plate_sizes, statuses), start=1):
        run_id = f"SIM-{seed_value:05d}-{run_index:04d}"
        sample_count = plate_size
        expected_tat = int(
            sum(process["expected_duration_seconds"] for process in PROCESS_DEFINITIONS)
            * 1.5
            * (plate_size / 24) ** 0.2
        )

        if run_status in {"running", "queued", "failed", "cancelled"}:
            if run_status == "running":
                stage_index = running_count % len(PROCESS_DEFINITIONS)
                running_count += 1
            elif run_status == "queued":
                stage_index = 0
            else:
                stage_index = rng.randrange(len(PROCESS_DEFINITIONS))
        else:
            stage_index = len(PROCESS_DEFINITIONS) - 1

        if run_status in {"completed", "failed", "cancelled"}:
            tat_seconds = int(expected_tat * rng.uniform(0.7, 1.5))
            completed_at = now - timedelta(minutes=rng.randint(1, 45 * 24 * 60))
            started_at = completed_at - timedelta(seconds=tat_seconds)
            progress_percent = 100 if run_status == "completed" else round(
                (stage_index + 1) / len(PROCESS_DEFINITIONS) * 100, 1
            )
        elif run_status == "running":
            progress_percent = round(
                (stage_index + rng.uniform(0.2, 0.8)) / len(PROCESS_DEFINITIONS) * 100,
                1,
            )
            elapsed_seconds = int(expected_tat * progress_percent / 100)
            started_at = now - timedelta(seconds=elapsed_seconds)
            completed_at = None
            tat_seconds = None
        else:
            progress_percent = 0
            started_at = None
            completed_at = None
            tat_seconds = None

        failed_sample_indexes = set()
        if run_status == "failed":
            failed_sample_indexes = set(
                rng.sample(range(sample_count), max(1, sample_count // 48))
            )

        sequencer = fake.random_element(elements=SEQUENCERS)
        run_values = {
            "run_id": run_id,
            "status": run_status,
            "sample_count": sample_count,
            "started_at": started_at,
            "completed_at": completed_at,
            "tat_seconds": tat_seconds,
            "expected_tat_seconds": expected_tat,
            "tat_variance_seconds": (
                tat_seconds - expected_tat if tat_seconds is not None else None
            ),
            "sequencer": sequencer,
            "current_step": (
                PROCESS_DEFINITIONS[stage_index]["name"]
                if run_status in {"running", "queued", "failed", "cancelled"}
                else None
            ),
            "progress_percent": progress_percent,
            "failed_task_count": 0,
            "retried_task_count": 0,
        }
        result["runs"].append(run_values)
        failed_task_count = 0
        retried_task_count = 0

        for sample_index, well_position in enumerate(_well_positions(plate_size)):
            sample_id = f"{run_id}-{well_position}"
            if run_status == "completed" or (
                run_status == "failed" and sample_index not in failed_sample_indexes
            ):
                sample_status = "completed"
            elif run_status == "running":
                sample_status = "running"
            elif run_status == "queued":
                sample_status = "queued"
            else:
                sample_status = run_status

            result["samples"].append(
                {"run_id": run_id, "sample_id": sample_id, "status": sample_status}
            )

            sample_offset = rng.randint(0, min(1800, max(1, expected_tat // 10)))
            timeline_offset = sample_offset
            for process_index, process in enumerate(PROCESS_DEFINITIONS):
                if process.get("scope") == "run":
                    continue
                process_name = process["name"]
                process_task_code = PROCESS_TASK_CODES[process_name]
                requested_cpus, requested_memory_mb = RESOURCES[process_name]
                queue_seconds = rng.randint(30, 900)
                execution_seconds = max(
                    30,
                    int(process["expected_duration_seconds"] * rng.uniform(0.6, 1.5)),
                )
                execution_status = self_execution_status(
                    run_status,
                    process_index,
                    stage_index,
                    sample_index,
                    failed_sample_indexes,
                )
                attempt = 2 if execution_status == "completed" and rng.random() < 0.025 else 1
                task_id = f"{run_id}-T{sample_index + 1:03d}{process_task_code}"
                submitted_at = None
                task_started_at = None
                task_completed_at = None
                queue_time_seconds = None
                task_execution_seconds = None
                peak_memory_mb = round(
                    requested_memory_mb * rng.uniform(0.35, 0.92), 1
                )

                if execution_status in {"completed", "failed", "cancelled"}:
                    submitted_at = started_at + timedelta(seconds=timeline_offset)
                    task_started_at = submitted_at + timedelta(seconds=queue_seconds)
                    task_completed_at = task_started_at + timedelta(seconds=execution_seconds)
                    queue_time_seconds = queue_seconds
                    task_execution_seconds = execution_seconds
                elif execution_status == "running":
                    queue_time_seconds = queue_seconds
                    task_started_at = now - timedelta(minutes=rng.randint(1, 20))
                    submitted_at = task_started_at - timedelta(seconds=queue_seconds)
                elif execution_status == "queued":
                    submitted_at = now - timedelta(minutes=rng.randint(1, 90))
                    queue_time_seconds = int((now - submitted_at).total_seconds())

                slurm_job = None
                if execution_status in {"completed", "failed", "cancelled", "running", "queued"}:
                    slurm_status = "pending" if execution_status == "queued" else execution_status
                    exit_code = 0 if execution_status == "completed" else (
                        rng.randint(1, 9) if execution_status == "failed" else None
                    )
                    job_id = f"{run_id}-J{sample_index + 1:03d}{process_task_code}"
                    slurm_job = {
                        "job_id": job_id,
                        "status": slurm_status,
                        "submitted_at": submitted_at,
                        "started_at": task_started_at,
                        "completed_at": task_completed_at,
                        "requested_cpus": requested_cpus,
                        "requested_memory_mb": requested_memory_mb,
                        "peak_memory_mb": peak_memory_mb,
                        "exit_code": exit_code,
                        "node_list": fake.bothify(text="compute-###"),
                    }

                result["executions"].append(
                    {
                        "task_id": task_id,
                        "run_id": run_id,
                        "process_name": process_name,
                        "sample_id": sample_id,
                        "status": execution_status,
                        "submitted_at": submitted_at,
                        "started_at": task_started_at,
                        "completed_at": task_completed_at,
                        "queue_time_seconds": queue_time_seconds,
                        "execution_time_seconds": task_execution_seconds,
                        "cpu_count": requested_cpus,
                        "cpu_utilization_percent": (
                            rng.randint(25, 98)
                            if execution_status in {"completed", "running"}
                            else None
                        ),
                        "memory_requested_mb": requested_memory_mb,
                        "peak_memory_mb": peak_memory_mb if task_started_at else None,
                        "exit_code": exit_code if slurm_job else None,
                        "attempt": attempt,
                        "slurm_job": slurm_job,
                    }
                )
                failed_task_count += execution_status == "failed"
                retried_task_count += attempt - 1
                timeline_offset += queue_seconds + execution_seconds

        for process_index, process in enumerate(PROCESS_DEFINITIONS):
            if process.get("scope") != "run":
                continue

            process_name = process["name"]
            requested_cpus, requested_memory_mb = RESOURCES[process_name]
            queue_seconds = rng.randint(30, 900)
            execution_seconds = max(
                30,
                int(process["expected_duration_seconds"] * rng.uniform(0.6, 1.5)),
            )
            failed_sample_index = min(failed_sample_indexes) if failed_sample_indexes else 0
            execution_status = self_execution_status(
                run_status,
                process_index,
                stage_index,
                failed_sample_index,
                failed_sample_indexes,
            )
            task_id = f"{run_id}-R{process_index + 1}"
            stage_offset = sum(
                stage["expected_duration_seconds"]
                for stage in PROCESS_DEFINITIONS[:process_index]
            )
            submitted_at = None
            task_started_at = None
            task_completed_at = None
            queue_time_seconds = None
            task_execution_seconds = None

            if execution_status in {"completed", "failed", "cancelled"}:
                submitted_at = started_at + timedelta(seconds=stage_offset)
                task_started_at = submitted_at + timedelta(seconds=queue_seconds)
                task_completed_at = task_started_at + timedelta(seconds=execution_seconds)
                queue_time_seconds = queue_seconds
                task_execution_seconds = execution_seconds
            elif execution_status == "running":
                queue_time_seconds = queue_seconds
                task_started_at = now - timedelta(minutes=rng.randint(1, 20))
                submitted_at = task_started_at - timedelta(seconds=queue_seconds)
            elif execution_status == "queued":
                submitted_at = now - timedelta(minutes=rng.randint(1, 90))
                queue_time_seconds = int((now - submitted_at).total_seconds())

            peak_memory_mb = round(requested_memory_mb * rng.uniform(0.35, 0.92), 1)
            slurm_job = None
            if execution_status in {"completed", "failed", "cancelled", "running", "queued"}:
                slurm_status = "pending" if execution_status == "queued" else execution_status
                exit_code = 0 if execution_status == "completed" else (
                    rng.randint(1, 9) if execution_status == "failed" else None
                )
                slurm_job = {
                    "job_id": f"{run_id}-RJ{process_index + 1}",
                    "status": slurm_status,
                    "submitted_at": submitted_at,
                    "started_at": task_started_at,
                    "completed_at": task_completed_at,
                    "requested_cpus": requested_cpus,
                    "requested_memory_mb": requested_memory_mb,
                    "peak_memory_mb": peak_memory_mb,
                    "exit_code": exit_code,
                    "node_list": fake.bothify(text="compute-###"),
                }

            result["executions"].append(
                {
                    "task_id": task_id,
                    "run_id": run_id,
                    "process_name": process_name,
                    "sample_id": None,
                    "status": execution_status,
                    "submitted_at": submitted_at,
                    "started_at": task_started_at,
                    "completed_at": task_completed_at,
                    "queue_time_seconds": queue_time_seconds,
                    "execution_time_seconds": task_execution_seconds,
                    "cpu_count": requested_cpus,
                    "cpu_utilization_percent": (
                        rng.randint(25, 98)
                        if execution_status in {"completed", "running"}
                        else None
                    ),
                    "memory_requested_mb": requested_memory_mb,
                    "peak_memory_mb": peak_memory_mb if task_started_at else None,
                    "exit_code": exit_code if slurm_job else None,
                    "attempt": 1,
                    "slurm_job": slurm_job,
                }
            )
            failed_task_count += execution_status == "failed"

        run_values["failed_task_count"] = failed_task_count
        run_values["retried_task_count"] = retried_task_count

    return result


def self_execution_status(
    run_status,
    process_index,
    stage_index,
    sample_index,
    failed_sample_indexes,
):
    if run_status == "completed":
        return "completed"
    if run_status == "running":
        if process_index < stage_index:
            return "completed"
        return "running" if process_index == stage_index else "pending"
    if run_status == "queued":
        return "queued" if process_index == stage_index else "pending"
    if run_status == "failed":
        if sample_index not in failed_sample_indexes or process_index < stage_index:
            return "completed"
        return "failed" if process_index == stage_index else "skipped"
    if process_index < stage_index:
        return "completed"
    return run_status if process_index == stage_index else "skipped"
