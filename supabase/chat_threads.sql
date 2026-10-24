-- Several chats per course (each with its own history), switchable in the course chat. Safe to run again.
create table if not exists chat_threads (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  title text not null,
  created_at timestamptz not null default now()
);
create index if not exists chat_threads_course on chat_threads (course_id, created_at);
alter table chat_threads enable row level security;
drop policy if exists own_rows on chat_threads;
create policy own_rows on chat_threads for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table chat_threads to authenticated;
grant all on table chat_threads to service_role;
do $$ begin
  if to_regprocedure('public.mfa_ok()') is not null then
    drop policy if exists require_mfa on chat_threads;
    create policy require_mfa on chat_threads as restrictive for all to authenticated
      using ((select public.mfa_ok())) with check ((select public.mfa_ok()));
  end if;
end $$;
-- Messages without a thread belong to the course's first ("main") chat.
alter table chat_messages add column if not exists thread_id uuid references chat_threads on delete cascade;
create index if not exists chat_messages_thread on chat_messages (thread_id, created_at);
