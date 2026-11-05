-- HAFTA 5 — GROUP BY, NULL, tarih fonksiyonları ve CASE WHEN
-- Her sorgunun açıklaması; ne sorduğunu, beklenen sonucu ve sonucun nasıl yorumlanacağını belirtir.

-- Sorgu 1: Konuşma türüne göre konuşma sayısını ve ortalama mesaj sayısını bul.
-- Beklenti: Her konuşma türü için bir satır oluşur. Ortalama mesaj sayısı yüksek olan türler daha uzun sohbet eğilimi gösterir.
-- GROUP BY, COUNT, AVG ve ROUND kullanılır. event_count yalnızca ek bağlam sağlar.
SELECT
    conversation_type,
    COUNT(*) AS conversation_count,
    ROUND(AVG(message_count), 2) AS avg_message_count,
    SUM(event_count) AS total_flagged_events
FROM conversations
GROUP BY conversation_type
ORDER BY conversation_count DESC;

-- Sorgu 2: Mesaj uzunluğu bulunmayan kayıtları COUNT(*) ve COUNT(length_chars) ile hesapla.
-- Beklenti: COUNT(*) toplam mesajı, COUNT(length_chars) uzunluğu bilinen mesajları verir.
-- İki sayının farkı NULL uzunluklu kayıt sayısıdır; NULL değerini 0 kabul etmek doğru değildir.
SELECT
    COUNT(*) AS total_messages,
    COUNT(length_chars) AS messages_with_length,
    COUNT(*) - COUNT(length_chars) AS missing_length_messages
FROM messages;

-- Sorgu 3: Olayla işaretlenen konuşmaların oranı yüzde 5'in üzerinde olan konuşma türlerini bul.
-- Beklenti: Yalnızca oranı %5'i aşan türler listelenir. Sonuç, model işaretlerinin dağılımını gösterir; gerçek ihlal oranı değildir.
-- GROUP BY ve HAVING kullanılır. event_count konuşma bazında veri hazırlanırken hesaplandığı için JOIN gerekmez.
SELECT
    conversation_type,
    COUNT(*) AS conversation_count,
    SUM(CASE WHEN event_count > 0 THEN 1 ELSE 0 END) AS flagged_conversations,
    ROUND(
        100.0 * SUM(CASE WHEN event_count > 0 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS flagged_conversation_pct
FROM conversations
GROUP BY conversation_type
HAVING 100.0 * SUM(CASE WHEN event_count > 0 THEN 1 ELSE 0 END) / COUNT(*) > 5
ORDER BY flagged_conversation_pct DESC;

-- Sorgu 4: Konuşmaları mesaj sayısına göre short, medium ve long sınıflarına ayır.
-- Beklenti: Her uzunluk sınıfı ve konuşma türü için adetler görünür.
-- CASE WHEN ile 1–4 kısa, 5–10 orta, 11 ve üzeri uzun konuşma olarak tanımlanır.
SELECT
    CASE
        WHEN message_count <= 4 THEN 'short'
        WHEN message_count <= 10 THEN 'medium'
        ELSE 'long'
    END AS conversation_length,
    conversation_type,
    COUNT(*) AS conversation_count
FROM conversations
GROUP BY
    CASE
        WHEN message_count <= 4 THEN 'short'
        WHEN message_count <= 10 THEN 'medium'
        ELSE 'long'
    END,
    conversation_type
ORDER BY conversation_length, conversation_type;

-- Sorgu 5: Haftalara göre işaretlenen olay sayısını ve olayın konuşmadaki ortalama mesaj sırasını bul.
-- Beklenti: Her hafta için olay sayısı ve ortalama mesaj sırası görünür.
-- date_trunc('week') haftalık gruplama yapar. message_order, ilk mesajdan itibaren kronolojik sırayı temsil eder.
SELECT
    DATE_TRUNC('week', detected_at) AS event_week,
    COUNT(*) AS weekly_event_count,
    ROUND(AVG(message_order::numeric), 2) AS avg_message_order_at_event
FROM events
GROUP BY DATE_TRUNC('week', detected_at)
ORDER BY event_week;
