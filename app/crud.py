from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from app.models import Document


async def get_documents(db: AsyncSession, skip: int = 0, limit: int = 20):
    result = await db.execute(select(Document).offset(skip).limit(limit))
    return result.scalars().all()


async def delete_document(db: AsyncSession, document_id: int):
    try:
        result = await db.execute(select(Document).filter_by(id=document_id))
        document = result.scalar_one()
    except NoResultFound:
        return None

    await db.delete(document)
    await db.commit()
    return document

