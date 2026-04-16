from typing import Optional, List, Dict, Any
import re

from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUseCase:
    def __init__(
        self, message_repo: ChatMessageRepository, llm_client: OpenRouterClient
    ):

        self._message_repo = message_repo
        self._llm_client = llm_client

    async def ask_llm(
        self,
        user_id: int,
        prompt: str,
        system: Optional[str] = None,
        max_history: int = 10,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:

        # 1. Получить историю сообщений для контекста (БЕЗ текущего prompt)
        history = await self._message_repo.get_recent_messages(
            user_id, limit=max_history
        )

        # 2. Сформировать массив messages для LLM
        messages = []

        # Добавить системную инструкцию с требованием suggested questions
        system_content = system or "Ты полезный ассистент."
        system_content += (
            "\n\nПосле основного ответа предложи два варианта следующего вопроса от лица пользователя. "
            "Формат строго следующий (включая фигурные скобки):\n"
            "{Вопрос 1}\n{Вопрос 2}"
        )
        messages.append({"role": "system", "content": system_content})

        # Добавить историю (уже в хронологическом порядке)
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

        # Добавить текущий prompt как user-сообщение
        messages.append({"role": "user", "content": prompt})

        # 3. Сохранить текущий prompt в БД (роль "user")
        await self._message_repo.add_message(
            user_id=user_id, role="user", content=prompt
        )

        # 4. Отправить запрос в OpenRouter
        llm_answer = await self._llm_client.chat_completion(
            messages=messages, temperature=temperature
        )

        # 5. Извлечь suggested questions из ответа
        suggested_questions = self._extract_suggested_questions(llm_answer)

        # Очистить ответ от suggested questions
        clean_answer = self._remove_suggested_questions(llm_answer)

        # 6. Сохранить ответ LLM в БД (роль "assistant")
        await self._message_repo.add_message(
            user_id=user_id, role="assistant", content=clean_answer
        )

        return {"answer": clean_answer, "suggested_questions": suggested_questions}

    async def clear_history(self, user_id: int) -> int:

        deleted_count = await self._message_repo.delete_user_history(user_id)
        return deleted_count

    def _extract_suggested_questions(self, llm_response: str) -> List[str]:

        # Паттерн: {текст}\n{текст} в конце строки
        pattern = r"\{([^}]+)\}\s*\n\s*\{([^}]+)\}\s*$"
        match = re.search(pattern, llm_response, re.MULTILINE)

        if match:
            return [match.group(1).strip(), match.group(2).strip()]

        return []

    def _remove_suggested_questions(self, llm_response: str) -> str:

        # Удаляем паттерн {вопрос}\n{вопрос} в конце
        pattern = r"\{[^}]+\}\s*\n\s*\{[^}]+\}\s*$"
        clean = re.sub(pattern, "", llm_response, flags=re.MULTILINE)

        return clean.strip()
