import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from db import Base


class Failure(Base):
    __tablename__ = "failures"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid.uuid4()))
    build_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("builds.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    # Values: DEPENDENCY_CONFLICT, TEST_REGRESSION, COMPILATION_ERROR,
    #         ENV_MISMATCH, OOM, TIMEOUT
    failure_type: Mapped[str | None] = mapped_column(String(50),
                                                      nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Stored as a JSON array of strings
    evidence_lines: Mapped[list | None] = mapped_column(JSONB,
                                                         nullable=True)
    # Values: PENDING, AGENT_RUNNING, FIX_GENERATED, FIX_MERGED,
    #         NEEDS_REVIEW, ERROR, CLASSIFICATION_FAILED
    agent_status: Mapped[str] = mapped_column(String(50), nullable=False,
                                               default="PENDING")
    pr_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    llm_provider_used: Mapped[str | None] = mapped_column(String(50),
                                                           nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )