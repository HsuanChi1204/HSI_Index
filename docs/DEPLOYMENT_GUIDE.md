# Deployment Guide

Since `localhost` is only accessible on your own machine, you need to expose your API to the internet so other developers can access it.

## Option 1: Temporary Sharing (Fastest for Dev)
Use **ngrok** to create a secure tunnel to your localhost. This is great for quick testing with your team.

1.  **Install ngrok:**
    ```bash
    brew install ngrok/ngrok/ngrok
    ```
2.  **Start your backend:**
    ```bash
    python3 main.py
    ```
3.  **Start ngrok (in a new terminal):**
    ```bash
    ngrok http 8000
    ```
4.  **Share the URL:**
    ngrok will give you a URL like `https://a1b2-c3d4.ngrok-free.app`.
    Give this URL to your frontend developer. They will use:
    `https://a1b2-c3d4.ngrok-free.app/api/chat`

---

## Option 2: Cloud Deployment (Recommended for Production)
Deploy your backend to a cloud provider for a permanent URL.

### Recommended: Render (Free Tier Available)

**Step 1: Prepare your Code**
1.  I have already generated `requirements.txt` for you in the root folder.
2.  **Push your code to GitHub.** (You need to do this manually).
    ```bash
    git add .
    git commit -m "Ready for deployment"
    git push origin main
    ```

**Step 2: Create Service on Render**
1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository.

**Step 3: Configure Settings**
Fill in these exact values:
| Setting | Value |
| :--- | :--- |
| **Name** | `dc-crime-chatbot` (or anything you like) |
| **Region** | `Oregon (US West)` (or closest to you) |
| **Branch** | `main` |
| **Root Directory** | `.` (Leave empty or dot) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |

> **Note on Start Command:** Since your `main.py` is inside the `backend` folder, we use `backend.main:app`.

**Step 4: Environment Variables**
Scroll down to "Environment Variables" and add these keys (copy from your `.env` file):
1.  `SUPABASE_URL`: (Your Supabase URL)
2.  `SUPABASE_KEY`: (Your Supabase Key)
3.  `GEMINI_API_KEY`: (Your Gemini API Key)

**Step 5: Deploy**
Click **Create Web Service**. Render will start building. It usually takes 2-3 minutes.
Once done, you will get a URL like `https://dc-crime-chatbot.onrender.com`.

**Step 6: Share**
Give this URL to your frontend developer. They should use:
`https://dc-crime-chatbot.onrender.com/api/chat`


### Alternative: Railway (railway.app)
Similar to Render, very easy to set up.
1.  Connect GitHub.
2.  Add variables.
3.  Railway automatically detects `requirements.txt` and `Procfile` (if present).

### Important: Requirements File
Make sure you have a `requirements.txt` file in your root directory.
Generate it with:
```bash
pip freeze > requirements.txt
```
