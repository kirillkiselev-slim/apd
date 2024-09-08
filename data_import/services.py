import os, sys
import asyncio

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from app.models import Document
from app.schemas import Document as DocumentSchema
from app.database import engine


posts = os.path.abspath('data_import/posts.csv')

df = pd.read_csv(posts)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def load_data():
    """Загружает данные из CSV в БД с асинхронной сессией SQLAlchemy."""
    async with AsyncSessionLocal() as async_session:
        try:
            for _, row in df.iterrows():
                document = Document(
                    text=row['text'],
                    rubrics=row['rubrics'],
                    created_date=datetime.strptime(row['created_date'],
                                                   '%Y-%m-%d %H:%M:%S')
                )
                async_session.add(document)

            await async_session.commit()
        except Exception:
            await async_session.rollback()


asyncio.run(load_data())
