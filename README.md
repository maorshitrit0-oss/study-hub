# Study Hub

פותח על ידי **Maor Shitrit**.

פותח על ידי **Maor Shitrit**.

מערכת לימוד אישית לכל התואר: מדביקים קישור להקלטת זום (או לאתר), ומקבלים **פרק קריאה** עם צילומי הלוח ו**שאלון אמריקאי**,
עם מעקב אחרי החוזקות והחולשות בכל נושא, צ'אט על כל קורס (כולל תמונות וקבצים כמו מבחני עבר), ומשימות/מבחנים מסונכרנים מהמודל.
עובד באייפון (מוסיפים למסך הבית) ובמחשב. בלי שרת בתשלום.

```
אפליקציה (Vercel)  ──קישור──▶  GitHub Actions: הורדה מזום → צילומי לוח → תמלול עברית → פרק + שאלון (Gemini)
        ▲                                     │
        └──────────── Supabase: משתמשים, נתונים, קבצים ◀────┘
```

## הקמה (פעם אחת)

### 1. Supabase – נתונים ומשתמשים
1. פותחים פרויקט ב-[supabase.com](https://supabase.com) (Region: Europe).
2. **SQL Editor → New query** → מדביקים את כל התוכן של [`supabase/schema.sql`](supabase/schema.sql) → **Run**.
3. **Project Settings → API Keys**: שומרים את ה-**Project URL**, את ה-**publishable / anon key** ואת ה-**secret / service_role key** (סודי!).

### 2. Gemini – מפתח API חינמי
[aistudio.google.com](https://aistudio.google.com) → **Get API key → Create API key**.

### 3. GitHub – העיבוד של ההקלטות
1. במאגר: **Settings → Secrets and variables → Actions → New repository secret**, שלושה סודות:
   `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (ה-secret key), `GEMINI_API_KEY`.
2. טוקן שמאפשר לאפליקציה להפעיל את העיבוד: [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
   → Repository access: רק `study-hub` → Permissions: **Actions: Read and write** → Generate. שומרים אותו לשלב הבא.

### 4. Vercel – האפליקציה
1. [vercel.com/new](https://vercel.com/new) → Import את `study-hub` → **Root Directory: `web`**.
2. **Environment Variables**:

   | שם | ערך |
   |---|---|
   | `NEXT_PUBLIC_SUPABASE_URL` | ה-Project URL |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ה-publishable / anon key |
   | `GEMINI_API_KEY` | מפתח Gemini |
   | `GITHUB_REPO` | `maorshitrit0-oss/study-hub` |
   | `GITHUB_TOKEN` | הטוקן משלב 3 |
3. **Deploy**. בסוף מקבלים כתובת כמו `study-hub-xxx.vercel.app`.
4. חוזרים ל-Supabase: **Authentication → URL Configuration → Site URL** = הכתובת הזו.

### 5. באייפון
פותחים את הכתובת ב-Safari → שיתוף → **הוסף למסך הבית**.

## שימוש
- **קורס חדש**: שם, שנה, סמסטר, סוג מבחן, משקלים. מעלים מצגות, סילבוס ומבחני עבר.
- **כל שבוע**: בדף הקורס מדביקים קישור זום להרצאה ולתרגול. הפרק והשאלון מוכנים אחרי בערך 40% מאורך ההקלטה (ומגיעה התראה).
- **לומדים**: קוראים את הפרק → "סיימתי לקרוא" → שאלון. דף הקורס מראה איפה אתה עומד בכל נושא; "תרגול" מתחיל מהשאלות שטעית בהן.
- **צ'אט**: שאלות, הסברים, "תלמד אותי", ניתוח מבחני עבר, תמונה של שאלה מהמחברת.
- **משימות**: הגדרות → קישור לוח השנה של המודל → סנכרון.
- **קורס הסתיים**: עריכה → העברה לארכיון. שום דבר לא נמחק.

### כתיבת פרק ע"י Claude (איכות גבוהה יותר, דרך מנוי Claude Pro)
בהוספת הרצאה בוחרים "Claude", ואז ב-Claude Code (גם מהאייפון) על המאגר הזה כותבים: **"תכתוב את הפרקים שמחכים"**.
סביבת הענן של Claude Code צריכה את הסודות `SUPABASE_URL` ו-`SUPABASE_SERVICE_KEY`, וגישת רשת ל-`*.supabase.co`, `*.zoom.us`, `huggingface.co`.
ההוראות ל-Claude נמצאות ב-[`CLAUDE.md`](CLAUDE.md).

## עלויות
הכל במסלולים החינמיים: Supabase (500MB נתונים, 1GB קבצים – צילום לוח שוקל ~30KB), Vercel Hobby, GitHub Actions
(2,000 דקות בחודש למאגר פרטי; הרצאה של 80 דקות ≈ 35 דקות עיבוד), Gemini API (מגבלה יומית).
אם בעתיד משתפים את המערכת עם אחרים בתשלום – צריך לעבור למסלולים בתשלום.
