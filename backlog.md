# backlog.md — İş Havuzu ve Görev Takibi

> Avenox metodolojisine göre yarıda kalan her iş, açık sorular ve yol haritası buraya not düşülür; hiçbir yarım iş kaybolmaz.

## 🔴 Aktif İşler (Now)
- [ ] Proje iskeletinin Python ortamı ile ayağa kaldırılması (`pyproject.toml`, `requirements.txt`).
- [ ] TypeSafe SDK (`typesafe-sdk`) istemcisinin kurulması ve temel API bağlantı testi.
- [ ] `hook.py` giriş noktasının hazırlanması (Codex stdin/stdout JSON formatı).

## 🟡 Sırada Bekleyenler (Next)
- [ ] Jev karar sorularının (`domain`, `needs_vault`, `is_trivial`) optimize edilmesi.
- [ ] Dinamik bağlam enjeksiyonu ve karakter sınırı bütçelemesi (`context_chars <= 2000`).
- [ ] Avenox İkinci Beyin V3 CLI ile entegrasyon (`beyin.py context`).
- [ ] Gecikme (latency) benchmark testleri (Hedef: <150 ms).

## ⚪ İleride Düşünülecekler (Future / Ideas)
- [ ] `PostToolUse` hook'u ile kod düzenleme sonrası anlık Jev doğrulama/güvenlik kontrolü.
- [ ] Sık tekrarlanan promptlar için yerel semantik önbellek (in-memory cache) ekleme.
- [ ] Web arayüzü veya CLI üzerinden yönlendirme istatistiklerinin (token tasarrufu, yönlendirilen domainler) görüntülenmesi.

## 🟢 Tamamlananlar Logu (Done Archive)
- [x] Avenox proje standartlarına uygun iskelet kuruldu (`AGENTS.md`, `CLAUDE.md`, `notes.md`, `backlog.md`, `reports/`, `constants.md`) — (2026-09-19)
- [x] Jev Sistem 1 mimarisi ve Codex Hook entegrasyon fizibilitesi araştırıldı — (2026-09-19)
- [x] TypeSafe AI Jev modeli, `typesafe-sdk` karar tipleri (`Choice`, `Noul`, `Score`), Codex CLI Hook stdin/stdout mimarisi ve düşük gecikme bütçesi derin araştırması tamamlandı; `notes.md` kapsamlı teknik döküm ile güncellendi — (2026-09-20)
