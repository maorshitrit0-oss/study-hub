-- His grade sheet as of 07/10/2026 (from the university PDF). Safe to run again.
insert into grades (user_id, academic_year, semester, code, name, kind, lecturer, credits, grade, failed)
select (select id from auth.users order by created_at limit 1), v.*
from (values
  ('תשפ"ה', 'א', '002-4310110', 'אלגברה ליניארית', 'הרצאה', 'ד"ר אשכנזי יהודה', 3.5, '73', false),
  ('תשפ"ה', 'א', '002-4310410', 'חשבון אינפיניטסימלי 1', 'הרצאה', 'פרופ'' עשוש פרנק', 5, '90', false),
  ('תשפ"ה', 'א', '002-4311310', 'פיזיקה 1-מכניקה', 'הרצאה', 'פרופ'' גפט מיכאל', 3.5, '94', false),
  ('תשפ"ה', 'א', '002-4311810', 'מערכות ספרתיות', 'הרצאה', 'פרופ'' גולן גדי', 5, '87', false),
  ('תשפ"ה', 'א', '002-4311910', 'מבוא לתכנות', 'הרצאה', 'גב'' קוזנצוב ליובוב', 3, '100', false),
  ('תשפ"ה', 'א', '5500310-04', 'אנגלית-בסיסי', 'אנגלית', 'פאר הרצל', 0, '48', true),
  ('תשפ"ה', 'ב', '002-4310610', 'חשבון אינפיניטסימלי 2', 'הרצאה', 'מר סגל רן', 5, '95', false),
  ('תשפ"ה', 'ב', '002-4312010', 'משוואות דיפרנציאליות רגילות', 'הרצאה', 'גב'' ידוובי ילנה', 3.5, '90', false),
  ('תשפ"ה', 'ב', '002-4312110', 'אנליזה מתקדמת פורייה ולפלאס', 'הרצאה', 'פרופ'' לוריא יורי', 3.5, 'עבר', false),
  ('תשפ"ה', 'ב', '002-4312210', 'מבנה מחשבים', 'הרצאה', 'ד"ר יזוביץ רועי', 3.5, '100', false),
  ('תשפ"ה', 'ב', '5502600-24', 'אנגלית- בסיסי ייחודי מקוון', 'אנגלית', 'גב'' חמד קוטקה קרן', 0, '79', false),
  ('תשפ"ה', 'ק', '5502800-27', 'אנגלית מתקדמים ב'' ייחודי מזורז מקוון', 'אנגלית', 'ד"ר לור יעל', 0, '100', false),
  ('תשפ"ה', 'ק', '5505300-27', 'אנגלית מתקדמים א'' ייחודי מזורז מקוון', 'אנגלית', 'ד"ר לור יעל', 0, '84', false),
  ('תשפ"ו', 'א', '002-4320610', 'הסתברות וסטטיסטיקה', 'הרצאה', 'ד"ר הירשברג אליעזר', 3.5, '100', false),
  ('תשפ"ו', 'א', '002-4321010', 'משוואות דיפרנציאליות חלקיות', 'הרצאה', 'ד"ר ווליניסקי אירינה', 2.5, 'עבר', false),
  ('תשפ"ו', 'א', '002-4321710', 'אותות ומערכות', 'הרצאה', 'פרופ'' לוריא יורי', 3.5, '78', false),
  ('תשפ"ו', 'א', '002-4321910', 'גלים ופיזיקה מודרנית', 'הרצאה', 'ד"ר טלקר אלירן', 4.5, '72', false),
  ('תשפ"ו', 'א', '002-4322010', 'מבוא להנדסת חשמל', 'הרצאה', 'ד"ר ששונקר מוריה', 5, '92', false),
  ('תשפ"ו', 'א', '002-4322210', 'התקני מל"מ', 'הרצאה', 'פרופ'' שחם שמואל', 4.5, '60', false),
  ('תשפ"ו', 'ב', '002-4311110', 'פיזיקה 2-חשמל', 'הרצאה', 'ד"ר אור גלעד, פרופ'' בן ישי פול, מר שיף יוסף כרם', 3.5, '67', false),
  ('תשפ"ו', 'ב', '002-4321210', 'שדות אל"מ', 'הרצאה', 'ד"ר טלקר אלירן', 4, '78', false),
  ('תשפ"ו', 'ב', '002-4321430', 'מעבדה 1', 'מעבדה', 'מר אזולאי יהודה', 2, '82', false),
  ('תשפ"ו', 'ב', '002-4322310', 'מבוא לבקרה', 'הרצאה', 'ד"ר ששונקר מוריה', 4.5, null, false),
  ('תשפ"ו', 'ב', '002-4322410', 'עיבוד אותות', 'הרצאה', 'ד"ר עופר נתנאל', 4.5, '100', false),
  ('תשפ"ו', 'ב', '002-4322510', 'תורת החשמל ואלקטרומגנטיקה', 'הרצאה', 'ד"ר אהרן אילן', 3.5, '26', true),
  ('תשפ"ו', 'ק', '002-4322110', 'אותות אקראיים ורעש', 'הרצאה', 'גב'' הלוי הודיה טובה', 4.5, null, false),
  ('תשפ"ו', 'ק', '002-4920310', 'Technical communication in English for engineers (אנגלית)', 'הרצאה', 'ד"ר לוי אורי ניסים', 3, '84', false)
) as v(academic_year, semester, code, name, kind, lecturer, credits, grade, failed)
on conflict (user_id, code, academic_year, semester) do update
  set grade = excluded.grade, failed = excluded.failed, credits = excluded.credits;

-- Tasks from the Moodle screenshots (22/10/2026) and dates from the university site. Safe to run again.
with u as (select id from auth.users order by created_at limit 1),
c as (
  select
    (select id from courses where name ilike '%java%' order by created_at limit 1) as java,
    (select id from courses where name like '%ליניאר%' and kind <> 'lab' order by created_at limit 1) as linear,
    (select id from courses where name like '%אותות אקראיים%' order by created_at limit 1) as noise
)
insert into deadlines (user_id, course_id, title, kind, due_at, check_due, notes, external_uid)
select u.id, x.course_id, x.title, x.kind, x.due_at, x.check_due, x.notes, x.uid
from u, c, lateral (values
  (c.java, 'מטלה 1', 'assignment', now() + interval '120 days', true, 'נפתחה במודל 21/10/2026. אין מועד סגירה - לבדוק.', 'moodle-shot-java-1'),
  (c.java, 'מטלה 2', 'assignment', now() + interval '120 days', true, 'נפתחת 14/12/2026 19:14. במודל כתוב שנסגרת 30/06/2027 - כנראה לא המועד האמיתי, לבדוק.', 'moodle-shot-java-2'),
  (c.java, 'מטלה 3', 'assignment', now() + interval '120 days', true, 'נפתחת 24/12/2026 19:14. במודל כתוב שנסגרת 30/06/2027 - כנראה לא המועד האמיתי, לבדוק.', 'moodle-shot-java-3'),
  (c.java, 'מטלה 4', 'assignment', timestamptz '2027-02-09 19:13+02', false, 'נפתחת 12/01/2027 19:14 (תרגול 9).', 'moodle-shot-java-4'),
  (c.java, 'מטלה 5', 'assignment', timestamptz '2027-02-09 19:13+02', false, 'נפתחת 19/01/2027 19:14 (תרגול 10).', 'moodle-shot-java-5'),
  (c.linear, 'מטלה 1 (תרגיל בית 1)', 'assignment', now() + interval '120 days', true, 'נפתחה במודל 21/10/2026. תאריך הסגירה בצילום לא קריא - לבדוק במודל.', 'moodle-shot-linear-1'),
  (c.linear, 'מטלה 2 (עבודת בית 2)', 'assignment', now() + interval '120 days', true, 'נפתחה במודל 21/10/2026. תאריך הסגירה בצילום לא קריא - לבדוק במודל.', 'moodle-shot-linear-2'),
  (c.linear, 'מטלה 3 (עבודת בית 3)', 'assignment', now() + interval '120 days', true, 'נפתחה במודל 21/10/2026. תאריך הסגירה בצילום לא קריא - לבדוק במודל.', 'moodle-shot-linear-3'),
  (c.linear, 'מטלה 4 (עבודת בית 4)', 'assignment', now() + interval '120 days', true, 'נפתחה במודל 21/10/2026. תאריך הסגירה בצילום לא קריא - לבדוק במודל.', 'moodle-shot-linear-4'),
  (c.linear, 'מטלה 5 (עבודת בית 5)', 'assignment', now() + interval '120 days', true, 'נפתחה במודל 21/10/2026. תאריך הסגירה בצילום לא קריא - לבדוק במודל.', 'moodle-shot-linear-5'),
  (c.noise, 'אותות אקראיים ורעש - בחינה', 'exam', timestamptz '2026-10-26 09:00+02', false, 'מאתר האוניברסיטה (מידע). השעה לא ידועה - 09:00 זמני, לבדוק.', 'meyda-noise-2026-10-26'),
  (null::uuid, 'רישום לקורסים במסלול הנדסה', 'other', timestamptz '2026-10-25 09:00+02', false, 'מאתר האוניברסיטה (מידע). השעה לא ידועה.', 'meyda-registration-2026-10-25')
) as x(course_id, title, kind, due_at, check_due, notes, uid)
on conflict (user_id, external_uid) do nothing;
