# PCC Gözcü Demo

Vodafone temalı, veritabanına bağlanmayan demo sürümüdür. BA_ID girildiğinde hazır mock senaryolarla analiz ekranı gösterir.

## İçerik
- `app.py` → Flask demo uygulaması
- `templates/index.html` → arayüz
- `static/style.css` → Vodafone temalı stil
- `Dockerfile` → container (Gunicorn, 8080)
- `openshift/application.yaml` → Deployment + Service + Route (şablon; çalışan [InvoiceTool](https://github.com/benbewul/InvoiceTool) ile aynı port/health fikri)
- `Jenkinsfile` → image build + `oc apply` ile deploy
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
Bu projedeki `Jenkinsfile` şu akışı izler:
1. Repo'yu checkout eder
2. `oc login` ile cluster'a bağlanır
3. Eski app/build kaynaklarını temizler
4. Dockerfile üzerinden binary build başlatır
5. Image'dan app oluşturur
6. Service ve Route açar

### Gereken Jenkins credential
- `ocp-token` → OpenShift token'ı `Secret text` olarak tanımlanmalı

### Dikkat
- Bu demo sürümünde veritabanı bağlantısı yoktur.
- İlk amaç route ile arayüzü cluster üzerinde ayağa kaldırmaktır.
- Sonraki fazda Oracle bağlantıları ve gerçek analiz kuralları eklenebilir.
