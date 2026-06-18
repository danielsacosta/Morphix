from __future__ import annotations


class WorkerError(Exception):
    pass


class UnsupportedConversionError(WorkerError):
    pass


class ConversionTimeoutError(WorkerError):
    pass

