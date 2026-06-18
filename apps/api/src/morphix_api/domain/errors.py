from __future__ import annotations


class DomainError(Exception):
    status_code = 400


class AuthenticationRequiredError(DomainError):
    status_code = 401


class FileTooLargeError(DomainError):
    status_code = 413


class UnsupportedConversionError(DomainError):
    status_code = 400


class JobNotFoundError(DomainError):
    status_code = 404


class JobOwnershipError(DomainError):
    status_code = 404


class JobStateError(DomainError):
    status_code = 409

