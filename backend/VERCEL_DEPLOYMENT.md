# Django Backend Deployment to Vercel - Setup Guide

## ✅ Files Already Created/Updated

The following changes have been made to prepare your Django backend for Vercel deployment:

### 1. **`wealthwise/settings.py`** - Updated
   - Removed `vercel_wsgi` import (not needed)
   - Added `whitenoise.middleware.WhiteNoiseMiddleware` for static file serving
   - Updated `SECRET_KEY` to use environment variable with fallback
   - Added `dj_database_url` support for PostgreSQL in production
   - Configured `STATIC_ROOT` and `STATICFILES_STORAGE` for Whitenoise

### 2. **`api/django.py`** - NEW
   - WSGI handler for Vercel serverless functions
   - Converts Vercel requests to Django WSGI format
   - Ready to deploy as serverless function

### 3. **`vercel.json`** - Updated
   - Configured to build and deploy `api/django.py`
   - Routes all requests to the Django handler
   - Sets environment variables for production

### 4. **`runtime.txt`** - NEW
   - Specifies Python 3.11 for Vercel

### 5. **`requirements.txt`** - Updated
   - All necessary packages already included:
     - `django`, `djangorestframework`, `django-cors-headers`
     - `whitenoise>=6.0` (for static files)
     - `psycopg2-binary>=2.9.6` (for PostgreSQL)
     - `dj-database-url>=2.0.0` (for DATABASE_URL parsing)
     - `gunicorn` (included)

### 6. **`.gitignore`** - Updated
   - Added `.env` to never commit secrets
   - Added `.vercel/` directory

---

## 🚀 Next Steps to Deploy

### Step 1: Set Up Production Database

Before deploying to Vercel, you need a managed PostgreSQL database:

**Option A: Use Vercel Postgres** (Recommended)
- Go to https://vercel.com/dashboard
- Select your project → Storage → Create Database
- Copy the `DATABASE_URL` connection string

**Option B: Use an external provider**
- Supabase (https://supabase.com) - Free tier available
- Railway (https://railway.app) - Free tier available
- Neon (https://neon.tech) - Serverless Postgres
- AWS RDS, DigitalOcean, etc.

### Step 2: Generate a New SECRET_KEY

Generate a secure Django SECRET_KEY for production:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output - you'll need it in the next step.

### Step 3: Set Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Click **Settings** → **Environment Variables**
3. Add the following variables (set to "Production"):

| Key | Value | Notes |
|-----|-------|-------|
| `ENV_MODE` | `prod` | Production mode |
| `DEBUG` | `False` | Disable debug mode |
| `SECRET_KEY` | *generated above* | Use the generated SECRET_KEY |
| `DATABASE_URL` | *from your DB provider* | PostgreSQL connection string |
| `SITE_URL_PROD` | `https://your-frontend.vercel.app` | Your frontend URL |
| `FASTAPI_URL_PROD` | `https://your-api.example.com` | Your FastAPI predictions backend URL |
| `KITE_API_KEY_PROD` | *your value* | From .env |
| `KITE_API_SECRET_PROD` | *your value* | From .env |
| `GOOGLE_CLIENT_ID` | *your value* | From .env |
| `GOOGLE_CLIENT_SECRET` | *your value* | From .env |
| `GOOGLE_API_KEY` | *your value* | From .env |
| `YOUTUBE_API_KEY` | *your value* | From .env |
| `GOOGLE_SEARCH_API_KEY` | *your value* | From .env |
| `GOOGLE_CSE_ID` | *your value* | From .env |

### Step 4: Run Database Migrations

Before first deploy, run migrations against the production database:

```powershell
# Set the production database URL (temporary)
$env:DATABASE_URL = "your-database-url-here"

# Run migrations
python manage.py migrate --settings=wealthwise.settings

# Collect static files (optional, for local testing)
python manage.py collectstatic --noinput --settings=wealthwise.settings
```

### Step 5: Deploy via Vercel CLI

```powershell
# Install Vercel CLI globally (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# From the backend directory, deploy to production
vercel --prod

# Or just deploy to preview (testing)
vercel
```

### Step 6: Configure Your Frontend

Update your frontend to use the new backend URL from Vercel:

In your frontend environment variables:
```
VITE_API_URL=https://your-backend.vercel.app
```

---

## 🔍 Verification & Troubleshooting

### Check Deployment Status
1. Go to https://vercel.com/dashboard
2. Click your project
3. Click **Deployments** tab
4. View logs for any errors

### Test the Backend
```powershell
# Test if backend is accessible
curl https://your-backend.vercel.app/

# Test a specific endpoint
curl https://your-backend.vercel.app/api/users/
```

### Common Issues & Fixes

**Issue: "ModuleNotFoundError: No module named 'wealthwise'"**
- Solution: Ensure all imports in `settings.py` are correct
- Check that `DJANGO_SETTINGS_MODULE` in `api/django.py` is set correctly

**Issue: "Database connection refused"**
- Solution: Verify `DATABASE_URL` is correct in Vercel env vars
- Check database provider's connection limits

**Issue: "Static files not loading"**
- Solution: Whitenoise should handle this automatically
- Verify `STATICFILES_STORAGE` is set in settings.py

**Issue: "Cold start timeout"**
- Solution: This is normal for serverless (first request is slower)
- Consider moving heavy ML inference to a dedicated FastAPI host

### View Real-time Logs
```powershell
vercel logs https://your-backend.vercel.app --follow
```

---

## 📋 Checklist Before Going Live

- [ ] Generated new `SECRET_KEY` and added to Vercel env vars
- [ ] Set up production PostgreSQL database
- [ ] Added `DATABASE_URL` to Vercel env vars
- [ ] Copied all API keys from `.env` to Vercel env vars
- [ ] Set `ENV_MODE=prod` and `DEBUG=False` in Vercel env vars
- [ ] Ran `python manage.py migrate` against production database
- [ ] Tested backend endpoints after deployment
- [ ] Updated frontend to use new backend URL
- [ ] Removed `.env` file from git (check it's in `.gitignore`)
- [ ] Verified CORS settings work with frontend domain

---

## 🎯 Important Notes

⚠️ **SECURITY**: Never commit `.env` files with secrets. They are already in `.gitignore`.

⚠️ **DATABASE**: SQLite won't work in serverless; PostgreSQL is required.

⚠️ **STATIC FILES**: Whitenoise automatically serves static files in production.

⚠️ **COLD STARTS**: First request may take 5-10 seconds (normal for serverless).

⚠️ **TIMEOUTS**: Long-running tasks (ML inference) should be moved to a separate FastAPI backend.

---

## 📚 Useful Links

- Vercel Django Docs: https://vercel.com/docs/concepts/functions/serverless-functions/python
- Django with Vercel: https://vercel.com/blog/
- Environment Variables: https://vercel.com/docs/projects/environment-variables
- PostgreSQL Providers:
  - Vercel Postgres: https://vercel.com/postgres
  - Supabase: https://supabase.com
  - Railway: https://railway.app
  - Neon: https://neon.tech

---

**Ready to deploy? Follow the steps above and run `vercel --prod` from the backend directory!**
