import os
import sys

from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
from termcolor import colored

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")),
)

from z_utils.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


class LLMFactory:
    # 存储不同配置的实例：{(base_url, api_key): client_instance}
    _instances: Dict[tuple, AsyncOpenAI] = {}

    @classmethod
    def get_llm(cls, override_params: Optional[Dict[str, Any]] = None) -> AsyncOpenAI:
        """
        获取 AsyncOpenAI 实例。
        基于配置信息进行缓存，配置相同则返回同一实例。
        """
        override_params = override_params or {}

        # 1. 汇总配置（优先级：override_params > .env）
        base_url = override_params.get("base_url") or os.getenv("BASE_URL")
        api_key = override_params.get("api_key") or os.getenv("API_KEY")

        # 客户端初始化参数
        timeout = float(override_params.get("timeout") or os.getenv("TIMEOUT", "60.0"))
        max_retries = int(
            override_params.get("max_retries") or os.getenv("MAX_RETRIES", "3")
        )

        # 2. 生成缓存 Key
        instance_key = (base_url, api_key, timeout, max_retries)

        # 3. 检查缓存逻辑
        if instance_key not in cls._instances:
            # 创建新实例
            new_instance = AsyncOpenAI(
                base_url=base_url,
                api_key=api_key,
                timeout=timeout,
                max_retries=max_retries,
            )
            cls._instances[instance_key] = new_instance
            logger.debug(
                colored("[LLMFactory] Created new AsyncOpenAI instance", "blue")
            )

        return cls._instances[instance_key]


llm_factory = LLMFactory()
async_client = llm_factory.get_llm()

if __name__ == "__main__":
    """
    uv run z_utils/llm_factory.py
    """
    import asyncio

    async def main():
        messages = [{"role": "user", "content": "Hello, Who are you?"}]

        response = await async_client.chat.completions.create(
            model=os.getenv("MODEL"),
            max_tokens=int(os.getenv("MAX_TOKENS", "65536")),
            temperature=os.getenv("TEMPERATURE"),
            messages=messages,
        )

        print(colored(f"{response.choices[0].message.content}", "light_yellow"))

    asyncio.run(main())
