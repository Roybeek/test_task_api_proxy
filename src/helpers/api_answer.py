"""Модуль для формирования ответов API"""
import logging
from typing import Dict, Any

__all__ = ['ApiAnswer']

from starlette.responses import JSONResponse


class ApiAnswer:
    """Класс для формирования ответов API"""

    @staticmethod
    def response(error: str = "", status_code: int = 200, data=None) -> JSONResponse:
        """Формирование ответа API, если возникла ошибка, передайте описание в строке error"""
        if error != "":
            answer = dict(
                status="error",
                detail=error
            )
            if data is not None:
                answer.update(dict(data=data))
        else:
            answer = dict(
                status="ok",
                data=data
            )

        return JSONResponse(
            status_code=status_code,
            content=answer
        )
