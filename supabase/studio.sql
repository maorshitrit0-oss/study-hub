-- Studio: podcasts, videos and everyday examples made from lesson chapters (worker/studio.py). Safe to run again.
create table if not exists lesson_media (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  lesson_ids uuid[] not null,
  kind text not null check (kind in ('podcast', 'video', 'examples')),
  title text,
  status text not null default 'queued' check (status in ('queued', 'processing', 'ready', 'error')),
  progress text,
  error text,
  storage_path text,
  script text,
  duration_sec int,
  created_at timestamptz not null default now()
);
create index if not exists lesson_media_course on lesson_media (course_id, created_at);
alter table lesson_media enable row level security;
drop policy if exists own_rows on lesson_media;
create policy own_rows on lesson_media for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table lesson_media to authenticated;
grant all on table lesson_media to service_role;
do $$ begin
  if to_regprocedure('public.mfa_ok()') is not null then
    drop policy if exists require_mfa on lesson_media;
    create policy require_mfa on lesson_media as restrictive for all to authenticated
      using ((select public.mfa_ok())) with check ((select public.mfa_ok()));
  end if;
end $$;
