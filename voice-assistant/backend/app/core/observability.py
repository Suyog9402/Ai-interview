"""
Pipeline Observability, Telemetry & Stage Timing

Provides structured JSON logging, stage-by-stage pipeline latency tracking, and local
token/cost estimation with ZERO external paid observability services (100% local & free).
"""
import time
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

logger = logging.getLogger("pipeline.telemetry")

class PipelineTimer:
    """Measures and records latency across discrete stages of the AI Interview pipeline."""
    
    def __init__(self, workflow_id: Optional[str] = None):
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None
        self.stage_timings: Dict[str, float] = {}
        self.stage_metadata: Dict[str, Any] = {}

    @contextmanager
    def time_stage(self, stage_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager to measure execution time of a specific pipeline node/stage."""
        stage_start = time.time()
        if metadata:
            self.stage_metadata[stage_name] = metadata
        try:
            yield
        finally:
            stage_duration = round((time.time() - stage_start) * 1000, 2)  # in milliseconds
            self.stage_timings[stage_name] = stage_duration
            logger.info(
                f"[Telemetry] Stage '{stage_name}' completed in {stage_duration}ms "
                f"(workflow_id={self.workflow_id})"
            )

    def record_stage(self, stage_name: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
        """Manually record the latency of a stage in milliseconds."""
        self.stage_timings[stage_name] = round(duration_ms, 2)
        if metadata:
            self.stage_metadata[stage_name] = metadata

    def finish(self) -> Dict[str, Any]:
        """Finish timing and return complete structured telemetry summary."""
        self.end_time = time.time()
        total_duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        
        telemetry = {
            "workflow_id": self.workflow_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "total_latency_ms": total_duration_ms,
            "total_latency_sec": round(total_duration_ms / 1000.0, 2),
            "stages": {
                stage: f"{duration}ms" for stage, duration in self.stage_timings.items()
            },
            "stage_latencies_ms": self.stage_timings,
            "stage_metadata": self.stage_metadata
        }
        
        logger.info(
            f"[Telemetry Summary] Workflow {self.workflow_id} total: {total_duration_ms}ms | "
            f"Breakdown: {json.dumps(self.stage_timings)}"
        )
        return telemetry


class TokenEstimator:
    """Estimates LLM prompt/completion tokens and cost without paid API tracking."""
    
    # Approx rates per 1M tokens (for local estimation)
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "text-embedding-3-small": {"input": 0.02, "output": 0.00}
    }

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count based on typical ~4 chars per token rule of thumb."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    @classmethod
    def estimate_cost(cls, model: str, prompt_text: str, completion_text: str = "") -> Dict[str, Any]:
        """Estimate token count and cost for a given prompt and completion."""
        p_tokens = cls.estimate_tokens(prompt_text)
        c_tokens = cls.estimate_tokens(completion_text)
        total_tokens = p_tokens + c_tokens
        
        rates = cls.PRICING.get(model, cls.PRICING["gpt-4o-mini"])
        cost = (p_tokens / 1_000_000 * rates["input"]) + (c_tokens / 1_000_000 * rates["output"])
        
        return {
            "model": model,
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(cost, 6)
        }
