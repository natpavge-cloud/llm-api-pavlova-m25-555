from app.repositories.users import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.core.errors import ConflictError, UnauthorizedError, NotFoundError
from app.db.models import User


class AuthUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def register(self, email: str, password: str) -> User:

        # Проверка, что email не занят
        existing_user = await self._user_repo.get_by_email(email)
        if existing_user:
            raise ConflictError(f"Email {email} уже зарегистрирован")

        # Хеширование пароля
        password_hash = hash_password(password)

        # Создание пользователя через репозиторий
        user = await self._user_repo.create(
            email=email, password_hash=password_hash, role="user"
        )

        # Возвращаем объект пользователя, чтобы эндпоинт мог вернуть UserPublic
        return user

    async def login(self, email: str, password: str) -> dict:
        """
        Вход пользователя в систему. Возвращает токен.
        """
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedError("Неверный email или пароль")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Неверный email или пароль")

        # Генерация JWT токена (только при логине)
        access_token = create_access_token(user_id=user.id, role=user.role)

        return {"access_token": access_token, "token_type": "bearer"}

    async def get_user_profile(self, user_id: int) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")

        return user
