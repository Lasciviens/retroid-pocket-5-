# Supabase RLS Apply

This project's minimal RLS pass is prepared in:

- `supabase_rls_hardening.sql`

## Goal

- guest visitors keep read-only access
- signed-in users keep the current write flows

## Apply

1. Open Supabase Dashboard
2. Open `SQL Editor`
3. Paste `supabase_rls_hardening.sql`
4. Run the query

## Verify

1. Open the public site in a fresh browser session
2. Confirm guest browsing still works without login
3. Try a write action while logged out:
   - queue add
   - tips add
   - request add
4. Confirm the UI asks for login
5. Log in and retry one write action
6. Confirm the change succeeds

## Scope

This pass is intentionally small:

- public `select`
- authenticated `insert/update/delete`

It does not introduce custom per-user ownership rules or a separate admin role model.
