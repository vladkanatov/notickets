import aiomysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from cachetools import cached, TTLCache
from decouple import config

HOST = config('HOST')
DB = config('DB')
PASSWORD = config('PASSWORD')
LOGIN = config('LOGIN')


# Функция для получения списка названий площадок из базы данных
@cached(cache=TTLCache(maxsize=128, ttl=600))
async def get_venue_names_from_database():
    async with aiomysql.create_pool(host=HOST, port=3306,
                                    user=LOGIN, password=PASSWORD,
                                    db=DB) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT venue_name FROM venues")
                result = await cur.fetchall()
                return [row[0] for row in result]


async def create_venue(input_venue_name: str):
    async with aiomysql.create_pool(host=HOST, port=3306,
                                    user=LOGIN, password=PASSWORD,
                                    db=DB) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("INSERT INTO venues (venue_name) VALUES (%s)", (input_venue_name,))
                await conn.commit()
                return cur.lastrowid


# Функция для поиска или создания площадки
async def find_or_create_venue(input_venue_name: str) -> int:
    venue_names = await get_venue_names_from_database()

    # Преобразуем исходные названия площадок в векторы TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(venue_names)

    # Преобразуем новое название площадки в вектор TF-IDF
    new_tfidf_vector = vectorizer.transform([input_venue_name])

    # Расчет косинусного сходства между новым названием и всеми площадками
    cosine_similarities = linear_kernel(new_tfidf_vector, tfidf_matrix).flatten()

    # Находим индекс площадки с наивысшим косинусным сходством
    best_match_index = cosine_similarities.argmax()

    # Если ближайшее соответствие имеет достаточно высокий балл, возвращаем id
    if cosine_similarities[best_match_index] >= 0.6:
        # Индексация начинается с 0, поэтому добавляем 1.
        venue_id = int(best_match_index + 1)
    else:
        # Если не найдено подходящего соответствия, создаем новую площадку
        venue_id = await create_venue(input_venue_name)

    return venue_id


# Пример использования

async def main():
    input_venue_name = "Театр Ленком"
    venue_id = await find_or_create_venue(input_venue_name)
    print(f"ID площадки '{input_venue_name}': {venue_id}")

if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
