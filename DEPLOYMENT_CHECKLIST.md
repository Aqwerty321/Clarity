# Pre-Deployment Checklist for Clarity

## ✅ Local Development Complete

- [ ] All features working locally
- [ ] Backend runs on `localhost:5000`
- [ ] Frontend runs on `localhost:5173`
- [ ] PostgreSQL database working
- [ ] Ollama models pulled and working
- [ ] All tests passing

## ✅ Code Repository

- [ ] Code committed to Git
- [ ] `.env` files added to `.gitignore`
- [ ] `.env.example` files created
- [ ] README.md updated
- [ ] DEPLOYMENT.md reviewed
- [ ] GitHub repository created
- [ ] Code pushed to GitHub

## ✅ Auth0 Setup

- [ ] Auth0 account created
- [ ] Application created (Single Page Application)
- [ ] API created in Auth0
- [ ] Callback URLs configured (local + production)
- [ ] Logout URLs configured
- [ ] Web Origins configured
- [ ] CORS configured
- [ ] Note `AUTH0_DOMAIN`
- [ ] Note `AUTH0_CLIENT_ID`
- [ ] Note `AUTH0_API_AUDIENCE`

## ✅ Render Database

- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Database name: `clarity_db`
- [ ] Note Internal Database URL
- [ ] Note External Database URL
- [ ] Test connection with `psql`
- [ ] Database region selected

## ✅ Render Backend

- [ ] Web Service created
- [ ] GitHub repository connected
- [ ] Build command configured
- [ ] Start command configured
- [ ] Python 3.11 selected
- [ ] Environment variables set:
  - [ ] `DATABASE_URL`
  - [ ] `AUTH0_DOMAIN`
  - [ ] `AUTH0_API_AUDIENCE`
  - [ ] `CORS_ORIGINS`
  - [ ] `LLM_MODEL`
  - [ ] `EMBEDDER_MODEL`
- [ ] Health check configured: `/api/health`
- [ ] Auto-deploy enabled
- [ ] Note backend URL

## ✅ Frontend Deployment

- [ ] Vercel/Netlify account created
- [ ] Project imported from GitHub
- [ ] Build command: `npm run build`
- [ ] Output directory: `dist`
- [ ] Environment variables set:
  - [ ] `VITE_API_BASE_URL`
  - [ ] `VITE_AUTH0_DOMAIN`
  - [ ] `VITE_AUTH0_CLIENT_ID`
  - [ ] `VITE_AUTH0_AUDIENCE`
  - [ ] `VITE_AUTH0_REDIRECT_URI`
- [ ] Auto-deploy enabled
- [ ] Note frontend URL

## ✅ Auth0 Production Config

- [ ] Added production callback URL to Auth0
- [ ] Added production logout URL to Auth0
- [ ] Added production web origin to Auth0
- [ ] Tested Auth0 login flow in production

## ✅ Testing

### Backend Tests
- [ ] Health endpoint: `curl https://your-backend.onrender.com/api/health`
- [ ] Expected: `{"status":"healthy",...}`

### Frontend Tests
- [ ] Visit production URL
- [ ] Login with Auth0
- [ ] Create notebook
- [ ] Upload document
- [ ] Ask question
- [ ] Generate flashcards
- [ ] Take quiz
- [ ] Check analytics
- [ ] Check marketplace
- [ ] Check settings

### Integration Tests
- [ ] CORS working (no console errors)
- [ ] Database queries working
- [ ] File uploads working
- [ ] AI responses working
- [ ] Authentication working
- [ ] All pages accessible

## ✅ Optional Enhancements

- [ ] Custom domain configured (Vercel/Netlify)
- [ ] SSL certificate (auto with Vercel/Netlify)
- [ ] Error tracking (Sentry)
- [ ] Analytics (Google Analytics, Plausible)
- [ ] Database backups configured
- [ ] Monitoring alerts set up
- [ ] Rate limiting configured
- [ ] API documentation (Swagger)

## ✅ Documentation

- [ ] Update README with production URLs
- [ ] Document environment variables
- [ ] Add troubleshooting guide
- [ ] Create user guide
- [ ] Add API documentation

## ✅ Security

- [ ] API keys not in code
- [ ] Environment variables secure
- [ ] HTTPS enabled
- [ ] Auth0 properly configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation working
- [ ] SQL injection protection

## ✅ Performance

- [ ] Database queries optimized
- [ ] Indexes added to database
- [ ] Caching configured (if applicable)
- [ ] CDN configured for static assets
- [ ] Image optimization
- [ ] Bundle size optimized

## ✅ Monitoring

- [ ] Health checks working
- [ ] Logs accessible
- [ ] Error tracking configured
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Alert notifications

## 🚀 Go Live

- [ ] All checklist items complete
- [ ] Final testing on production
- [ ] Announce launch
- [ ] Monitor for issues
- [ ] Gather user feedback

## 📝 Post-Deployment

- [ ] Monitor error rates
- [ ] Check database performance
- [ ] Review logs regularly
- [ ] Plan for scaling
- [ ] Update documentation
- [ ] Fix reported bugs
- [ ] Add requested features

---

## Quick Commands

### Test Backend Health
```bash
curl https://your-backend.onrender.com/api/health
```

### View Render Logs
```bash
# In Render Dashboard → Service → Logs
```

### Test Database Connection
```bash
psql <EXTERNAL_DATABASE_URL>
```

### Deploy Frontend
```bash
cd frontend
vercel --prod
# or
netlify deploy --prod
```

### View Frontend Logs
```bash
# Vercel
vercel logs

# Netlify
netlify logs
```

---

## Emergency Rollback

### Render Backend
1. Go to Render Dashboard
2. Select your service
3. Go to "Events" tab
4. Click "Rollback" on previous deployment

### Vercel Frontend
```bash
vercel rollback
```

### Netlify Frontend
1. Go to Netlify Dashboard
2. Select site
3. Go to "Deploys"
4. Click "..." on previous deploy
5. Click "Publish deploy"

---

## Support Contacts

- Render Support: https://render.com/support
- Vercel Support: https://vercel.com/support
- Auth0 Support: https://support.auth0.com
- GitHub Issues: https://github.com/yourusername/clarity/issues
