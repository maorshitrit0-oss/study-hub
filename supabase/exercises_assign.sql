-- An exercise from a file (homework, past exam, booklet) belongs to ONE lesson: the earliest one after which all it
-- needs has been taught (31/10/2026). Until then it shows only under "all files". Safe to run again.
alter table exercises add column if not exists fits_lesson_id uuid references lessons on delete set null;
alter table exercises add column if not exists duplicate boolean not null default false; -- same as one solved in class
