# Print ve Tune kontrolleri

![Print and Tune demo](assets/print-controls-demo.gif)

Print ekranında önbellekteki G-code önizlemesi, ilerleme, geçen/kalan süre, tahmini bitiş saati ve `print_stats.info` sağlıyorsa katman bilgisi bulunur. Alt canlı gösterge bloğu korunur. Görsel indirme ve dönüştürme UI thread'i dışında yapılır; panele sınırlı SRAM parçaları ve yalnızca değişen alanlar gönderilir. Print önizlemesi 88 × 88 baseline 4:2:0 JPEG kullanır; siyah model ayrıntılarını koruyan mevcut filtreli arka plan yöntemi geçerlidir.

Enkoderle Tune, Pause/Resume veya Stop seçilir. Pause ve Resume doğrudan çalışır; Stop ilk seçeneği Back olan onay ekranını açar. Basılı tutma genel power kısayolunu açar. Baskı sürerken veya duraklatılmışken güç kapatma engellenir; önce baskı iptal edilmelidir. Power kısayolundan vazgeçmek Tune'daki düzenlenen değeri kaybettirmez.

Happy Hare varsa aktif tool'un eşlendiği gate'in rengi ve malzemesi gösterilir. Filament değişiminde bildirilen `last_tool` / `next_tool` kullanılır; eksik değerler tahmin edilmez. MMU kilitlenince hata Print üzerinde görünür ve Resume yerine MMU çıkar. Bu kontrol kaydırılabilir tam hata metnini ve mevcut korumalı kurtarma/manuel durum menülerini açar. Back ile Print'e dönülür. MMU yoksa MMU kontrolleri gösterilmez.

Tune tek ekranda Print, Motion, Extrusion ve After Job gruplarını sunar. Kontroller yalnızca ilgili cihaz ve çalışma zamanı verisi varsa görünür. Yazılımsal geri çekme için `[firmware_retraction]` gerekir; PA ve yumuşatma aktif extruder'ı takip eder. Katman bilgisi isteğe bağlıdır; Z yüksekliğinden tahmin edilmez.

Sayısal değere basıp enkoderle değiştirin, Apply ile gönderin. Değerler ve switchler bekleme/başarı popupı olmadan hemen gösterilir. Komut reddedilirse güncel abonelik değerine dönülür ve iki kısa kırmızı blink gösterilir. Sadece yanıtın gecikmesi ret sayılmaz; tamamlanan komutlar abonelik verisiyle karşılaştırılır. Eski yanıt yeni düzenlemeyi ezmez; yeniden bağlantı bekleyen düzenlemeleri geçersiz kılar.

## İsteğe bağlı baskı politikası switchleri

Bu üç isim ayrı ayrı tanınır:

```ini
[output_pin Turn_OFF_Heaters_After_Job]
pin: virtual_pin:Turn_OFF_Heaters_After_Job_pin
value: 1

[output_pin Disable_Motors_After_Job]
pin: virtual_pin:Disable_Motors_After_Job_pin
value: 1

[output_pin Power_OFF_Printer_After_Job]
pin: virtual_pin:Power_OFF_Printer_After_Job_pin
value: 0
```

`virtual_pin:` için kurulumunuzdaki Klipper virtual-pins eklentisi gerekir; standart Klipper pin sağlayıcısı değildir. Uygun fiziksel output pinler de kullanılabilir. Petrel eklenti kurmaz veya makroları değiştirmez.

Switch sadece `SET_PIN PIN=<tam isim> VALUE=0|1` gönderir. O anda ısıtıcı/motor/güç kapatmaz. START_PRINT / END_PRINT makrolarınız bu değerleri okuyup davranışı belirler. Örnek:

```jinja
{% if printer['output_pin Turn_OFF_Heaters_After_Job'].value|int %}
  TURN_OFF_HEATERS
{% endif %}
{% if printer['output_pin Disable_Motors_After_Job'].value|int %}
  M84
{% endif %}
```

`Power_OFF_Printer_After_Job` değerini kendi baskı sonu güç makronuzda, tanımlı Moonraker güç cihazınız ve soğutma politikanızla kullanın. Tanımsız pinler, PWM pinleri ve dijital değeri bilinmeyen pinler gizlenir.

Print butonlarının normal/seçili zemini ve sembolü tek library JPEG’idir. Seçim değişimi sadece eski ve yeni butonu, birer ikon ve yazı komutuyla günceller (dört çizim paketi). Pause/Resume değişimi yalnızca ortadaki butonu günceller. Buton şeridi sadece üç butonlu yerleşimden baskı sonundaki iki butonlu yerleşime geçerken temizlenir.
