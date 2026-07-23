# Kitap ve Depo Yayın İş Akışı

Bu depo, *Lisansüstü Araştırmalar İçin Uygulamalı İstatistik* kitabının
veri, kod, şekil ve beklenen çıktı kaynağıdır. Kitap metni ile depo aşağıdaki
sırayla güncellenir.

## Bölüm Güncellemesi

1. Veri veya analiz kodunu ilgili chapterXX önekiyle güncelleyin.
2. **make manifest** çalıştırarak SPSS dosyalarını ve bölüm manifestosunu yenileyin.
3. **make audit** çalıştırarak bütün Python analizlerini doğrulayın.
4. **make r-audit** çalıştırarak bütün R analizlerini doğrulayın.
5. Değişen sonuçları support/chapterXX_* dosyalarından kontrol edin.
6. Yalnızca doğrulanmış sonuçları kitabın chapters/chapterXX.tex dosyasına aktarın.
7. Kod, veri, çıktı ve kitap değişikliklerini aynı bölüm numarasıyla açıklayın.

## Basım Adayı

1. chapter-manifest.csv içinde bütün bölümlerin ready olduğunu doğrulayın.
2. GitHub Actions denetiminin başarılı olduğunu doğrulayın.
3. Kitabı XeLaTeX ve Biber ile temiz bir çalışma alanında derleyin.
4. Kitaptaki tabloları ve sayısal sonuçları support/ çıktılarıyla karşılaştırın.
5. CITATION.cff, CHANGELOG.md ve kitap içindeki tamamlayıcı kaynak sürümünü güncelleyin.
6. v1.0.0-book-2026 etiketini oluşturun ve aynı adla GitHub Release yayımlayın.
7. Release arşivinin sağlama toplamını ve kalıcı DOI bilgisini kitap dosyasına işleyin.

## Düzeltme Sürümleri

Basılı sonucu değiştirmeyen belge ve kod düzeltmeleri yama sürümü olarak
etiketlenir: v1.0.1, v1.0.2. Analiz sonucunu veya veri yapısını değiştiren
güncellemeler yeni küçük sürüm gerektirir: v1.1.0.
