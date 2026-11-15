# Scout admin frontend

React + TypeScript + Vite + Tailwind CSS v3 with Supabase Auth sign-in.

## Local setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Configure these values in `.env.local` using the dedicated Scout Supabase project:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY` (or the project's publishable key)
- `VITE_SCOUT_API_URL`

In Supabase Auth, enable email/password sign-in and disable public sign-ups. Create or invite only the configured administrator account from the Supabase dashboard. The account email must match the backend's `SCOUT_ADMIN_EMAIL`.

Configure the backend separately:

- `SCOUT_SUPABASE_URL`
- `SCOUT_SUPABASE_PUBLISHABLE_KEY`
- `SCOUT_ADMIN_EMAIL`

The browser receives only the Supabase URL and publishable/anon key. Never put a service-role key in a `VITE_*` variable. FastAPI independently verifies every administrator access token and checks the server-side email allowlist. The health endpoint remains public; the Thungatha server-to-server vacancy export keeps its separate export-key authentication.
