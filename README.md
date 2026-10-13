# SHMYO Web Uygulaması — pilot sürüm

## Yerel kurulum
Python 3.10+ kurun. Klasör içinde terminal açıp:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tarayıcıda çıkan http://localhost:8501 adresini açın. Sol menüden modüller arasında geçiş yapabilirsiniz.

## İnternette yayımlama
Streamlit Community Cloud veya kurumsal bir sunucuda Git deposundan `app.py` giriş dosyasıyla yayımlanabilir. **Bu pilot sürümü gerçek öğrenci verileriyle internete açmayın.** Önce giriş/rol yetkilendirmesi, güvenli veritabanı, yedekleme, veri saklama politikası ve KVKK değerlendirmesi gerekir.

## Sınırlar
- İki önceki prototip tek Streamlit web arayüzünde birleştirilmiştir; ortak veritabanı entegrasyonu henüz yapılmadı.
- EvalBee'nin gerçek dışa aktarım formatı test edilmedi; örnek CSV/XLSX şablonuyla çalışır.
- Hematoloji çıktıları mevcut pilot modüldeki tanımlardan gelir; kurum kaynağıyla yayımdan önce teyit edilmelidir.
- Üretim güvenliği, kullanıcı giriş sistemi ve çoklu kullanıcı desteği bulunmaz.
