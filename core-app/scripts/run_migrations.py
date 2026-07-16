#!/usr/bin/env python3
"""
Migration runner for DeployBrain.
Applies all V*.sql files in migrations/ in filename order.
Tracks applied filenames in schema_migrations table.

Usage (from deploybrain/ root):
    python core-app/scripts/run_migrations.py

Requirements:
    pip install asyncpg python-dotenv
"""

import asyncio
import os
import sys
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

# Load infra/.env.local relative to this script's location
_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_ROOT / "infra" / ".env.local")

RAW_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/deploybrain",
).replace("postgresql+asyncpg://", "postgresql://")

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


async def run():
    print(f"Connecting to: {RAW_URL.split('@')[-1]}")  # hide credentials
    conn = await asyncpg.connect(RAW_URL)

    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename   VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMPTZ  DEFAULT NOW()
            )
        """)

        applied = {
            r["filename"]
            for r in await conn.fetch(
                "SELECT filename FROM schema_migrations"
            )
        }

        files = sorted(MIGRATIONS_DIR.glob("V*.sql"))
        if not files:
            print("No migration files found in", MIGRATIONS_DIR)
            return

        ok = skipped = 0
        for f in files:
            if f.name in applied:
                print(f"  ⏭  {f.name}")
                skipped += 1
                continue

            print(f"  ▶  {f.name} ...", end=" ", flush=True)
            sql = f.read_text()
            try:
                async with conn.transaction():
                    await conn.execute(sql)
                    await conn.execute(
                        "INSERT INTO schema_migrations(filename) VALUES($1)",
                        f.name,
                    )
                print("✅")
                ok += 1
            except Exception as exc:
                print(f"❌ FAILED\n{exc}")
                sys.exit(1)

        print(f"\nDone — {ok} applied, {skipped} skipped.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())
