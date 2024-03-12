from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from database.models.main_models import Venues, session
from cachetools import cached, TTLCache

# Функция для получения театров из базы данных
@cached(cache=TTLCache(maxsize=128, ttl=600))  # TTL в секундах (например, 600 секунд = 10 минут)
def get_venues_from_database():
    venues = session.query(Venues).all()
    session.close()
    return [venue.venue_name for venue in venues]


def find_venue_id(input_venue_name):
    venues = get_venues_from_database()

    # Список всех названий площадок
    venue_names = [venue.venue_name for venue in venues]

    # Добавляем входное название в список
    venue_names.append(input_venue_name)

    # Преобразование названий площадок в векторы TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(venue_names)

    # Расчет косинусного сходства между входным названием и всеми площадками
    cosine_similarities = linear_kernel(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    # Находим индекс площадки с наивысшим косинусным сходством
    best_match_index = cosine_similarities.argmax()

    # Если ближайшее соответствие имеет достаточно высокий балл, возвращаем id
    if cosine_similarities[best_match_index] >= 0.5:  # Выберите подходящий порог близости
        venue_id = venues[best_match_index].id
        return venue_id
    else:
        return None  # Если не найдено подходящего соответствия, возвращаем None
 


if __name__ == '__main__':
    # Пример использования
    input_theater_name = "Театр А"
    venue_id = find_venue_id(input_theater_name)

    if venue_id is not None:
        print(f"ID площадки '{input_theater_name}': {venue_id}")
    else:
        print(f"Площадка '{input_theater_name}' не найдена.")