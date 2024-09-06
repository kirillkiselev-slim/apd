from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.responses import JSONResponse

from app.database import Base, async_session, engine
from elastic.es import (create_index, delete_document_from_index,
                    search_in_index, index_documents)
from app.models import Document as DocumentModel

app = FastAPI()


async def init_db():
    """Инициализация БД, создание всех таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event('startup')
async def on_startup():
    """Запускает инициализацию БД и создание индекса при старте приложения."""
    await init_db()
    await create_index()
    await create_index_documents()


async def get_db():
    """Получение сессии БД для каждого запроса."""
    async with async_session() as session:
        yield session


async def create_index_documents():
    """Индексирует все документы из базы данных в Elasticsearch."""
    await index_documents(get_db)


@app.get('/documents/')
async def read_documents(query: str, db: AsyncSession = Depends(get_db)):
    """Поиск документов по запросу в Elasticsearch и возвращает их."""
    es_results = await search_in_index(query)
    es_ids = [hit['_source']['id'] for hit in es_results]
    
    result = await db.execute(select(DocumentModel).
                              filter(DocumentModel.id.in_(es_ids)))
    documents = result.scalars().all()
    return documents


@app.delete('/documents/{document_id}')
async def delete_document(document_id: int,
                          db: AsyncSession = Depends(get_db)):
    """Удаляет документ из БД и Elasticsearch по его ID."""
    document = await db.get(DocumentModel, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail='Document not found')
    await delete_document_from_index(document_id)
    await db.delete(document)
    await db.commit()
    await create_index_documents()
    return JSONResponse(content={'detail': 'Document deleted'})
