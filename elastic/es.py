import sys, os

from elasticsearch import AsyncElasticsearch
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from elasticsearch.helpers import async_bulk

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from app.schemas import Document as DocumentSchema
from app.models import Document as Document
from app.database import async_session

es = AsyncElasticsearch(hosts=['http://localhost:9200'])
index_name = 'documents'


async def create_index():
    mapping = {
        "mappings": {
            "properties": {
                "created_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time"
                },
                "text": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "rubrics": {
                    "type": "keyword"
                }
            }
        }
    }

    await es.indices.create(index=index_name, body=mapping, ignore=400)


async def delete_document_from_index(document_id: int):
    await es.delete(index=index_name, id=document_id)


async def get_document_from_db(session: AsyncSession):
    async with async_session() as session:
        query = await session.execute(select(Document))
        documents = query.scalars().all()
    return documents


async def index_documents(session: AsyncSession):
    documents = await get_document_from_db(session=session)
    bulk_data = []
    for document in documents:
        document_schema = DocumentSchema.from_orm(document)
        document_dict = document_schema.dict()
        
        action = {
            "_index": index_name,
            "_id": document.id,
            "_source": document_dict
        }
        bulk_data.append(action)

    success, failed = await async_bulk(es, bulk_data)
    print(f"Successfully indexed: {success}, Failed: {failed}")

 


async def search_in_index(query: str):
    response = await es.search(
        index=index_name,
        query={'match': {'text': query}},
        size=20,
        sort=[{'created_date': {'order': 'desc'}}]
    )
    print("Query:", query)
    print("Response:", response)
    return response['hits']['hits']
