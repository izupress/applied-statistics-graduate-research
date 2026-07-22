# Lisansüstü Araştırmalar İçin Uygulamalı İstatistik

Bu depo, Prof. Dr. İbrahim Güney'in *Lisansüstü Araştırmalar İçin
Uygulamalı İstatistik: Veri Hazırlığından Yapısal Eşitlik Modellemesine*
kitabına eşlik eden öğretim verilerini, analiz kodlarını ve beklenen
çıktıları içerir.

## İçerik

- **data/**: kitapta kullanılan sentetik öğretim veri setleri
- **code/Python/**: Python analizleri ve yeniden üretilebilirlik denetimleri
- **code/R/**: R analizleri
- **code/SPSS/**: SPSS söz dizimleri ve AMOS model kurulum kılavuzları
- **support/**: beklenen tablolar, tanılama sonuçları ve karşılaştırma dosyaları
- **figures/**: kodla üretilen bölüm şekilleri

## Hızlı Başlangıç

    git clone https://github.com/izupress/applied-statistics-graduate-research.git
    cd applied-statistics-graduate-research
    python -m pip install -r requirements.txt
    make audit

Python betikleri depo ana klasöründen çalıştırılmalıdır:

    python code/Python/chapter11_analysis.py

R betikleri için gerekli paketleri kurduktan sonra:

    Rscript code/R/chapter11_analysis.R

SPSS dosyaları IBM SPSS Statistics içinde açılarak **Run > All** komutuyla
çalıştırılır. Ayrıntılar için **code/SPSS/README.md** dosyasına bakın.

## Bölüm Dizini

| Bölüm | Konu | Python | R | SPSS/AMOS |
|---:|---|:---:|:---:|:---:|
| 2 | Betimsel istatistikler | ✓ | ✓ | ✓ |
| 3 | Veri hazırlama ve temizleme | ✓ | ✓ | ✓ |
| 4 | Eksik veri ve tanılamalar | ✓ | ✓ | ✓ |
| 5 | Hipotez testleri ve etki büyüklüğü | ✓ | ✓ | ✓ |
| 6 | Güç ve örneklem büyüklüğü | ✓ | ✓ | ✓ |
| 7 | Bağımsız ve eşleştirilmiş testler | ✓ | ✓ | ✓ |
| 8 | ANOVA ve faktöriyel tasarımlar | ✓ | ✓ | ✓ |
| 9 | Dayanıklı ve parametrik olmayan yöntemler | ✓ | ✓ | ✓ |
| 10 | Korelasyon ve basit regresyon | ✓ | ✓ | ✓ |
| 11 | Çoklu regresyon ve tanılamalar | ✓ | ✓ | ✓ |
| 12 | Genelleştirilmiş doğrusal modeller | ✓ | ✓ | ✓ |
| 13 | Aracılık ve düzenleyicilik | ✓ | ✓ | ✓ |
| 14 | ANCOVA ve boylamsal modeller | ✓ | ✓ | ✓ |
| 15 | Güvenirlik ve ölçek geliştirme | ✓ | ✓ | ✓ |
| 16 | Açımlayıcı faktör analizi | ✓ | ✓ | ✓ |
| 17 | Doğrulayıcı faktör analizi | ✓ | ✓ | AMOS |
| 18 | Yapısal eşitlik modellemesi | ✓ | ✓ | AMOS |
| 19 | Ölçme değişmezliği | ✓ | ✓ | AMOS |
| 20 | Bütünleşik vaka çalışmaları | ✓ | ✓ | - |
| 21 | Raporlama, açık bilim ve etik yapay zeka | ✓ | ✓ | ✓ |

## Yeniden Üretilebilirlik Denetimi

Tüm Python iş akışlarını çalıştırmak için:

    make audit

Denetim sonucu **support/python_reproducibility_audit.json** dosyasına,
ayrıntılı günlükler ise yerel olarak **support/reproducibility_logs/**
klasörüne yazılır.

SPSS/AMOS sonuçlarını Python sonuçlarıyla karşılaştırmak için:

    python code/Python/compare_spss_python.py

SPSS değerlerini **support/spss_observed_metrics.csv** dosyasına girdikten
sonra sıkı denetimi çalıştırın:

    python code/Python/compare_spss_python.py --strict

## Veri Hakkında

Bu depodaki veri setleri öğretim amacıyla hazırlanmış sentetik verilerdir.
Gerçek katılımcı verisi veya doğrudan tanımlayıcı bilgi içermez. Her veri
setinin anlamı ve analiz bağlamı ilgili kitap bölümünde açıklanmaktadır.

## Lisans

- Kodlar: MIT Lisansı, bk. **LICENSE-CODE**
- Sentetik veriler ve dokümantasyon: CC BY 4.0, bk. **LICENSE-DATA**

## Atıf

Önerilen atıf bilgileri **CITATION.cff** dosyasındadır. GitHub üzerindeki
**Cite this repository** özelliği bu dosyayı kullanır.

## Sürüm Eşleştirme

Kitabın basılı baskısıyla kullanılan kod ve verilerin değişmemesi için
yayın sürümleri Git etiketleriyle sabitlenecektir. Kitapta belirtilen sürüm
etiketini kullanın; geliştirme dalındaki sonuçlar sonraki düzeltmeleri
içerebilir.