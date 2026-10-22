-- Usage monitoring + the "previous report" file type. Run once in Supabase: SQL Editor -> New query -> Run.

-- Totals for the free-plan limits (1 GB files, 500 MB database).
create or replace function usage_stats() returns json
language sql stable security definer set search_path = public, storage
as $$
  select json_build_object(
    'storage_bytes', (select coalesce(sum((metadata->>'size')::bigint), 0) from storage.objects),
    'db_bytes', pg_database_size(current_database())
  )
$$;
revoke all on function usage_stats() from public;
grant execute on function usage_stats() to authenticated, service_role;

-- Latest usage check, written daily by the notification worker and shown in the app.
create table if not exists usage_snapshot (
  id int primary key default 1 check (id = 1),
  data jsonb not null,
  updated_at timestamptz not null default now()
);
alter table usage_snapshot enable row level security;
drop policy if exists read_usage on usage_snapshot;
create policy read_usage on usage_snapshot for select to authenticated using (true);
grant select on table usage_snapshot to authenticated;
grant all on table usage_snapshot to service_role;

-- Summary reports from earlier lab partners, used as a base for new reports.
alter table materials drop constraint if exists materials_kind_check;
alter table materials add constraint materials_kind_check
  check (kind in ('syllabus', 'slides', 'past_exam', 'solution', 'lab_guide', 'prev_report', 'other'));
