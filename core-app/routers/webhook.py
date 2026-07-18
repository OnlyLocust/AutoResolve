from fastapi import APIRouter, Header, Request, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.webhook_payload import WebhookPayload
from services.webhook_verification import verify_signature
from services.build_ingestion import ingest_build
from db import get_db
from config import settings

router = APIRouter()

@router.post("/api/webhooks/github")
async def handle_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
    x_github_delivery: str = Header(None),
    session: AsyncSession = Depends(get_db)
):
    # Only process workflow_run events
    if x_github_event != "workflow_run":
        return {"message": f"Ignored event: {x_github_event}"}
    
    # 1. Read raw body and verify HMAC signature
    payload_body = await request.body()
    verify_signature(payload_body, settings.webhook_secret, x_hub_signature_256)
    
    # 2. Parse the validated JSON
    data = await request.json()
    payload = WebhookPayload(**data)
    
    # 3. Filter for failed workflows
    if payload.action != "completed" or payload.workflow_run.conclusion != "failure":
        return {"message": "Workflow not a failure, ignoring"}
    
    # 4. Trigger ingestion without blocking the GitHub response
    background_tasks.add_task(ingest_build, payload, session)
    
    return {"message": "Webhook received, build ingestion started"}