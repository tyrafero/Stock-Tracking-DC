# Railway Deployment Guide

This guide will help you deploy the Stock Tracking DC application to Railway.

## Prerequisites

- Railway account (sign up at railway.app)
- GitHub repository with your code
- Railway CLI (optional, but recommended)

## Step 1: Prepare Your Project

The project has been configured with the following files:

1. **nixpacks.toml** - Tells Railway how to build and run the application
2. **Updated Django settings** - Configured to serve React build files
3. **Updated URLs** - Configured to serve React app for all non-API routes

## Step 2: Create a New Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository: `Stock-Tracking-DC`
4. Railway will automatically detect the project

## Step 3: Add MySQL Database

1. In your Railway project, click "New" → "Database" → "Add MySQL"
2. Railway will automatically create a MySQL database
3. The database connection variables will be available as:
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`

## Step 4: Add Redis (Optional, for caching)

1. Click "New" → "Database" → "Add Redis"
2. Railway will provide `REDIS_URL`

## Step 5: Configure Environment Variables

In your Railway project settings, add these environment variables:

### Required Variables:

```
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=your-app-name.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app

# Database (automatically set by Railway MySQL, but verify)
MYSQL_HOST=${{MySQL.MYSQL_HOST}}
MYSQL_PORT=${{MySQL.MYSQL_PORT}}
MYSQL_USER=${{MySQL.MYSQL_USER}}
MYSQL_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
MYSQL_DATABASE=${{MySQL.MYSQL_DATABASE}}

# Redis (if using)
REDIS_URL=${{Redis.REDIS_URL}}
```

### Optional Variables:

```
# Email/SendGrid (if using email features)
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Cloudinary (if using cloud storage for images)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

## Step 6: Update ALLOWED_HOSTS

After Railway assigns your domain:

1. Note your Railway app URL (e.g., `stock-tracking-dc-production.up.railway.app`)
2. Update the environment variable:
   ```
   ALLOWED_HOSTS=stock-tracking-dc-production.up.railway.app,localhost
   CSRF_TRUSTED_ORIGINS=https://stock-tracking-dc-production.up.railway.app
   ```

Or update directly in `src/backend/stockmgtr/settings.py` if you prefer.

## Step 7: Deploy

1. Railway will automatically deploy when you push to your main branch
2. You can also manually trigger a deployment from the Railway dashboard

## Step 8: Run Migrations

After the first deployment, you need to run database migrations:

### Option A: Using Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run python src/backend/manage.py migrate

# Create superuser (optional)
railway run python src/backend/manage.py createsuperuser
```

### Option B: Using Railway Dashboard
1. Go to your service in Railway
2. Click on "Settings" → "Custom Start Command"
3. Add a one-time migration command:
   ```
   cd src/backend && python manage.py migrate && gunicorn stockmgtr.wsgi:application --bind 0.0.0.0:$PORT
   ```
4. After migrations run, you can remove the migrate command

## Step 9: Collect Static Files

Static files are automatically collected during build (see nixpacks.toml).
If you need to manually collect:

```bash
railway run python src/backend/manage.py collectstatic --noinput
```

## Step 10: Create Admin User

```bash
railway run python src/backend/manage.py createsuperuser
```

## Troubleshooting

### Build Fails

1. **Check logs** in Railway dashboard for specific errors
2. **Verify all dependencies** are in requirements.txt and package.json
3. **Check Node/Python versions** match your local environment

### Database Connection Issues

1. Verify environment variables are correctly referenced
2. Check that MySQL service is running
3. Verify MYSQL_* variables are set correctly

### Static Files Not Loading

1. Run `railway run python src/backend/manage.py collectstatic`
2. Check STATIC_ROOT and STATICFILES_DIRS in settings.py
3. Verify frontend build completed successfully

### Frontend Not Loading

1. Check that `src/frontend/dist` was created during build
2. Verify vite.config.ts has correct base path
3. Check browser console for errors

## File Structure

```
Stock-Tracking-DC/
├── nixpacks.toml          # Railway build configuration
├── src/
│   ├── backend/
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   ├── stockmgtr/
│   │   │   ├── settings.py  # Updated for production
│   │   │   ├── urls.py      # Updated to serve React
│   │   │   └── views.py     # React view handler
│   │   └── ...
│   └── frontend/
│       ├── package.json
│       ├── vite.config.ts
│       └── dist/            # Built React app (created during deployment)
```

## Environment Variable Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| SECRET_KEY | Yes | Django secret key | `django-insecure-xyz123...` |
| DEBUG | Yes | Debug mode (False for production) | `False` |
| MYSQL_HOST | Yes | Database host | From Railway MySQL |
| MYSQL_PORT | Yes | Database port | `3306` |
| MYSQL_USER | Yes | Database user | From Railway MySQL |
| MYSQL_PASSWORD | Yes | Database password | From Railway MySQL |
| MYSQL_DATABASE | Yes | Database name | From Railway MySQL |
| REDIS_URL | No | Redis connection URL | From Railway Redis |
| SENDGRID_API_KEY | No | SendGrid API key | `SG.xyz...` |

## Post-Deployment Checklist

- [ ] Application builds successfully
- [ ] Database migrations ran successfully
- [ ] Static files are loading
- [ ] React app loads correctly
- [ ] API endpoints are accessible
- [ ] Admin panel is accessible (/admin)
- [ ] Created superuser account
- [ ] Tested authentication
- [ ] Verified database connections

## Useful Commands

```bash
# View logs
railway logs

# Run shell commands
railway run python src/backend/manage.py shell

# SSH into container
railway shell

# Run migrations
railway run python src/backend/manage.py migrate

# Create superuser
railway run python src/backend/manage.py createsuperuser

# Flush database (careful!)
railway run python src/backend/manage.py flush
```

## Support

If you encounter issues:

1. Check Railway logs for errors
2. Verify all environment variables are set
3. Ensure database is running
4. Check the Railway documentation: https://docs.railway.app

## Next Steps After Successful Deployment

1. Set up custom domain (optional)
2. Configure monitoring and alerts
3. Set up automated backups for MySQL
4. Configure email notifications
5. Set up CI/CD pipeline
