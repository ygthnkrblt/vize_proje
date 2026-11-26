-- Ödev 2, Bölüm 1: Filo soruları
-- Ad Soyad:
-- Veritabanı: robot_fleet
-- Her sorgunun altına sonucu açıklayan tek cümlelik yorum yaz.
--
-- DİKKAT: Sütun adları tahmindir (operators: id, name, phone; robots: id, name, model,
-- battery_level, operator_id; missions: id, robot_id). Önce `\d operators`, `\d robots`,
-- `\d missions` çalıştır; adlar farklıysa sorgularda düzelt.
-- Yorumları sorguyu çalıştırıp çıktıyı gördükten SONRA yaz.

-- Soru 1: Her robotun adı, operatör adı ve operatör telefonu (INNER JOIN)
SELECT r.name AS robot_adi, o.name AS operator_adi, o.phone AS operator_telefon
FROM robots r
INNER JOIN operators o ON o.id = r.operator_id;

-- Yorum: (kaç satır döndü, neden? INNER JOIN operatörü olmayan robotlara ne yapar?)


-- Soru 2: Aynı liste, bütün robotlar görünsün (LEFT JOIN). 1. sorguyla karşılaştır, kim kayboldu?
SELECT r.name AS robot_adi, o.name AS operator_adi, o.phone AS operator_telefon
FROM robots r
LEFT JOIN operators o ON o.id = r.operator_id;

-- Kaybolanları görmek için yardımcı sorgu (sağ tablonun anahtarında IS NULL):
SELECT r.name AS robot_adi
FROM robots r
LEFT JOIN operators o ON o.id = r.operator_id
WHERE o.id IS NULL;

-- Yorum: (1. sorguya göre kaç satır fazla, hangi robot(lar) neden kayboldu?)


-- Soru 3: Hiç görev almamış robotların adı ve modeli
SELECT r.name AS robot_adi, r.model
FROM robots r
LEFT JOIN missions m ON m.robot_id = r.id
WHERE m.id IS NULL;

-- Yorum: (kaç robot döndü, neden bu robotlar?)


-- Soru 4a: JOIN ile hesaplanan toplam batarya (görevi olan robotlar)
SELECT sum(r.battery_level) AS toplam_batarya_join
FROM robots r
INNER JOIN missions m ON m.robot_id = r.id;

-- Soru 4b: JOIN kullanmadan doğru toplam
SELECT sum(r.battery_level) AS toplam_batarya_dogru
FROM robots r
WHERE EXISTS (SELECT 1 FROM missions m WHERE m.robot_id = r.id);

-- Yorum (iki sonuç ve fark): (4a kaç, 4b kaç; fark neden oluştu, hangi robot kaç kez sayıldı?)


-- Soru 5: Robot başına görev sayısı; count(*) ve count(m.id) yan yana
SELECT r.id, r.name AS robot_adi,
       count(*)    AS count_yildiz,
       count(m.id) AS gorev_sayisi
FROM robots r
LEFT JOIN missions m ON m.robot_id = r.id
GROUP BY r.id, r.name
ORDER BY r.id;

-- Yorum (hangi robotlarda ikisi farklı?): (hangi robotlarda count_yildiz ile gorev_sayisi ayrıldı, neden?)
