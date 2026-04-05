import uuid
from src.services.llm_service import LLMService
from src.services.memory_service import MemoryService


class ConversationService:
    """Оркестратор — связывает LLM и память в единый диалог."""

    def __init__(self):
        self.llm = LLMService()
        self.memory = MemoryService()
        self.current_session_id: str | None = None

    async def start_session(self) -> str:
        """Начинает новую сессию разговора."""
        self.current_session_id = str(uuid.uuid4())
        await self.memory.create_session(self.current_session_id)
        return self.current_session_id

    async def chat(self, user_message: str, speaker: str | None = None) -> str:
        """Основной метод — обрабатывает сообщение пользователя и возвращает ответ."""

        if not self.current_session_id:
            await self.start_session()

        # 1. Достаём историю текущего разговора
        history = await self.memory.get_conversation_history(self.current_session_id)

        # 2. Ищем релевантные воспоминания
        memories_list = await self.memory.search_memories(user_message, speaker=speaker)
        memories_text = None
        if memories_list:
            memories_text = "\n".join(
                f"- [{m['category']}] {m['content']}" for m in memories_list
            )

        # 3. Генерируем ответ
        response = await self.llm.generate(
            user_message=user_message,
            conversation_history=history,
            memories=memories_text,
        )

        # 4. Сохраняем оба сообщения в историю
        await self.memory.save_message(self.current_session_id, "user", user_message, speaker)
        await self.memory.save_message(self.current_session_id, "assistant", response)

        # 5. Извлекаем и сохраняем новые воспоминания из разговора
        await self._extract_memories(user_message, speaker)

        return response

    async def _extract_memories(self, user_message: str, speaker: str | None = None):
        """Извлекает важные факты из сообщения для долгосрочной памяти.

        Пока простая эвристика. Позже можно заменить на LLM-экстрактор.
        """
        # Ключевые слова, указывающие на факт о пользователе
        fact_indicators = [
            "меня зовут", "мне нравится", "я люблю", "я работаю", "я учусь",
            "я живу", "мой любимый", "я ненавижу", "я не люблю", "у меня есть",
            "мне", "лет", "я из", "я родился", "мой день рождения",
        ]

        message_lower = user_message.lower()
        for indicator in fact_indicators:
            if indicator in message_lower:
                await self.memory.save_memory(
                    content=user_message,
                    category="факт",
                    speaker=speaker,
                    importance=7,
                )
                break

    async def end_session(self):
        """Завершает текущую сессию."""
        if self.current_session_id:
            await self.memory.end_session(self.current_session_id)
            self.current_session_id = None
