import uuid

from fastapi import APIRouter, UploadFile, Depends
from services.base import get_search_service, SearchService


router = APIRouter()


@router.post(
    '/search',
    description='Метод выполняет поиск по голосовому запросу',
)
async def search_data(
    file: UploadFile,
    service: SearchService = Depends(get_search_service),
) -> uuid.UUID:

    result = await service.create_task(
        audio_file=file,
    )
    return result


@router.get(
    '/search/result',
    description='Метод возвращает результаты поиска из БД',
)
async def get_data(
    process_id: str,
    service: SearchService = Depends(get_search_service),
):
    # TODO: Необходимо возвращать модель
    result = await service.get_status_task(
        process_id=process_id,
    )
