import asyncio
import sys
import time

from app.db import db


async def connect():
    sys.stdout.write("Attempting database connection...\n")

    retries: int = 30
    sleep_interval: int = 2
    conn = None

    for i in range(1, retries + 1):
        sys.stdout.write(f"Attempt {i}...\n")
        try:
            conn = await db.engine.connect()
            break
        except:
            i += 1
            time.sleep(sleep_interval)

    if conn:
        sys.stdout.write("Connected...\n")
        await conn.close()
    else:
        sys.stderr.write("Failed to connect...\n")


if __name__ == "__main__":
    asyncio.run(connect())
