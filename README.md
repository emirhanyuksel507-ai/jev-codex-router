# Jev-Codex-Router

[![Tests](https://img.shields.io/badge/tests-11%20passed-brightgreen.svg)](#testleri-%C3%A7al%C4%B1%C5%9Ft%C4%B1rma)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Zero Hardcoded Secrets](https://img.shields.io/badge/secrets-zero-blueviolet.svg)](#g%C3%BCvenlik-ve-gizlilik)
[![Architecture](https://img.shields.io/badge/Avenox-Agentic%20Engineering-orange.svg)](#proje-dosya-yap%C4%B1s%C4%B1)

> **Jev (Sistem 1) Destekli Ultra-Hızlı Codex Bağlam Yönlendiricisi ve Dinamik Context Budayıcı**

Bu proje, **Avenox Agentic Engineering** metodolojisiyle yapılandırılmıştır.

---

## 🎯 Proje Amacı
Codex CLI ile yazılım geliştirirken karşılaşılan yüksek token tüketimi ve context bloat (bağlam şişmesi) sorununu çözmek için; TypeSafe AI'ın **Jev** karar modelini `UserPromptSubmit` hook'una yerleştirir. Geliştirici prompt girdiğinde **70–150 ms** içinde semantik niyet analizi yapar ve yalnızca ilgili kuralları/dosyaları Codex'e enjekte eder.

### Temel Özellikler
1. **Ultra Düşük Gecikme:** ~100 ms içinde karar verir; sert timeout (200 ms) korumasıyla geliştirici akışını asla kilitlemez.
2. **%80 Token Tasarrufu:** Prompt'un ihtiyaç duymadığı alanların kurallarını dışlar, selamlama ve basit yanıtlarda bağlamı sıfırlar.
3. **Graceful Fallback:** API anahtarı veya ağ bağlantısı olmadığında otomatik olarak yüksek hızlı yerel kalibre sezgisel motoruna geçer.
4. **Sert Karakter Bütçesi:** Enjekte edilen ek bağlamı belirlenen sınırda (`MAX_INJECTED_CONTEXT_CHARS = 2000`) tutar.

---

## 🔒 Güvenlik ve Gizlilik
Bu repo **sıfır harici sır / sıfır API anahtarı** prensibiyle inşa edilmiştir:
- Hiçbir API anahtarı, parola veya kişisel kimlik bilgisi kod içinde yer almaz.
- Opsiyonel `TYPESAFE_API_KEY` ortam değişkeni (`os.getenv`) üzerinden okunur. Anahtar tanımlı olmadığında sistem tamamen bağımsız yerel motorla çalışır.

---

## 📂 Proje Dosya Yapısı (Avenox Standardı)
```
jev-codex-router/
├── jev_codex_router/
│   ├── __init__.py                  # Paket sürüm bilgisi
│   ├── hook.py                      # Codex CLI UserPromptSubmit hook giriş noktası
│   ├── engine.py                    # Jev Sistem 1 karar motoru ve yerel sezgisel fallback
│   ├── assembler.py                 # Dinamik kural montajcısı ve karakter bütçesi kontrolü
│   ├── constants.py                 # Zaman aşımları, eşikler ve domain tanımları
│   └── rules/                       # Modüler teknik alan kuralları
│       ├── backend.md
│       ├── database.md
│       ├── devops.md
│       ├── frontend.md
│       ├── general.md
│       └── memory_vault.md
├── tests/
│   ├── fixtures/
│   │   └── sample_prompt.json       # Örnek Codex CLI stdin JSON verisi
│   └── test_hook.py                 # Kapsamlı birim ve CLI entegrasyon testleri (11 test)
├── AGENTS.md                        # Codex ve otonom ajanların davranış sözleşmesi
├── CLAUDE.md                        # Claude Code köprüsü (AGENTS.md ile senkron)
├── notes.md                         # Ham fikirler, derin araştırma dökümü ve mimari notlar
├── backlog.md                       # Avenox metodolojisi görev takip günlüğü
├── constants.md                     # Proje sabitleri referansı
├── pyproject.toml                   # Standart Python paket yapılandırması
├── requirements.txt                 # Test ve opsiyonel bağımlılıklar
├── LICENSE                          # MIT Lisansı
└── README.md                        # Ana dokümantasyon
```

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
pip install -e .
```

### 2. Codex Hook Testi
Örnek girdi ile CLI hook'unu test edin:

```bash
python -m jev_codex_router.hook < tests/fixtures/sample_prompt.json
```

Örnek Çıktı:
```json
{
  "hookSpecificOutput": {
    "additionalContext": "[Jev-Router] Injected Domain Context (BACKEND) | Complexity: Medium\n# Backend Domain Rules\n...",
    "domain": "backend",
    "complexity": "Medium",
    "decisionSource": "local_heuristic"
  }
}
```

### 3. Testleri Çalıştırma
Tüm birim testleri koşturmak için:

```bash
python -m unittest discover -s tests -v
```

---

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) altında sunulmaktadır.
