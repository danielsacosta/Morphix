from __future__ import annotations

from dataclasses import dataclass

from ..errors import ConversionTimeoutError


@dataclass(frozen=True)
class TimeoutPolicy:
    timeout_seconds: int

    def assert_positive(self) -> None:
        if self.timeout_seconds <= 0:
            raise ConversionTimeoutError("Conversion timeout must be greater than zero")

