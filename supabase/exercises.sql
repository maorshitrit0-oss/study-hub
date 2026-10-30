-- Practice instead of reading (30/10/2026): every lesson gives a short summary + the exercises it had (with full
-- solutions, hidden until he has tried); homework and past-exam files give their exercises too. Safe to run again.
alter table lessons add column if not exists summary_md text;

create table if not exists exercises (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  course_id uuid not null references courses on delete cascade,
  lesson_id uuid references lessons on delete cascade,        -- from a lesson (solved in class / given in class)
  material_id uuid references materials on delete set null,   -- from a file (homework, past exam, exercise sheet)
  source text not null default 'lesson' check (source in ('lesson', 'homework', 'exam', 'sheet')),
  ord int not null default 0,
  title text,
  question_md text not null,
  solution_md text,
  topic text,
  exam_style boolean not null default false,  -- the lecturer said it is exam-like, or it is from a past exam
  uncertain boolean not null default false,   -- solution written by Gemini and doubtful: check it
  done_at timestamptz,                        -- he marked it solved
  created_at timestamptz not null default now()
);
create index if not exists exercises_course on exercises (course_id, lesson_id);
alter table exercises enable row level security;
drop policy if exists own_rows on exercises;
create policy own_rows on exercises for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on table exercises to authenticated;
grant all on table exercises to service_role;
do $$ begin
  if to_regprocedure('public.mfa_ok()') is not null then
    drop policy if exists require_mfa on exercises;
    create policy require_mfa on exercises as restrictive for all to authenticated
      using ((select public.mfa_ok())) with check ((select public.mfa_ok()));
  end if;
end $$;
