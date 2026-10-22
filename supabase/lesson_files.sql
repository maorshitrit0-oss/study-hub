-- Lessons made from an uploaded file (lab booklet / prelab PDF). Run once in Supabase SQL Editor.
alter table lessons add column if not exists source_path text;
