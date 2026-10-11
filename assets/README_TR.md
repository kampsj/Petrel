# LCD görselleri

[English](README.md) · [Türkçe](README_TR.md) · [Katkı](../CONTRIBUTING_TR.md)

## Bu klasördeki dosyalar

| Dosya | Amaç |
|---|---|
| `klipperdwin_atlas_0.jpg` | Özel sabit ikonlar: MMU, klasör, makine/host/MCU/yazılım, güç, Display, homing penceresi ve ortak boş makara |
| `klipperdwin_atlas_1.jpg` | Ortak makara ikonunun dar boyutları |
| `klipperdwin_bootsplash.jpg` | Panel picture slot 0 için seçilen açılış görseli |
| `spool-empty.png` | Ortak 42×52 boş makara sprite’ı: ahşap kenarlar ve ince gri merkez |
| `display-settings.png` | Özgün şeffaf Display ikon sprite'ı |
| `klipperdwin-readme.png` | Açılış görselinden uyarlanan README logo ve yazı başlığı |
| [emulator/](emulator/README_TR.md) | Ekran görüntüleri için bilgisayar tarafı stok ikon ve font girdileri |

Atlas dosya adları değişmemelidir. Atlas JPEG'leri fiziksel panel için **480×272 baseline JPEG**'dir; ikon konumları dikey **272×480** düzenindedir. Açılış görseli burada sağlanır; klasöre koymak tek başına panelin mevcut açılış görselini değiştirmez.

## Yeni ikon hazırlama

Şeffaf PNG sprite kullanın. Patch aracı Atlas 0'da yer bulur, mevcut çözülmüş ikonları değiştirmez ve panelin 32 KiB görsel sınırını kontrol eder. Yalnız görsel hazırlamada gereken bağımlılıkları ayrı geliştirme ortamına kurun:

```bash
python3 -m venv .venv-artwork
.venv-artwork/bin/python -m pip install Pillow numpy jpeglib
.venv-artwork/bin/python tools/patch_atlas_icon.py sprite.png candidate-atlas.jpg
```

Repo kökünden çalıştırın. **Ayrı çıktı adı** kullanın; araç kaynak atlasın üzerine yazmayı reddeder. Yeni ikon dikdörtgenini yazdırır. Kod değişikliğinin parçası olarak ikonu `lcd_atlas.py` içinde kaydedin, eski/yeni ikonları inceleyin, ilgili testleri çalıştırın ve takip edilen atlası değiştirmeden önce panelde doğrulayın.

## Ekran görüntüleri

Kullanıcı arayüzü ekran görüntüleri bu görsel klasörüne değil `docs/assets/screens/` içine aittir. [Görüntü alma rehberini](../docs/ui-emulator_TR.md) izleyin ve özgün 272×480 PNG çıktısını koruyun.
