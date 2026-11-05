# Ham veri

`2023-04-12_oasst_ready.messages.jsonl.gz` dosyası `scripts/download_and_prepare.py` tarafından resmi Hugging Face adresinden indirilir.

- Bu dosya orijinal kaynak dosyadır; açıp düzenleme veya üzerine yazma.
- İndirme ve SHA-256 kontrolü script tarafından yapılır.
- Metin ve olası kişisel bilgi içerebileceğinden `.gitignore` ile Git'e eklenmez. İşlenmiş ve metinsiz CSV'ler `data/processed/` altına üretilir.
