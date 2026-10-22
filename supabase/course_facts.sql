-- Course info extracted from lectures (exam, grading, reservist rules...) + reservist flag.
-- Run once in Supabase: SQL Editor -> New query -> paste -> Run.

create table if not exists course_facts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  lesson_id uuid references lessons on delete cascade,
  category text not null default 'other',
  text text not null,
  created_at timestamptz not null default now()
);
create index if not exists course_facts_course on course_facts (course_id);
alter table course_facts enable row level security;
drop policy if exists own_rows on course_facts;
create policy own_rows on course_facts for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table course_facts to authenticated;
grant all on table course_facts to service_role;

alter table settings add column if not exists is_reservist boolean not null default false;
