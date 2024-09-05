from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.responses import JSONResponse

from app.database import Base, async_session, engine
from app.crud import delete_document
from elastic.es import (create_index, delete_document_from_index,
                    search_in_index, index_documents)
from app.schemas import Document as DocumentSchema
from app.models import Document as DocumentModel

app = FastAPI()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event('startup')
async def on_startup():
    await init_db()
    await create_index()
    await create_index_documents()


async def get_db():
    async with async_session() as session:
        yield session

async def create_index_documents():
    await index_documents(get_db)


@app.get('/documents/', response_model=List[DocumentSchema])
async def read_documents(query: str, db: AsyncSession = Depends(get_db)):
    es_results = await search_in_index(query)
    documents = []
    for hit in es_results:
        result = await db.execute(select(DocumentModel)
                                  .filter_by(id=hit['_source']['id']))
        document = result.scalar()
        if document:
            documents.append(document)
    return [DocumentSchema.from_orm(doc) for doc in documents]


@app.delete('/documents/{document_id}')
async def delete_document(document_id: int,
                          db: AsyncSession = Depends(get_db)):
    document = await delete_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail='Document not found')
    await delete_document_from_index(document_id)
    return JSONResponse(content={'detail': 'Document deleted'})
