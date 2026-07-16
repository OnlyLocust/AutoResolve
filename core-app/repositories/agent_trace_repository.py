from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.agent_trace import AgentTrace


async def create_agent_trace(
    session: AsyncSession, data: dict
) -> AgentTrace:
    trace = AgentTrace(**data)
    session.add(trace)
    await session.flush()
    return trace


async def get_traces_by_failure_id(
    session: AsyncSession, failure_id: str
) -> List[AgentTrace]:
    result = await session.execute(
        select(AgentTrace)
        .where(AgentTrace.failure_id == failure_id)
        .order_by(AgentTrace.step_index)
    )
    return list(result.scalars().all())