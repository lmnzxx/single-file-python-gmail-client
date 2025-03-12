# Python Single Page Gmail Client

Python Single Page Gmail Client is a simple Python script for sending and reading emails from Gmail using SMTP and IMAP.

## 📌 Features

- 🔑 Login to Gmail using SMTP and IMAP
- 📩 Send emails with attachments
- 📬 Read emails from **Inbox** and **Sent Mail**
- 🔍 Search emails by keyword
- 🔄 Automatic reconnect mechanism if the connection is lost

## 🛠️ Installation

Make sure Python 3.x is installed, then run the following command to install dependencies:

```sh
pip install smtplib imaplib email getpass
```

## 🚀 Usage

1. Run the script:
   ```sh
   python gmailClient.py
   ```
2. Enter your Gmail address and **App Password** (not your regular password).
   > **Note:** Enable **2FA** on your Gmail account, then create an **App Password** from [Google Security](https://myaccount.google.com/security)
3. Use the interactive menu to send or read emails.

## 📧 SMTP & IMAP Configuration

This script uses Gmail's default servers:

- **SMTP Server**: `smtp.gmail.com` (port `587`)
- **IMAP Server**: `imap.gmail.com` (port `993`)

## 📝 License

This project is licensed under the **MIT** license. Feel free to use and modify it as needed.
