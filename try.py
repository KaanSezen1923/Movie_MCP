import requests
from dotenv import load_dotenv
import os

load_dotenv()
auth_key = os.getenv("AUTH_KEY")

BASE_URL = "https://api.themoviedb.org/3"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {auth_key}"
}

genre_dict = {
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35,
    "Crime": 80, "Documentary": 99, "Drama": 18, "Family": 10751,
    "Fantasy": 14, "History": 36, "Horror": 27, "Music": 10402,
    "Mystery": 9648, "Romance": 10749, "Science Fiction": 878,
    "TV Movie": 10770, "Thriller": 53, "War": 10752, "Western": 37
}


reverse_genre_dict = {v: k for k, v in genre_dict.items()}


    
def get_person_id(name: str) :
    """İsimden kişi ID'sini bulur."""
    search_url = f"{BASE_URL}/search/person"
    params = {"query": name, "language": "en-US"}
    resp = requests.get(search_url, headers=headers, params=params)
    results = resp.json().get('results', [])
    return results[0]['id'] if results else None

def get_keyword_id(keyword: str):
    """Kelime araması yaparak ilgili keyword ID'sini döndürür."""
    search_url = f"{BASE_URL}/search/keyword"
    params = {"query": keyword}
    resp = requests.get(search_url, headers=headers, params=params)
    results = resp.json().get('results', [])
    
    # İlk sonucun ID'sini döndürür
    return results[0]['id'] if results else None

def discover_movies(genre_name=None, actor_name=None, director_name=None, keyword=None, min_rating=None, sort_by="vote_average.desc"):
    """
    Tüm filtreleri birleştirerek film araması yapar.
    Varsayılan olarak popülerliğe göre sıralar.
    """
    discover_url = f"{BASE_URL}/discover/movie"
    
    # Varsayılan parametreler
    params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "page": 1,
        "sort_by": sort_by
    }

    # Filtreleri ekleyelim
    if genre_name:
        genre_id = genre_dict.get(genre_name)
        if genre_id:
            params["with_genres"] = genre_id

    if actor_name:
        actor_id = get_person_id(actor_name)
        if actor_id:
            params["with_cast"] = actor_id

    if director_name:
        director_id = get_person_id(director_name)
        if director_id:
            params["with_crew"] = director_id

    if keyword:
        keyword_id = get_keyword_id(keyword)
        if keyword_id:
            params["with_keywords"] = keyword_id

    if min_rating:
        params["vote_average.gte"] = min_rating
        # Puan filtresi kullanıldığında genellikle daha anlamlı sonuç için oy sayısını da kısıtlarız
        params["vote_count.gte"] = 100 

    response = requests.get(discover_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Hata: {response.status_code}")
        return []
    

if __name__ == "__main__":
    # Örnek: Christopher Nolan'ın yönettiği, 7.5 puan üzeri Bilim Kurgu filmleri
    movies = discover_movies(
        actor_name="Johnny Depp",
        genre_name="fantasy",
        
    )

    for movie in movies:
        # Verileri güvenli çekelim
        title = movie.get('title', 'Bilinmiyor')
        year = movie.get('release_date', '????')[:4]
        rating = movie.get('vote_average', 0)
        overview = movie.get('overview', 'Özet bulunamadı.')
        poster = movie.get('poster_path')
        
        # Tür ID'lerini isimlere çevirelim
        g_ids = movie.get('genre_ids', [])
        g_names = [reverse_genre_dict.get(gid, str(gid)) for gid in g_ids]
        genres_str = ", ".join(g_names)

        # Temiz ve şık bir çıktı
        print(f"🎬 {title} ({year})")
        print(f"⭐ Puan: {rating} | 🎭 Türler: {genres_str}")
        print(f"📝 Özet: {overview}")
        if poster:
            print(f"🖼️ Poster: https://image.tmdb.org/t/p/w500{poster}")
        print("-" * 50)



