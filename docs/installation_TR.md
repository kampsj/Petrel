# Kurulum ve yapılandırma

[English](installation.md) · [Türkçe](installation_TR.md) · [Dokümantasyon](README_TR.md)

## Kurulumdan önce

Uyumlu DWIN T5UIC1 panel, UART/GPIO erişimli Linux SBC, Python 3.11+ ve çalışan Klipper/Moonraker kurulumu kullanın. [LCD uyumluluğunu](lcd-assets_TR.md) kontrol edin. Uygulamanın kurulum betiği panel firmware'ini veya stok font/ikon paketini yüklemez.

## Bağlantı ve seri port hazırlığı

| Ekran bağlantısı | Raspberry Pi bağlantısı |
|---|---|
| RX | GPIO14 / UART TX |
| TX | GPIO15 / UART RX |
| Encoder A | GPIO21 |
| Encoder B | GPIO19 |
| Encoder düğmesi | GPIO20 |
| VCC | 5 V |
| GND | GND |

GPIO numaraları **BCM numaralarıdır**. Encoder pinleri yapılandırma sırasında değiştirilebilir. Fiziksel bağlantılar için [bağlantı görsellerine](../images/) bakın.

`sudo raspi-config` içinde seri donanımı etkinleştirin, seri giriş konsolunu kapatın ve yeniden başlatın. Pi ve işletim sisteminizde GPIO14/15'i hangi UART aygıtının kullandığını doğrulayın. Kurulum `/dev/ttyS0` önerir; kendi kurulumunuza uygun aygıtı seçin.

## Kurulum

Servisin sahibi olacak kullanıcıyla çalıştırın. Repo temiz olmalı ve `~/KlipperDWIN` konumunda bulunmalıdır:

```bash
cd ~
git clone https://github.com/sezgynus/KlipperDWIN.git
cd ~/KlipperDWIN
./install.sh
```

Varsayılanı kabul etmek için Enter'a basın veya kendi değerinizi girin:

| Ayar | Kurulum varsayılanı |
|---|---|
| Moonraker URL | `http://127.0.0.1:7125` |
| UART | `/dev/ttyS0` |
| Encoder A/B | `21 19` |
| Encoder düğmesi | `20` |
| Moonraker güç aygıtı | `Printer` |
| Güç açma basılı tutma süresi | `2000` ms (2 saniye) |

Kurulum `~/klipperdwin-env` ortamını hazırlar, bağımlılıkları yükler ve `KlipperDWIN.service` servisini etkinleştirir. Ayarlar `~/.config/KlipperDWIN/KlipperDWIN.env` içinde tutulur; `moonraker.conf` yanına `KlipperDWIN.conf` include dosyası eklenir ve servis Moonraker güncellemelerine kaydedilir. Kurulum tekrarlandığında mevcut ayarlar korunur.

Moonraker yapılandırmanız farklı konumdaysa:

```bash
MOONRAKER_CONFIG=/path/to/moonraker.conf ./install.sh
```

## Ayarları değiştirme

```bash
cd ~/KlipperDWIN
./configure.sh
```

Mevcut değerler soruların varsayılanı olur. Kaydettikten sonra değişiklikleri uygulamak için sunulan servis yeniden başlatmasını kabul edin. Ekran parlaklığı/kısma ayarları burada değil, LCD'de **Home → Display** altında yapılır.

Yapılandırıcının sormadığı ayarlar için harici ortam dosyasını düzenleyin. `export` kullanmadan düz `KEY=value` satırları yazın:

| Ayar | Amaç / varsayılan |
|---|---|
| `MOONRAKER_URL` | Moonraker adresi / `http://127.0.0.1:7125` |
| `MOONRAKER_API_KEY` | Gerekiyorsa kimlik doğrulama anahtarı / boş |
| `DWIN_REQUEST_TIMEOUT` | Saniye cinsinden istek zaman aşımı / `5` |
| `DWIN_SERIAL_PORT` | Yapılandırılmış UART / kurulum `/dev/ttyS0` önerir |
| `DWIN_ENCODER_PINS` | BCM numaralarıyla encoder A/B / `21 19` |
| `DWIN_BUTTON_PIN` | BCM numarasıyla encoder düğmesi / `20` |
| `DWIN_SETTINGS_FILE` | Yerel preset yedeği / `~/.config/KlipperDWIN/presets.json` |
| `DWIN_POWER_DEVICE` | Moonraker güç aygıtınızın adı / `Printer` |
| `DWIN_POWER_ON_HOLD_MS` | Milisaniye cinsinden güç açma süresi / `2000`; `0` anında açar |
| `DWIN_EMULATOR` | Ekran görüntüsü alma / `0` kapalı, `1` açık |

Düzenleme sonrası `sudo systemctl restart KlipperDWIN.service` ile yeniden başlatın. Özel anahtarları ve makine ayarlarını takip edilen repo dosyalarının dışında tutun. Görüntü almaya özel seçenekler için [emülatör rehberine](ui-emulator_TR.md) bakın.

## Güncelleme

Moonraker yapılandırmasını yeniden okuduktan sonra **Mainsail → Machine → Update Manager → KlipperDWIN** yolunu kullanın. Listeyi yenileyip güncelleyin; bağımlılıklar ve servis yeniden başlatması otomatik yapılır. Update Manager `master` dalını takip eder.

Yazıcı boşta iken LCD'deki **Info** bölümünden de KlipperDWIN güncellemelerini kontrol edip yükleyebilirsiniz. [Info ve güncellemeler](user-guide_TR.md#info-ve-güncellemeler) bölümüne bakın. Takip edilen repo dosyalarındaki yerel değişiklikler güncellemeyi engelleyebilir; kurtarma bunları silmeden önce inceleyin veya yedekleyin.

## Sorun giderme

```bash
sudo systemctl status KlipperDWIN.service --no-pager
journalctl -u KlipperDWIN.service --since "10 minutes ago" --no-pager
sudo systemctl restart KlipperDWIN.service
```

| Belirti | Kontrol edilecekler |
|---|---|
| Ekran boş veya sürekli yeniden bağlanıyor | Panel gücü, çapraz TX/RX, seçilen UART, seri giriş konsolu ve izinler |
| Encoder yanıt vermiyor | BCM pin ayarları ve bağlantılar |
| Açılış bir aşamada kalıyor | Klipper/Moonraker hazır durumu, ekran kaynakları ve servis günlükleri |
| İsteğe bağlı menü yok veya kilitli | Gerekli Klipper/Happy Hare yapılandırması, bağlantı ve mevcut yazıcı durumu |
| Önizleme görseli veya metadata yok | Slicer thumbnail'ları ve Moonraker'daki metadata |
| Wi-Fi bilgisi kullanılamıyor | Kablosuz bağlantı ve Linux `iw` komutunun bulunması |
| Güncelleme engelleniyor | Yerel repo değişiklikleri ve Moonraker Update Manager durumu |
| İşlem başarısız veya zaman aşımına uğradı | Tekrarlamadan önce Mainsail'den gerçek yazıcı durumunu kontrol edin |

Hata bildirimine yazılım revizyonunu, Pi/işletim sistemini, ilgili yapılandırmayı ve günlük bölümünü ekleyin. Görsel sorunlarda fotoğraf veya [emülatör ekran görüntüsü](ui-emulator_TR.md) ekleyin; paylaşmadan önce kimlik bilgilerini kaldırın.
