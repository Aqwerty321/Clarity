# 🗄️ Render PostgreSQL Setup Guide

## Step-by-Step Instructions

### 1. Log into Render Dashboard

1. Go to https://dashboard.render.com
2. Sign in with your account

### 2. Create New PostgreSQL Database

1. Click **"New +"** button in the top-right
2. Select **"PostgreSQL"**

### 3. Configure Database

Fill in the following details:

#### Basic Information
- **Name**: `clarity-db` (or your preferred name)
- **Database**: `clarity_db` (database name)
- **User**: `clarity_user` (will be auto-generated if left empty)
- **Region**: Choose closest to you (e.g., Oregon, Frankfurt, Singapore)

#### Plan Selection
- **Free Tier**: 
  - ✅ 256 MB RAM
  - ✅ 1 GB Storage
  - ✅ Good for development/testing
  - ⚠️ Expires after 90 days of inactivity
  - ⚠️ No automatic backups

- **Starter Plan ($7/month)**:
  - ✅ 1 GB RAM
  - ✅ 10 GB Storage
  - ✅ Daily automatic backups
  - ✅ Point-in-time recovery
  - ✅ No expiration

**Recommendation**: Start with Free tier for testing, upgrade to Starter for production

4. Click **"Create Database"**

### 4. Wait for Database to Deploy

- This takes about 2-3 minutes
- Status will change from "Creating" → "Available"
- Don't close the page!

### 5. Get Connection Details

Once the database is ready, you'll see several connection strings:

#### Internal Database URL (Use This!)
```
postgresql://clarity_user:XXXX@dpg-XXXXX-a/clarity_db
```
**Use this for your backend** - it's faster and free within Render

#### External Database URL (Optional)
```
postgresql://clarity_user:XXXX@dpg-XXXXX-a.oregon-postgres.render.com/clarity_db
```
Use this only if connecting from outside Render (local testing)

### 6. Copy Connection Details

Click the **copy icon** next to:
1. **Internal Database URL** ← Main one you need
2. **External Database URL** ← For local testing (optional)

Keep these safe! You'll need them in the next steps.

---

## 📋 What You Need to Save

### Required Information
- [x] Internal Database URL
- [x] External Database URL (optional)
- [x] Database name: `clarity_db`
- [x] Username: (from connection string)
- [x] Password: (from connection string)
- [x] Host: (from connection string)
- [x] Port: Usually 5432

---

## ✅ Verification

### Test Connection from Your Computer (Optional)

If you have `psql` installed:

```bash
# Use External Database URL
psql "postgresql://clarity_user:XXXX@dpg-XXXXX-a.oregon-postgres.render.com/clarity_db"
```

You should see:
```
psql (14.x)
Type "help" for help.

clarity_db=>
```

If you see this, your database is ready! ✅

### Test Using Python (Alternative)

```bash
pip install psycopg2-binary

python -c "
import psycopg2
conn = psycopg2.connect('YOUR_EXTERNAL_DATABASE_URL')
print('✅ Connection successful!')
conn.close()
"
```

---

## 🔧 Next Steps

Now that your database is created, you need to:

### Option 1: Deploy Sync Service to Render

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add sync service"
   git push origin main
   ```

2. **Create Web Service on Render**
   - Dashboard → New → Web Service
   - Connect your GitHub repo
   - Follow prompts (see RENDER_DEPLOY.md)

3. **Add Environment Variable**
   - In Web Service settings
   - Add: `DATABASE_URL` = Internal Database URL

### Option 2: Use for Local Testing

Update your local `.env` file:

```bash
# Add this to test cloud database locally
# Use External Database URL here
DATABASE_URL=postgresql://clarity_user:XXXX@dpg-XXXXX-a.oregon-postgres.render.com/clarity_db
```

Then restart your local backend:
```bash
cd local_backend
uvicorn app.main:app --reload --port 5000
```

---

## 🎯 Quick Reference

### Connection String Format
```
postgresql://[username]:[password]@[host]:[port]/[database]
```

### Common Commands

**Connect with psql:**
```bash
psql "YOUR_EXTERNAL_DATABASE_URL"
```

**List databases:**
```sql
\l
```

**List tables:**
```sql
\dt
```

**Exit psql:**
```sql
\q
```

---

## 🔒 Security Notes

- ✅ Keep connection strings secret
- ✅ Never commit to Git
- ✅ Use environment variables
- ✅ Use Internal URL for Render services (faster)
- ✅ Use External URL only for local testing

---

## 💰 Cost Summary

### Free Tier
- **Cost**: $0
- **Duration**: Expires after 90 days inactivity
- **Good for**: Development, testing, learning

### Starter Plan  
- **Cost**: $7/month
- **Features**: Backups, no expiration, more resources
- **Good for**: Production, serious projects

### Upgrade Anytime
You can start free and upgrade later without losing data!

---

## 🐛 Troubleshooting

### "Database creation failed"
- Try a different region
- Check your payment method (even for free tier)
- Contact Render support

### "Can't connect"
- Check you're using correct URL (Internal vs External)
- Verify database status is "Available"
- Check firewall isn't blocking port 5432

### "Permission denied"
- Verify username/password in connection string
- Check database name is correct
- Try regenerating connection string

---

## ✨ Success!

Once you see your database in Render dashboard with status **"Available"**, you're done!

Your database is ready to use for:
- ✅ Cloud sync service (when deployed)
- ✅ Local development (optional)
- ✅ Testing sync functionality

**Next**: Deploy the sync service to use this database!

See: `RENDER_DEPLOY.md` for deploying the web service.
