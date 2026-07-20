from sqlalchemy.ext.asyncio import AsyncSession
from schemas.webhook_payload import WebhookPayload
from models.build import Build
from repositories.build_repository import create_build, update_build_status, get_build_by_id
from services.github_log_fetcher import fetch_and_extract_logs
from services.log_chunking import chunk_and_save_logs

async def ingest_build(payload: WebhookPayload, session: AsyncSession):
    run = payload.workflow_run
    
    # Idempotency guard: skip if this build was already ingested (duplicate webhook)
    existing = await get_build_by_id(session, str(run.id))
    if existing:
        print(f"Build {run.id} already exists (status={existing.status}), skipping duplicate webhook.")
        return
    
    build = Build(
        id=str(run.id),
        repo_name=payload.repository.full_name,
        commit_sha=run.head_sha,
        workflow_name=run.name,
        status="RECEIVED"
    )
    
    await create_build(session, build)
    
    # Capture plain values before any rollback can expire the ORM object
    build_id = build.id
    repo_name = build.repo_name
    print(f"Build {build_id} saved successfully! Ready to fetch logs...")
    
    # --- NEW DAY 3 PIPELINE ---
    try:
        extracted = await fetch_and_extract_logs(repo_name, build_id, run.logs_url)
        await chunk_and_save_logs(session, build_id, extracted)
    except Exception as e:
        print(f"Error processing logs: {e}")
        await session.rollback()
        await update_build_status(session, build_id, "FAILED_LOG_FETCH")    