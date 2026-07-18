import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.build import Build


async def create_build(session: AsyncSession, build: Build) -> Build:
    session.add(build)
    # Using commit instead of flush so the data is permanently saved to the DB right now
    await session.commit()
    await session.refresh(build)
    return build


async def get_build_by_id(session: AsyncSession,
                           build_id: str) -> Optional[Build]:
    result = await session.execute(
        select(Build).where(Build.id == build_id)
    )
    return result.scalar_one_or_none()


async def get_build_by_workflow_run_id(
    session: AsyncSession, workflow_run_id: str
) -> Optional[Build]:
    result = await session.execute(
        select(Build).where(Build.workflow_run_id == workflow_run_id)
    )
    return result.scalar_one_or_none()


async def update_build_status(
    session: AsyncSession, build_id: str, status: str, **kwargs
) -> None:
    await session.execute(
        update(Build)
        .where(Build.id == build_id)
        .values(status=status, **kwargs)
    )


async def get_recent_builds(
    session: AsyncSession, limit: int = 20, offset: int = 0
) -> List[Build]:
    result = await session.execute(
        select(Build)
        .order_by(Build.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())