# notes.md — Proje Fikir, Mimari ve Derin Araştırma Dökümü

> Bu dosya kullanıcının ham düşüncelerini, araştırma bulgularını, hedeflenen bileşenleri ve sistem gereksinimlerini toparlar; ajanın mimari tasarıma ve kodlamaya rehberlik etmesini sağlar.

---

## 1. Ham Fikirler ve Problem Tanımı (Raw Dump)
- Codex'te her prompt çalıştırıldığında devasa bağlam dosyaları ve geçmiş oturumlar yükleniyor. Bu durum token faturasını şişiriyor ve modeli yavaşlatıyor.
- Klasik regex tabanlı hook'lar çok aptal; kullanıcının ne istediğini semantik olarak anlayamıyor.
- Araya GPT-4o koyarsan hook 2-3 saniye bekliyor, insan delirecek gibi oluyor.
- TypeSafe AI'ın yeni çıkardığı **Jev** modeli 70-150 ms'de çalışıyor, serbest metin üretmiyor, doğrudan `Choice`, `Noul` ve `Score` dönüyor. Tam bir "akıllı if-statement".
- Fikir: Codex'in `UserPromptSubmit` hook'una Jev'i koyalım. Kullanıcı Enter'a basar basmaz Jev baksın; neye ihtiyaç olduğunu anlasın, bağlamı budasın, sadece gereken bilgiyi Codex'e enjekte etsin!

---

## 2. Derin Araştırma Bulguları (Research Findings)

### 2.1. TypeSafe AI & Jev (Sistem 1) Modeli Mimarisi
- **Model Tipi:** Sistem 1 (Non-Autoregressive, Non-Generative).
- **Amaç:** Serbest metin (prose/chat) üretmez; verilen `state` girdisini doğrudan yazılım mantığının dallanabileceği (branching logic) kalibre olasılıklar ve yapılandırılmış tipler ile yanıtlar.
- **Eğitim Yöntemi:** RLCD (Reinforcement Learning for Calibrated Decisions) ile eğitilmiştir. Bu sayede modelin sunduğu olasılıklar tam kalibredir (örn. model %80 diyorsa gerçekte de 10 kararın 8'inde doğrudur).
- **Gecikme (Latency):** 70 – 150 ms (uçtan uca ortalama ~100 ms).
- **Maliyet Avantajı:** Çıkış token maliyeti yoktur (yalnızca ~$0.042 / 1M girdi tokenı). Geleneksel LLM'lere göre ~%95 daha ucuzdur.
- **Sıfır Halüsinasyon Garantisi:** Model serbest metin üretemediği için matematiksel olarak şema dışına çıkamaz; regex veya JSON tamir algoritmalarına gerek bırakmaz.

### 2.2. Jev'in Üç Temel Karar Primitifi (`typesafe-sdk`)
TypeSafe SDK (`typesafe_sdk`) üç ana soru tipini destekler:

1. **`Noul` (Bernoulli / İkili Evet-Hayır Kararı):**
   - Belirtilen ifadenin doğruluğunu test eder.
   - Yanıt olarak `0.0` ile `1.0` arasında bir olasılık (`.noul`) döner.
   - Ayrı bir `confidence` alanı içermez; olasılık değeri modelin inanç derecesidir.
   - *Kullanımımız:* `is_trivial` (Selamlama mı?), `needs_vault` (Hafıza araması gerekiyor mu?).

2. **`Choice` (Kategorik Seçim - 255 Seçeceğe Kadar):**
   - Tanımlanan seçenekler arasından en uygun olanını seçer.
   - Döndürdüğü alanlar: `.choice` (seçilen etiket), `.probabilities` (tüm seçeneklerin dağılımı), `.confidence` (güven skoru).
   - *Kullanımımız:* `domain` (backend, database, frontend, memory_vault, devops, general).

3. **`Score` (Sıralı Ölçek / Rubrik Değerlendirmesi):**
   - Girdiyi dereceli bir skala üzerinde (örn. Low, Medium, High veya sayısal kademeler) değerlendirir.
   - Döndürdüğü alanlar: `.score` (ağırlıklı/kesirli skor), `.probabilities`, `.confidence`.
   - *Kullanımımız:* `urgency_or_complexity` (Düşük, Orta, Yüksek karmaşıklık -> dinamik token bütçesi belirleme).

#### Python SDK Kullanım Deseni:
```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"prompt": "FastAPI endpointine redis cache ekle"},
        questions={
            "domain": Choice(
                instructions="Kullanıcının üzerinde çalıştığı teknik alan nedir?",
                criteria={
                    "backend": "API, iş mantığı, servisler",
                    "database": "SQL, migration, model, redis",
                    "frontend": "UI, CSS, React, komponentler",
                    "devops": "Docker, CI/CD, deployment",
                    "general": "Diğer genel işler",
                },
            ),
            "is_trivial": Noul(instructions="Bu bir selamlama veya bağlam gerektirmeyen basit teşekkür mü?"),
            "needs_vault": Noul(instructions="Geçmiş proje kararlarına veya ikinci beyin notlarına bakılmalı mı?"),
            "complexity": Score(
                instructions="İşin bağlam derinliği gereksinimi nedir?",
                criteria=["Low", "Medium", "High"],
            ),
        },
    )

selected_domain = response.choices["domain"].choice
is_trivial = response.nouls["is_trivial"].noul > 0.8
needs_vault = response.nouls["needs_vault"].noul >= 0.70
```

---

### 2.3. Codex CLI Hook Mimarisi & Standartları
- **Tetikleyici Olay:** `UserPromptSubmit` (Kullanıcı promptu yazıp Enter'a bastığı an tetiklenir).
- **Konfigürasyon Yeri:** `.codex/hooks.json` veya `~/.codex/hooks.json`
- **Konfigürasyon Örneği:**
  ```json
  {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python -m jev_codex_router.hook"
      }
    ]
  }
  ```
- **Girdi (stdin):** Codex CLI standart JSON gönderir:
  ```json
  {
    "session_id": "sess_123456",
    "cwd": "C:/projeler/my-app",
    "prompt": "FastAPI rotalarına rate limiting uygula"
  }
  ```
- **Çıktı (stdout):**
  - Yapılandırılmış JSON çıktısı:
    ```json
    {
      "hookSpecificOutput": {
        "additionalContext": "[Jev Router]: Backend domain kuralları ve rate-limiting politikası eklendi..."
      }
    }
    ```
  - Veya standart context enjeksiyon metni (exit code 0 ile).
- **Çıkış Kodları (Exit Codes):**
  - `0`: Başarılı. Hook bağlamı enjekte eder veya sessizce geçer.
  - `2`: Prompt engelleme (güvenlik açığı, tehlikeli komut engelleme vb.).

---

### 2.4. Düşük Gecikme (Latency) & Graceful Fallback Bütçesi
- **Hedef Toplam Süre:** < 150 ms
- **Sert Zaman Aşımı (Hard Timeout):** 200 ms (Maksimum 250 ms)
- **Zaman Bütçesi Dağılımı:**
  * Stdin okuma & JSON parse: ~5 ms
  * Jev API çağrısı (`client.system_one`): ~80-120 ms
  * Kural / Context montajı (in-memory lookup): ~10 ms
  * Stdout JSON basma & exit: ~5 ms
- **Fallback Stratejisi:**
  * `TYPESAFE_API_KEY` eksikse, internet bağlantısı yoksa veya Jev 180 ms içinde yanıt vermezse:
  * Hook **hata fırlatmaz**, Codex oturumunu **kilitlemez**, boş çıktı ile anında `exit(0)` yapar.

---

## 3. Hedeflenen Sistem Mimarisi ve Bileşenleri

```
[Kullanıcı Promptu]
       │
       ▼
[Codex CLI (UserPromptSubmit)]
       │ (stdin JSON)
       ▼
┌────────────────────────────────────────────────────────┐
│  jev_codex_router.hook (Giriş Noktası & Guard)         │
│  - Timeout Guard (180ms cutoff)                        │
│  - Graceful Exception Catching                         │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│  JevDecisionEngine (jev_engine.py)                     │
│  - TypeSafeClient.system_one()                         │
│  - Sorular: domain (Choice), is_trivial (Noul),        │
│             needs_vault (Noul), complexity (Score)     │
└───────────────────────┬────────────────────────────────┘
                        │ Kararlar (domain, needs_vault vb.)
                        ▼
┌────────────────────────────────────────────────────────┐
│  ContextAssembler (context_assembler.py)               │
│  - is_trivial == True ise -> Bağlam Yok (Tasarruf %99) │
│  - domain kurallarını seç ve yükle                     │
│  - needs_vault >= 0.70 ise -> Avenox Beyin Context     │
│  - Karakter Bütçesi Filtresi (max 2000 karakter)       │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
           (stdout JSON: additionalContext)
                        │
                        ▼
[Codex LLM: Yalnızca Dar & İlgili Bağlamla Başlar]
```

### Bileşen Detayları
1. **`hook.py` (CLI Giriş Noktası):**
   - Stdin'den JSON verisini alır, zaman aşımı korumasıyla `JevDecisionEngine` ve `ContextAssembler`'ı çalıştırır.
   - Hata ve gecikme durumunda sessizce şeffaf geçiş sağlar.
2. **`jev_engine.py` (Jev Karar Motoru):**
   - `typesafe-sdk` ile tip güvenli iletişim kurar.
   - Model alias: `jev-latest`.
   - Prompt analizini paralel soru setiyle gerçekleştirir.
3. **`context_assembler.py` (Dinamik Bağlam Montajcısı):**
   - Proje kurallarını parçalı (modular) tutar: `rules/backend.md`, `rules/database.md`, `rules/frontend.md` vb.
   - Sadece tespit edilen etki alanının kurallarını yükler (tüm kuralları yüklemek yerine %70-80 token tasarrufu).
   - Karakter bütçesini (`MAX_INJECTED_CONTEXT_CHARS = 2000`) aşmayacak şekilde metni kırpar.
4. **`avenox_vault.py` (İkinci Beyin Entegratörü):**
   - `needs_vault` kararı tetiklendiğinde `beyin.py context <prompt>` çağrısı ile dar geçmişi çeker.
   - `notes/` klasörünü ezmeden sadece read-only özet sorgusu yapar.

---

## 4. Test ve Doğrulama Kriterleri
- **Birim Testler (`tests/`):**
  - Jev mock yanıtlarıyla `hook.py` stdin/stdout doğrulaması.
  - Zaman aşımı durumunda graceful fallback simülasyonu.
  - `is_trivial` durumunda boş context dönme doğrulaması.
  - Karakter bütçesi (2000 char) aşım kontrolü.
- **Uçtan Uca Fixture Testi:**
  - `tests/fixtures/sample_prompt.json` üzerinden doğrudan CLI testi.
- **Gecikme Ölçümü:**
  - Benchmark modülü ile P50, P90 ve P99 sürelerinin raporlanması.
