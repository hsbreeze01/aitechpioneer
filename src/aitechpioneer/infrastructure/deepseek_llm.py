import logging
from typing import Any, Dict, List, Optional

import httpx

from aitechpioneer.domain.ports import LLMServicePort
from aitechpioneer.settings import settings

logger = logging.getLogger(__name__)


class DeepSeekLLMService(LLMServicePort):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        max_retries: int = 3,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or settings.deepseek_api_key
        self.base_url = base_url
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("DeepSeek API key is required")

    async def generate_answer(
        self, question: str, context: str, conversation_history: Optional[List[Dict]] = None
    ) -> str:
        messages = self._build_messages(question, context, conversation_history)
        response = await self._call_api(messages)
        return response.get("content", "")

    async def generate_answer_with_sources(
        self,
        question: str,
        context: str,
        sources: List[Dict],
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        messages = self._build_messages_with_sources(
            question, context, sources, conversation_history
        )
        response = await self._call_api(messages)

        return {
            "answer": response.get("content", ""),
            "sources": sources,
            "model": self.model,
            "usage": response.get("usage", {}),
        }

    def _build_messages(
        self, question: str, context: str, conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict]:
        messages = []

        system_prompt = """你是一个专业的 AI 助手，擅长基于提供的上下文信息回答问题。
请根据以下上下文信息回答用户的问题。如果上下文中没有相关信息，请明确说明。
回答要准确、简洁、有条理。"""

        messages.append({"role": "system", "content": system_prompt})

        if conversation_history:
            messages.extend(conversation_history)

        user_message = f"""上下文信息：
{context}

问题：{question}

请基于上述上下文信息回答问题。"""

        messages.append({"role": "user", "content": user_message})

        return messages

    def _build_messages_with_sources(
        self,
        question: str,
        context: str,
        sources: List[Dict],
        conversation_history: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        messages = []

        system_prompt = """你是一个专业的 AI 助手，擅长基于提供的上下文信息回答问题。
请根据以下上下文信息回答用户的问题。如果上下文中没有相关信息，请明确说明。
回答要准确、简洁、有条理，并在适当的地方引用来源。"""

        messages.append({"role": "system", "content": system_prompt})

        if conversation_history:
            messages.extend(conversation_history)

        sources_text = "\n".join(
            [
                f"来源 {i + 1}: {source.get('content', '')[:200]}..."
                for i, source in enumerate(sources)
            ]
        )

        user_message = f"""上下文信息：
{context}

相关来源：
{sources_text}

问题：{question}

请基于上述上下文信息和相关来源回答问题，并在回答中适当引用来源。"""

        messages.append({"role": "user", "content": user_message})

        return messages

    async def _call_api(self, messages: List[Dict]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/v1/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()

                    result = response.json()
                    choices = result.get("choices", [])

                    if not choices:
                        raise ValueError("No response from DeepSeek API")

                    message = choices[0].get("message", {})
                    content = message.get("content", "")

                    usage = result.get("usage", {})

                    cleaned_usage = {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    }

                    return {
                        "content": content,
                        "usage": cleaned_usage,
                    }

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await self._backoff(attempt)

            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await self._backoff(attempt)

        raise RuntimeError("Failed to get response from DeepSeek API after retries")

    async def _backoff(self, attempt: int) -> None:
        import asyncio

        backoff_time = min(2**attempt, 10)
        logger.info(f"Backing off for {backoff_time} seconds...")
        await asyncio.sleep(backoff_time)
