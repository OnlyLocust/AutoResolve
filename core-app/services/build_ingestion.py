from sqlalchemy.ext.asyncio import AsyncSession
from schemas.webhook_payload import WebhookPayload
from models.build import Build
from repositories.build_repository import create_build

async def ingest_build(payload: WebhookPayload, session: AsyncSession):
    run = payload.workflow_run
    
    build = Build(
        id=str(run.id),
        repo_name=payload.repository.full_name,
        commit_sha=run.head_sha,
        workflow_name=run.name,
        status="RECEIVED"
    )
    
    await create_build(session, build)
    print(f"Build {build.id} saved successfully! Ready to fetch logs from: {run.logs_url}")