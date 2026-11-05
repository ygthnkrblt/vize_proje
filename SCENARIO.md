# SCENARIO — Kura 8

## Proje kimliği

- **Kura:** 8
- **Alan:** Eğitim
- **Sistem:** Sohbet asistanı
- **YZ dokunuşu:** Güvenlik ve olay takibi

## Hikâye ve problem

Bir dil öğrenme platformu, öğrencilerin kelime bilgisi, dil bilgisi, çeviri ve yazma pratiği yapabilmesi için sohbet asistanı kullanmaktadır. Bazı konuşmalarda asistanın uygunsuz veya saldırgan bir yanıt ürettiği ya da öğrenciyi yanlış yönlendirdiği bildirilmektedir. Platform, bu bildirimleri konuşma türüne göre izlemek; olası olayın türünü, şiddetini ve konuşmanın kaçıncı mesajında ortaya çıktığını görmek istemektedir.

Bu projenin ilk aşamasında amaç bir güvenlik sınıflandırıcısı geliştirmek değil, konuşma ve mesaj kayıtlarını PostgreSQL'de inceleyerek olayların dağılımını sorgulamaktır.

## Ana soru

**Hangi konuşma türünde güvenlik olayı en sık görülüyor ve olaylar kaç mesajdan sonra başlıyor?**

## Hedef kullanıcılar

- **Öğrenci:** Sohbet asistanını kullanan ve dil pratiği yapan kişi.
- **Eğitim yöneticisi:** Konuşma türlerine göre kalite ve güvenlik eğilimlerini izleyen görevli.
- **Güvenlik inceleme ekibi:** Modelin işaretlediği kayıtları inceleyip gerçek olay olup olmadığına karar veren ekip.

## Kapsam ve ölçüm yaklaşımı

- Bir konuşma, aynı `message_tree_id` altında toplanan mesaj ağacıdır.
- Mesaj sırası, kaynakta bulunan `created_date` zamanına göre sıralanarak oluşturulur. OASST1 dallanan bir yanıt ağacı olduğu için bu sıra tek bir gerçek zamanlı sohbet yolunu temsil etmek zorunda değildir; analizde kronolojik sıra göstergesi olarak kullanılır.
- `conversation_type` sınıfları kök mesajdaki İngilizce anahtar kelimelerle türetilir: `grammar_practice`, `vocabulary`, `translation`, `writing_help` ve `other_or_general`. Son kategori, belirli bir anahtar kelime eşleşmeyen sohbetleri toplar; hepsinin eğitim sohbeti olduğu iddia edilmez.
- Güvenlik işareti, mesajın Detoxify alt skorlarından herhangi birinin **0.20 veya üzerinde** olmasıdır. Bu eşik bu çalışma için seçilmiş bir tarama eşiğidir; evrensel veya klinik/kurumsal bir güvenlik standardı değildir.
- Bir mesajda en yüksek skora sahip kategori `event_type` olarak kaydedilir. Şiddet, aynı skorun 1–5 aralığına dönüştürülmesiyle hesaplanır.
- Her işaret `needs_human_review` niteliğinde değerlendirilmelidir. Model puanı tek başına ihlal kanıtı değildir.

## Hafta 3 — tablo adayları

Bu tablolar senaryonun kavramsal adaylarıdır. Vize kapsamında ERD, normalizasyon veya ilişkisel şema tasarımı yapılmamaktadır. Hafta 5 sorgularında JOIN gerektirmemek için bazı özet alanlar `conversations` tablosunda önceden hesaplanmıştır.

### `conversations`

| Kolon | Anlamı | Tür önerisi |
|---|---|---|
| `id` | Kaynaktaki konuşma ağacı kimliği | text |
| `conversation_type` | Kök mesaja göre türetilmiş konuşma türü | text |
| `started_at` | Konuşmadaki ilk mesaj zamanı | timestamptz |
| `message_count` | Konuşmadaki toplam mesaj sayısı | integer |
| `event_count` | Bu konuşmada işaretlenen olay sayısı | integer |
| `source_language` | Kaynak dil kodu | text |

### `messages`

| Kolon | Anlamı | Tür önerisi |
|---|---|---|
| `id` | Kaynaktaki mesaj kimliği | text |
| `conversation_id` | Bağlı olduğu konuşma | text |
| `sender` | `prompter` veya `assistant` rolü | text |
| `message_order` | Konuşma içindeki kronolojik sıra | integer |
| `length_chars` | Mesaj metninin karakter sayısı; boşsa NULL | integer |
| `sent_at` | Mesaj zamanı | timestamptz |
| `toxicity_score` | Toksisite skoru | numeric |
| `severe_toxicity_score` | Ağır toksisite skoru | numeric |
| `obscene_score` | Müstehcenlik skoru | numeric |
| `identity_attack_score` | Kimlik saldırısı skoru | numeric |
| `insult_score` | Hakaret skoru | numeric |
| `threat_score` | Tehdit skoru | numeric |
| `sexual_explicit_score` | Açık cinsel içerik skoru | numeric |
| `review_result` | Kaynağın genel kalite incelemesi sonucu; güvenlik onayı değildir | boolean |

### `events`

| Kolon | Anlamı | Tür önerisi |
|---|---|---|
| `id` | Projede türetilen olay kimliği | text |
| `conversation_id` | Olayın ait olduğu konuşma | text |
| `message_id` | İşaretlenen mesaj | text |
| `event_type` | En yüksek risk alt skoru kategorisi | text |
| `severity_1_5` | Skor aralığından türetilen şiddet | integer |
| `message_order` | Olayın başladığı mesaj sırası | integer |
| `detected_at` | İşaretlenen mesajın zamanı | timestamptz |
| `risk_score` | Olay türüne karşılık gelen en yüksek skor | numeric |
| `detection_source` | İşaretin kaynağı | text |

## Hafta 4 — veri sorunları ve temizlik planı

- **Boş mesaj:** `length_chars` hesaplanamayan mesaj için NULL kullanılır; sıfır uzunlukla eksik değer birbirine karıştırılmaz.
- **Atlanan mesaj sırası:** Kaynak bir konuşma ağacıdır ve dallanabilir. Sıra numarası mesaj zamanlarından yeniden üretilir; bu sıra tek bir diyalog yolunun kanıtı olarak yorumlanmaz.
- **Konuşma türü yazımı:** Kaynaktan türetilen bazı kategori etiketleri staging CSV'sinde büyük/küçük harf veya baş/son boşluk farkıyla gösterilir. Temiz CSV'de `lower(trim(...))` mantığıyla tek biçime getirilir. Bu varyasyonlar kaynak verinin orijinal etiketi değildir; temizlik adımını göstermek için türetilmiş alanda oluşturulmuştur.
- **Skor NULL değerleri:** Kaynakta bulunmayan Detoxify alt skorları NULL bırakılır; 0 olarak doldurulmaz.
- **Tarih:** ISO-8601 zaman damgaları PostgreSQL `timestamptz` alanına yüklenir.
- **Gizlilik:** İşlenmiş tablolara mesajın kendisi ve kaynak `user_id` alanı aktarılmaz. Mesaj metninden yalnızca karakter uzunluğu hesaplanır.

## Hafta 5 — analiz sorguları

1. **Konuşma türü başına konuşma sayısı ve ortalama mesaj sayısı.** `GROUP BY`, `COUNT`, `AVG`, `ROUND` kullanılır. Çok mesajlı konuşma türleri belirlenir.
2. **Boş mesaj/uzunluk kayıtları.** `COUNT(*)` ve `COUNT(length_chars)` farkı hesaplanır. Fark, karakter uzunluğu bulunmayan mesaj sayısını gösterir.
3. **Olay oranı %5'in üzerinde olan konuşma türleri.** `GROUP BY` ve `HAVING` kullanılır. Olayla işaretlenen konuşmaların oranı tür bazında karşılaştırılır.
4. **Konuşma uzunluğu sınıfları.** `CASE WHEN` ile `short` (1–4), `medium` (5–10), `long` (11+) sınıfları oluşturulur ve dağılım incelenir.
5. **Haftalık olay sayısı ve olaya kadar mesaj sırası.** `date_trunc('week', detected_at)` ve `AVG(message_order)` kullanılır. Olayların hangi haftalarda arttığı ve ortalama kaçıncı mesajda işaretlendiği incelenir.

## Dönem sonu YZ bileşeni — bu vizenin dışında

Dönem sonunda sınıflandırıcının işaretlediği mesajlarla insan incelemesinin sonuçlarını karşılaştıran bir değerlendirme tablosu kurulabilir. Böylece yanlış pozitif ve insan incelemesinin onayladığı işaret oranı izlenebilir. Bu aşamada veritabanında YZ bileşeni, rol veya yetki uygulaması yapılmamaktadır.

## Veri kaynağına ilişkin önemli sınırlama

OpenAssistant OASST1 genel amaçlı, çok dilli bir sohbet veri setidir; gerçek bir dil öğrenme platformundan toplanmamıştır. Bu nedenle proje, eğitim platformu senaryosunu analiz amacıyla örnekleyen bir veri çalışmasıdır. `conversation_type` sınıfı kök mesajdaki anahtar kelimelerle kural tabanlı üretilir ve insan tarafından doğrulanmış eğitim etiketi değildir.
