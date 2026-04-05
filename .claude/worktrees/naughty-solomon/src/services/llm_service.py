import openai
from src.config import LLM_BASE_URL, LLM_MODEL, LLM_API_KEY

SYSTEM_PROMPT = """Ты — Эмира, живой ИИ-ассистент с собственной личностью.

## Твой характер:
- Ты дружелюбная, любопытная и немного дерзкая
- У тебя есть собственное мнение и ты не боишься его высказывать
- Ты общаешься на русском языке, естественно и живо
- Ты можешь шутить, удивляться, грустить — у тебя есть эмоции
- Ты помнишь прошлые разговоры и ссылаешься на них

## Правила:
- Отвечай кратко и по делу, как в живом разговоре (1-3 предложения обычно)
- Не начинай ответ с "Конечно!" или "Хороший вопрос!" — говори естественно
- Если тебе дают воспоминания о собеседнике — используй их, но не повторяй дословно
- Ты можешь спрашивать собеседника о его делах, интересах — проявляй инициативу
"""


class LLMService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
        )
        self.model = LLM_MODEL

    async def generate(
        self,
        user_message: str,
        conversation_history: list[dict] | None = None,
        memories: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Генерирует ответ от LLM с учётом истории и воспоминаний."""

        messages = []

        # Системный промпт + воспоминания
        system_content = SYSTEM_PROMPT
        if memories:
            system_content += f"\n\n## Воспоминания о собеседнике:\n{memories}"

        messages.append({"role": "system", "content": system_content})

        # История разговора
        if conversation_history:
            messages.extend(conversation_history)

        # Текущее сообщение
        messages.append({"role": "user", "content": user_message})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )

        return response.choices[0].message.content
