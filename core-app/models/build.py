import uuid
from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from db import Base


class Build(Base):
    __tablename__ = "builds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid.uuid4()))
    repo_name: Mapped[str] = mapped_column(String(255), nullable=False,
                                            index=True)
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    workflow_run_id: Mapped[str | None] = mapped_column(String(50),
                                                         nullable=True,
                                                         unique=True)
    logs_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Values: RECEIVED, LOGS_FETCHED, CLASSIFIED, AGENT_RUNNING,
    #         COMPLETED, FAILED
    status: Mapped[str] = mapped_column(String(50), nullable=False,
                                         default="RECEIVED")
    log_size_bytes: Mapped[int | None] = mapped_column(BigInteger,
                                                        nullable=True)
    triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )