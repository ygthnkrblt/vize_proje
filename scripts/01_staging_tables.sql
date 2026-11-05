-- YEREL İÇE AKTARMA YARDIMCISI — vize kapsamında değerlendirilecek DDL/ERD değildir.
-- Amaç yalnızca CSV dosyalarını PostgreSQL'e alabilecek basit düz tablo yapıları oluşturmaktır.
-- İlişki, foreign key veya dönem sonu şeması tasarımı içermez.

DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;

CREATE TABLE conversations (
    id text,
    conversation_type text,
    started_at timestamptz,
    message_count integer,
    event_count integer,
    source_language text
);

CREATE TABLE messages (
    id text,
    conversation_id text,
    sender text,
    message_order integer,
    length_chars integer,
    sent_at timestamptz,
    toxicity_score numeric,
    severe_toxicity_score numeric,
    obscene_score numeric,
    identity_attack_score numeric,
    insult_score numeric,
    threat_score numeric,
    sexual_explicit_score numeric,
    review_result boolean
);

CREATE TABLE events (
    id text,
    conversation_id text,
    message_id text,
    event_type text,
    severity_1_5 integer,
    message_order integer,
    detected_at timestamptz,
    risk_score numeric,
    detection_source text
);
