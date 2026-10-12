# ChildSafe — Meta public pages

This package contains three public HTML pages for Meta Developer settings.

## Install
Unzip into the ChildSafe `backend` directory (the directory containing `app/`). The files should be:
- `app/static/legal/privacy.html`
- `app/static/legal/terms.html`
- `app/static/legal/data-deletion.html`

The current FastAPI app mounts `app/static` at `/static`, so these should be served without adding Python routes, provided that mount is still present.

Example:
```bash
cd ~/Documents/Childsafe/backend
unzip ~/Downloads/childsafe-meta-pages.zip
git status
git add app/static/legal
git commit -m "Add Meta privacy and legal pages"
git push
```
If the ZIP is saved somewhere other than Downloads, adjust its path.

## Test after Render deploy
- Privacy Policy: https://childsafe-alsh.onrender.com/static/legal/privacy.html
- Terms of Service: https://childsafe-alsh.onrender.com/static/legal/terms.html
- Data Deletion Instructions: https://childsafe-alsh.onrender.com/static/legal/data-deletion.html

Open all three in a private/incognito window. Each must load without login and without a 404/500 error.

## Meta Settings → Basic
- App Domains: `childsafe-alsh.onrender.com` (domain only; no `https://` or path)
- Privacy Policy URL: `https://childsafe-alsh.onrender.com/static/legal/privacy.html`
- Terms of Service URL: `https://childsafe-alsh.onrender.com/static/legal/terms.html`
- User Data Deletion: choose/provide **Data Deletion Instructions URL** and use `https://childsafe-alsh.onrender.com/static/legal/data-deletion.html`
- Contact email: `suelmaparis@hotmail.com`
- Data Protection Officer: leave blank unless a DPO has actually been designated.

These pages are a practical starting point, not legal advice or a guarantee of Meta approval. Review them against the exact data flows enabled in production before publishing. Update the policy if new collection, uploads, login, or integrations are added. Never commit the Meta App Secret or credentials to GitHub.
