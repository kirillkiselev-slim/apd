import sys, os

from elasticsearch import AsyncElasticsearch
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from elasticsearch.helpers import async_bulk

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from app.schemas import Document as DocumentSchema
from app.models import Document as Document
from app.database import async_session

es = AsyncElasticsearch(hosts=['http://host.docker.internal:9200'])
index_name = 'documents'


async def create_index():
    """Создает индекс в Elasticsearch с заданной схемой для документов."""
    mapping = {
        'mappings': {
            'properties': {
                'created_date': {
                    'type': 'date',
                    'format': 'yyyy-MM-dd HH:mm:ss||strict_date_optional_time'
                },
                'text': {
                    'type': 'text',
                    'analyzer': 'standard'
                },
                'rubrics': {
                    'type': 'keyword'
                }
            }
        }
    }

    await es.indices.create(index=index_name, body=mapping, ignore=400)


async def delete_document_from_index(document_id: int):
    """Удаляет документ из индекса Elasticsearch по его ИД."""
    await es.delete(index=index_name, id=document_id)


async def get_document_from_db(session: AsyncSession):
    """Получает все документы из БД с использованием асинхронной сессии."""
    async with async_session() as session:
        query = await session.execute(select(Document))
        documents = query.scalars().all()
    return documents


async def index_documents(session: AsyncSession):
    """Индексирует документы из БД в Elasticsearch через bulk-запрос."""
    documents = await get_document_from_db(session=session)
    bulk_data = []
    for document in documents:
        document_schema = DocumentSchema.model_validate(document)
        document_dict = document_schema.model_dump()
        
        action = {
            "_index": index_name,
            "_id": document.id,
            "_source": document_dict
        }
        bulk_data.append(action)

    await async_bulk(es, bulk_data)


async def search_in_index(query: str):
    """Выполняет поиск документов в индексе Elasticsearch по текстовому запросу."""
    response = await es.search(
        index=index_name,
        query={'match': {'text': query}},
        size=20,
        sort=[{'created_date': {'order': 'desc'}}]
    )
    print("Query:", query)
    print("Response:", response)
    return response['hits']['hits']
