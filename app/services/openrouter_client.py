from typing import List, Dict
import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    def __init__(self):

        self.base_url = settings.OPENROUTER_BASE_URL
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.site_url = settings.OPENROUTER_SITE_URL
        self.app_name = settings.OPENROUTER_APP_NAME

    def _build_headers(self) -> Dict[str, str]:

        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
            "Content-Type": "application/json",
        }

    async def chat_completion(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> str:

        url = f"{self.base_url}/chat/completions"
        headers = self._build_headers()

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)

                # Проверка успешности запроса
                if response.status_code != 200:
                    error_detail = response.text
                    raise ExternalServiceError(
                        message=f"HTTP {response.status_code}: {error_detail}",
                        service_name="OpenRouter",
                    )

                # Извлечение ответа
                data = response.json()
                answer = data["choices"][0]["message"]["content"]

                return answer

        except httpx.RequestError as e:
            raise ExternalServiceError(
                message=f"Ошибка соединения: {str(e)}", service_name="OpenRouter"
            )
        except KeyError as e:
            raise ExternalServiceError(
                message=f"Неожиданный формат ответа: отсутствует поле {str(e)}",
                service_name="OpenRouter",
            )
        except Exception as e:
            raise ExternalServiceError(
                message=f"Неизвестная ошибка: {str(e)}", service_name="OpenRouter"
            )
