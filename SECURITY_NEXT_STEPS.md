# Security Next Steps

## Current State

- Public pages are readable without login.
- Admin pages now require a remembered Supabase session in the browser.
- Write actions in public-facing pages prompt for login before sending writes.

This is good UX, but it is not the final server-side protection by itself.

## What Still Needs To Be Done

Apply RLS (Row Level Security -- row-based access control) so that:

- anonymous users can read
- authenticated users can write

That change must be applied in Supabase SQL editor or migration flow.
For this project, the ready-to-run script is `supabase_rls_hardening.sql`.

## Recommended Auth Setup

Create one admin user in Supabase Auth:

1. Supabase Dashboard
2. Authentication
3. Users
4. Create user
5. Use your own email + password

The frontend session is persisted by Supabase Auth, so the browser should remember you until you sign out or the session expires.

## SQL Template

Use the SQL in `supabase_rls_hardening.sql` as the starting point.
