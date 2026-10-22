-- English terms from each lesson, for the English vocabulary quiz.
create table if not exists glossary (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  lesson_id uuid references lessons on delete cascade,
  en text not null,
  he text not null,
  explanation text,
  created_at timestamptz not null default now()
);
create index if not exists glossary_course on glossary (course_id);
alter table glossary enable row level security;
drop policy if exists own_rows on glossary;
create policy own_rows on glossary for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table glossary to authenticated;
grant all on table glossary to service_role;
-- Same two-step sign-in rule as the other tables (supabase/security.sql).
do $$ begin
  if to_regprocedure('public.mfa_ok()') is not null then
    drop policy if exists require_mfa on glossary;
    create policy require_mfa on glossary as restrictive for all to authenticated
      using ((select public.mfa_ok())) with check ((select public.mfa_ok()));
  end if;
end $$;
