-- Weekly timetable. Run once in Supabase: SQL Editor -> New query -> paste -> Run.

create table if not exists schedule_slots (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid references courses on delete cascade,
  title text not null,
  kind text not null default 'lecture' check (kind in ('lecture', 'practice', 'lab', 'other')),
  weekday int not null check (weekday between 0 and 6),   -- 0 = Sunday
  start_time time not null,
  end_time time not null,
  room text,
  instructor text,
  created_at timestamptz not null default now()
);
create index if not exists schedule_user on schedule_slots (user_id, weekday, start_time);
alter table schedule_slots enable row level security;
drop policy if exists own_rows on schedule_slots;
create policy own_rows on schedule_slots for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table schedule_slots to authenticated;
grant all on table schedule_slots to service_role;

alter table courses add column if not exists code text;
