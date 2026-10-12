# Yönetilen LCD ikonları

[English](README.md) · [Türkçe](README_TR.md)

Baseline JPEG dosyalarını buraya ekleyin veya mevcut olanları değiştirin. Dosya adı ikon ID'siyle başlamalı: `092.jpg`, `092-about.jpg` veya `092_about.jpeg`. ID aralığı 0–255'tir; her ID yalnız bir dosyada kullanılabilir. Mevcut ID'lerin anlamı korunur. ID ve içerik aynı kalırken dosya adını değiştirmek yükleme başlatmaz. Yeni görsel kütüphaneye girer; ID'nin arayüzde nerede gösterileceğini UI kodu seçer.

JPEG'ler boyutlandırılmadan ve yeniden sıkıştırılmadan korunur. Progressive JPEG, yinelenen ID ve 32767 bayttan büyük görseller reddedilir. Kütüphane Picture Flash 3–15 slotlarına sığmalıdır; stok 1–2 resimleri korunur; resim 0 ayrı yönetilen Petrel açılış görselidir.

Uygulama güncellemesinden sonraki ilk LCD bağlantısında bu klasörden kütüphane oluşturulur. Paketleyici büyük ikonları önce yerleştirir ve küçük ikonlarla kalan boşlukları doldurur. ID sırası fiziksel yerleşimden bağımsızdır. Her bloğun son baytı ayrılır ve UART yazımına dahil edilmez. Hiçbir JPEG blok sınırını geçmez.

Yalnız değişen bloklar yüklenir; tablo bloğu en son yazılır. Paneldeki kayıt tamamlanan blokları saklar; sonraki açılış eksik yüklemeyi tamamlar. Değişmeyen kütüphanede Flash yazılmaz. Başarısız Picture Flash denemesi aynı süreçte tekrarlanmaz. Yükleme ilerlemesi ve hatalar loglarda yer alır.

Çalışma sırasında kullanılan paketin aynısını dışa aktarın:

```bash
python tools/pack_icon_library.py assets/icons /tmp/3.ICO
```

Emülatör de bu JPEG kaynaklarını kullanır. `assets/emulator/3.ICO` referans çıktıdır; otomatik güncellemenin kaynağı değildir.

Özel UI ikonları 100–109 ve 124 ID'lerini kullanır. MMU 100/101, Display 108/109 ID'leriyle seçili olmayan/seçili 110×100 ana menü ikonlarını kullanır; boyutlar mevcut ana menü yerleşimine uyar; normal ve seçili Graphite yüzeyleri farklıdır. Boş makara 124 ID’sini kullanır. Metal makara yan parçaları 1–7 genişlikleri için 110–123 ID'lerini kullanır; dar alanlarda ayrı tam makara görselleri gerekmez. Sembolik eşleştirme `lcd_resources.py` içindedir. Tüm UI ikonları doğrudan kütüphane 3'den çizilir.

Panel kaynaklarını yeniden yüklediğinizde, kayıt eski kurulumu tarif ediyor olabileceğinden zorla yeniden yükleyin:

```bash
sudo systemctl stop Petrel.service
~/petrel-env/bin/python ~/Petrel/tools/reload_icons.py
sudo systemctl start Petrel.service
```

Yazma onayları ve kayıt geri okuması doğrulanır; Picture Flash'ın kendisi geri okunmaz. Yeni ikon yerleşimini fiziksel ekranda kontrol edin.

## Graphite

Graphite; ışık, parlaklık, ses ayarları, hareket parametreleri, kalibrasyon ve profiller için 210–234 ID’lerini ekler. Düzenlenebilir SVG kaynakları `assets/icon-source` içindedir; JPEG üretmek için `python tools/render_icon_sources.py` çalıştırın (geliştirme bağımlılığı: CairoSVG). Siyah JPEG zemini panelin şeffaf/enhanced ikon modu ile filtrelenir; menü ve dashboard yüzeyleri korunur. İkon paketi 3 numaralı slotta başlar, 3–15 slotlarını kullanabilir; 512 baytlık metadata kaydı Data Flash `0x0200–0x03FF` aralığındadır.
