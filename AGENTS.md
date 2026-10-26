# Proje Sözleşmesi: Jev-Codex-Router

> **Önemli Kural:** `AGENTS.md` veya `CLAUDE.md` dosyalarından biri güncellenirse, diğeri de eşzamanlı olarak güncellenir.

## Proje Amacı
TypeSafe AI tarafından geliştirilen Jev (Sistem 1 - Non-Autoregressive) modelini Codex CLI Hook mimarisiyle entegre ederek, geliştirici prompt girdiğinde 70–150 ms içinde semantik niyet analizi yapan, dinamik context budayan ve token harcamasını %80 azaltan akıllı yönlendirici (router) sistemi geliştirmek.

## Temel Komutlar
- Kurulum: `pip install -e .` veya `uv pip install -r requirements.txt`
- Testleri Çalıştırma: `pytest tests/ -v`
- Lint & Format: `ruff check .` ve `ruff format .`
- Hook Manuel Test: `python -m jev_codex_router.hook < tests/fixtures/sample_prompt.json`

## Değişmezler & Kurallar
1. **Düşük Gecikme Garantisi:** Hook çalışma süresi hiçbir koşulda 250 ms'yi aşmamalıdır; aşarsa graceful fallback devreye girmelidir.
2. **Tip Güvenliği:** Jev modelleriyle olan tüm iletişimler `typesafe-sdk` standart tipleriyle (`Choice`, `Noul`, `Score`) yapılmalıdır; serbest metin pars edilmeye çalışılmamalıdır.
3. **Güvenlik Değişmezi:** `TYPESAFE_API_KEY` ve harici kimlik bilgileri asla git deposuna veya markdown dosyalarına yazılmaz; `.env` dosyasından okunur.
4. **Hafıza Disiplini:** Avenox İkinci Beyin V3 ile entegrasyonda `notes/` ezilmez; dar bağlam sorgusu yapılır.

## Bitti Tanımı (Definition of Done)
- [ ] İlgili birim testler geçmeli (%90+ test coverage).
- [ ] Codex stdin/stdout JSON spesifikasyonu bozulmamalı.
- [ ] Yapılan değişiklik `backlog.md` dosyasında güncellenmeli.
