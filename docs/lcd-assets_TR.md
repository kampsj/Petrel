# LCD uyumluluğu

[English](lcd-assets.md) · [Türkçe](lcd-assets_TR.md) · [Dokümantasyon](README_TR.md)

## Desteklenen ekran

Petrel, uyumlu 4,3 inç Ender 3 V2 panelinde kullanılan **272×480 dikey DWIN T5UIC1** düzenini hedefler. DWIN, DACAI ve TJC firmware/kaynak paketleri birbirinin yerine kullanılamaz.

Fiziksel panelde eşleşen stok ikon kütüphanesi **3 (`3.ICO`)**, fontlar ve İngilizce bitmap kaynakları bulunmalıdır. Ekran yönü **1**'dir. Özel Petrel görselleri uygulamayla ayrıca sağlanır; [görsel rehberine](../assets/README_TR.md) bakın.

## Panel kurmadan veya değiştirmeden önce

Yalnız ekran boyutunu değil, kontrolcü ailesini ve kurulu kaynak paketini kontrol edin. Uygulama kurulum betiği LCD kernel firmware'ini veya stok font/ikon paketini yüklemez. Panel firmware çalışmaları için isteğe bağlı [T5UIC1 referansını](t5uic1-reference.md) kullanın.

Kurulumdan sonra fiziksel ekranda menü yazılarını/ikonlarını, renkleri, önizlemeleri ve encoder gezinmesini inceleyin. Çalışan emülatör görüntüsü farklı panel/kaynak paketinde aynı görünümü garanti etmez.

## Baskı önizlemeleri

Önizlemeler Moonraker'dan gelir ve yeni panel kaynak paketi gerektirmez. Eksik thumbnail baskı başlatmayı engellemez. Görseller yeniden başlatma veya yeniden bağlantı sonrası tekrar hazırlanır; kurulu ikonların yerine geçmez.

## Kaynakları tanıma

Uygulama artık kütüphane 3'yi [`assets/icons`](../assets/icons/README_TR.md) kaynaklarından oluşturur ve güncelleme sonrası ilk LCD bağlantısında değişen blokları otomatik yükler. Değişmeyen kaynaklar atlanır. JPEG ekleme, paketi dışa aktarma ve panel kaynakları yeniden kurulduktan sonra zorla yükleme için bu kılavuzu kullanın.

Deneysel library-3 branch'inde, panel firmware'ini değiştirmeden depodaki `3.ICO` dosyasını UART üzerinden yükleyin:

```sh
sudo systemctl stop Petrel.service
~/petrel-env/bin/python ~/Petrel/tools/flash_icon_library.py && sudo systemctl start Petrel.service
```

Araç yapılandırılmış seri portu kullanır ve 7–14 slotlarına yazar. Yazma başarısız olursa servis kapalı kalır. Yazma onayları kontrol edilir; Flash geri okuması yapılmaz. Yüklemeden sonra ikonları fiziksel panelde kontrol edin.

Katkı görselleri için `tools/pack_icon_library.py kaynak.ICO hedef.ICO`, JPEG görsellerini koruyarak her ikonu tek bir 32 KiB blokta tutar. Böylece gözlenen çizim sorunlarıyla ilişkili blok sınırlarında ikonların bölünmesi önlenir.

[Stok envanteri](lcd-assets.json) proje için önceden incelenen kaynakları kaydeder. Kendi panelinizde kurulu dosyaları belirlemez. Katkı görselleri ve emülatör font seçimi talimatlarına [dokümantasyon dizininden](README_TR.md) ulaşabilirsiniz.

## Graphite font

İkon kütüphanesi UART üzerinden otomatik güncellenir. Graphite ekran görüntüleriyle aynı yazı görünümü için `assets/fonts/DWIN_SET/0T5UIC1.HZK` içindeki ASCII fontunu da LCD’nin SD kart kaynak güncelleme yöntemiyle kurun. Depodaki `DWIN_SET` klasörünü uyumlu LCD güncelleme kartına kopyalayın, yazıcıyı kapatın, kartı LCD’nin kart okuyucusuna takın, enerjiyi verin ve kaynak güncellemesi bitene kadar bekleyin. Yazıcıyı kapatıp kartı çıkarın ve normal başlatın. Pi servisi font Flash’ını UART üzerinden yüklemez. Emülatör aynı fontu kullanır; DejaVu lisansı `assets/emulator/Petrel-font-license.txt` içindedir.
