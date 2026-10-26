-- His full timetable for semester א תשפ"ז (university system screenshots, 26/10/2026) + exam dates he did not have yet.
-- Adds only what is missing: a slot is skipped when the course already has one of that kind on that day; exams by uid.
with u as (select id from auth.users order by created_at limit 1),
c as (
  select
    (select id from courses where name like 'גלים%' and kind <> 'lab' order by created_at limit 1) as waves,
    (select id from courses where name = 'מבוא למערכות תקשורת' order by created_at limit 1) as comm,
    (select id from courses where name like 'מעבדה 2%' order by created_at limit 1) as lab2,
    (select id from courses where (name ilike '%digital%' or name like '%ספרתיים%') order by created_at limit 1) as digital,
    (select id from courses where name ilike '%java%' order by created_at limit 1) as java,
    (select id from courses where name = 'מיקרו מעבדים' order by created_at limit 1) as micro,
    (select id from courses where (name like '%לינאר%' or name like '%ליניאר%') and kind <> 'lab' order by created_at limit 1) as linear
)
insert into schedule_slots (user_id, course_id, title, kind, weekday, start_time, end_time, room, instructor)
select u.id, x.course_id, x.title, x.kind, x.weekday, x.s::time, x.e::time, x.room, x.who
from u, c, lateral (values
  (c.waves,   'גלים ומערכות מפולגות', 'lecture', 0, '17:00', '21:00', '01.2.02', 'ד"ר רוזבן דניאל'),
  (c.waves,   'גלים ומערכות מפולגות - תרגיל', 'practice', 0, '21:00', '22:00', '01.2.02', 'מר פוליאקוב רוני'),
  (c.comm,    'מבוא למערכות תקשורת', 'lecture', 1, '09:00', '12:00', '52-1.12', 'מר אברהם יהונתן'),
  (c.comm,    'מבוא למערכות תקשורת - תרגיל', 'practice', 1, '13:00', '14:00', '56.3.10', 'מר אליאס חנן'),
  (c.lab2,    'מעבדה 2', 'lab', 2, '09:00', '13:00', '01.1.11', 'מר בלישה תומר, גב'' מנדלברוט טליה'),
  (c.digital, 'מעגלים ספרתיים', 'lecture', 2, '13:00', '16:00', '52-1.04', 'ד"ר עופר נתנאל'),
  (c.digital, 'מעגלים ספרתיים - תרגיל', 'practice', 2, '16:00', '17:00', '51.1.51', 'מר רסולי מתן'),
  (c.java,    'Java', 'lecture', 3, '13:00', '16:00', '55.1.33', 'פרופ'' רצאבי יואל'),
  (c.java,    'Java - תרגיל', 'practice', 3, '16:00', '17:00', '53.1.55 אודיטוריום', 'מר אברהם אלון'),
  (c.micro,   'מיקרו מעבדים', 'lecture', 3, '17:00', '20:00', '52-1.12', 'ד"ר יוזביץ רועי'),
  (c.micro,   'מיקרו מעבדים - תרגיל', 'practice', 3, '21:00', '22:00', '20.2.10', 'מר בראון ליאור'),
  (c.linear,  'מעגלים לינאריים', 'lecture', 4, '09:00', '13:00', '01.2.01', 'פרופ'' גולן גדי'),
  (c.linear,  'מעגלים לינאריים - תרגיל', 'practice', 4, '16:00', '17:00', '51.3.07', 'גב'' פרלמן הודיה')
) as x(course_id, title, kind, weekday, s, e, room, who)
where x.course_id is not null
  and not exists (select 1 from schedule_slots s where s.course_id = x.course_id and s.weekday = x.weekday and s.kind = x.kind);

-- This semester the communication lectures are given by Mr. Avraham Yehonatan (the material is Prof. Pinhasi's).
update courses set lecturer = 'מר אברהם יהונתן (החומר: פרופ'' יוסף פנחסי)' where name = 'מבוא למערכות תקשורת';

-- Exam dates from the university system that were not in the app yet (times unknown: 09:00 placeholder).
with u as (select id from auth.users order by created_at limit 1),
c as (
  select (select id from courses where name = 'מיקרו מעבדים' order by created_at limit 1) as micro,
         (select id from courses where name = 'מבוא למערכות תקשורת' order by created_at limit 1) as comm
)
insert into deadlines (user_id, course_id, title, kind, due_at, check_due, notes, external_uid)
select u.id, x.course_id, x.title, 'exam', x.due_at, false, 'ממערכת האוניברסיטה. השעה לא ידועה - 09:00 זמני.', x.uid
from u, c, lateral (values
  (c.micro, 'מיקרו מעבדים - מועד ב', timestamptz '2027-02-17 09:00+02', 'exam-micro-2027-02-17'),
  (c.comm, 'מבוא למערכות תקשורת - מועד ב', timestamptz '2027-02-24 09:00+02', 'exam-comm-2027-02-24'),
  (null::uuid, 'מבוא לבקרה - מועד א', timestamptz '2027-06-27 09:00+03', 'exam-control-2027-06-27'),
  (null::uuid, 'פיזיקה של מל"מ - מועד א', timestamptz '2027-07-08 09:00+03', 'exam-semiphys-2027-07-08'),
  (null::uuid, 'תורת החשמל ואלקטרומגנטיקה - מועד א', timestamptz '2027-07-11 09:00+03', 'exam-em-2027-07-11'),
  (null::uuid, 'מבוא לבקרה - מועד ב', timestamptz '2027-07-21 09:00+03', 'exam-control-2027-07-21'),
  (null::uuid, 'פיזיקה של מל"מ - מועד ב', timestamptz '2027-07-27 09:00+03', 'exam-semiphys-2027-07-27'),
  (null::uuid, 'תורת החשמל ואלקטרומגנטיקה - מועד ב', timestamptz '2027-08-01 09:00+03', 'exam-em-2027-08-01')
) as x(course_id, title, due_at, uid)
on conflict (user_id, external_uid) do nothing;
