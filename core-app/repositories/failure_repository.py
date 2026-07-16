from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.failure import Failure
from models.build import Build


async def create_failure(session: AsyncSession, data: dict) -> Failure:
    failure = Failure(**data)
    session.add(failure)
    await session.flush()
    return failure


async def get_failure_by_id(
    session: AsyncSession, failure_id: str
) -> Optional[Failure]:
    result = await session.execute(
        select(Failure).where(Failure.id == failure_id)
    )
    return result.scalar_one_or_none()


async def get_failure_by_build_id(
    session: AsyncSession, build_id: str
) -> Optional[Failure]:
    result = await session.execute(
        select(Failure).where(Failure.build_id == build_id)
    )
    return result.scalar_one_or_none()


async def update_failure_status(
    session: AsyncSession, failure_id: str, agent_status: str, **kwargs
) -> None:
    await session.execute(
        update(Failure)
        .where(Failure.id == failure_id)
        .values(agent_status=agent_status, **kwargs)
    )


async def get_resolved_failures_by_type(
    session: AsyncSession,
    repo_name: str,
    failure_type: str,
    limit: int = 3,
) -> List[Failure]:
    """Used by GetHistoryTool on Day 11."""
    result = await session.execute(
        select(Failure)
        .join(Build, Build.id == Failure.build_id)
        .where(
            Build.repo_name == repo_name,
            Failure.failure_type == failure_type,
            Failure.agent_status == "FIX_MERGED",
        )
        .order_by(Failure.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())