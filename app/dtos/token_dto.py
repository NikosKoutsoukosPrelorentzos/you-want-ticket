from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TokenDTO(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[UUID] = None
