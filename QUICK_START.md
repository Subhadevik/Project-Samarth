# 🚀 Quick Deployment Guide - Project Samarth

## 🎯 Choose Your Deployment Method

### 1. 🖥️ **Local Development** (Fastest to test)
```bash
python deploy.py local
```
Access at: http://localhost:5000

### 2. 🐳 **Docker** (Recommended for production)
```bash
# Simple Docker
python deploy.py docker

# Or with Nginx (full production setup)
python deploy.py docker-compose
```
Access at: http://localhost

### 3. ☁️ **Cloud Platforms** (Public deployment)

#### **Heroku** (Free tier available)
```bash
# Install Heroku CLI first: https://devcenter.heroku.com/articles/heroku-cli
python deploy.py heroku
```

#### **Railway** (Modern alternative)
```bash
# Install Railway CLI first: npm install -g @railway/cli
python deploy.py railway
```

#### **Render** (Git-based deployment)
1. Push code to GitHub
2. Connect to https://render.com
3. Deploy automatically from repository

## ⚡ One-Line Deployments

### **Instant Local Testing**
```bash
cd backend && python main.py
```

### **Docker with all services**
```bash
docker-compose up -d
```

### **Production with Streamlit**
```bash
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

## 🔧 Environment Variables (Optional)

Create `.env` file in backend directory:
```bash
FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000
```

## 📊 Verify Deployment

Test these URLs after deployment:
- `/` - Main application
- `/api/health` - Health check
- `/api/examples` - Example queries
- `/api/datasets` - Available data sources

## 🆘 Troubleshooting

**Port already in use?**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac  
lsof -ti:5000 | xargs kill -9
```

**Missing dependencies?**
```bash
pip install -r requirements.txt
```

**Docker issues?**
```bash
docker system prune -a
docker-compose down && docker-compose up --build
```

## 🌍 Access Your Deployed App

After successful deployment, test these features:
1. **Ask a question**: "Compare rice production between Punjab and Haryana"
2. **Check citations**: Verify data.gov.in source links
3. **Test caching**: Ask the same question twice (should be faster)
4. **View API**: Visit `/api/health` endpoint

---

**Need help?** Check the full [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.