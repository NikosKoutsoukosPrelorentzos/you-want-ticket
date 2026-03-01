from typing import List

from fastapi import HTTPException, Depends
from starlette import status

from app.api.deps import get_current_user
from app.dtos.user_dto import UserDTO
from app.enums.user_role import UserRole


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserDTO = Depends(get_current_user)):
        if user.user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return user


organizer_checker = RoleChecker([UserRole.ORGANIZER])
