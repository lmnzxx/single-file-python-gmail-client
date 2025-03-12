import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from getpass import getpass 
import time

SMTP_SERVER = "smtp.gmail.com"
IMAP_SERVER = "imap.gmail.com"
SMTP_PORT = 587
IMAP_PORT = 993

MAX_RECONNECT_ATTEMPTS = 3
RECONNECT_DELAY = 2  

GLOBAL_SMTP_SERVER = None
GLOBAL_IMAP_SERVER = None
GLOBAL_EMAIL = None
GLOBAL_PASSWORD = None

def login_gmail(email, password):
    global GLOBAL_SMTP_SERVER, GLOBAL_IMAP_SERVER, GLOBAL_EMAIL, GLOBAL_PASSWORD
    try:
        smtp_server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_server.starttls()
        smtp_server.login(email, password)

        imap_server = imaplib.IMAP4_SSL(IMAP_SERVER)
        status, _ = imap_server.login(email, password)
        
        if status != 'OK':
            raise Exception("IMAP login failed")
        
        GLOBAL_SMTP_SERVER = smtp_server
        GLOBAL_IMAP_SERVER = imap_server
        GLOBAL_EMAIL = email
        GLOBAL_PASSWORD = password

        return smtp_server, imap_server
    except Exception as e:
        print(f"Login Error: {e}")
        return None, None
    
def reconnect():
    global GLOBAL_SMTP_SERVER, GLOBAL_IMAP_SERVER
    for attempt in range(MAX_RECONNECT_ATTEMPTS):
        try:
            print(f"\nPercobaan reconnect ke {attempt + 1}")
            
            if GLOBAL_SMTP_SERVER:
                try:
                    GLOBAL_SMTP_SERVER.quit()
                except:
                    pass
            
            if GLOBAL_IMAP_SERVER:
                try:
                    GLOBAL_IMAP_SERVER.logout()
                except:
                    pass
            
            smtp_server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            smtp_server.starttls()
            smtp_server.login(GLOBAL_EMAIL, GLOBAL_PASSWORD)

            imap_server = imaplib.IMAP4_SSL(IMAP_SERVER)
            status, _ = imap_server.login(GLOBAL_EMAIL, GLOBAL_PASSWORD)
            
            if status == 'OK':
                GLOBAL_SMTP_SERVER = smtp_server
                GLOBAL_IMAP_SERVER = imap_server
                print("Reconnect berhasil!")
                return True
            
        except Exception as e:
            print(f"Reconnect gagal: {e}")
            time.sleep(RECONNECT_DELAY)
    
    return False

def handle_connection_error(operation):
    def wrapper(*args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except (smtplib.SMTPException, imaplib.IMAP4.error) as e:
            print(f"Koneksi terputus: {e}")
            
            print("\nPilihan:")
            print("1. Coba reconnect otomatis")
            print("2. Keluar dari program")
            choice = input("Pilih (1/2): ").strip()
            
            if choice == '1':
                if reconnect():
                    return operation(*args, **kwargs)
                else:
                    print("Reconnect gagal. Silakan periksa koneksi internet.")
                    return None
            else:
                print("Keluar dari program.")
                exit()
    return wrapper

@handle_connection_error
def send_email(from_email, to_emails, subject, body, attachment_paths=None):
    global GLOBAL_SMTP_SERVER
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    try:
        for to_email in to_emails:
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            if attachment_paths:
                if isinstance(attachment_paths, str):
                    attachment_paths = [attachment_paths]

                for attachment_path in attachment_paths:
                    if not os.path.isfile(attachment_path):
                        print(f"Error: File '{attachment_path}' not found. Skipping attachment.")
                        continue

                    try:
                        attachment = MIMEBase('application', 'octet-stream')
                        with open(attachment_path, 'rb') as file:
                            attachment.set_payload(file.read())
                        encoders.encode_base64(attachment)
                        attachment.add_header('Content-Disposition', f"attachment; filename={os.path.basename(attachment_path)}")
                        msg.attach(attachment)
                    except Exception as e:
                        print(f"Error attaching file {attachment_path}: {e}")

            try:
                GLOBAL_SMTP_SERVER.sendmail(from_email, to_email, msg.as_string())
                print(f"Email successfully sent to {to_email}")
            except Exception as e:
                print(f"Error sending email to {to_email}: {e}")

    except Exception as e:
        print(f"General email sending error: {e}")

@handle_connection_error
def fetch_emails(folder='inbox', page=1, per_page=8, search_keyword=None):
    global GLOBAL_IMAP_SERVER
    try:
        status, messages = GLOBAL_IMAP_SERVER.select(folder)
        if status != 'OK':
            print(f"Error selecting folder {folder}: {messages}")
            return [], 0

        if search_keyword:
            status, msg_data = GLOBAL_IMAP_SERVER.search(None, f'(TEXT "{search_keyword}")')
        else:
            status, msg_data = GLOBAL_IMAP_SERVER.search(None, 'ALL')

        if status != 'OK':
            print(f"Error searching emails: {msg_data}")
            return [], 0

        email_ids = msg_data[0].split()[::-1] 

        total_emails = len(email_ids)
        start = (page - 1) * per_page
        end = start + per_page

        selected_emails = email_ids[start:end]
        emails = []

        for email_id in selected_emails:
            status, msg_data = GLOBAL_IMAP_SERVER.fetch(email_id, '(RFC822)')
            if status != 'OK':
                print(f"Error fetching email {email_id}: {msg_data}")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    from_addr = msg['from']
                    subject = msg['subject']
                    emails.append((email_id, from_addr, subject))
        
        return emails, total_emails
    except Exception as e:
        print(f"Error in fetch_emails: {e}")
        return [], 0

# Display Emails
def display_emails(emails, page, total_emails):
    print(f"\n=== PAGE {page} ===")
    for idx, (email_id, from_addr, subject) in enumerate(emails, start=1):
        print(f"{idx}. From: {from_addr} | Subject: {subject}")

    print("\n9. Next Page")
    print("99. Previous Page")
    print("0. Exit to Main Menu")

    if (page - 1) * 8 + len(emails) < total_emails:
        print(f"\nTotal emails: {total_emails}")

@handle_connection_error
def read_full_email(email_id):
    global GLOBAL_IMAP_SERVER
    try:
        status, msg_data = GLOBAL_IMAP_SERVER.fetch(email_id, '(RFC822)')
        if status != 'OK':
            clear_screen()
            print(f"Error fetching email details: {msg_data}")
            return

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                from_addr = msg['from']
                subject = msg['subject']
                
                if msg.is_multipart():
                    body = ""
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        try:
                            # Get email body
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True)
                                if body:
                                    body = body.decode('utf-8', errors='ignore')
                                    break
                        except Exception as e:
                            clear_screen()
                            print("Error while decoding:", e)
                else:
                    body = msg.get_payload(decode=True)
                    if body:
                        body = body.decode('utf-8', errors='ignore')
                    else:
                        body = "(No content in email body)"

                print(f"\nFrom: {from_addr}")
                print(f"Subject: {subject}")
                print(f"Body: {body}\n")
                return
    except Exception as e:
        clear_screen()
        print(f"Error reading full email: {e}")

@handle_connection_error
def paginated_email_view(folder='inbox'):
    global GLOBAL_IMAP_SERVER
    page = 1

    while True:
        emails, total_emails = fetch_emails(folder, page)
        if not emails:
            print("\nNo more emails to display.")
            break

        display_emails(emails, page, total_emails)
        choice = input("Select an email (1-8), 9 for next page, 99 for previous page, 0 to exit: ").strip()
        clear_screen()

        if choice == '0':
            break
        elif choice == '9':
            if (page - 1) * 8 + len(emails) < total_emails:
                page += 1
            else:
                print("No more pages available.")
        elif choice == '99':
            if page > 1:
                page -= 1
            else:
                print("You are on the first page.")
        elif choice.isdigit() and 1 <= int(choice) <= len(emails):
            read_full_email(emails[int(choice) - 1][0])
        else:
            print("Invalid choice. Please try again.")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    email = input("Enter your Gmail address: ")
    password = getpass("Enter your App Password: ")

    smtp_server, imap_server = login_gmail(email, password)
    
    if not smtp_server or not imap_server:
        print("Login gagal. Keluar dari program.")
        return

    clear_screen()

    try:
        while True:
            print("\nMenu:")
            print("1. Kirim Email")
            print("2. Baca Email (Inbox)")
            print("3. Baca Email (Sent)")
            print("4. Cari Email")
            print("0. Keluar")

            choice = input("Pilih menu: ").strip()
            clear_screen()

            if choice == '1':
                to_emails = input("Recipient emails (send to multiple email comma-separated): ").split(',')
                to_emails = [email.strip() for email in to_emails]
                
                subject = input("Subject: ")
                body = input("Body: ")
                
                attachments = input("Attachment paths (comma-separated for multiple attachment, optional): ")
                attachment_paths = [path.strip() for path in attachments.split(',')] if attachments else None
                
                clear_screen()
                
                send_email(email, to_emails, subject, body, attachment_paths)

            elif choice == '2':
                paginated_email_view('inbox')

            elif choice == '3':
                paginated_email_view('"[Gmail]/Sent Mail"')

            elif choice == '4':
                keyword = input("Keyword to search: ")
                page = 1
                while True:
                    emails, total_emails = fetch_emails('inbox', page, search_keyword=keyword)
                    if not emails:
                        print("\nNo search results found.")
                        break

                    print(f"\n=== Search Results for '{keyword}' (Page {page}) ===")
                    display_emails(emails, page, total_emails)
                    
                    choice = input("Select an email (1-8), 9 for next page, 99 for previous page, 0 to exit: ").strip()
                    clear_screen()

                    if choice == '0':
                        break
                    elif choice == '9':
                        if (page - 1) * 8 + len(emails) < total_emails:
                            page += 1
                        else:
                            print("No more pages available.")
                    elif choice == '99':
                        if page > 1:
                            page -= 1
                        else:
                            print("You are on the first page.")
                    elif choice.isdigit() and 1 <= int(choice) <= len(emails):
                        read_full_email(emails[int(choice) - 1][0])
                    else:
                        print("Invalid choice. Please try again.")

            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        try:
            if GLOBAL_SMTP_SERVER:
                GLOBAL_SMTP_SERVER.quit()
            if GLOBAL_IMAP_SERVER:
                GLOBAL_IMAP_SERVER.logout()
        except Exception as e:
            print(f"Error during logout: {e}")

if __name__ == "__main__":
    main()