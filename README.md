🎬 Movie Explorer AI
Movie Explorer AI, kullanıcıların sinema zevklerini analiz ederek onlara kişiselleştirilmiş film önerileri sunan, sesli asistan destekli ve yapay zeka tabanlı bir mobil uygulamadır. Gelişmiş LLM agent mimarisi (LangGraph) ve TMDB API entegrasyonu (FastMCP) kullanılarak geliştirilmiştir.

✨ Özellikler
🤖 Akıllı Sohbet & Öneri Motoru: Kullanıcının sohbet geçmişini ve favorilerini analiz ederek dinamik bir "Kullanıcı Personası" çıkarır ve buna en uygun filmleri önerir (Ollama & LangGraph).

🎙️ Sesli Komut (Voice-to-Text): Groq Whisper API entegrasyonu sayesinde kullanıcılar sesli olarak film arayabilir veya sohbet edebilir.

🎬 Gerçek Zamanlı Film Verisi: FastMCP kullanılarak TMDB (The Movie Database) üzerinden anlık film, fragman, oyuncu ve platform (Netflix, Amazon vb.) bilgileri çekilir.

❤️ İzleme Listesi (Watchlist): Beğenilen filmleri kaydetme ve yönetme.

🔔 Akıllı Bildirimler: Arka planda çalışan zamanlayıcı (APScheduler) ile kullanıcının zevkine uygun, yapay zeka tarafından üretilmiş rastgele film önerisi bildirimleri (Expo Push Notifications).

🔒 Güvenli Kimlik Doğrulama: Bcrypt ile şifrelenmiş kullanıcı giriş ve kayıt sistemi (PostgreSQL).

🛠️ Teknoloji Stoku
Frontend (Mobil Uygulama)
Framework: React Native & Expo

Ses İşleme: expo-av

İkonlar: lucide-react-native

Ağ İstekleri: axios

Backend (API & AI Agent)
Web Framework: FastAPI & Uvicorn

Veritabanı: PostgreSQL (psycopg2)

AI & Orkestrasyon: LangGraph, Ollama (gpt-oss:120b-cloud), Groq (Whisper-large-v3)

Araçlar (Tools): FastMCP (Model Context Protocol) ile TMDB Entegrasyonu

Arka Plan Görevleri: APScheduler

🚀 Kurulum Adımları
Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin.

Ön Koşullar
Node.js ve npm (veya yarn)

Python 3.10+

PostgreSQL veritabanı

Ollama (Lokalde yüklü ve gpt-oss:120b-cloud veya eşdeğer bir model indirilmiş olmalı)

Expo Go uygulaması (Test cihazınız için)

1. Backend Kurulumu
Terminali açın ve backend dizinine gidin:

Bash
# Sanal ortam (virtual environment) oluşturun ve aktifleştirin
python -m venv venv
source venv/bin/activate  # Windows için: venv\Scripts\activate

# Gerekli kütüphaneleri yükleyin
pip install fastapi uvicorn psycopg2-binary bcrypt mcp fastmcp python-dotenv httpx langgraph groq apscheduler exponent_server_sdk whisper
Projenin ana dizininde bir .env dosyası oluşturun ve aşağıdaki değişkenleri kendinize göre doldurun:

Kod snippet'i
# Veritabanı Ayarları
DB_NAME=veritabani_adiniz
DB_USER=kullanici_adiniz
DB_PASSWORD=sifreniz
DB_HOST=localhost

# API Anahtarları
AUTH_KEY=tmdb_api_okuma_anahtariniz
WHISPER_API_KEY=groq_api_anahtariniz
Backend sunucusunu başlatın:

Bash
python api.py
# veya
uvicorn api:app --host 0.0.0.0 --port 3000 --reload
2. Frontend Kurulumu
Yeni bir terminal açın ve mobil uygulama dizinine gidin:

Bash
# Bağımlılıkları yükleyin
npm install

# Uygulamayı başlatın
npx expo start
Not: Uygulama dosyalarınızda (AuthScreen.tsx, Chat.tsx, vb.) bulunan API_BASE_URL değişkenindeki IP adresini (http://192.168.1.104:3000), kendi yerel ağ IP adresinizle değiştirmeyi unutmayın.

🏗️ Mimari ve Çalışma Mantığı
İstemci (Client): Kullanıcı, React Native arayüzünden yazılı veya sesli bir mesaj gönderir. Sesli mesajlar Groq Whisper ile metne dökülür.

API Katmanı: FastAPI, isteği alır ve kullanıcının geçmiş sohbet ile favori verilerini veritabanından (PostgreSQL) çeker.

Yönlendirme (LangGraph): client.py içerisindeki LangGraph akışı, kullanıcının niyetini analiz eder (analyze_intent_node). Gelen mesaj basit bir selamlaşma ise general_chatter düğümüne, bir film isteği ise recommendation_engine düğümüne yönlendirilir.

Araç Çağrısı (MCP): Eğer film aranıyorsa, FastMCP sunucusu (server.py) devreye girer ve TMDB API üzerinden filtreleme yaparak sonuçları LLM'e (Ollama) iletir.

Profil Çıkarımı: Kullanıcı her 5 mesaj gönderdiğinde, arka planda çalışan asenkron görev kullanıcının "Personasını" günceller.

📄 Lisans
Kaan Sezen — [GitHub](https://github.com/KaanSezen1923)
