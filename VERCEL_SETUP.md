# Vercel Deployment Guide for Django School Project

## Prerequisites
1. Install [Vercel CLI](https://vercel.com/cli)
   ```bash
   npm install -g vercel
   ```

2. Create a free account at [vercel.com](https://vercel.com)

## Deployment Steps

### 1. Login to Vercel
```bash
vercel login
```

### 2. Deploy Your Project
```bash
vercel
```

The first deployment will ask for your project name and configuration. Accept the defaults or customize as needed.

### 3. Set Environment Variables
After the first deployment, set these environment variables in your Vercel project dashboard:

1. Go to your project dashboard on vercel.com
2. Click "Settings" → "Environment Variables"
3. Add the following variables:

| Variable | Value | Example |
|----------|-------|---------|
| `SECRET_KEY` | Your Django secret key (keep it secure!) | `your-long-random-string` |
| `DEBUG` | Set to `False` for production | `False` |
| `ALLOWED_HOSTS` | Your Vercel domain | `your-project.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | Your Vercel domain (HTTPS) | `https://your-project.vercel.app` |

### 4. Redeploy After Setting Variables
```bash
vercel --prod
```

## What Changed

- **vercel.json**: Updated with proper build commands and routes
- **config/settings.py**: 
  - DEBUG and SECRET_KEY now use environment variables
  - ALLOWED_HOSTS now configurable via environment variables
  - Added security settings (SSL redirect, secure cookies)
  - Removed django-heroku dependency
- **requirements.txt**: Removed psycopg2 and django-heroku (not needed for Vercel with SQLite)
- **.vercelignore**: Excludes unnecessary files from deployment

## Important Notes

⚠️ **Database**: Your app currently uses SQLite, which is fine for small projects but:
- Vercel's filesystem is ephemeral (resets on deployments)
- For production, consider using a cloud database like PostgreSQL on Railway, Supabase, or AWS RDS

⚠️ **Static Files**: WhiteNoise is configured to serve static files. Make sure to run:
```bash
python manage.py collectstatic
```
locally before deploying if you've added new static files.

⚠️ **Media Files**: User uploads won't persist between deployments. Consider using cloud storage (AWS S3, Cloudinary, etc.)

## Local Testing

To test your Vercel setup locally:
```bash
vercel dev
```

This runs your app similarly to how it will run on Vercel.

## Troubleshooting

**Build fails with "No such file or directory"**
- Make sure all required packages are in requirements.txt

**Static files not loading**
- Run `python manage.py collectstatic`
- Check that STATIC_ROOT points to the correct directory

**Database errors**
- For SQLite, Vercel has a 512MB file size limit
- Consider migrating to PostgreSQL for production

**502 Bad Gateway**
- Check the deployment logs on Vercel dashboard
- Ensure WSGI application is properly configured

## Updating Your Deployment

Simply push to your repository (if connected) or run:
```bash
vercel --prod
```

## Additional Resources

- [Vercel Python Runtime Docs](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
