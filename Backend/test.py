import requests
import json
import time

# API Yapılandırması
API_URL = "http://127.0.0.1:8000/chat"

# 4 Kategori - Her birinde 5 soru (Toplam 20 Soru)
test_queries = {
    "Oyuncu ve Yönetmen Odaklı": [
        "Christopher Nolan'ın yönettiği filmleri listele.",
        "Leonardo DiCaprio'nun oynadığı en iyi filmler hangileri?",
        "Quentin Tarantino filmlerinden bir seçki sunar mısın?",
        "Tom Hanks'in başrolde olduğu dram filmlerini bul.",
        "Martin Scorsese'nin yönettiği ve Robert De Niro'nun oynadığı filmler var mı?",
        "Scarlett Johansson'ın aksiyon filmlerini getir.",
        "Denis Villeneuve tarafından yönetilen bilim kurgu filmleri nelerdir?",


    ],

    "Tür Odaklı": [
        "Bana biraz aksiyon filmi önerir misin?",
        "En iyi bilim kurgu filmleri hangileri?",
        "Korku türünde izlenebilecek yeni bir şeyler var mı?",
        "Hem komedi hem de aile türünde olan filmleri listele.",
        "Belgesel izlemek istiyorum, önerin var mı?",
        "Romantik türde ama içinde biraz da dram olan filmler bul.",
        "Western türündeki popüler filmler neler?",
        "Animasyon kategorisinde en çok izlenenler hangileri?",
        "Savaş (War) türünde etkileyici bir film arıyorum."
    ],
    "Anahtar Kelime ": [
        "İçinde 'uzay' (space) teması geçen filmleri bul.",
        "'Zaman yolculuğu' (time travel) konulu en iyi filmler hangileri?",
        "'Yapay zeka' (artificial intelligence) hakkındaki filmleri listele.",
        "'Soygun' (heist) temalı heyecanlı bir film önerir misin?",
        "'Distopya' (dystopia) dünyasında geçen dram filmleri neler?",
        "'Süper kahraman' (superhero) konulu popüler yapımları getir.",
        "'Dedektif' (detective) hikayesi anlatan gizem filmleri öner.",
        "İçinde 'zombi' (zombie) olan aksiyon filmleri var mı?",
        "'Siberpunk' (cyberpunk) atmosferine sahip filmleri listele.",
        "'İntikam' (revenge) temasını işleyen en çarpıcı filmler hangileri?"
    ]
}

def run_performance_test():
    all_results = []
    print(f"🚀 Movie MCP Testi Başlatılıyor: {API_URL}")
    print("-" * 50)

    for category, questions in test_queries.items():
        print(f"\n📂 Kategori: {category}")
        for question in questions:
            print(f"  ❓ Soru: {question}")
            
            start_time = time.time()
            try:
                # api.py'deki ChatRequest modeline uygun (prompt alanı)
                response = requests.post(
                    API_URL, 
                    json={
                        "prompt": question,
                        "user_id": 2,           # Sabit bir test kullanıcı ID'si ekleyin
                        "session_id": "test_sn" # Bir test oturum ID'si ekleyin
                    }, 
                    timeout=None
                )
                end_time = time.time()
                duration = round(end_time - start_time, 2)
                
                if response.status_code == 200:
                    # ChatResponse modelinden 'answer'ı al
                    answer = response.json().get("answer", "Cevap boş döndü.")
                    status = "Başarılı"
                    print(f"  ✅ Tamamlandı ({duration} sn)")
                else:
                    answer = f"Hata Kodu: {response.status_code} - {response.text}"
                    status = "Hata"
                    print(f"  ❌ Sunucu Hatası ({duration} sn)")
                
                all_results.append({
                    "kategori": category,
                    "soru": question,
                    "yanit": answer,
                    "durum": status,
                    "yanit_suresi_sn": duration
                })
                
            except Exception as e:
                print(f"  ❌ İstek Hatası: {str(e)}")
                all_results.append({
                    "kategori": category,
                    "soru": question,
                    "yanit": f"İstek Hatası: {str(e)}",
                    "durum": "Hata",
                    "yanit_suresi_sn": 0
                })

    # Sonuçları JSON olarak kaydet
    output_filename = "test_results_gemma.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)
    
    print("-" * 50)
    print(f"✨ Testler tamamlandı! Toplam {len(all_results)} soru işlendi.")
    print(f"💾 Sonuçlar '{output_filename}' dosyasına kaydedildi.")

if __name__ == "__main__":
    run_performance_test()