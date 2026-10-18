import asyncio
from fastapi.responses import StreamingResponse
from fastapi import APIRouter

router = APIRouter(tags=["StreamingResponse"])

async def generate_text():
    words = ["Hello", " from", " your", " FastAPI", " server."]
    
    for word in words:
        yield word
        await asyncio.sleep(0.3)


@router.get("/stream")
async def stream_response():
    return StreamingResponse(
        generate_text(),
        media_type="text/plain"
    )