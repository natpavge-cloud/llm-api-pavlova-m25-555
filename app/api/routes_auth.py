from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_usecase, get_current_user_id
from app.usecases.auth import AuthUseCase

from app.schemas.user import RegisterRequest, UserPublic, TokenResponse
from app.core.errors import ConflictError, UnauthorizedError, NotFoundError


router = APIRouter(tags=["Аутентификация"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest, auth_usecase: AuthUseCase = Depends(get_auth_usecase)
):

    try:
        user = await auth_usecase.register(data.email, data.password)
        return user
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_usecase: AuthUseCase = Depends(get_auth_usecase),
):
    """
    Вход в систему (OAuth2-совместимый эндпоинт).
    """
    try:
        result = await auth_usecase.login(form_data.username, form_data.password)
        return result
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserPublic)
async def get_profile(
    user_id: int = Depends(get_current_user_id),
    auth_usecase: AuthUseCase = Depends(get_auth_usecase),
):
    """
    Получить профиль текущего пользователя.
    """
    try:
        user = await auth_usecase.get_user_profile(user_id)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
