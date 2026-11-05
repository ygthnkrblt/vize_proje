# Yapay Zekâ Kullanım Beyanı

Bu proje hazırlanırken **ChatGPT (GPT-6)** şu işler için yardımcı araç olarak kullanılmıştır:

- Kura 8 senaryosunun teslim kapsamına göre dosya yapısının planlanması.
- `SCENARIO.md`, veri kartı açıklamaları ve proje README taslağının hazırlanması.
- Açık kaynak veri dosyasından metinsiz analiz CSV'leri üreten Python betiğinin yazılması.
- Hafta 4 SELECT/WHERE ve Hafta 5 analiz sorgularının taslaklarının hazırlanması.
- Tek sayfalık rapor taslağının oluşturulması.

**Gerçek veri üretimi:** Sohbet metni veya sahte konuşma satırı ChatGPT tarafından üretilmemiştir. Veri, OpenAssistant OASST1 kaynağından indirilmek üzere betikle hazırlanmıştır. Konuşma türleri anahtar kelime kurallarıyla; olay işaretleri ise kaynakta bulunan Detoxify skorlarına göre türetilir. Bunlar insan tarafından doğrulanmış güvenlik kararı değildir.

**Öğrencinin doğrulama adımları (çalıştırdıktan sonra doldur):**

1. [ ] İndirme betiğinin SHA-256 kontrolünün başarılı olduğunu kontrol ettim.
2. [ ] Üretilen `data/processed/data_card_run.md` içindeki gerçek satır sayılarını kontrol ettim.
3. [ ] PostgreSQL'e yükledikten sonra üç tablonun `COUNT(*)` sonuçlarını karşılaştırdım.
4. [ ] Her SQL sorgusunu kendi veritabanımda çalıştırdım ve örnek satırları kontrol ettim.
5. [ ] Raporumdaki sayısal sonuçları gerçek sorgu çıktılarından aldım.

**Not:** Bu beyan, yapay zekâ yardımını gizlemez. Öğrenci sorguları okuyup açıklayabilmeli ve kendi bilgisayarında çalıştırarak doğrulamalıdır.
