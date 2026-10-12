# Emülatör ekran görüntüleri

[English](ui-emulator.md) · [Türkçe](ui-emulator_TR.md) · [Katkı](../CONTRIBUTING_TR.md)

## Ne işe yarar

İsteğe bağlı emülatör, çalışan Petrel servisinin çizdiği ekranları yakalar. Yerleşimleri incelemek, dokümantasyonu yenilemek ve görsel hataları özgün boyutlu görsellerle bildirmek için kullanın. Gerçek LCD arayüzünü takip eder; bağımsız yazıcı simülatörü veya canlı tarayıcı görüntüleyicisi değildir. Fiziksel encoderle gezinin, ardından SSH üzerinden görüntü isteyin.

## Açma veya kapatma

Bağımlılıklar normal kurulum ve Moonraker güncellemelerine dahildir. `~/.config/Petrel/Petrel.env` içinde varsayılanı değiştirin:

```ini
PETREL_EMULATOR=1
```

Ardından yeniden başlatın:

```bash
sudo systemctl restart Petrel.service
```

Kapatmak için `PETREL_EMULATOR=0` yapıp yeniden başlatın. Kurulum/yapılandırma tekrarlandığında mevcut açık değer korunur. Eski kurulumda bağımlılıklar eksikse:

```bash
cd ~/Petrel
~/petrel-env/bin/python -m pip install -r requirements.txt
```

## SSH üzerinden görüntü alma

1. LCD'de istediğiniz ekranı açın ve çizimin bitmesini bekleyin.
2. SSH içinde **servis kullanıcısıyla, sudo kullanmadan** çalıştırın:

```bash
~/petrel-env/bin/python ~/Petrel/tools/screenshot.py
```

Komut kayıt yolunu yazdırır. Görseller varsayılan olarak `~/Petrel-screenshots/` içine zaman damgalı, benzersiz adlarla kaydedilir. Çıktı yeniden boyutlandırılmamış, kayıpsız **272×480 RGB PNG**'dir. Otomatik görüntü kaydedilmez.

BMP çıktısı için:

```bash
~/petrel-env/bin/python ~/Petrel/tools/screenshot.py --format bmp
```

İncelemek için görselleri bilgisayarınıza kopyalayın. Repo ekran görüntüleri, ekranı/durumu anlatan adlarla `docs/assets/screens/` içine konur.

## Ek ayarlar

Aynı harici ortam dosyasına yazıp servisi yeniden başlatın:

| Değişken | Amaç |
|---|---|
| `PETREL_SCREENSHOT_DIRECTORY` | Özel çıktı klasörü |
| `PETREL_EMULATOR_SOCKET` | Özel yerel görüntü soketi; varsayılan `~/.cache/Petrel-emulator/control.sock` |
| `PETREL_EMULATOR_FONT` | Özelleştirilmiş fiziksel panelle eşleşen font dosyası |

Özel sokette görüntü komutuna aynı yolu verin:

```bash
~/petrel-env/bin/python ~/Petrel/tools/screenshot.py --socket /path/to/control.sock
```

## Sorun giderme ve sınırlar

| Sorun | Yapılacak işlem |
|---|---|
| Bağlanamıyor veya izin reddediliyor | `PETREL_EMULATOR=1` kontrol edin, servisi yeniden başlatın, servis kullanıcısıyla çalıştırın ve soket yolunu kontrol edin |
| Görüntü reddediliyor | Panel bağlantısını, yüklenen kaynakları ve servis günlüğünü kontrol edin; tamamlanmış ekranı bekleyin |
| Yazı/ikonlar panelden farklı | Font/ikon dosyalarını karşılaştırın; [emülatör kaynaklarına](../assets/emulator/README_TR.md) bakın |
| Kısma görselde görünmüyor | Görüntüler fiziksel arka ışık parlaklığını değil ekran piksellerini gösterir |

Emülatör LCD belleğini okumak yerine çizim komutlarını takip eder. Fontlar, JPEG çözümü ve QR deseni fiziksel panelden farklı olabilir. Bu sorunlarda hem ekran görüntüsü hem fotoğraf paylaşın; tek başına görüntü fiziksel ekran doğruluğunu kanıtlamaz.
