# Veri Kartı — OpenAssistant OASST1 (Kura 8)

## Kaynak

- **Ad:** OpenAssistant Conversations Dataset (OASST1)
- **Hugging Face:** https://huggingface.co/datasets/OpenAssistant/oasst1
- **Orijinal proje:** https://github.com/LAION-AI/Open-Assistant
- **Kullanılan dosya:** `2023-04-12_oasst_ready.messages.jsonl.gz`
- **Doğrudan indirme:** https://huggingface.co/datasets/OpenAssistant/oasst1/resolve/main/2023-04-12_oasst_ready.messages.jsonl.gz
- **Lisans:** Apache License 2.0. Kaynak kartındaki lisans ve koşullar korunmalıdır.
- **İndirme tarihi:** `scripts/download_and_prepare.py` çalıştırıldığı gün `data/processed/data_card_run.md` içine yazılır.
- **Kaynağın açıklanan ölçeği:** Hazır dışa aktarma bölümünde 88.838 mesaj ve 10.364 konuşma ağacı bulunur. Veri setinin genel sürümü daha fazla ağaç ve mesaj içerir.

## Bu projede kullanılan alt küme

- Yalnızca `lang = en`, `tree_state = ready_for_export` ve silinmemiş kayıtlar seçilir.
- Varsayılan hedef 800 farklı konuşma ağacıdır; script en az 500 farklı konuşma seçilemezse durur.
- Dört CSV'nin (`conversations.csv`, `conversations_stage.csv`, `messages.csv`, `events.csv`) satır sayıları gerçek indirme ve işleme tamamlandığında `data/processed/data_card_run.md` dosyasına yazılır.
- `data/processed/` altında dört CSV tutulur: `conversations.csv`, temizlik öncesi varyantı gösteren `conversations_stage.csv`, `messages.csv` ve `events.csv`. Gerçek satır sayıları çalıştırma kartında ve `build_summary.json` içinde tutulur.
- **Üretilmiş gerçek konuşma veya mesaj satırı:** 0. Konuşma ve mesaj içerikleri kaynak veriden gelir; script yeni konuşma veya mesaj metni üretmez.
- **Türetilmiş alanlar:** Konuşma türü, mesaj karakter uzunluğu, olay kategorisi, risk skoru ve şiddet sınıfı programatik olarak hesaplanır. Bunlar kaynakta insan tarafından atanmış platform etiketleri değildir.
- **Konuşma türleri:** `grammar_practice`, `vocabulary`, `translation`, `writing_help`, `other_or_general`. Son kategori, yukarıdaki anahtar kelime kurallarına girmeyen konuları içerir.
- **Gizlilik:** İşlenmiş CSV'lere mesaj metni veya kaynak `user_id` aktarılmaz. Kaynaktaki metin sadece uzunluğu hesaplamak ve kök mesajı sınıflandırmak için bellekte okunur.

## Sayısal ve tarih alanları

- Sayısal: `message_order`, `length_chars`, Detoxify alt skorları, `message_count`, `event_count`, `severity_1_5`, `risk_score`.
- Tarih/zaman: `started_at`, `sent_at`, `detected_at`.

## Olay tanımı

Kaynakta her mesaj için Detoxify skorları bulunabilir: `toxicity`, `severe_toxicity`, `obscene`, `identity_attack`, `insult`, `threat`, `sexual_explicit`. Bu projede en yüksek alt skor **0.20 veya üzerindeyse** bir inceleme işareti (`event`) üretilir. En yüksek skora sahip kategori olay türü olur. Bu eşik yalnızca ders projesinin keşif amaçlı kuralıdır. Model puanları hata yapabilir; işaretler doğrulanmış güvenlik ihlali sayılmaz.

Şiddet dönüşümü:

| En yüksek skor | Şiddet |
|---:|---:|
| 0.20–0.3499 | 1 |
| 0.35–0.4999 | 2 |
| 0.50–0.6499 | 3 |
| 0.65–0.7999 | 4 |
| 0.80–1.00 | 5 |

## Temizleme adımları

1. Ham `.jsonl.gz` dosyası `data/raw/` altına indirilir ve **hiçbir zaman elle değiştirilmez**.
2. Hazır dışa aktarma durumundaki, silinmemiş İngilizce mesajlar seçilir.
3. Konuşma ağacı kimliğiyle gruplama yapılır; konuşma başlangıcı en erken mesaj zamanı olarak alınır.
4. Mesaj sırası `created_date` alanına göre kronolojik atanır. OASST1 dallanan bir ağaç olduğu için bu numara tek bir sohbet yolunu temsil etmez.
5. Mesaj metni ve kaynak kullanıcı kimliği çıktı CSV'lerine yazılmaz; yalnızca karakter uzunluğu ve gerekli ölçüm alanları tutulur.
6. Kaynak skoru eksikse NULL bırakılır; 0 ile değiştirilmez.
7. Konuşma türü anahtar kelime kuralıyla türetilir. Staging dosyasında bazı kategori yazımları temizlik adımını göstermek amacıyla kasıtlı olarak farklılaştırılır; temiz CSV'de küçük harf ve boşluklar normalize edilir.
8. Olaylar, belirtilen Detoxify eşiğiyle türetilir; bunların insan tarafından doğrulanmış ihlal olmadığı raporlanır.

## Lisans ve paylaşım notu

OASST1 sayfası veri setini Apache-2.0 lisansıyla sunar. Yine de ham dosya serbest metin ve kullanıcı girdileri içerdiği için bu projede ham `.gz` Git'e eklenmez (`.gitignore`). İşlenmiş CSV'lerde mesaj metni ve kaynak kullanıcı kimliği yoktur. Eğitmen ham dosyanın da teslim edilmesini isterse, dosyanın paylaşım biçimini kişisel veri/gizlilik şartlarına göre eğitmenle netleştir; herkese açık depoya metin içeren ham kayıt yükleme.

## Tekrar üretilebilirlik

Proje kök dizininden:

```bash
python scripts/download_and_prepare.py --limit-conversations 800
```

İşlem sonunda gerçek satır sayıları, tarih aralığı, NULL sayıları ve olay sayıları `data/processed/data_card_run.md` dosyasına yazılır. Bu kartı teslimden önce kontrol et.
