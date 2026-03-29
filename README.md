# PCC Gözcü Demo

Vodafone temalı, veritabanına bağlanmayan demo sürümüdür. BA_ID girildiğinde hazır mock senaryolarla analiz ekranı gösterir.

## İçerik
- `app.py` → Flask demo uygulaması
- `templates/index.html` → arayüz
- `static/style.css` → Vodafone temalı stil
- `Dockerfile` → container (Gunicorn, 8080)
- `Jenkinsfile` → OpenShift: `oc new-build` / `start-build` / `new-app` / `expose` (çalışan analiz-ekrani pipeline ile aynı akış)
- `.dockerignore` → gereksiz dosyaları build dışı bırakır

## Local çalıştırma
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows için: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Tarayıcı:
```bash
http://127.0.0.1:5000
```

## Hazır demo BA_ID'leri
- `6092902934`
- `6070166156`

## Docker ile local test
```bash
docker build -t pcc-analiz-tool .
docker run -p 8080:8080 pcc-analiz-tool
```

Tarayıcı: `http://127.0.0.1:8080`

## OpenShift uygulama adı
`Jenkinsfile` içinde `APP_NAME=pcc-analiz-tool`; route örneği: `pcc-analiz-tool-<proje>.apps.<cluster>/`

## Jenkins / OpenShift pipeline mantığı
`environment` içindeki `GIT_URL` varsayılan olarak analiz-ekrani reposunu çeker; repo adresini değiştirebilirsin. Akış:
1. `git` ile checkout
2. `oc login` + proje
3. `oc delete all -l app=...` ve BuildConfig / ImageStream temizliği
4. `oc new-build --binary --strategy=docker` + `oc start-build --from-dir=.`
5. `oc new-app <is>:latest` + `oc expose service`

**Multibranch:** Job zaten repoyu checkout ediyorsa, `Checkout` aşamasında `checkout scm` kullan ve `GIT_URL` adımını kaldırabilirsin.

### Gereken Jenkins credential
- `ocp-token` → OpenShift token'ı `Secret text` olarak tanımlanmalı

### Dikkat
- Bu demo sürümünde veritabanı bağlantısı yoktur.
- İlk amaç route ile arayüzü cluster üzerinde ayağa kaldırmaktır.
- Sonraki fazda Oracle bağlantıları ve gerçek analiz kuralları eklenebilir.
