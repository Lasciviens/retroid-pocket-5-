-- Minimal RLS hardening for the RP5 dashboard.
-- Goal:
--   - anonymous visitors can keep reading the public site
--   - authenticated users can write through the existing admin flows
-- Notes:
--   - this is intentionally small and conservative
--   - service_role still bypasses RLS, which is expected for trusted server-side work
--   - apply in Supabase SQL Editor

begin;

-- Public read, authenticated write for the main content tables
alter table public.games enable row level security;
alter table public.game_platforms enable row level security;
alter table public.game_genres enable row level security;
alter table public.notes enable row level security;
alter table public.glossary enable row level security;
alter table public.series enable row level security;
alter table public.genres enable row level security;
alter table public.systems enable row level security;
alter table public.emulators enable row level security;
alter table public.emulator_systems enable row level security;

drop policy if exists "public read games" on public.games;
create policy "public read games" on public.games for select using (true);
drop policy if exists "authenticated insert games" on public.games;
create policy "authenticated insert games" on public.games for insert to authenticated with check (true);
drop policy if exists "authenticated update games" on public.games;
create policy "authenticated update games" on public.games for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete games" on public.games;
create policy "authenticated delete games" on public.games for delete to authenticated using (true);
drop policy if exists "authenticated write games" on public.games;

drop policy if exists "public read game_platforms" on public.game_platforms;
create policy "public read game_platforms" on public.game_platforms for select using (true);
drop policy if exists "authenticated insert game_platforms" on public.game_platforms;
create policy "authenticated insert game_platforms" on public.game_platforms for insert to authenticated with check (true);
drop policy if exists "authenticated update game_platforms" on public.game_platforms;
create policy "authenticated update game_platforms" on public.game_platforms for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete game_platforms" on public.game_platforms;
create policy "authenticated delete game_platforms" on public.game_platforms for delete to authenticated using (true);
drop policy if exists "authenticated write game_platforms" on public.game_platforms;

drop policy if exists "public read game_genres" on public.game_genres;
create policy "public read game_genres" on public.game_genres for select using (true);
drop policy if exists "authenticated insert game_genres" on public.game_genres;
create policy "authenticated insert game_genres" on public.game_genres for insert to authenticated with check (true);
drop policy if exists "authenticated update game_genres" on public.game_genres;
create policy "authenticated update game_genres" on public.game_genres for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete game_genres" on public.game_genres;
create policy "authenticated delete game_genres" on public.game_genres for delete to authenticated using (true);
drop policy if exists "authenticated write game_genres" on public.game_genres;

drop policy if exists "public read notes" on public.notes;
create policy "public read notes" on public.notes for select using (true);
drop policy if exists "authenticated insert notes" on public.notes;
create policy "authenticated insert notes" on public.notes for insert to authenticated with check (true);
drop policy if exists "authenticated update notes" on public.notes;
create policy "authenticated update notes" on public.notes for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete notes" on public.notes;
create policy "authenticated delete notes" on public.notes for delete to authenticated using (true);
drop policy if exists "authenticated write notes" on public.notes;

drop policy if exists "public read glossary" on public.glossary;
create policy "public read glossary" on public.glossary for select using (true);
drop policy if exists "authenticated insert glossary" on public.glossary;
create policy "authenticated insert glossary" on public.glossary for insert to authenticated with check (true);
drop policy if exists "authenticated update glossary" on public.glossary;
create policy "authenticated update glossary" on public.glossary for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete glossary" on public.glossary;
create policy "authenticated delete glossary" on public.glossary for delete to authenticated using (true);
drop policy if exists "authenticated write glossary" on public.glossary;

drop policy if exists "public read series" on public.series;
create policy "public read series" on public.series for select using (true);
drop policy if exists "authenticated insert series" on public.series;
create policy "authenticated insert series" on public.series for insert to authenticated with check (true);
drop policy if exists "authenticated update series" on public.series;
create policy "authenticated update series" on public.series for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete series" on public.series;
create policy "authenticated delete series" on public.series for delete to authenticated using (true);
drop policy if exists "authenticated write series" on public.series;

drop policy if exists "public read genres" on public.genres;
create policy "public read genres" on public.genres for select using (true);
drop policy if exists "authenticated insert genres" on public.genres;
create policy "authenticated insert genres" on public.genres for insert to authenticated with check (true);
drop policy if exists "authenticated update genres" on public.genres;
create policy "authenticated update genres" on public.genres for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete genres" on public.genres;
create policy "authenticated delete genres" on public.genres for delete to authenticated using (true);
drop policy if exists "authenticated write genres" on public.genres;

drop policy if exists "public read systems" on public.systems;
create policy "public read systems" on public.systems for select using (true);
drop policy if exists "authenticated insert systems" on public.systems;
create policy "authenticated insert systems" on public.systems for insert to authenticated with check (true);
drop policy if exists "authenticated update systems" on public.systems;
create policy "authenticated update systems" on public.systems for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete systems" on public.systems;
create policy "authenticated delete systems" on public.systems for delete to authenticated using (true);
drop policy if exists "authenticated write systems" on public.systems;

drop policy if exists "public read emulators" on public.emulators;
create policy "public read emulators" on public.emulators for select using (true);
drop policy if exists "authenticated insert emulators" on public.emulators;
create policy "authenticated insert emulators" on public.emulators for insert to authenticated with check (true);
drop policy if exists "authenticated update emulators" on public.emulators;
create policy "authenticated update emulators" on public.emulators for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete emulators" on public.emulators;
create policy "authenticated delete emulators" on public.emulators for delete to authenticated using (true);
drop policy if exists "authenticated write emulators" on public.emulators;

drop policy if exists "public read emulator_systems" on public.emulator_systems;
create policy "public read emulator_systems" on public.emulator_systems for select using (true);
drop policy if exists "authenticated insert emulator_systems" on public.emulator_systems;
create policy "authenticated insert emulator_systems" on public.emulator_systems for insert to authenticated with check (true);
drop policy if exists "authenticated update emulator_systems" on public.emulator_systems;
create policy "authenticated update emulator_systems" on public.emulator_systems for update to authenticated using (true) with check (true);
drop policy if exists "authenticated delete emulator_systems" on public.emulator_systems;
create policy "authenticated delete emulator_systems" on public.emulator_systems for delete to authenticated using (true);
drop policy if exists "authenticated write emulator_systems" on public.emulator_systems;

commit;
