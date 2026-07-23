# R Workflow Aktarım Dosyaları

Prism noktayla başlayan .github dizinini ve uzantısız dosyaları
gizleyebildiği için GitHub otomasyon dosyaları bu görünür klasörde
aktarılmaktadır.

Windows PowerShell'de depo kökünde aşağıdaki komutları çalıştırın:

    New-Item -ItemType Directory -Force .\.github\workflows | Out-Null
    Copy-Item .\github-upload\r-reproducibility.yml .\.github\workflows\r-reproducibility.yml
    Copy-Item .\github-upload\DESCRIPTION.txt .\DESCRIPTION
    Copy-Item .\github-upload\Makefile.txt .\Makefile

Ardından:

    python code/Python/run_r_reproducibility_audit.py --list-only
    git add .
    git commit -m "Add R reproducibility audit"
    git push origin main
