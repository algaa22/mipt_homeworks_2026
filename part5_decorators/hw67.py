import json
from datetime import UTC, datetime
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
    def __init__(self, message: str, func_name: str, block_time: datetime):
        self.func_name = func_name
        self.block_time = block_time
        super().__init__(message)


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        self._validate_params(critical_count, time_to_recover)
        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self._failure_count = 0
        self._block_time: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            self._check_blocked(func)

            try:
                result = func(*args, **kwargs)
            except Exception as error:
                self._handle_error(error, func)
                raise
            else:
                self._failure_count = 0
                return result

        wrapper.__name__ = func.__name__
        wrapper.__module__ = func.__module__
        return wrapper

    def _check_blocked(self, func: CallableWithMeta[P, R_co]) -> None:
        func_name = f"{func.__module__}.{func.__name__}"

        if self._block_time is None:
            return

        time_passed = (datetime.now(UTC) - self._block_time).total_seconds()
        if time_passed >= self.time_to_recover:
            self._failure_count = 0
            self._block_time = None
            return

        raise BreakerError(TOO_MUCH, func_name, self._block_time)

    def _validate_params(self, critical_count: int, time_to_recover: int) -> None:
        errors = []

        if not isinstance(critical_count, int) or isinstance(critical_count, bool):
            errors.append(TypeError(f"critical_count must be int, got {type(critical_count).__name__}"))
        elif critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or isinstance(time_to_recover, bool):
            errors.append(TypeError(f"time_to_recover must be int, got {type(time_to_recover).__name__}"))
        elif time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

    def _handle_error(self, error: Exception, func: CallableWithMeta[P, R_co]) -> None:
        func_name = f"{func.__module__}.{func.__name__}"

        if not isinstance(error, self.triggers_on):
            raise error
        self._failure_count += 1
        if self._failure_count >= self.critical_count:
            self._block_time = datetime.now(UTC)
            raise BreakerError(TOO_MUCH, func_name, self._block_time) from error
        raise error


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
