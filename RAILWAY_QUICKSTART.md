# Railway Deployment - Quick Start

## 🚀 What's Been Configured

Your project is now ready for Railway deployment with:

✅ **nixpacks.toml** - Build configuration for Railway (fixed pip command issue)
✅ **Django settings** - Updated to serve React build files
✅ **Django URLs** - Configured to route to React app
✅ **React view** - Serves index.html for client-side routing
✅ **.railwayignore** - Excludes unnecessary files
✅ **Migrations** - Auto-run on deployment

### Recent Fix
The `pip: command not found` error has been resolved by updating nixpacks.toml to use `python -m pip` instead of `pip` directly.

## 📋 Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

### 2. Create Railway Project
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your `Stock-Tracking-DC` repository
4. Wait for Railway to detect the project

### 3. Add MySQL Database
1. In Railway dashboard, click "New" → "Database" → "Add MySQL"
2. Railway auto-creates these variables:
   - MYSQL_HOST
   - MYSQL_PORT
   - MYSQL_USER
   - MYSQL_PASSWORD
   - MYSQL_DATABASE

### 4. Add Environment Variables

Click on your service → "Variables" tab → Add these:

```bash
SECRET_KEY=o7hnzs@px&jzfrb3#rb3)0#zlb71ohk3vvqf#(q)!ce2i+@9m
DEBUG=False
```

**Important:** After Railway assigns your domain (e.g., `your-app.up.railway.app`), add:
```bash
ALLOWED_HOSTS=your-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app
```

### 5. Deploy!
Railway will automatically deploy. Watch the logs for any errors.

### 6. Create Admin User
After successful deployment:
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and link
railway login
railway link

# Create superuser
railway run python src/backend/manage.py createsuperuser
```

## 🔧 Common Issues & Fixes

### "Nixpacks build failed"
**Fix:** Check Railway logs for specific error. Common causes:
- Missing dependencies in requirements.txt or package.json
- Node/Python version mismatch
- Build command errors

### "Static files not loading"
**Fix:**
```bash
railway run python src/backend/manage.py collectstatic --noinput
```

### "Database connection error"
**Fix:** Verify MySQL service is running and environment variables are set correctly.

### "React app not loading"
**Fix:**
1. Check frontend build succeeded: `ls src/frontend/dist`
2. Verify vite built successfully in Railway logs
3. Check browser console for errors

## 🎯 Post-Deployment Checklist

- [ ] App deployed successfully
- [ ] Database connected
- [ ] Admin panel accessible at `/admin`
- [ ] Created superuser account
- [ ] Frontend loads correctly
- [ ] API endpoints working (`/api/...`)
- [ ] Authentication working

## 📊 Monitoring Your App

```bash
# View logs
railway logs

# Check service status
railway status

# Open app in browser
railway open
```

## 🆘 Need Help?

1. **Check Railway Logs:** Most issues show up in logs
2. **Verify Environment Variables:** Make sure all required vars are set
3. **Database Status:** Ensure MySQL service is running
4. **Full Guide:** See `RAILWAY_DEPLOYMENT.md` for detailed instructions

## 🔑 Your Generated SECRET_KEY

```
o7hnzs@px&jzfrb3#rb3)0#zlb71ohk3vvqf#(q)!ce2i+@9m
```

⚠️ **Never commit this to version control!** Add it only in Railway's environment variables.

## 🎉 Success!

Once deployed, your app will be accessible at:
- **Frontend:** https://your-app.up.railway.app
- **Admin:** https://your-app.up.railway.app/admin
- **API:** https://your-app.up.railway.app/api

Happy deploying! 🚀
