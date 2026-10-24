-- On-time notifications: GitHub's schedule ran hours late, so the database calls the app instead.
-- Runs at 05/06/17/18 UTC; the app sends only at his times (Sun-Thu 08:00+20:00, Fri 08:00, Sat 20:00 Israel)
-- and only once per slot. Safe to run again.
create extension if not exists pg_cron;
create extension if not exists pg_net;
select cron.unschedule(jobid) from cron.job where jobname = 'study-hub-notify';
select cron.schedule('study-hub-notify', '0 5,6,17,18 * * *',
  $$select net.http_get('https://study-hub-tawny-mu-63.vercel.app/api/cron/notify')$$);
