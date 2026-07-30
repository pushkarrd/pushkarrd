# GitHub Profile Setup Guide for @pushkarrd

Follow these quick manual steps to push your new profile live and configure Phase 2 (Self-hosted Stats) and Phase 3 (Contribution Snake).

---

## 1. Create Repository & Push Code

1. Go to [GitHub New Repository](https://github.com/new).
2. Repository name **MUST** be exactly: `pushkarrd` (matching your username `pushkarrd/pushkarrd`).
3. Make it **Public**.
4. Check **Add a README file**? **NO** (keep it unchecked).
5. Click **Create repository**.
6. Open your terminal in this directory (`c:\Users\Pushkar\Documents\Web Peojects\Github profile enhancement`) and run:
   ```bash
   git push -u origin main --force
   ```

---

## 2. Enable GitHub Actions Permissions (For Contribution Snake)

1. Go to your repository settings on GitHub: `https://github.com/pushkarrd/pushkarrd/settings`.
2. On the left sidebar, click **Actions** -> **General**.
3. Scroll down to **Workflow permissions**.
4. Select **Read and write permissions**.
5. Click **Save**.
6. Go to the **Actions** tab on your repository: `https://github.com/pushkarrd/pushkarrd/actions`.
7. Click **Generate Contribution Snake** under workflows, click **Run workflow** -> **Run workflow**.
8. Once it finishes (turns green), the `output` branch will automatically be created and your contribution snake will be visible on your profile!

---

## 3. Self-Host Stats Cards on Vercel (Phase 2)

> [!WARNING]
> **Token Security Warning**: Copy your Classic PAT immediately when generated, and **NEVER** commit it or share it publicly.

1. **Create GitHub Classic Token**:
   - Go to [GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)](https://github.com/settings/tokens).
   - Click **Generate new token (classic)**.
   - Note: `Vercel Stats Card`
   - Expiration: **No expiration**
   - Select scopes: Check `repo` (Full control of private repositories).
   - Click **Generate token**. Copy it immediately!

2. **Fork Stats Repository**:
   - Go to [anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats).
   - Click **Fork** (top right) to create a copy under your account (`pushkarrd/github-readme-stats`).

3. **Deploy to Vercel**:
   - Go to [Vercel](https://vercel.com/) and sign in with GitHub.
   - Click **Add New...** -> **Project**.
   - Import your `github-readme-stats` fork.
   - Under **Environment Variables**:
     - Key: `PAT_1`
     - Value: `[Your GitHub Classic Token]`
   - Click **Deploy**.

4. **Update README.md**:
   - Once deployed, copy your Vercel deployment domain (e.g. `https://github-readme-stats-pushkarrd.vercel.app`).
   - Open `README.md` in your `pushkarrd/pushkarrd` repository and replace `https://github-readme-stats.vercel.app` with your Vercel domain!
