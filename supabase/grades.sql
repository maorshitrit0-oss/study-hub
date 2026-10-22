-- Grade sheet (גיליון ציונים) for the whole degree, and tasks without a submission date.

create table if not exists grades (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  academic_year text not null,   -- 'תשפ"ה'
  semester text not null,        -- 'א' / 'ב' / 'ק'
  code text,
  name text not null,
  kind text,
  lecturer text,
  credits numeric not null default 0,
  grade text,                    -- number, 'עבר', or null while not given
  failed boolean not null default false,
  created_at timestamptz not null default now(),
  unique (user_id, code, academic_year, semester)
);
alter table grades enable row level security;
drop policy if exists own_rows on grades;
create policy own_rows on grades for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table grades to authenticated;
grant all on table grades to service_role;
do $$ begin
  if to_regprocedure('public.mfa_ok()') is not null then
    drop policy if exists require_mfa on grades;
    create policy require_mfa on grades as restrictive for all to authenticated
      using ((select public.mfa_ok())) with check ((select public.mfa_ok()));
  end if;
end $$;

-- No submission date published yet: the app and the push notifications remind to check.
alter table deadlines add column if not exists check_due boolean not null default false;
