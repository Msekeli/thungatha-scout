# Scout admin frontend

React + TypeScript + Vite + Tailwind CSS v3 with Supabase Auth sign-in.

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Set the Scout Supabase URL and publishable/anon key in `.env.local`. Never put a service-role key in a `VITE_*` variable. Backend must independently validate access tokens and enforce admin authorization; client-side session checks do not secure API endpoints.
