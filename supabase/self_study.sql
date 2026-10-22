-- Self-study roadmap: topics and project steps with his 4-level scale (0 = not started).
create table if not exists skills (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  kind text not null default 'topic' check (kind in ('topic', 'project')),
  ord int not null default 0,
  title text not null,
  level int not null default 0 check (level between 0 and 4),
  notes text,
  updated_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);
create index if not exists skills_course on skills (course_id, kind, ord);
alter table skills enable row level security;
drop policy if exists own_rows on skills;
create policy own_rows on skills for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table skills to authenticated;
grant all on table skills to service_role;
do $$ begin
  if to_regprocedure('public.mfa_ok()') is not null then
    drop policy if exists require_mfa on skills;
    create policy require_mfa on skills as restrictive for all to authenticated
      using ((select public.mfa_ok())) with check ((select public.mfa_ok()));
  end if;
end $$;
