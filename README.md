# Python Single Page Gmail Client

Python Single Page Gmail Client adalah script Python sederhana untuk mengirim dan membaca email dari Gmail menggunakan SMTP dan IMAP.

## 📌 Fitur

- 🔑 Login ke Gmail menggunakan SMTP dan IMAP
- 📩 Kirim email dengan lampiran
- 📬 Baca email dari **Inbox** dan **Sent Mail**
- 🔍 Cari email berdasarkan keyword
- 🔄 Mekanisme reconnect otomatis jika koneksi terputus

## 🛠️ Instalasi

Pastikan Python 3.x sudah terinstal, lalu jalankan perintah berikut untuk menginstal dependensi:

```sh
pip install smtplib imaplib email getpass
```

## 🚀 Cara Penggunaan

1. Jalankan script:
   ```sh
   python gmailClient.py
   ```
2. Masukkan alamat Gmail dan **App Password** (bukan password biasa).
   > **Catatan:** Aktifkan **2FA** di akun Gmail lo, lalu buat **App Password** dari [Google Security](https://myaccount.google.com/security)
3. Gunakan menu interaktif untuk mengirim atau membaca email.

## 📧 Konfigurasi SMTP & IMAP

Script ini menggunakan server Gmail default:

- **SMTP Server**: `smtp.gmail.com` (port `587`)
- **IMAP Server**: `imap.gmail.com` (port `993`)

## 📝 Lisensi

Proyek ini menggunakan lisensi **MIT**. Silakan gunakan dan modifikasi sesuai kebutuhan.

