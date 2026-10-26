-- Lab entry quizzes (בוחן כניסה): questions classmates reported after their lab session, and questions read from
-- course files. Each report becomes multiple-choice questions (questions.source) for the experiment's practice.
-- Safe to run again.
create table if not exists entry_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  experiment int,                         -- null when read from a file holding several quizzes
  text text,
  image_paths jsonb not null default '[]',
  material_id uuid references materials on delete set null,   -- set when read from a course file
  status text not null default 'new' check (status in ('new', 'done', 'error')),
  error text,
  created_at timestamptz not null default now()
);
create index if not exists entry_reports_course on entry_reports (course_id);
alter table entry_reports enable row level security;
drop policy if exists own_rows on entry_reports;
create policy own_rows on entry_reports for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table entry_reports to authenticated;
grant all on table entry_reports to service_role;
do $$ begin
  if to_regprocedure('public.mfa_ok()') is not null then
    drop policy if exists require_mfa on entry_reports;
    create policy require_mfa on entry_reports as restrictive for all to authenticated
      using ((select public.mfa_ok())) with check ((select public.mfa_ok()));
  end if;
end $$;

-- null = a chapter's quiz; 'entry_reported' = a question someone was actually asked; 'entry_practice' = a similar one.
alter table questions add column if not exists source text;
alter table questions add column if not exists experiment int;
create index if not exists questions_entry on questions (course_id, experiment) where source is not null;
