-- Ödev 2, Bölüm 1: Filo soruları
-- Ad Soyad: Yiğit Han Karabulut
-- Veritabanı: robot_fleet
-- Her sorgunun altına sonucu açıklayan tek cümlelik yorum yaz.
-- Yorumları sorguyu çalıştırıp çıktıyı gördükten SONRA yaz.

-- Soru 1: Her robotun adı, operatör adı ve operatör telefonu (INNER JOIN)
SELECT r.name AS robot_adi, o.operator_name AS operator_adi, o.phone AS operator_telefon
FROM robots r
INNER JOIN operators o ON o.operator_name = r.operator_name;

-- Yorum: Sadece kendisine atanmış geçerli bir operatörü bulunan 9 robot listelenmiş, operatörü olmayan veya eşleşmeyen kayıtlar sonuç dışında kalmıştır.


-- Soru 2: Aynı liste, bütün robotlar görünsün (LEFT JOIN). 1. sorguyla karşılaştır, kim kayboldu?
SELECT r.name AS robot_adi, o.operator_name AS operator_adi, o.phone AS operator_telefon
FROM robots r
LEFT JOIN operators o ON o.operator_name = r.operator_name;

-- Kaybolanları görmek için yardımcı sorgu:
SELECT r.name AS robot_adi
FROM robots r
LEFT JOIN operators o ON o.operator_name = r.operator_name
WHERE o.operator_name IS NULL;

-- Yorum: LEFT JOIN ile filodaki 10 robotun tamamı listelenmiş ve 1. sorgudaki INNER JOIN sonucunda kaybolan robotun operatörü atanmamış (NULL) olan Mars-03 olduğu tespit edilmiştir.


-- Soru 3: Hiç görev almamış robotların adı ve modeli
SELECT r.name AS robot_adi, r.model
FROM robots r
LEFT JOIN missions m ON m.robot_id = r.id
WHERE m.id IS NULL;

-- Yorum: Missions tablosunda eşleşen bir kaydı bulunmayan ve henüz hiç görev almamış 4 robotun (Kartal-04, Kartal-02, Mars-03, Atlas-03) adı ve modeli listelenmiştir.


-- Soru 4a: JOIN ile hesaplanan toplam batarya (görevi olan robotlar)
SELECT sum(r.battery_level) AS toplam_batarya_join
FROM robots r
INNER JOIN missions m ON m.robot_id = r.id;

-- Soru 4b: JOIN kullanmadan doğru toplam
SELECT sum(r.battery_level) AS toplam_batarya_dogru
FROM robots r
WHERE EXISTS (SELECT 1 FROM missions m WHERE m.robot_id = r.id);

-- Yorum: INNER JOIN birden fazla görevi olan robotların batarya seviyelerini her görev satırı için tekrar topladığından (700) hatalı sonuç verirken, EXISTS kullanımı her robotu yalnızca bir kez hesaba katarak gerçek toplamı (262) vermiştir.


-- Soru 5: Robot başına görev sayısı; count(*) ve count(m.id) yan yana
SELECT r.id, r.name AS robot_adi,
       count(*)    AS count_yildiz,
       count(m.id) AS gorev_sayisi
FROM robots r
LEFT JOIN missions m ON m.robot_id = r.id
GROUP BY r.id, r.name
ORDER BY r.id;

-- Yorum: count(*) NULL satırları da saydığı için hiç görevi olmayan Kartal-02, Atlas-03, Mars-03 ve Kartal-04 robotlarında 1 sonucunu döndürürken, count(m.id) sadece gerçek görev kayıtlarını sayarak bu dört robot için doğru değer olan 0'ı vermiştir.