# constants.md — Proje Sabitleri

Bu dosya proje genelinde değişmeyen sabit değerleri, zaman aşımlarını ve yapılandırma eşiklerini barındırır.

## Model ve Servis Sabitleri
- **JEV_MODEL_ALIAS:** `"jev-latest"`
- **API_BASE_URL:** `"https://api.typesafe.ai/v1"`
- **MAX_HOOK_TIMEOUT_SECONDS:** `2.0` (Codex hook'unun kilitlenmemesi için üst sınır)
- **TARGET_LATENCY_MS:** `150` (Hedeflenen Sistem 1 yanıt süresi)

## Bağlam ve Bütçe Sınırları
- **MAX_INJECTED_CONTEXT_CHARS:** `2000` (Codex'e enjekte edilecek maksimum karakter bütçesi)
- **MIN_CONFIDENCE_THRESHOLD:** `0.70` (Jev kararlarının kabul edilmesi için gereken taban güven skoru)

## Desteklenen Teknik Alanlar (Domain Enum)
```python
DOMAINS = [
    "backend",      # API'ler, servisler, iş mantığı
    "database",     # SQL, migration, şema
    "frontend",     # UI bileşenleri, CSS, durum yönetimi
    "memory_vault", # İkinci beyin, görevler, notlar, dokümantasyon
    "devops",       # Docker, CI/CD, scriptler, env
    "general"       # Diğer genel kodlama işleri
]
```
