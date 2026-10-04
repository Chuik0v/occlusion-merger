# Occlusion Merger

FiveM için iki map aynı GTA V `occlusion.ymap` dosyasını kullandığında, birinde olup diğerinde olmayan occluder'lar çakışma yaratır. Bu araç iki `occlusion.ymap.xml` dosyasını karşılaştırır, **sadece ikisinde de bulunan kayıtları** tutar ve tek bir dosyada birleştirir.

*English: When two FiveM maps ship the same GTA V `occlusion.ymap`, entries present in one but not the other cause conflicts. This tool compares two `occlusion.ymap.xml` files, keeps only the entries found in **both**, and writes a single merged file.*

## İndirme / Download

| Sürüm | Nasıl |
|---|---|
| **Windows uygulaması (.exe)** | [Releases](../../releases) sayfasından indir |
| **Tarayıcı sürümü** | `occlusion_merge.html` dosyasını indir, çift tıkla (internet gerekmez, dosyalar yüklenmez) |
| **Komut satırı** | `python occlusion_merge.py 1.xml 2.xml sonuc.xml` (Python 3.9+) |

## Kullanım

1. [CodeWalker](https://github.com/dexyfex/CodeWalker) ile iki `occlusion.ymap` dosyasını XML'e çevir (RPF Explorer → dosyayı seç → Export XML).
2. Araca iki XML'i ver, **Birleştir**'e bas, sonucu kaydet.
3. CodeWalker'da sonucu **Import XML** ile tekrar `.ymap`'e çevir.
4. Eski occlusion dosyalarını iki mapten de sil, yeni dosyayı yalnızca bir yerde kullan.

## Nasıl çalışır?

`boxOccluders` ve `occludeModels` bölümlerindeki her kayıt içerik olarak karşılaştırılır. İki dosyada da birebir aynı olan kayıtlar kalır, geri kalanı silinir (kesişim). Diğer alanlar (başlık, extent vb.) ilk dosyadan alınır.

**Dikkat:**
- Bir map orijinal occluder'ı bilerek kaldırdıysa, birleşik dosyada da bulunmaz. Bu sayede görünmez obje sorunları oluşmaz.
- Mapin kendi eklediği özel occluder'lar da silinir. Görsel bozukluk yapmaz, yalnızca o noktalarda küçük bir performans kaybı olabilir.
- Orijinal dosyalarını yedekle ve sonucu oyunda test et.

## Windows uyarısı

`.exe` dosyası kod imzalı değildir. Windows SmartScreen "Windows bilgisayarınızı korudu" uyarısı gösterebilir: **Daha fazla bilgi → Yine de çalıştır**. İstersen:
- Release sayfasındaki SHA-256 değerini kontrol et: `certutil -hashfile OcclusionMerger.exe SHA256`
- Kaynak koddan kendin üret: Python kur, `build.bat` dosyasını çalıştır.
- Ya da `occlusion_merge.html` sürümünü kullan, uyarı çıkmaz.

## Lisans

MIT. Bu proje Rockstar Games veya CodeWalker ile bağlantılı değildir.
