import uuid
from typing import Optional

from pydantic import BaseModel


class TokenDTO(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[uuid] = None
