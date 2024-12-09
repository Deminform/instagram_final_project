import inspect
from typing import Callable, Any, Optional, Tuple, Dict, Awaitable, Union

from fastapi_cache import FastAPICache
from starlette.requests import Request
from starlette.responses import Response

class CustomKeyBuilder:
    def __call__(
        self,
        __function: Callable[..., Any],
        __namespace: str = '',
        *,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
    ) -> Union[Awaitable[str], str]:

        key_parts = [__namespace]

        signature = inspect.signature(__function)
        parameters = list(signature.parameters.values())

        args_dict = {}
        for param, arg in zip(parameters, args):
            args_dict[param.name] = arg

        user = args_dict.get("user")
        if user and hasattr(user, "id"):
            key_parts.append(f"user={user.id}")
        else:
            key_parts.append("user=anonymous")

        args_dict.pop("db", None)
        args_dict.pop("user", None)

        for k in sorted(args_dict.keys()):
            v = args_dict[k]
            key_parts.append(f"{k}={v}")

        # Если есть kwargs, также добавляем их
        for k in sorted(kwargs.keys()):
            v = kwargs[k]
            key_parts.append(f"{k}={v}")

        cache_key = ":".join(key_parts)
        return cache_key

async def clear_cache(user_id):
    await FastAPICache.clear(namespace=f'get_my_contacts:user={user_id}')

custom_key_builder = CustomKeyBuilder()
