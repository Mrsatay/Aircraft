# Aircraft Test Fault Django

Versi Django dari project Aircraft Test Fault Management System yang dipindahkan dari implementasi Java Servlet/JSP ke stack yang lebih sederhana untuk pengembangan lanjutan dan demo yang lebih stabil.

## Cara run

```powershell
cd "c:\Program Files\Collage\De'Wei\Aircraft_Test_Fault_Django"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/demo_data.json
python manage.py runserver
```

Lalu buka `http://127.0.0.1:8000/accounts/login/`.

## Catatan

- Project ini sekarang dikonfigurasi untuk PostgreSQL secara default.
- Konfigurasi database dibaca dari environment variable:
  `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- Untuk mengaktifkan AI via OpenRouter, set environment variable `OPENROUTER_API_KEY`. Jika tidak diatur, aplikasi memakai fallback lokal.
- Asset CSS, JS, Bootstrap, Bootstrap Icons, Chart.js, dan Font Awesome disalin dari project Java.
- Modul yang sudah functional: login, register, dashboard, fault list, create fault, fault detail, aircraft management, reports, user management, workflow status history, dan AI helper endpoint.
- Fitur AI akan memakai fallback lokal bila `OPENROUTER_API_KEY` belum diatur.
- Data demo 100 fault disimpan di `fixtures/demo_data.json`. Jalankan `python manage.py loaddata fixtures/demo_data.json` setelah `migrate` untuk mengisi database baru.
- Bila memakai data demo dan belum tahu password login, set ulang password akun admin dengan `python manage.py changepassword admin`.

## Verifikasi

```powershell
python manage.py test
```

Semua test aplikasi inti saat ini sudah disiapkan untuk modul `accounts`, `aircraft`, `faults`, `reports`, dan `ai_tools`.

## Migrasi data dari SQLite lama

Kalau sebelumnya project ini memakai `db.sqlite3` dan sekarang sudah pindah ke PostgreSQL, Anda bisa memindahkan data lama dengan command berikut:

```powershell
python manage.py import_sqlite_data --sqlite-path db.sqlite3 --flush
```

Gunakan `--flush` bila database PostgreSQL target sudah punya data dan Anda ingin menggantinya dengan isi dari SQLite.
