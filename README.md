# Kura 8 — Eğitim Sohbet Asistanı Güvenlik ve Olay Takibi

**Ders:** BLP 105 / Veritabanı Yönetim Sistemleri · Güz 2026  
**Kura:** 8 · **Alan:** Eğitim · **Sistem:** Sohbet asistanı · **YZ bileşeni:** Güvenlik ve olay takibi

Bu depo, vize belgesindeki Hafta 3–5 kapsamına göre hazırlanmıştır. Tam dönem projesi, ERD, JOIN veya dönem sonu YZ bileşeninin veritabanında uygulanması bu teslimin parçası değildir.

## İçerik

| Dosya | Amaç |
|---|---|
| `SCENARIO.md` | Problem, ana soru, kullanıcılar ve tablo adayları |
| `data/README.md` | Veri kartı, kaynak, lisans ve temizleme açıklaması |
| `scripts/download_and_prepare.py` | Açık veri kaynağını indirip güvenli/analize hazır dört CSV ve çalıştırma özetini üretir |
| `scripts/01_staging_tables.sql` | CSV içe aktarma için basit yerel hazırlık tabloları (vize değerlendirme çıktısı değildir) |
| `scripts/02_load_csv.psql` | CSV dosyalarını PostgreSQL'e yükler |
| `sql/hafta-04-select.sql` | SELECT ve WHERE örnekleri |
| `sql/hafta-05.sql` | Senaryoya özel en az beş analiz sorgusu |
| `AI_BEYAN.md` | Yapay zekâ kullanım beyanı |
| `reports/rapor.md` | Sınıfta elden verilecek tek sayfalık rapor taslağı |

## 1. Veriyi hazırlama

Gereksinim: Python 3.10 veya üzeri. Ek Python paketi gerekmez; yalnızca Python standart kütüphanesi kullanılır.

Proje klasörünün kök dizininde terminal aç ve çalıştır:

```bash
python scripts/download_and_prepare.py --limit-conversations 800
```

İlk çalıştırmada OpenAssistant'ın orijinal, sıkıştırılmış `ready.messages.jsonl.gz` dosyası `data/raw/` altına indirilir. Ardından İngilizce konuşma ağaçlarından en fazla 800 konuşmalık örnek seçilir ve `data/processed/` altında `conversations.csv`, `conversations_stage.csv`, `messages.csv`, `events.csv` ile `build_summary.json` ve `data_card_run.md` üretilir. **En az 500 farklı konuşma seçilemezse script hata vererek durur; daha az veriyi 500 gibi göstermeye çalışmaz.**

Ham `.gz` dosyası değiştirilmez. Kaynak dosyada serbest metin ve kullanıcı mesajları bulunabildiği için `.gitignore` ile Git'e eklenmesi engellenmiştir. İşlenmiş CSV'lerde mesaj metni veya kullanıcı kimliği yoktur; yalnızca mesaj uzunluğu, rol, zaman ve güvenlik skorları bulunur. Eğitmenin ham dosyanın GitHub'a yüklenmesini özellikle istemesi hâlinde, bunu **özel (private) depo** ve dersin veri-gizliliği kuralları çerçevesinde yap.

Bu çalıştırmada gerçek çıktı özeti `data/processed/data_card_run.md` ve makine tarafından okunabilir `data/processed/build_summary.json` dosyalarında saklanır. CSV çıktıları yeniden üretilebilir ve depoda tutulabilir; ham `.jsonl.gz` ile indirme sırasında oluşan `.part` dosyaları `.gitignore` kapsamındadır.

## 2. PostgreSQL'e yükleme

Önce PostgreSQL'de `egitim_chatbot` adında boş bir veritabanı oluştur. PostgreSQL 18 Windows kurulumunda Git Bash üzerinden örnek komutlar:

```bash
"/c/Program Files/PostgreSQL/18/bin/createdb.exe" -U postgres egitim_chatbot
"/c/Program Files/PostgreSQL/18/bin/psql.exe" -U postgres -d egitim_chatbot -f scripts/01_staging_tables.sql
"/c/Program Files/PostgreSQL/18/bin/psql.exe" -U postgres -d egitim_chatbot -f scripts/02_load_csv.psql
```

`psql` parola sorarsa PostgreSQL kurulumunda belirlediğin parolayı gir. Komutları proje klasörünün kök dizinindeyken çalıştır; `\copy` yolları bu dizine göredir.

Yükleme kontrolü:

```sql
SELECT COUNT(*) FROM conversations;
SELECT COUNT(*) FROM messages;
SELECT COUNT(*) FROM events;
```

`conversations` tablosunda en az 500 satır görmelisin. Sonra:

```bash
"/c/Program Files/PostgreSQL/18/bin/psql.exe" -U postgres -d egitim_chatbot -f sql/hafta-04-select.sql
"/c/Program Files/PostgreSQL/18/bin/psql.exe" -U postgres -d egitim_chatbot -f sql/hafta-05.sql
```

## 3. Teslimden önce

1. `data/processed/data_card_run.md` dosyasındaki gerçek satır sayılarını kontrol et.
2. Hafta 4 ve Hafta 5 SQL dosyalarını kendi PostgreSQL veritabanında çalıştır; hata varsa düzelt.
3. `reports/rapor.md` içindeki boş sonuç alanlarını kendi sorgu çıktılarından doldur. Çalıştırmadığın bir sorgu için sonuç uydurma.
4. `AI_BEYAN.md` dosyasını oku ve kendi yaptığın doğrulama adımlarını ekle.
5. Bu klasörü dersin ortak kaynak reposuna değil, kendi GitHub proje repona koy.

## Veri ve yöntem sınırı

OASST1 genel amaçlı, çok dilli bir sohbet koleksiyonudur; belirli bir dil okulunun veya gerçek bir eğitim platformunun kayıtları değildir. Bu projede yalnızca İngilizce konuşma ağaçları kullanılır. `conversation_type` kök kullanıcı mesajındaki anahtar kelimelerle türetilen yaklaşık bir sınıftır. Güvenlik olayları, kaynakta bulunan Detoxify skorlarının seçilen eşik üzerindeki işaretleridir; **doğrulanmış ihlal anlamına gelmez**. Gerçek üründe insan incelemesi gerekir.
