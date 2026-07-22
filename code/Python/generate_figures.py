import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

out = Path('figures')
out.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 160,
    'savefig.bbox': 'tight',
})
colors = {'burgundy':'#78202d','gold':'#c49b5c','charcoal':'#3c3c41','blue':'#4c78a8','green':'#54a24b','orange':'#f58518','red':'#e45756'}

def save(name):
    plt.savefig(out/name, format='pdf')
    plt.close()

# b02 histogram + boxplot
rng = np.random.default_rng(42)
x = np.r_[rng.normal(68, 8, 110), [42, 96, 99]]
fig, ax = plt.subplots(1,2,figsize=(8,3.2), gridspec_kw={'width_ratios':[2,1]})
ax[0].hist(x, bins=12, color=colors['gold'], edgecolor='white')
ax[0].axvline(np.mean(x), color=colors['burgundy'], lw=2, label='Ortalama')
ax[0].axvline(np.median(x), color=colors['charcoal'], lw=2, ls='--', label='Medyan')
ax[0].set_xlabel('Puan'); ax[0].set_ylabel('Frekans'); ax[0].legend(frameon=False)
ax[1].boxplot(x, vert=True, patch_artist=True, boxprops={'facecolor':colors['gold'],'alpha':0.65}, medianprops={'color':colors['burgundy'],'linewidth':2})
ax[1].set_ylabel('Puan'); ax[1].set_xticks([1], ['Örneklem'])
fig.suptitle('Dağılım, merkezi eğilim ve aykırı değerlerin birlikte okunması')
save('b02-histogram-kutu.pdf')

# b02a missing heatmap
mat = rng.random((18,8)) < np.array([.05,.08,.15,.02,.12,.06,.18,.03])
fig, ax = plt.subplots(figsize=(7,3.2))
ax.imshow(mat, aspect='auto', cmap='Greys', interpolation='nearest')
ax.set_xlabel('Değişkenler'); ax.set_ylabel('Gözlemler')
ax.set_xticks(range(8), [f'V{i}' for i in range(1,9)])
ax.set_title('Eksik veri deseni: koyu hücreler eksik gözlemleri gösterir')
save('b02a-eksik-veri-isi-haritasi.pdf')

# b03 t rejection
xx = np.linspace(-4,4,500); yy=stats.t.pdf(xx, df=24); crit=stats.t.ppf(.975,24)
fig, ax=plt.subplots(figsize=(7,3.2)); ax.plot(xx,yy,color=colors['charcoal'],lw=2)
ax.fill_between(xx,0,yy,where=(xx<=-crit)|(xx>=crit),color=colors['burgundy'],alpha=.35,label='Ret bölgesi')
ax.axvline(-crit,color=colors['burgundy'],ls='--'); ax.axvline(crit,color=colors['burgundy'],ls='--')
ax.set_xlabel('t değeri'); ax.set_ylabel('Yoğunluk'); ax.set_title('Çift kuyruklu hipotez testinde ret bölgeleri'); ax.legend(frameon=False)
save('b03-t-ret-bolgeleri.pdf')

# b03a power curve approximate one-sample t two-sided alpha .05 d .5
ns=np.arange(10,151); alpha=.05; d=.5
power=[]
for n in ns:
    df=n-1; tcrit=stats.t.ppf(1-alpha/2, df); ncp=d*np.sqrt(n)
    power.append(stats.nct.sf(tcrit, df, ncp)+stats.nct.cdf(-tcrit, df, ncp))
fig, ax=plt.subplots(figsize=(7,3.2)); ax.plot(ns,power,color=colors['burgundy'],lw=2.5)
ax.axhline(.80,color=colors['charcoal'],ls='--',label='%80 güç'); ax.set_ylim(0,1.02)
ax.set_xlabel('Örneklem büyüklüğü (n)'); ax.set_ylabel('İstatistiksel güç'); ax.set_title('Örneklem büyüklüğü arttıkça gücün yükselmesi'); ax.legend(frameon=False)
save('b03a-guc-egrisi.pdf')

# b04 correlations panels
fig, axes=plt.subplots(1,3,figsize=(9,3),sharex=True,sharey=True)
for ax,r,title in zip(axes,[.2,.5,.8],[r'$r \approx .20$',r'$r \approx .50$',r'$r \approx .80$']):
    cov=[[1,r],[r,1]]; data=rng.multivariate_normal([0,0],cov,80)
    ax.scatter(data[:,0],data[:,1],s=16,color=colors['blue'],alpha=.75)
    coef=np.polyfit(data[:,0],data[:,1],1); grid=np.linspace(data[:,0].min(),data[:,0].max(),50)
    ax.plot(grid,coef[0]*grid+coef[1],color=colors['burgundy'],lw=2)
    ax.set_title(title)
axes[0].set_ylabel('Y'); axes[1].set_xlabel('X'); fig.suptitle('Korelasyon büyüklüğü arttıkça doğrusal örüntü belirginleşir')
save('b04-korelasyon-sacilim.pdf')

# b05 regression residuals
xv=np.linspace(1,10,40); y=5+2.4*xv+rng.normal(0,3,40); coef=np.polyfit(xv,y,1); yhat=np.polyval(coef,xv)
fig, ax=plt.subplots(figsize=(7,3.5)); ax.scatter(xv,y,color=colors['blue'],label='Gözlenen')
ax.plot(xv,yhat,color=colors['burgundy'],lw=2,label='Regresyon doğrusu')
for xi, yi, yh in zip(xv[::4], y[::4], yhat[::4]): ax.plot([xi,xi],[yh,yi],color=colors['gold'],lw=1)
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_title('Regresyon doğrusu ve artıkların sezgisel gösterimi'); ax.legend(frameon=False)
save('b05-regresyon-artiklar.pdf')

# b05a logistic s curve
xx=np.linspace(-6,6,400); pp=1/(1+np.exp(-(xx)))
fig, ax=plt.subplots(figsize=(7,3.2)); ax.plot(xx,pp,color=colors['burgundy'],lw=2.5)
ax.axhline(.5,color=colors['charcoal'],ls='--',lw=1); ax.set_xlabel('Doğrusal yordayıcı'); ax.set_ylabel('Olasılık')
ax.set_title('Lojistik regresyonda S biçimli olasılık eğrisi'); ax.set_ylim(-.02,1.02)
save('b05a-lojistik-s-egrisi.pdf')

# b05b moderation slopes
x=np.linspace(-2,2,80); fig,ax=plt.subplots(figsize=(7,3.2))
for m,c,label in [(0.25,colors['blue'],'Düşük düzenleyici'),(.75,colors['gold'],'Orta'),(1.25,colors['burgundy'],'Yüksek düzenleyici')]:
    ax.plot(x,1+m*x,color=c,lw=2,label=label)
ax.set_xlabel('Yordayıcı'); ax.set_ylabel('Sonuç'); ax.set_title('Düzenleyicilik: eğimlerin düzeye göre değişmesi'); ax.legend(frameon=False)
save('b05b-etkilesim-egimleri.pdf')

# b07 anova means
means=[72,78,84]; err=[3.5,3,4]; fig,ax=plt.subplots(figsize=(6,3.2))
ax.bar(['Yöntem A','Yöntem B','Yöntem C'],means,yerr=err,color=[colors['blue'],colors['gold'],colors['burgundy']],alpha=.85,capsize=5)
ax.set_ylabel('Ortalama puan'); ax.set_title('ANOVA için grup ortalamaları ve hata çubukları'); ax.set_ylim(60,92)
save('b07-anova-ortalamalar.pdf')

# b10 scree
vals=np.array([3.4,2.1,1.25,.72,.55,.42,.33,.22]); fig,ax=plt.subplots(figsize=(7,3.2))
ax.plot(range(1,len(vals)+1),vals,marker='o',color=colors['burgundy'],lw=2); ax.axhline(1,color=colors['charcoal'],ls='--',label='Özdeğer = 1')
ax.set_xlabel('Faktör numarası'); ax.set_ylabel('Özdeğer'); ax.set_title('Scree grafiği: kırılma noktası ve faktör sayısı'); ax.legend(frameon=False)
save('b10-scree-grafigi.pdf')

# b13 adjusted means
pre=np.linspace(40,90,60); groups=['Kontrol','Deney']; fig,ax=plt.subplots(figsize=(7,3.2))
for offset,c,label in [(0,colors['blue'],'Kontrol'),(5,colors['burgundy'],'Deney')]:
    y=30+.55*pre+offset
    ax.plot(pre,y,color=c,lw=2,label=label)
ax.set_xlabel('Kovaryat: ön test'); ax.set_ylabel('Düzeltilmiş son test'); ax.set_title('ANCOVA: kovaryat kontrolü sonrası düzeltilmiş ortalamalar'); ax.legend(frameon=False)
save('b13-duzeltilmis-ortalamalar.pdf')
# b06 confidence interval illustration
fig, ax = plt.subplots(figsize=(7, 3.2))
labels = ['Grup A', 'Grup B']
means = np.array([72.4, 78.1])
ci = np.array([3.1, 3.4])
ax.errorbar(labels, means, yerr=ci, fmt='o', color=colors['burgundy'], ecolor=colors['charcoal'], elinewidth=2, capsize=8, markersize=7)
ax.set_ylabel('Ortalama puan')
ax.set_title('Parametrik testlerde ortalama ve güven aralığı gösterimi')
ax.set_ylim(66, 83)
ax.grid(axis='y', alpha=.22)
save('b06-guven-araligi.pdf')

# b08 rank distribution comparison
rank_a = rng.normal(34, 7, 40)
rank_b = rng.normal(24, 8, 38)
fig, ax = plt.subplots(figsize=(7, 3.2))
parts = ax.violinplot([rank_a, rank_b], showmeans=True, showmedians=True)
for pc, c in zip(parts['bodies'], [colors['blue'], colors['gold']]):
    pc.set_facecolor(c); pc.set_alpha(.65); pc.set_edgecolor(colors['charcoal'])
for key in ['cmeans', 'cmedians', 'cbars', 'cmins', 'cmaxes']:
    parts[key].set_color(colors['burgundy'])
ax.set_xticks([1, 2], ['Grup 1', 'Grup 2'])
ax.set_ylabel('Sıra puanı')
ax.set_title('Parametrik olmayan testlerde sıra dağılımlarının karşılaştırılması')
ax.grid(axis='y', alpha=.22)
save('b08-sira-dagilimi.pdf')

# b09 item-total correlations
items = np.arange(1, 9)
corr = np.array([.62, .57, .18, .49, .66, .53, .41, .71])
fig, ax = plt.subplots(figsize=(7, 3.2))
bar_colors = [colors['red'] if v < .30 else colors['blue'] for v in corr]
ax.bar(items, corr, color=bar_colors, alpha=.85)
ax.axhline(.30, color=colors['burgundy'], linestyle='--', linewidth=1.5, label='Sık kullanılan alt sınır (.30)')
ax.set_xlabel('Madde')
ax.set_ylabel('Düzeltilmiş madde-toplam r')
ax.set_ylim(0, .80)
ax.set_title('Güvenirlik analizinde madde-toplam korelasyonlarının taranması')
ax.legend(frameon=False)
save('b09-madde-toplam-grafigi.pdf')

# b14 SPSS workflow diagram as matplotlib boxes
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.axis('off')
steps = [('Veri\nhazırlığı', .10), ('Menü\nseçimi', .30), ('Çıktı\nokuma', .50), ('Etki\nbüyüklüğü', .70), ('Akademik\nrapor', .90)]
for label, x0 in steps:
    ax.text(x0, .55, label, ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=.45', facecolor='#f8f4ec', edgecolor='#78202d', linewidth=1.4))
for (_, x1), (_, x2) in zip(steps[:-1], steps[1:]):
    ax.annotate('', xy=(x2-.08, .55), xytext=(x1+.08, .55), arrowprops=dict(arrowstyle='->', color='#3c3c41', lw=1.8))
ax.set_title('SPSS çıktısını akademik rapora dönüştürme akışı')
save('b14-spss-raporlama-akisi.pdf')