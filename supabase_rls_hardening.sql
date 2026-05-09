-- Public read, authenticated write policy template for the RP5 dashboard.
-- Review carefully before applying in production.

begin;

-- Public read, authenticated write for main content tables
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
drop policy if exists "authenticated write games" on public.games;
create policy "authenticated write games" on public.games for all to authenticated using (true) with check (true);

drop policy if exists "public read game_platforms" on public.game_platforms;
create policy "public read game_platforms" on public.game_platforms for select using (true);
drop policy if exists "authenticated write game_platforms" on public.game_platforms;
create policy "authenticated write game_platforms" on public.game_platforms for all to authenticated using (true) with check (true);

drop policy if exists "public read game_genres" on public.game_genres;
create policy "public read game_genres" on public.game_genres for select using (true);
drop policy if exists "authenticated write game_genres" on public.game_genres;
create policy "authenticated write game_genres" on public.game_genres for all to authenticated using (true) with check (true);

drop policy if exists "public read notes" on public.notes;
create policy "public read notes" on public.notes for select using (true);
drop policy if exists "authenticated write notes" on public.notes;
create policy "authenticated write notes" on public.notes for all to authenticated using (true) with check (true);

drop policy if exists "public read glossary" on public.glossary;
create policy "public read glossary" on public.glossary for select using (true);
drop policy if exists "authenticated write glossary" on public.glossary;
create policy "authenticated write glossary" on public.glossary for all to authenticated using (true) with check (true);

drop policy if exists "public read series" on public.series;
create policy "public read series" on public.series for select using (true);
drop policy if exists "authenticated write series" on public.series;
create policy "authenticated write series" on public.series for all to authenticated using (true) with check (true);

drop policy if exists "public read genres" on public.genres;
create policy "public read genres" on public.genres for select using (true);
drop policy if exists "authenticated write genres" on public.genres;
create policy "authenticated write genres" on public.genres for all to authenticated using (true) with check (true);

drop policy if exists "public read systems" on public.systems;
create policy "public read systems" on public.systems for select using (true);
drop policy if exists "authenticated write systems" on public.systems;
create policy "authenticated write systems" on public.systems for all to authenticated using (true) with check (true);

drop policy if exists "public read emulators" on public.emulators;
create policy "public read emulators" on public.emulators for select using (true);
drop policy if exists "authenticated write emulators" on public.emulators;
create policy "authenticated write emulators" on public.emulators for all to authenticated using (true) with check (true);

drop policy if exists "public read emulator_systems" on public.emulator_systems;
create policy "public read emulator_systems" on public.emulator_systems for select using (true);
drop policy if exists "authenticated write emulator_systems" on public.emulator_systems;
create policy "authenticated write emulator_systems" on public.emulator_systems for all to authenticated using (true) with check (true);

commit;
