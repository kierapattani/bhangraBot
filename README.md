# BhangraBot

A web app for scheduling GroupMe messages from your personal account. Built with Vue 3 and FastAPI, with Google OAuth for access control.

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+

### Setup

1. Install Python dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Create a `.env` file in the project root:
   ```env
   ACCESS_TOKEN=your_groupme_access_token
   GROUP_ID=your_groupme_group_id

   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback

   JWT_SECRET_KEY=any_random_string_for_dev
   JWT_EXPIRATION_HOURS=24

   ALLOWED_EMAILS=your_email@gmail.com

   FRONTEND_URL=http://localhost:5173
   ENVIRONMENT=development
   ```

4. Start the backend:
   ```bash
   uvicorn backend.main:app --reload
   ```

5. Start the frontend dev server:
   ```bash
   cd frontend
   npm run dev
   ```

Visit `http://localhost:5173` to use the app.

