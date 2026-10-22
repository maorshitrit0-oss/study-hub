-- "Did you upload the recording?" marks per class meeting. Run once in Supabase SQL Editor.
create table if not exists recording_marks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  slot_id uuid not null references schedule_slots on delete cascade,
  class_date date not null,
  status text not null check (status in ('uploaded', 'none')),
  created_at timestamptz not null default now(),
  unique (slot_id, class_date)
);
alter table recording_marks enable row level security;
drop policy if exists own_rows on recording_marks;
create policy own_rows on recording_marks for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table recording_marks to authenticated;
grant all on table recording_marks to service_role;
