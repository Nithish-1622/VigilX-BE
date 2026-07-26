import asyncio
from v2.orchestrator import V2AIOrchestrator
from schemas.conversation import AskRequest

async def run():
    o = V2AIOrchestrator()
    req = AskRequest(session_id='cd39651d-aae', user_id='officer-001', question='What is Siddharth Lala age?')
    resp = await o.run(req)
    print(resp)

asyncio.run(run())
