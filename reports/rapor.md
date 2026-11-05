# Vize Projesi Raporu — Kura 8

**Ders:** BLP 105 / Veritabanı Yönetim Sistemleri · **Tarih:** 04.11.2026  
**Proje:** Eğitim sohbet asistanı — güvenlik ve olay takibi  
**Ad Soyad:** __________________________  **Öğrenci No:** __________________

## 1. Problem ve amaç

Bu projede dil öğrenme platformunda kullanılan sohbet asistanının konuşmalarında ortaya çıkabilecek güvenlik işaretleri incelenmektedir. Ana soru, hangi konuşma türünde olay işaretlerinin daha sık görüldüğü ve bu işaretlerin konuşmanın kaçıncı mesajında ortaya çıktığıdır. Çalışmanın vize kapsamı Hafta 3–5 ile sınırlıdır: senaryo ve tablo adayları, veri hazırlama/SELECT-WHERE ve beş analiz sorgusu.

## 2. Veri ve yöntem

Kaynak olarak Apache-2.0 lisanslı OpenAssistant OASST1 veri setinin İngilizce, hazır dışa aktarma konuşma ağaçları kullanılır. Kaynak genel amaçlı sohbet verisidir; gerçek bir dil okulunun kayıtları değildir. Mesaj metni ve kaynak kullanıcı kimliği işlenmiş CSV'lere aktarılmaz. Konuşma türü kök mesajdaki anahtar kelimelerle yaklaşık olarak sınıflandırılır. Olaylar, Detoxify alt skorlarından en az biri 0.20 veya üzerindeyse inceleme işareti olarak üretilir. Bu işaretler doğrulanmış ihlal olarak yorumlanmaz.

**Gerçek veri özeti (04.11.2026 yerel çalıştırması):**

- Konuşma sayısı: **800**
- Mesaj sayısı: **8.698**
- İşaretlenen olay sayısı: **70**
- Veri tarih aralığı: **2023-01-16 21:17:45.947855+00 — 2023-02-26 02:46:15.121984+00**
- NULL `length_chars` sayısı: **0**

## 3. Sorgu sonuçları

- Olay oranı en yüksek konuşma türü: **translation**
- Bu türün işaretli konuşma oranı: **20,00 %** (5 konuşmanın 1'i)
- Olay anındaki ortalama mesaj sırası: **7,23**
- En sık görülen olay kategorisi: **toxicity** (59 olay)

Bu sonuçlar, işlenmiş CSV'ler üzerinden sorguların hesapladığı gerçek değerlerdir; PostgreSQL sunucusu bu çalışma ortamında kurulu olmadığı için canlı `psql` çıktısı alınamamıştır. Veri setindeki dallanan konuşma ağaçları nedeniyle `message_order` kronolojik sıra göstergesidir; tek bir diyalog yolunu kanıtlamaz. Model işaretleri insan incelemesi olmadan kesin güvenlik olayı sayılamaz.

## 4. Yapay zekâ kullanım beyanı ve doğrulama

ChatGPT; senaryo dokümantasyonu, veri hazırlama betiği, SQL taslakları ve rapor düzeni için yardımcı olarak kullanılmıştır. Kullanım `AI_BEYAN.md` içinde açıklanmıştır. Betik yerel bilgisayarda yeniden çalıştırılmış ve statik CSV kontrolleri yapılmıştır; PostgreSQL/`psql` bu çalışma ortamında bulunmadığı için SQL dosyalarının canlı veritabanı çalıştırması ayrıca yapılmalıdır.

**İmza:** __________________________
