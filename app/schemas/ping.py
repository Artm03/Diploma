import typing as tp

from pydantic import BaseModel


class Ping(BaseModel):
    message: tp.Optional[str]
