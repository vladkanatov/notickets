import sys
sys.path.append("/home/lon8/python/notickets")

from datamining.module.manager.session import AsyncSession
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from decouple import config
import asyncio


SERVER_HOST=config("SERVER_HOST")
SERVER_PORT= config("SERVER_PORT")


# Функция для получения списка названий площадок из базы данных
# @cached(cache=TTLCache(maxsize=128, ttl=600))
async def get_venue_names_from_database():
    async with AsyncSession() as session:
        r = await session.get(f'http://{SERVER_HOST}:{SERVER_PORT}/get_venues/')
        data = r.json()
        
        result = list(data.values())
    
        return result


async def create_venue(input_venue_name: str):
    async with AsyncSession() as session:
        r = await session.post(f'http://{SERVER_HOST}:{SERVER_PORT}/create_venue/', json= {'venue': input_venue_name})
        
        data = r.json()
        lastrowid = data['venue_id']
        
        return lastrowid
        
# Функция для поиска или создания площадки
async def find_or_create_venue(input_venue_name: str) -> int:
    venue_names = await get_venue_names_from_database()

    # Преобразуем исходные названия площадок в векторы TF-IDF
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform(venue_names)
    except ValueError:
        return await create_venue(input_venue_name)

    # Преобразуем новое название площадки в вектор TF-IDF
    new_tfidf_vector = vectorizer.transform([input_venue_name])

    # Расчет косинусного сходства между новым названием и всеми площадками
    cosine_similarities = linear_kernel(new_tfidf_vector, tfidf_matrix).flatten()

    # Находим индекс площадки с наивысшим косинусным сходством
    best_match_index = cosine_similarities.argmax()

    # Если ближайшее соответствие имеет достаточно высокий балл, возвращаем id
    if cosine_similarities[best_match_index] >= 0.8:
        # Индексация начинается с 0, поэтому добавляем 1.
        venue_id = int(best_match_index + 1)
    else:
        # Если не найдено подходящего соответствия, создаем новую площадку
        venue_id = await create_venue(input_venue_name)
        venue_id = int(venue_id)

    return venue_id


# Пример использования

async def main():
    input_venue_name = "Театр Ленком"
    venue_id = await find_or_create_venue(input_venue_name)
    print(f"ID площадки '{input_venue_name}': {venue_id}")

if __name__ == '__main__':
    asyncio.run(main())
