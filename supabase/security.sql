-- Security hardening. Safe to run more than once.
-- Once an authenticator app is turned on for an account, the database itself refuses that account's data
-- unless the session finished the second sign-in step (aal2), even if a password leaks.

create or replace function public.mfa_ok() returns boolean
language sql stable security definer set search_path = ''
as $$
  select coalesce(auth.jwt()->>'aal', '') = 'aal2'
      or not exists (select 1 from auth.mfa_factors f where f.user_id = auth.uid() and f.status = 'verified')
$$;
revoke all on function public.mfa_ok() from public;
grant execute on function public.mfa_ok() to authenticated;

do $$
declare t text;
begin
  foreach t in array array['courses', 'lessons', 'questions', 'attempts', 'materials', 'deadlines', 'chat_messages',
                           'settings', 'push_subscriptions', 'course_facts', 'schedule_slots', 'recording_marks', 'usage_snapshot', 'glossary', 'grades']
  loop
    if to_regclass('public.' || t) is not null then
      execute format('drop policy if exists require_mfa on %I', t);
      execute format('create policy require_mfa on %I as restrictive for all to authenticated using ((select public.mfa_ok())) with check ((select public.mfa_ok()))', t);
    end if;
  end loop;
end $$;

drop policy if exists study_require_mfa on storage.objects;
create policy study_require_mfa on storage.objects as restrictive for all to authenticated
  using ((select public.mfa_ok())) with check ((select public.mfa_ok()));

-- Visitors who are not signed in get nothing, even by mistake in a future table.
revoke all on all tables in schema public from anon;
