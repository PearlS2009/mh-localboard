-- Sample of the database setup. Names may differ slightly from the live project.

-- Mountain House Local Board: database setup (Supabase / PostgreSQL)
create table if not exists public.listings (
  id bigint generated always as identity primary key,
  type text,
  title text,
  description text,
  category text,
  contact text,
  is_minor boolean not null default false,
  created_at timestamptz default now(),
  expires_at date not null default (current_date + 60),
  user_id uuid default auth.uid()
);

alter table public.listings enable row level security;

-- Visitors who are not logged in can read active listings
create policy "Public reads active listings"
  on public.listings for select to anon
  using (expires_at >= current_date);

-- Logged-in users can read active listings, plus their own expired ones
create policy "Logged-in read active or own listings"
  on public.listings for select to authenticated
  using (expires_at >= current_date or auth.uid() = user_id);

-- Only logged-in users can post, and only as themselves
create policy "Logged-in users can post"
  on public.listings for insert to authenticated
  with check (auth.uid() = user_id);

-- Only the owner can edit or delete a listing
create policy "Owners can update own listings"
  on public.listings for update to authenticated
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Owners can delete own listings"
  on public.listings for delete to authenticated
  using (auth.uid() = user_id);

-- Logged-out visitors can read every column except contact
revoke all on public.listings from anon;
grant select (id, type, title, description, category, created_at, expires_at, is_minor, user_id)
  on public.listings to anon;
grant select, insert, update, delete on public.listings to authenticated;
