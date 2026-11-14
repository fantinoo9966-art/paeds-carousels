# Paediatrick-or-Treats Carousel Agent: Setup Guide

**What it does:** 3 times a week (Mon/Wed/Fri at 8 AM IST) it picks a topic, has Google Gemini write a 6–10 slide carousel, designs the slides, and sends you a **review page** on GitHub. You check it on your phone and tap **Merge**, and it posts to Instagram. If you close the page instead, nothing gets posted.

**Cost: ₹0.** GitHub, Gemini's free tier and the Instagram API are all free, and no card is needed.
Note: on the free tier, Google may use what you send to Gemini to improve its products. That's fine for public educational content, but never put patient details in topics.

---

## One-time setup (about 45 minutes)

### 1. GitHub (free)
1. Create an account at github.com and install the **GitHub mobile app** (that's where you'll approve posts).
2. Create a **new public repository**, e.g. `paeds-carousels`.
   *It must be public because Instagram downloads the slide images from it. Your passwords and keys stay hidden in Secrets.*
3. Upload all the files from this folder to the repository (on the repo page: **Add file → Upload files** and drag the whole folder in, including the `.github` folder).
4. In the repo, go to **Settings → Actions → General**:
   - Workflow permissions: **Read and write permissions**
   - Tick **Allow GitHub Actions to create and approve pull requests**
   - Save.

### 2. Free Gemini API key
1. Go to **aistudio.google.com** and sign in with your Google account.
2. Click **Get API key → Create API key** and copy it. Don't add billing; the free tier is enough for 3 posts a week.
3. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**
   Name: `GEMINI_API_KEY`, Value: the key.

### 3. Instagram posting access (Meta)
This uses **Instagram Login**, so no Facebook Page is needed. Your Facebook account is only used to sign in to the developer site.
1. developers.facebook.com → **My Apps → Create App**. For the use case, choose **Manage messaging & content on Instagram**; if it asks for an app type, choose **Business**.
2. In the app's left menu: **Instagram → API setup with Instagram business login**.
3. Under **Generate access tokens**, click **Add account** and log in with **paediatrick_or_treats**. If it asks you to accept a tester invite, do that in Instagram: **Settings → Website permissions → Apps and websites → Tester invites → Accept**.
4. Click **Generate token** next to paediatrick_or_treats, allow the permissions, and copy the token.
5. Add a GitHub secret named `IG_ACCESS_TOKEN` with the token as its value. Your Instagram ID is looked up automatically.
6. Check it: **Actions → Test Instagram connection → Run workflow**. A green tick means it's connected (this posts nothing).

⏰ **The token lasts 60 days.** Set a phone reminder for every 50 days to generate a new one (step 4) and update the secret.

### 4. Test it
GitHub repo → **Actions → Create carousel → Run workflow** (you can type a topic or leave it blank).
After about 3 minutes, a new **Pull request** appears. Open it on your phone.

---

## Daily use
- 🔔 GitHub notifies you when a new carousel is ready.
- Read the slides and the **"Please double-check"** list (every dose and number is listed there). Read carefully: free AI models make more medical mistakes than paid ones.
- **Looks right?** → tap **Merge pull request** and it's live on Instagram in about 2 minutes.
- **Needs a fix?** → in the PR, open **Files changed**, edit `slides.json` (✏️), and commit. The slides re-render by themselves in about 2 minutes. To change only the caption, edit `caption.txt`.
- **Don't like it?** → **Close pull request**.
- **Want a specific topic now?** → Actions → Create carousel → Run workflow → type the topic.
- **Change the topic queue** → edit `topics.txt`.
- **Change the posting days/time** → edit the `cron` line in `.github/workflows/create-post.yml`.
- **Change colours, tone, model** → `agent/config.py`.

**Best time to merge:** 7–9 PM IST, when Indian medical students are most active.

---

## Troubleshooting
| Problem | Fix |
|---|---|
| "Create carousel" fails at *Write slides* | Check the `GEMINI_API_KEY` secret. If the log says every model failed, Google may have renamed its free models: update `GEMINI_MODELS` in `agent/config.py` from aistudio.google.com/docs/pricing |
| PR isn't created | Step 1.4 (Actions permissions) isn't set |
| Publish fails with `OAuthException` / code 190 | The Instagram token expired (it lasts 60 days). Generate a new one (step 3.4) and update the `IG_ACCESS_TOKEN` secret |
| Publish fails with "media could not be fetched" | The repo isn't public |
| Instagram says "rate limit" | Instagram allows 50 API posts per 24 h; you won't hit this normally |
