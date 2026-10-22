-- Syllabus topics per course, which of them each lesson covered, and where each course fact came from.
-- Run once in Supabase: SQL Editor -> New query -> paste -> Run.
alter table courses add column if not exists syllabus_topics jsonb not null default '[]';
alter table lessons add column if not exists syllabus_covered jsonb not null default '[]';
alter table course_facts add column if not exists source text not null default 'auto';
