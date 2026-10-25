-- He added מיקרו מעבדים and מבוא למערכות תקשורת to this semester (25/10/2026), moving both out of year 4 semester A.
-- Safe to run again. Nothing is deleted: the two plan rows are moved, courses and exams are added only if missing.
with u as (select id from auth.users order by created_at limit 1)
insert into courses (user_id, name, kind, year, semester, lecturer, exam_type, grade_weights, notes, code)
select u.id, x.name, 'course', 3, 'א', x.lecturer, x.exam_type, x.weights::jsonb, x.notes, x.code
from u, (values
  ('מיקרו מעבדים', 'ד"ר רועי יוזביץ', 'open', '[{"name": "בחינה", "weight": 100}]',
   'ליבה - מחשבים. בחינה סופית 100%, תיאורטית. יש הקלטות ומבחנים קודמים. מבחן 18/01/2027 - שלושה ימים רצופים עם Java (17/1) ולינאריים (19/1): ללמוד כל שבוע.', '002-4371710'),
  ('מבוא למערכות תקשורת', 'פרופ'' יוסף פנחסי', 'open', '[]',
   'תקשורת אנלוגית: AM, SSB, סופרהטרודין, FM/NBFM (טבלת בסל), ספרת רעש ויחס אות לרעש, dB/dBm. דף זהויות טריגונומטריות וטבלת בסל מצורפים לשאלות. חוברת פתורה של ד"ר לוריא. מבחן 02/02/2027.', '002-4330610')
) as x(name, lecturer, exam_type, weights, notes, code)
where not exists (select 1 from courses c where c.user_id = u.id and c.name = x.name);

-- Plan rows: from the rest of the degree (year 4 A) to this year, semester A.
update grades set academic_year = 'תשפ"ז', semester = 'א'
where code in ('002-4371710', '002-4330610') and academic_year = 'יתרת התואר' and grade is null;

with u as (select id from auth.users order by created_at limit 1),
c as (
  select (select id from courses where name = 'מיקרו מעבדים' order by created_at limit 1) as micro,
         (select id from courses where name = 'מבוא למערכות תקשורת' order by created_at limit 1) as comm
)
insert into deadlines (user_id, course_id, title, kind, due_at, check_due, notes, external_uid)
select u.id, x.course_id, x.title, 'exam', x.due_at, false, x.notes, x.uid
from u, c, lateral (values
  (c.micro, 'מיקרו מעבדים - בחינה', timestamptz '2027-01-18 09:00+02', 'השעה לא ידועה - 09:00 זמני, לבדוק.', 'exam-micro-2027-01-18'),
  (c.comm, 'מבוא למערכות תקשורת - בחינה', timestamptz '2027-02-02 09:00+02', 'השעה לא ידועה - 09:00 זמני, לבדוק.', 'exam-comm-2027-02-02')
) as x(course_id, title, due_at, notes, uid)
on conflict (user_id, external_uid) do nothing;
