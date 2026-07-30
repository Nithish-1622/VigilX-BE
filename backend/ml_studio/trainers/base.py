from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class TrainerStepMetrics:
    step: int
    total_steps: int
    loss: float
    learning_rate: float
    epoch: float
    eta_seconds: float


# Type alias for progress callback function
ProgressCallback = Callable[[TrainerStepMetrics], None]


class BaseTrainer(ABC):
    """
    Abstract Base Class for all Local ML Studio Training Strategies.
    Enforces unified lifecycle: prepare -> train -> save_adapter -> cleanup.
    """

    def __init__(
        self,
        job_id: str,
        base_model: str,
        output_dir: str,
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        self.job_id = job_id
        self.base_model = base_model
        self.output_dir = output_dir
        self.progress_callback = progress_callback
        self.is_prepared: bool = False

    @abstractmethod
    def prepare(self, dataset_rows: list[dict[str, str]], config: dict[str, Any]) -> None:
        """Prepare tokenizer, dataset split, and model weights."""
        pass

    @abstractmethod
    def train(self, steps: int, batch_size: int, learning_rate: float) -> dict[str, Any]:
        """
        Execute training loop for given steps and batch size.
        Returns final training metrics dict.
        """
        pass

    @abstractmethod
    def save_adapter(self) -> str:
        """
        Persist trained LoRA/quantized adapter weights to output_dir.
        Returns absolute path to adapter directory.
        """
        pass
