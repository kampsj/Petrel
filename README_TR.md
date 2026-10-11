<p align="center">
  <img src="assets/klipperdwin-readme.png" width="600" alt="KlipperDWIN — Printer Display">
</p>

**Klipper yazıcınızı DWIN ekranı ve döner encoder ile kontrol edin.**

Web arayüzünü açmadan baskı dosyalarına göz atın, modeli önizleyin, yazıcıyı ayarlayın, tablayı düzeltin ve Happy Hare MMU'nuzu yönetin.

[English](README.md) · [Türkçe](README_TR.md)

<p align="center">
  <a href="https://github.com/sezgynus/KlipperDWIN/tree/v2.0.0"><img alt="v2.0.0" src="https://img.shields.io/badge/version-v2.0.0-0969da"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-3776ab?logo=python&amp;logoColor=white">
  <img alt="Klipper / Moonraker" src="https://img.shields.io/badge/Klipper-Moonraker-7d3cff">
  <a href="LICENSE"><img alt="GPL-3.0" src="https://img.shields.io/badge/License-GPL--3.0-blue"></a>
</p>

<p align="center">
  <img src="docs/assets/screens/home.png" width="240" alt="Ana ekran, birinci sayfa">
  <img src="docs/assets/screens/home-page-2.png" width="240" alt="Ana ekran, ikinci sayfa">
  <img src="docs/assets/screens/print-preview.png" width="240" alt="Baskı önizlemesi">
</p>

## Özellikler

| Yapmak istediğiniz işlem | Sunulan özellikler |
|---|---|
| Baskı seçmek | İç içe klasörler, Mainsail sıralaması, model önizlemesi, tahmini süre, filament kullanımı ve takım değişimleri |
| Baskıyı yönetmek | İlerleme ve süre, Pause/Resume, Stop, hız, sıcaklık, fan, çalışma zamanı Z offset ve akış takibi |
| Yazıcıyı hazırlamak | Home, motorları bırakma, XYZ/extruder hareketi, Live jog, ön ısıtma presetleri ve soğutma |
| Tablayı kalibre etmek | Dört köşe vida ayarı, probe offset kalibrasyonu, bed mesh ölçümü ve kayıtlı mesh görüntüleme |
| MMU yönetmek | Happy Hare kanalları, yükleme/boşaltma, bypass, takım eşlemesi, EndlessSpool, kurtarma, bakım, LED'ler ve çoklu ünite |
| Filamenti incelemek | Kanal malzemesi/rengi, makara ataması ve mevcutsa Spoolman kalan yüzdesi |
| Ekranı ayarlamak | Güç döngüsünde korunan parlaklık, boşta kısma süresi ve kısılmış parlaklık |
| Işık ve gücü yönetmek | PWM kabin ışığı, encoder basılı tutarak güç açma ve onaylı güç kapatma |
| Sistemi kontrol etmek | Ağ/Wi-Fi, host ve MCU durumu, yazılım sürümleri, proje QR kodu ve KlipperDWIN güncellemeleri |
| Ekran görüntüsü almak | Dokümantasyon ve hata bildirimi için isteğe bağlı emülatör görüntüsü |

İsteğe bağlı kontroller yazıcının yapılandırmasına göre görünür. Her iki rehberde de ekrandaki menü adları İngilizcedir. Bu belgeler güncel `master` sürümünü anlatır.

## Gereksinimler

- Uyumlu 4,3 inç Ender 3 V2 ekranı gibi, uygun ekran kaynaklarına sahip **272×480 DWIN T5UIC1** panel.
- UART/GPIO erişimi ve **Python 3.11 veya üzeri** olan Raspberry Pi veya uyumlu Linux SBC.
- Çalışan bir **Klipper ve Moonraker** kurulumu.
- İsteğe bağlı: ortak sıralama/sıcaklık presetleri için Mainsail, MMU kontrolü için Happy Hare, makara bilgisi için Spoolman ve yapılandırılmış Moonraker güç aygıtı.

DWIN, DACAI ve TJC paneller birbirinin yerine kullanılamaz. Kurulumdan önce [ekran uyumluluğunu](docs/lcd-assets_TR.md) kontrol edin.

## Kurulum

Bağlantı, seri port hazırlığı ve iletişim ayarları için [kurulum ve yapılandırma rehberini](docs/installation_TR.md) izleyin. Repoyu kurulum kullanıcısının ev dizinine klonlayın:

```bash
cd ~
git clone https://github.com/sezgynus/KlipperDWIN.git
cd ~/KlipperDWIN
./install.sh
```

Kurulum betiği bağımlılıkları, servisi ve Moonraker Update Manager'ı hazırlar. Bağlantı, encoder veya güç ayarlarını sonradan değiştirmek için `~/KlipperDWIN` içinde `./configure.sh` çalıştırın.

## İlk kullanım

Gezinmek için encoderi çevirin; seçmek için basın. Sayısal ayarlarda basın, çevirin ve onaylamak için tekrar basın. **Back** önceki menüye döner. Ana ekran birden fazla sayfadan oluşur; sonraki sayfaya geçmek için çevirmeye devam edin.

| Ana ekran öğesi | Açılan bölüm |
|---|---|
| Print | Dosya tarayıcısı ve baskı önizlemesi |
| Prepare | Hareket, home, ön ısıtma ve soğutma |
| Control | Sıcaklık, çalışma zamanı hareket sınırları ve kabin ışığı |
| Leveling | Bed mesh kalibrasyonu, mesh görüntüleyici, vida ayarı ve prob kalibrasyonu |
| MMU | Happy Hare filament kontrolleri ve kurtarma |
| Display | Parlaklık ve boşta kısma |
| Info | Sistem durumu, yazılım sürümleri ve güncellemeler |

Leveling ve MMU, yapılandırılmış özelliklere bağlıdır. Açılıştaki ilerleme çubuğu hazırlık aşamasını gösterir; gezinmek için ana ekranı bekleyin. Beklerken basılı tutarak güç açma çalışmaya devam eder.

## Kullanıcı rehberleri

| Rehber | İçerik |
|---|---|
| [Kurulum ve yapılandırma](docs/installation_TR.md) | Bağlantı, kurulum, ayarlar, güncellemeler ve sorun giderme |
| [Günlük kullanım](docs/user-guide_TR.md) | Baskı akışı, Live jog, sıcaklıklar, kalibrasyon, Display, Info, ışık ve güç |
| [MMU ve filament](docs/mmu-guide_TR.md) | Kanallar, makara ID'leri, takım eşlemesi, EndlessSpool, bypass, kurtarma ve seçenekler |
| [Dokümantasyon dizini](docs/README_TR.md) | Tüm kullanıcı rehberleri, katkı araçları ve isteğe bağlı referanslar |

Rehberler güncel emülatör ekran görüntülerini içerir. Yeni eklenen ekranlar için [Display](docs/user-guide_TR.md#ekran-ayarları), [Info ve güncellemeler](docs/user-guide_TR.md#info-ve-güncellemeler) ve [vida ayarı](docs/user-guide_TR.md#vida-ayarı) bölümlerine bakın.

## Kullanımla ilgili önemli bilgiler

- Hareket sınırları ve çalışma zamanı Z offset, mevcut oturum için geçerlidir; kalıcı yazıcı/probe kalibrasyonunun yerine geçmez.
- Vida ayarı, probe ve Klipper'da tanımlı dört ayrı köşe vidası gerektirir.
- Mesh görüntülemek onu etkinleştirmez. Kalibrasyonu kaydetmek Klipper'ı yeniden başlatır; devam eden mesh ölçümünü durdurmak Klipper'ı shutdown durumuna geçirir.
- MMU kalibrasyonu ve ileri LED efektleri web arayüzündedir. LCD'deki işlemler kurulu Happy Hare yapılandırmasına bağlıdır.
- Başarısız veya sonucu doğrulanmamış işlemi tekrarlamadan önce Mainsail'den kontrol edin.

## Geliştirme ve katkı

Hata bildirimi, pull request, testler, ekran görüntüsü alma ve ikon hazırlama aracı için [CONTRIBUTING_TR.md](CONTRIBUTING_TR.md) belgesine bakın. [Emülatör rehberi](docs/ui-emulator_TR.md), çalışan serviste görüntü almayı etkinleştirmeyi ve özgün boyutlu görseller kaydetmeyi anlatır.

## Katkılar ve lisans

Proje [odwdinc/DWIN_T5UIC1_LCD](https://github.com/odwdinc/DWIN_T5UIC1_LCD) ve [bustedlogic/DWIN_T5UIC1_LCD](https://github.com/bustedlogic/DWIN_T5UIC1_LCD) çalışmalarından doğmuştur. Özgün telif bildirimleri ve Git geçmişi korunur.

Entegrasyonlar [Klipper](https://github.com/Klipper3d/klipper), [Moonraker](https://github.com/Arksine/moonraker), [Mainsail](https://github.com/mainsail-crew/mainsail), [Happy Hare](https://github.com/moggieuk/Happy-Hare) ve [Spoolman](https://github.com/Donkie/Spoolman) kullanır.

**GNU GPL v3.0** lisanslıdır; [LICENSE](LICENSE) dosyasına bakın.
