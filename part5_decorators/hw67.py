# ruff: noqa: UP017
import json
from datetime import datetime, timezone
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, message: str, func_name: str, block_time: datetime,
                 source_exception: Exception | None = None):
        self.func_name = func_name
        self.block_time = block_time
        self.source_exception = source_exception
        super().__init__(message)


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int,
        time_to_recover: int,
        triggers_on: type[Exception],
    ):
        errors = []
        if critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self._failure_count = 0
        self._block_time: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            func_name = f"{func.__module__}.{func.__name__}"

            if self._block_time is not None:
                if (datetime.now(timezone.utc) - self._block_time).total_seconds() >= self.time_to_recover:
                    self._failure_count = 0
                    self._block_time = None
                else:
                    raise BreakerError(TOO_MUCH, func_name, self._block_time)

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                if isinstance(e, self.triggers_on):
                    self._failure_count += 1
                    if self._failure_count >= self.critical_count:
                        self._block_time = datetime.now(timezone.utc)
                        raise BreakerError(TOO_MUCH, func_name, self._block_time, e) from e
                raise
            else:
                self._failure_count = 0
                return result

        wrapper.__name__ = func.__name__
        wrapper.__module__ = func.__module__
        return wrapper


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
