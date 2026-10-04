Occlusion Merger

English | Türkçe

English

When two FiveM maps ship the same GTA V occlusion.ymap, entries that exist in one but not in the other cause conflicts. This tool compares two occlusion.ymap.xml files, keeps only the entries found in both, and writes a single merged file.

Download
Version	How
Windows app (.exe)	Download from the Releases page
Browser version	Download occlusion_merge.html and double-click it (no internet needed, files are never uploaded)
Command line	python occlusion_merge.py 1.xml 2.xml result.xml (Python 3.9+)
Usage
Convert both occlusion.ymap files to XML with CodeWalker (RPF Explorer → select the file → Export XML).
Give the two XML files to the tool, click Merge, and save the result.
In CodeWalker, convert the result back to .ymap with Import XML.
Remove the old occlusion files from both maps and use the new file in one place only.
How it works

Every entry in the boxOccluders and occludeModels sections is compared by content. Entries that are identical in both files are kept, everything else is removed (set intersection). All other fields (name, extents, etc.) are taken from the first file.

Notes:

If a map deliberately removed an original occluder (for example to build a new interior), it will not be present in the merged file either. This avoids objects turning invisible.
Custom occluders added by a map are also removed. This does not cause visual glitches, only a small performance loss in those spots.
Back up your original files and test the result in game.
Windows warning

The .exe is not code-signed, so Windows SmartScreen may show "Windows protected your PC": click More info → Run anyway. If you prefer:

Check the SHA-256 value on the Release page: certutil -hashfile OcclusionMerger.exe SHA256
Build it yourself from source: install Python and run build.bat.
Or use the occlusion_merge.html version, which triggers no warning.
License

MIT. This project is not affiliated with Rockstar Games or Cfx.re.

Türkçe

FiveM için iki map aynı GTA V occlusion.ymap dosyasını kullandığında, birinde olup diğerinde olmayan occluder'lar çakışma yaratır. Bu araç iki occlusion.ymap.xml dosyasını karşılaştırır, sadece ikisinde de bulunan kayıtları tutar ve tek bir dosyada birleştirir.

İndirme
Sürüm	Nasıl
Windows uygulaması (.exe)	Releases sayfasından indir
Tarayıcı sürümü	occlusion_merge.html dosyasını indir, çift tıkla (internet gerekmez, dosyalar yüklenmez)
Komut satırı	python occlusion_merge.py 1.xml 2.xml sonuc.xml (Python 3.9+)
Kullanım
CodeWalker ile iki occlusion.ymap dosyasını XML'e çevir (RPF Explorer → dosyayı seç → Export XML).
Araca iki XML'i ver, Birleştir'e bas, sonucu kaydet.
CodeWalker'da sonucu Import XML ile tekrar .ymap'e çevir.
Eski occlusion dosyalarını iki mapten de sil, yeni dosyayı yalnızca bir yerde kullan.
Nasıl çalışır?

boxOccluders ve occludeModels bölümlerindeki her kayıt içerik olarak karşılaştırılır. İki dosyada da birebir aynı olan kayıtlar kalır, geri kalanı silinir (kesişim). Diğer alanlar (başlık, extent vb.) ilk dosyadan alınır.

Dikkat:

Bir map orijinal occluder'ı bilerek kaldırdıysa (örneğin yeni bir iç mekan yaptığı için), birleşik dosyada da bulunmaz. Bu sayede görünmez obje sorunları oluşmaz.
Mapin kendi eklediği özel occluder'lar da silinir. Görsel bozukluk yapmaz, yalnızca o noktalarda küçük bir performans kaybı olabilir.
Orijinal dosyalarını yedekle ve sonucu oyunda test et.
Windows uyarısı

.exe dosyası kod imzalı değildir. Windows SmartScreen "Windows bilgisayarınızı korudu" uyarısı gösterebilir: Daha fazla bilgi → Yine de çalıştır. İstersen:

Release sayfasındaki SHA-256 değerini kontrol et: certutil -hashfile OcclusionMerger.exe SHA256
Kaynak koddan kendin üret: Python kur, build.bat dosyasını çalıştır.
Ya da occlusion_merge.html sürümünü kullan, uyarı çıkmaz.
Lisans

MIT. Bu proje Rockstar Games veya Cfx.re ile bağlantılı değildir.
