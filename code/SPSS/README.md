# SPSS Tamamlayıcı Dosyaları

Bu klasör, *Lisansüstü Araştırmalar İçin Uygulamalı İstatistik* kitabındaki
uygulamaları IBM SPSS Statistics ve AMOS ile yeniden üretmek için hazırlanan
söz dizimlerini içerir.

## Çalıştırma

1. Tamamlayıcı depoyu bilgisayarınıza indirin veya klonlayın.
2. SPSS içinde depo ana klasörünü çalışma dizini olarak kullanın.
3. İlgili .sps dosyasını açın ve **Run > All** komutunu çalıştırın.
4. Söz dizimleri verileri **data/** klasöründen okur. Dosyaların göreli
   konumlarını değiştirmeyin.

Ondalık ayırıcı nokta, metin kodlaması UTF-8 olarak kabul edilmiştir.
SPSS sürümüne bağlı küçük menü veya çıktı farkları olabilir.

## Dosya Dizini

| Bölüm | Dosya | Kapsam |
|---|---|---|
| 2 | chapter02_analysis.sps | Betimsel istatistikler ve korelasyon |
| 3 | chapter03_cleaning.sps | Veri temizleme, tekilleştirme ve doğrulama |
| 4 | chapter04_analysis.sps | Eksik veri, çoklu atama ve regresyon tanılamaları |
| 5 | chapter05_analysis.sps | Bağımsız gruplar, ANCOVA ve kategorik sonuçlar |
| 6 | chapter06_planning.sps | Güç, kesinlik ve örneklem büyüklüğü planlaması |
| 7 | chapter07_analysis.sps | Bağımsız ve eşleştirilmiş karşılaştırmalar |
| 8 | chapter08_analysis.sps | Tek yönlü ve faktöriyel ANOVA |
| 9 | chapter09_analysis.sps | Dayanıklı ve parametrik olmayan yöntemler |
| 10 | chapter10_analysis.sps | Korelasyon ve basit regresyon |
| 12 | chapter12_analysis.sps | Lojistik, Poisson ve Gamma regresyonu |
| 13 | chapter13_analysis.sps | Aracılık, düzenleyicilik ve koşullu süreç |
| 14 | chapter14_analysis.sps | ANCOVA ve boylamsal karma model |
| 15 | chapter15_analysis.sps | Güvenirlik ve içerik geçerliği |
| 16 | chapter16_analysis.sps | Açımlayıcı faktör analizi |
| 17 | chapter17_data_preparation.sps | CFA için veri hazırlama |
| 17 | chapter17_AMOS_model_specification.txt | AMOS CFA model adımları |
| 18 | chapter18_AMOS_model_specification.txt | AMOS yapısal model adımları |
| 19 | chapter19_data_preparation.sps | Ölçme değişmezliği için veri hazırlama |
| 19 | chapter19_AMOS_invariance_guide.txt | AMOS değişmezlik model sırası |
| 21 | chapter21_audit_workflows.sps | Raporlama, açık bilim ve yapay zeka kullanım denetimi |

## Yeniden Üretim ve Denetim

.sps dosyaları **code/Python/generate_spss_companions.py** betiğiyle veri
şemalarından yeniden oluşturulabilir. Bir yayın sürümü hazırlanırken kitapta
verilen dosya yolları, veri dosyaları ve SPSS söz dizimleri birlikte
denetlenmelidir.

## Python Sonuçlarıyla Karşılaştırma

Python referans değerlerini ve boş SPSS giriş şablonunu oluşturmak için:

    python code/Python/compare_spss_python.py

SPSS veya AMOS çıktılarındaki değerleri
**support/spss_observed_metrics.csv** dosyasının **spss_value** sütununa
girin. Ardından karşılaştırmayı yeniden çalıştırın:

    python code/Python/compare_spss_python.py --strict

Sonuçlar **support/spss_python_comparison.csv** dosyasına yazılır.
**matched** tolerans içinde eşleşmeyi, **mismatch** yöntem veya sonuç
farkını, **awaiting_spss** ise henüz SPSS değeri girilmediğini gösterir.

SPSS ve AMOS ticari yazılımlardır. Bu depoda yazılımın kendisi değil,
yalnızca kitaba ait söz dizimi ve model kurulum yönergeleri dağıtılır.