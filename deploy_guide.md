# 🌐 Jarvis AI Copilot-ni Serverga Deploy Qilish Yo'riqnomasi

Ushbu yo'riqnoma orqali siz **Jarvis AI Copilot** loyihangizni internetga joylashtirib, istalgan qurilmangizdan (telefon, noutbuk, planshet) foydalanishingiz mumkin.

---

## 1-USUL: Streamlit Community Cloud (Eng oson, TEKIN va 1 daqiqalik usul) ⭐⭐⭐⭐⭐

Streamlit tomonidan taqdim etiladigan rasmiy va bepul bulutli hosting.

### 1-qadam: Kodlarni GitHub-ga joylash
Terminalingizda quyidagi buyruqlarni bajaring:

```bash
# 1. GitHub-da yangi (Shaxsiy / Private) repozitoriy yarating (masalan: jarvis-ai)
git add .
git commit -m "deploy: Jarvis Pro suite va server fayllari"

# 2. O'zingizning GitHub repozitoriyangizga ulating
git remote add origin https://github.com/USERNAME/jarvis-ai.git
git branch -M main
git push -u origin main
```

### 2-qadam: Streamlit Cloud-da Deploy qilish
1. **[share.streamlit.io](https://share.streamlit.io)** saytiga kiring va GitHub hisobingiz orqali avtorizatsiyadan o'ting.
2. **"Create app"** -> **"Yup, I have an app"** tugmasini bosing.
3. Repozitoriyingizni tanlang (`USERNAME/jarvis-ai`).
4. Main file path: `jarvis.py`
5. **"Advanced settings"** bo'limida **Secrets** oynasiga API kalitingizni kiriting:
   ```toml
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
   ```
6. **"Deploy!"** tugmasini bosing.
7. 1-2 daqiqada sizga tayyor unikal domen beriladi (masalan: `https://jarvis-javoxir.streamlit.app`).

---

## 2-USUL: Docker orqali Istalgan VPS Serverga Deploy qilish (Ubuntu / DigitalOcean / Hetzner) ⭐⭐⭐⭐

Agar o'zingizning shaxsiy VPS serveringiz bo'lsa:

### Serverda ishga tushirish:
```bash
# 1. Serverga kodlarni yuklang
git clone https://github.com/USERNAME/jarvis-ai.git
cd jarvis-ai

# 2. .env fayliga API kalitni kiriting
echo "GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE" > .env

# 3. Docker Compose orqali ishga tushiring
docker-compose up -d --build
```
Ilova `http://YOUR_SERVER_IP:8501` manzilida ishlay boshlaydi!

---

## 3-USUL: Render.com orqali Cloud Deploy ⭐⭐⭐⭐

1. **[render.com](https://render.com)** saytida bepul ro'yxatdan o'ting.
2. **"New Web Service"** tugmasini bosing va GitHub repozitoriyangizni ulating.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `streamlit run jarvis.py --server.port=$PORT --server.address=0.0.0.0`
5. Environment Variables bo'limiga `GEMINI_API_KEY` kalitini qo'shing.
6. **Deploy** tugmasini bosing!

---

### 🛡️ Xavfsizlik Eslatmasi:
Repozitoriyingizni GitHub-da **Private (Shaxsiy)** qilib ochishingizni tavsiya etamiz. Tizim avtomatik tarzda `.env` faylini `.gitignore` ga kiritgan, shuning uchun maxfiy kalitlaringiz xavfsiz qoladi.
