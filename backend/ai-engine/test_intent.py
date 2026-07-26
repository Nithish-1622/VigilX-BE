import asyncio
from llm.client import LLMClient
from services.prompt_service import PromptService
from services.intent_service import IntentService

async def main():
    p = PromptService('prompts')
    client = LLMClient()
    s = IntentService(p, client)
    res = await s.detect("what is Lucky Bal's age", [])
    print("INTENT:", res)

asyncio.run(main())
