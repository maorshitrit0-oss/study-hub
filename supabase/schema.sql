-- Study Hub schema. Run once in Supabase: SQL Editor -> New query -> paste -> Run.
-- Every row belongs to a user (user_id) and row-level security keeps users apart.

create extension if not exists pgcrypto;

-- ---------- tables ----------

create table if not exists courses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  name text not null,
  kind text not null default 'course' check (kind in ('course', 'lab', 'project', 'self')),
  year int,                      -- 1..4 (null for self-study)
  semester text,                 -- 'א' / 'ב' / 'קיץ'
  lecturer text,
  ta text,
  exam_type text check (exam_type in ('mcq', 'open', 'mixed', 'none')),
  grade_weights jsonb not null default '[]',   -- [{"name": "בחינה", "weight": 80}, ...]
  notes text,                    -- free text: rules, formula sheet allowed, etc.
  archived boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists lessons (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  kind text not null default 'lecture' check (kind in ('lecture', 'practice', 'lab', 'web', 'other')),
  number int,
  title text,
  source_url text,
  status text not null default 'queued'
    check (status in ('queued', 'processing', 'transcribed', 'ready', 'error')),
  progress text,                 -- human-readable progress line from the worker
  error text,
  chapter_md text,               -- the reading chapter (markdown + LaTeX, images as ![..](slide:N))
  topics jsonb not null default '[]',
  transcript text,
  slide_count int not null default 0,
  author text,                   -- 'gemini' / 'claude'
  read_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists lessons_course on lessons (course_id, created_at);

create table if not exists questions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  lesson_id uuid references lessons on delete cascade,
  topic text,
  question text not null,
  options jsonb not null,        -- ["...", "...", "...", "..."]
  correct int not null,          -- index into options
  explanation text,
  difficulty int default 2,      -- 1 easy .. 3 hard
  created_at timestamptz not null default now()
);
create index if not exists questions_lesson on questions (lesson_id);
create index if not exists questions_course on questions (course_id);

create table if not exists attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  question_id uuid not null references questions on delete cascade,
  course_id uuid not null references courses on delete cascade,
  chosen int not null,
  is_correct boolean not null,
  created_at timestamptz not null default now()
);
create index if not exists attempts_course on attempts (user_id, course_id);

create table if not exists materials (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  title text not null,
  kind text not null default 'other' check (kind in ('syllabus', 'slides', 'past_exam', 'solution', 'lab_guide', 'other')),
  storage_path text not null,
  mime text,
  size_bytes bigint,
  created_at timestamptz not null default now()
);

create table if not exists deadlines (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid references courses on delete set null,
  title text not null,
  kind text not null default 'assignment' check (kind in ('assignment', 'exam', 'quiz', 'lab_report', 'other')),
  due_at timestamptz not null,
  done boolean not null default false,
  notes text,
  external_uid text,             -- set when imported from the Moodle calendar
  created_at timestamptz not null default now(),
  unique (user_id, external_uid)
);

create table if not exists chat_messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  role text not null check (role in ('user', 'model')),
  content text not null,
  image_paths jsonb not null default '[]',
  created_at timestamptz not null default now()
);
create index if not exists chat_course on chat_messages (course_id, created_at);

create table if not exists settings (
  user_id uuid primary key default auth.uid() references auth.users on delete cascade,
  moodle_ics_url text,
  updated_at timestamptz not null default now()
);

-- ---------- row-level security ----------

do $$
declare t text;
begin
  foreach t in array array['courses', 'lessons', 'questions', 'attempts', 'materials', 'deadlines', 'chat_messages', 'settings']
  loop
    execute format('alter table %I enable row level security', t);
    execute format('drop policy if exists own_rows on %I', t);
    execute format('create policy own_rows on %I for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid())', t);
    execute format('grant select, insert, update, delete on table %I to authenticated', t);
    execute format('grant all on table %I to service_role', t);
  end loop;
end $$;

-- ---------- storage: one private bucket, files under <user_id>/... ----------

insert into storage.buckets (id, name, public)
values ('study', 'study', false)
on conflict (id) do nothing;

drop policy if exists study_own_files on storage.objects;
create policy study_own_files on storage.objects for all to authenticated
  using (bucket_id = 'study' and (storage.foldername(name))[1] = auth.uid()::text)
  with check (bucket_id = 'study' and (storage.foldername(name))[1] = auth.uid()::text);


create table if not exists push_subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  endpoint text not null unique,
  p256dh text not null,
  auth text not null,
  created_at timestamptz not null default now()
);
alter table push_subscriptions enable row level security;
drop policy if exists own_rows on push_subscriptions;
create policy own_rows on push_subscriptions for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table push_subscriptions to authenticated;
grant all on table push_subscriptions to service_role;

-- VAPID signing keys, generated by the notification worker on its first run.
-- No policies: only the service role (the worker) can read the private key.
create table if not exists push_config (
  id int primary key default 1 check (id = 1),
  public_key text not null,
  private_key text not null
);
alter table push_config enable row level security;
grant all on table push_config to service_role;

-- The app only ever needs the public key.
create or replace function push_public_key() returns text
language sql stable security definer set search_path = public
as $$ select public_key from push_config where id = 1 $$;
revoke all on function push_public_key() from public;
grant execute on function push_public_key() to authenticated;


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

create table if not exists recording_marks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  slot_id uuid not null references schedule_slots on delete cascade,
  class_date date not null,
  status text not null check (status in ('uploaded', 'none')),
  created_at timestamptz not null default now(),
  unique (slot_id, class_date)
);
alter table recording_marks enable row level security;
drop policy if exists own_rows on recording_marks;
create policy own_rows on recording_marks for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table recording_marks to authenticated;
grant all on table recording_marks to service_role;

alter table lessons add column if not exists source_path text;

alter table courses add column if not exists syllabus_topics jsonb not null default '[]';
alter table lessons add column if not exists syllabus_covered jsonb not null default '[]';
alter table course_facts add column if not exists source text not null default 'auto';
