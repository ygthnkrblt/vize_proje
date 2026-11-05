-- HAFTA 4 — SELECT ve WHERE
-- Bu dosyada yalnızca tek tablo üzerinde temel okuma ve filtreleme yapılır.

-- Soru 1: Örnek 10 konuşmanın temel alanlarını göster.
-- Beklenti: En fazla 10 satır. Sonuç, konuşma türü ve başlangıç zamanını kontrol etmeyi sağlar.
SELECT id, conversation_type, started_at, message_count
FROM conversations
ORDER BY started_at
LIMIT 10;

-- Soru 2: Grammar practice türündeki konuşmaları bul.
-- Beklenti: Sıfır veya daha fazla satır. Türün doğru yazıldığını kontrol eder.
SELECT id, conversation_type, started_at, message_count
FROM conversations
WHERE conversation_type = 'grammar_practice'
ORDER BY started_at
LIMIT 25;

-- Soru 3: Belirli tarihten sonra başlayan konuşmaları listele.
-- Beklenti: Tarih filtresine uyan konuşmalar döner; zaman damgası timestamptz olarak okunur.
SELECT id, conversation_type, started_at
FROM conversations
WHERE started_at >= TIMESTAMPTZ '2023-02-01 00:00:00+00'
ORDER BY started_at
LIMIT 25;

-- Soru 4: Uzun konuşmaları (10 mesajdan fazla) görüntüle.
-- Beklenti: message_count > 10 olan konuşmalar gelir.
SELECT id, conversation_type, message_count, event_count
FROM conversations
WHERE message_count > 10
ORDER BY message_count DESC
LIMIT 25;

-- Soru 5: Karakter uzunluğu NULL olan mesajları bul.
-- Beklenti: Eksik uzunluk ölçümü bulunan satırlar gelir; sıfır uzunlukla NULL aynı şey değildir.
SELECT id, conversation_id, sender, message_order, sent_at
FROM messages
WHERE length_chars IS NULL
ORDER BY sent_at
LIMIT 50;

-- Soru 6: Yalnızca asistan mesajlarını göster.
-- Beklenti: sender değeri assistant olan kayıtlar gelir.
SELECT id, conversation_id, sender, message_order, length_chars
FROM messages
WHERE sender = 'assistant'
ORDER BY sent_at DESC
LIMIT 20;

-- Soru 7: Toksisite skoru tarama eşiğinin üzerinde olan mesajları listele.
-- Beklenti: Skoru 0.20 veya üzeri olan mesajlar gelir; bu satırlar doğrulanmış ihlal değildir.
SELECT id, conversation_id, message_order, toxicity_score, severe_toxicity_score
FROM messages
WHERE toxicity_score >= 0.20
ORDER BY toxicity_score DESC
LIMIT 25;

-- Soru 8: Şiddeti 4 veya 5 olarak türetilen olayları göster.
-- Beklenti: Yüksek skorlu işaretler görünür; insan incelemesi gerekir.
SELECT id, conversation_id, event_type, severity_1_5, message_order, detected_at
FROM events
WHERE severity_1_5 >= 4
ORDER BY detected_at
LIMIT 50;

-- Soru 9: Tehdit kategorisinde işaretlenen olayları listele.
-- Beklenti: event_type değeri threat olan işaretler döner.
SELECT id, conversation_id, event_type, risk_score, severity_1_5
FROM events
WHERE event_type = 'threat'
ORDER BY risk_score DESC;

-- Soru 10: Dil alanı İngilizce olmayan kayıt var mı?
-- Beklenti: Veri hazırlama adımında yalnızca İngilizce seçildiği için 0 satır beklenir.
SELECT id, source_language
FROM conversations
WHERE source_language <> 'en';
