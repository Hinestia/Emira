import aiosqlite
from datetime import datetime
from src.config import DATABASE_PATH


class MemoryService:
    """Управляет долгосрочной памятью Эмиры."""

    def _connect(self):
        return aiosqlite.connect(DATABASE_PATH)

    # ── Сообщения (краткосрочная память) ──

    async def save_message(self, session_id: str, role: str, content: str, speaker: str | None = None):
        """Сохраняет сообщение в историю."""
        async with self._connect() as db:
            await db.execute(
                "INSERT INTO messages (session_id, role, content, speaker) VALUES (?, ?, ?, ?)",
                (session_id, role, content, speaker),
            )
            await db.commit()

    async def get_conversation_history(self, session_id: str, limit: int = 20) -> list[dict]:
        """Возвращает последние N сообщений из сессии."""
        async with self._connect() as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            )
            rows = await cursor.fetchall()

        # Переворачиваем чтобы шли в хронологическом порядке
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    # ── Воспоминания (долгосрочная память) ──

    async def save_memory(self, content: str, category: str, speaker: str | None = None, importance: int = 5):
        """Сохраняет воспоминание."""
        async with self._connect() as db:
            await db.execute(
                "INSERT INTO memories (speaker, category, content, importance) VALUES (?, ?, ?, ?)",
                (speaker, category, content, importance),
            )
            await db.commit()

    async def search_memories(self, query: str, speaker: str | None = None, limit: int = 10) -> list[dict]:
        """Ищет воспоминания по ключевым словам.

        Пока простой LIKE-поиск. Позже можно заменить на векторный поиск.
        """
        async with self._connect() as db:
            db.row_factory = aiosqlite.Row

            # Разбиваем запрос на слова для поиска
            words = query.lower().split()
            conditions = " OR ".join(["LOWER(content) LIKE ?" for _ in words])
            params = [f"%{word}%" for word in words]

            if speaker:
                sql = f"SELECT * FROM memories WHERE speaker = ? AND ({conditions}) ORDER BY importance DESC, last_accessed DESC LIMIT ?"
                params = [speaker] + params + [limit]
            else:
                sql = f"SELECT * FROM memories WHERE ({conditions}) ORDER BY importance DESC, last_accessed DESC LIMIT ?"
                params = params + [limit]

            cursor = await db.execute(sql, params)
            rows = await cursor.fetchall()

        return [
            {
                "id": row["id"],
                "category": row["category"],
                "content": row["content"],
                "importance": row["importance"],
                "speaker": row["speaker"],
            }
            for row in rows
        ]

    async def get_all_memories(self, speaker: str | None = None, limit: int = 20) -> list[dict]:
        """Возвращает все воспоминания (или для конкретного собеседника)."""
        async with self._connect() as db:
            db.row_factory = aiosqlite.Row

            if speaker:
                cursor = await db.execute(
                    "SELECT * FROM memories WHERE speaker = ? ORDER BY importance DESC LIMIT ?",
                    (speaker, limit),
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM memories ORDER BY importance DESC LIMIT ?",
                    (limit,),
                )
            rows = await cursor.fetchall()

        return [
            {
                "id": row["id"],
                "category": row["category"],
                "content": row["content"],
                "importance": row["importance"],
                "speaker": row["speaker"],
            }
            for row in rows
        ]

    # ── Сессии ──

    async def create_session(self, session_id: str):
        """Создаёт новую сессию разговора."""
        async with self._connect() as db:
            await db.execute("INSERT INTO sessions (id) VALUES (?)", (session_id,))
            await db.commit()

    async def end_session(self, session_id: str):
        """Завершает сессию."""
        async with self._connect() as db:
            await db.execute(
                "UPDATE sessions SET ended_at = ? WHERE id = ?",
                (datetime.now().isoformat(), session_id),
            )
            await db.commit()
