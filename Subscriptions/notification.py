import sqlite3
import streamlit as st
# def send_emails_from_db(db_path, smtp_server, port, email, password, subject, message_body):
#     try:
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
#         cursor.execute("SELECT email FROM email_list")
#         email_list = [row[0] for row in cursor.fetchall()]
#         conn.close()

#         valid_emails = []
#         for email_addr in email_list:
#             try:
#                 validate_email(email_addr)  # Validate email format
#                 valid_emails.append(email_addr)
#             except EmailNotValidError as e:
#                 print(f"Invalid email {email_addr}: {e}")

#         server = smtplib.SMTP(smtp_server, port)
#         server.starttls()  # Secure the connection
#         server.login(email, password)

#         for recipient in valid_emails:
#             msg = MIMEMultipart()
#             msg['From'] = email
#             msg['To'] = recipient
#             msg['Subject'] = subject

#             # Attach the email body
#             msg.attach(MIMEText(message_body, 'plain'))

#             # Send the email
#             server.sendmail(email, recipient, msg.as_string())
#             print(f"Email sent to {recipient}")

#         server.quit()
#         print("All emails sent successfully.")

#     except Exception as e:
#         print(f"Error: {e}")

# # Usage
# if __name__ == "__main__":
#     SMTP_SERVER = "smtp.gmail.com"  # For Gmail
#     PORT = 587
#     EMAIL = "burnerone726@gmail.com"
#     PASSWORD = "Your Password"  # App-specific password

#     SUBJECT = "Totally not suspicious email"
#     MESSAGE_BODY = "Hello, this is a test email from Python."

#     DB_PATH = "subscribers.db"

#     send_emails_from_db(DB_PATH, SMTP_SERVER, PORT, EMAIL, PASSWORD, SUBJECT, MESSAGE_BODY)



def notification_script():
    print("Sending notifications if needed.")