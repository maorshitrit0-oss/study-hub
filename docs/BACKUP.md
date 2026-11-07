# Backup and restore

Every Sunday night `.github/workflows/backup.yml` runs `worker/backup.py dump`: all rows of every table and every file in
storage. The result is encrypted and kept as a GitHub release `backup-<date>` (pre-release, the last 8 are kept).

- Encryption: a random AES-256 key encrypts `backup.tgz.enc.part*`; that key is encrypted with `backup/backup_pub.pem`
  into `key.bin.enc`. Only the private key opens it. It is in Maor's Google Drive: **"study-hub - מפתח גיבוי (backup_priv.pem)"**.
  Never put the private key in this (public) repository.
- Nothing in the backup is readable without that key.

## Restore (a Claude session can do it; needs the private key and SUPABASE_URL / SUPABASE_SERVICE_KEY)

```bash
gh release download backup-<date> --repo maorshitrit0-oss/study-hub --dir b && cd b
openssl pkeyutl -decrypt -inkey backup_priv.pem -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 \
  -in key.bin.enc -out key.bin
cat backup.tgz.enc.part* | openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass file:key.bin | tar -xz
python ../worker/backup.py restore data      # upserts rows, uploads missing files, deletes nothing
```

Into a new Supabase project: run the `supabase/*.sql` files first, and create his user (same e-mail) so `user_id`
matches - rows reference `auth.users`.
