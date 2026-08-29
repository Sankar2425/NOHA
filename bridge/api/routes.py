from unittest import result

from fastapi import APIRouter
from pydantic import BaseModel

from bridge.services.runtime_service import process_command

router = APIRouter()

class CommandRequest(BaseModel):
    command: str

@router.post("/command")
async def command_endpoint(data: CommandRequest):
    result = await process_command(data.command)

    return result
