# Ödev 2 Raporu: JOIN, ERD ve Normalizasyon

- **Ad Soyad:** Yiğit Han Karabulut
- **Ders:** BLP 105 / Veritabanı Yönetim Sistemleri (Güz 2026)
- **Proje / Kura:** Kura 8 — Eğitim Sohbet Asistanı Güvenlik ve Olay Takibi
- **Tarih:** 27 Kasım 2026

---

## 1. Fan-out Analizi (Bölüm 1 - Soru 4)

`robot_fleet` veritabanında görevi olan robotların toplam batarya seviyesini hesaplarken `robots` ve `missions` tablolarını `INNER JOIN` ile birleştirdiğimizde sonuç **700** çıkarken, `EXISTS` kullanarak yaptığımız doğru hesaplamada sonuç **262** çıkmıştır[cite: 5].

Bu farkın nedeni **fan-out (satır çoğalması)** etkisidir. Bire-çok (`1-N`) ilişkide bir robotun birden fazla görevi bulunduğunda `INNER JOIN`, robot satırını her görev kaydı için tekrar üretir:
- **Atlas-01** (batarya: 85) ve **Kartal-03** (batarya: 90) **3'er** kez,
- **Mars-01** (batarya: 62) ve **Mars-02** (batarya: 45) **2'şer** kez,
- **Atlas-02** (batarya: 60) ise **1** kez toplama dahil edilmiştir (3×85 + 3×90 + 2×62 + 2×45 + 1×60 = 700)[cite: 4].

Gerçek bir depo operasyon raporunda bu hata, filodaki mevcut toplam enerji kapasitesinin olduğundan yaklaşık **2,7 kat fazla** görünmesine yol açar[cite: 5]. Yöneticiler filonun şarj durumunu yeterli sanarak vardiya planlamasını hatalı yapabilir ve görev ortasında bataryası tükenen robotlar nedeniyle operasyonel aksamalar yaşanabilir.

---

## 2. En Zor Tasarım Kararı (Kendi ERD'm)

Kura 8 projesinin vize taslağında (`SCENARIO.md`) `events` tablosunda yer alan **`conversation_id` sütununu final ERD'den çıkarmak** üzerinde en çok düşündüğüm tasarım kararı oldu[cite: 9, 10].

Karar sürecinde şu üç seçenek arasında kaldım:
1. **`conversation_id` sütununu `events` tablosunda tutmak (Denormalize yapı):** Analiz sorgularında `messages` tablosunu atlayıp doğrudan `conversations` ile `events` tablolarını birleştirme kolaylığı sağlıyordu[cite: 10].
2. **`conversation_id` sütununu `events` tablosundan çıkarmak (3NF):** Olayın bağlı olduğu konuşmaya `events.message_id → messages.conversation_id` yoluyla ulaşmak.
3. **Konuşma ve olay özetlerini tek tabloda birleştirmek:** Sorgu performansını artırmak için veri tekrarını göze almak.

**Seçim ve Gerekçe:** İkinci seçeneği tercih ederek `conversation_id` alanını `events` tablosundan çıkardım[cite: 9]. Çünkü `events.id` zaten `message_id`'yi, `message_id` ise `conversation_id`'yi belirlemektedir[cite: 9]. Sütunun `events` içinde kalması **`events.id → message_id → conversation_id`** şeklinde geçişli bağımlılık (3NF ihlali) yaratıyordu[cite: 9]. Ayrıca bir mesajın yanlışlıkla farklı bir konuşmaya bağlanması veya güncellenmesi durumunda iki tablo arasında tutarsızlık (güncelleme anomalisi) oluşma riski vardı. İlişkiyi yalnızca `message_id` üzerinden kurarak veri bütünlüğünü korudum[cite: 9].

---

## Yapay Zekâ Kullanım Beyanı

Bu ödev kapsamında **ChatGPT** ve **Gemini**; SQL sorgu çıktılarının yorum cümlelerini netleştirmek, normalizasyon notunu tablo düzenine oturtmak ve rapor metnini düzenlemek amacıyla yardımcı araç olarak kullanılmıştır[cite: 8]. Sorgu çalıştırma çıktıları (`robot_fleet`) ve ERD tasarım kararları bizzat tarafımdan doğrulanıp uygulanmıştır[cite: 8].