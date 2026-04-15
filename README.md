🎬 Movie MCP - Akıllı Film Danışmanı
Bu proje, Model Context Protocol (MCP) kullanarak yerel bir LLM (Ollama) ile TMDB (The Movie Database) API'si arasında bir köprü kurar. Kullanıcıların doğal dilde film araması yapmasına, fragmanları bulmasına ve kişiselleştirilmiş film önerileri almasına olanak tanır.

✨ Özellikler
Gelişmiş Filtreleme: Tür, oyuncu, yönetmen, anahtar kelime ve minimum puana göre film arama.

Medya Entegrasyonu: Her film için otomatik poster bağlantıları ve YouTube fragman araması.

Akıllı Sohbet: Gemma veya Llama modelleriyle entegre, bağlamı koruyan profesyonel bir film danışmanı arayüzü.

Temiz Çıktı: Teknik JSON verilerini gizleyen, kullanıcı dostu ve Türkçe yanıtlar veren sistem yönergeleri.

🛠️ Kurulum
Gereksinimler:

Python 3.10+

Ollama (Gemma veya Llama modeli yüklü olmalı)

TMDB API Anahtarı

Bağımlılıkları Yükleyin:

Bash
pip install mcp ollama requests python-dotenv
Ortam Değişkenlerini Ayarlayın:
.env dosyası oluşturun ve TMDB API anahtarınızı ekleyin:

Kod snippet'i
AUTH_KEY=your_tmdb_bearer_token_here
🚀 Kullanım
Projeyi başlatmak için ana uygulama dosyasını çalıştırın:

Bash
python app.py
Bağlantı hazır olduğunda, örneğin şu soruları sorabilirsiniz:

"Christopher Nolan'ın yönettiği bilim kurgu filmlerini listele."

"Johnny Depp'in oynadığı fantastik filmleri bul."

"Puanı 8'den yüksek olan korku filmlerini göster."

📁 Dosya Yapısı ve İşlevler
app.py: Uygulamanın giriş noktası. MCP session'ını yönetir ve kullanıcı döngüsünü başlatır.

server.py: TMDB API ile haberleşen MCP sunucusu. search_movies_by_filters aracını (tool) tanımlar.

client.py: Ollama ve MCP arasındaki mantığı kurar. Sistem yönergelerini ve tool çağrılarını yönetir.

try.py: API entegrasyonlarını test etmek için kullanılan bağımsız test betiği.

⚙️ Teknik Detaylar
Sunucu Parametreleri: app.py üzerinden server.py dosyası bir alt süreç olarak başlatılır.

Tür Eşleştirme: Proje, TMDB tür ID'lerini (Genre IDs) otomatik olarak anlaşılır isimlere çeviren GENRE_DICT yapısını kullanır.

Otomatik Fragman Bulucu: Bir film arandığında, sistem arka planda filmin ID'si ile YouTube üzerindeki fragman linkini de sorgular.
