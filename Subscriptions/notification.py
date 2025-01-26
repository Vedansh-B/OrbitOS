import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Function to fetch email addresses from SQLite database
def fetch_emails_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM subscribers")  # Assuming your table is 'subscribers' and column is 'email'
    emails = [row[0] for row in cursor.fetchall()]
    conn.close()
    return emails

def fetch_event_data():
    events = []
    today = datetime.now()
    six_days_later = today + timedelta(days=6)

    # Replace the file paths with your actual CSV file paths
    csv_files = {
        "Solar Eclipse": "data/cleaned_data/nasa_solar_eclipse_data_revised.csv",
        "Lunar Eclipse": "data/cleaned_data/nasa_lunar_eclipse_data_revised.csv",
        "Full Moon": "data/cleaned_data/filtered_full_moons.csv",
        "Near Earth Object": "data/cleaned_data/neo_data.csv"
    }
    
    for event_name, file_path in csv_files.items():
        try:
            # Read the file and convert the Date column
            df = pd.read_csv(file_path)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # Filter for events within the next 6 days
            upcoming_events = df[(df['Date'] >= today) & (df['Date'] <= six_days_later)]

            if not upcoming_events.empty:
                event_details = "\n".join(
                    f"{row['Date'].strftime('%Y-%m-%d')} - {event_name}" for _, row in upcoming_events.iterrows()
                )
                events.append((event_name, event_details))
            else:
                events.append((event_name, "No events in the next 6 days."))
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return events


# Function to send emails
def send_email(smtp_server, port, login, password, sender_email, recipient_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Add the body text
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(login, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")

# Function to generate the email content
def generate_email_content(event_data):
    # Base message about celestial events
    base_message_start = """
    We have exciting news for you! There's a fantastic opportunity to witness a rare celestial event: the Super Blue Moon.

    """
    base_message_end = """
    We hope you’re as excited as we are to witness this spectacular display in the night sky!
    """
    
    # Event-specific blurbs
    event_blurbs = {
        "Solar Eclipse": "A solar eclipse occurs when the moon passes between the Earth and the Sun, casting a shadow on Earth. It's a rare and incredible sight.",
        "Lunar Eclipse": "A lunar eclipse happens when the Earth passes between the Sun and the Moon, casting a shadow on the Moon. It's an impressive sight, especially during a total lunar eclipse.",
        "Full Moon": "A full moon is when the moon is fully illuminated by the Sun's light, making it appear completely round. It's a time when the moon is at its most visible.",
        "Near Earth Object": "A near-Earth object (NEO) is any small solar system body whose orbit brings it close to Earth. Keep an eye out for these objects passing near us!"
    }
    
    # Add event-specific details
    message_body = base_message_start + "\n\nUpcoming Celestial Events:\n\n"
    
    # Loop through each event in the list of tuples
    for event_name, details in event_data:
        # Add the preset blurb for each event
        message_body += f"{event_name}: {event_blurbs.get(event_name, 'No description available.')}\n\n"
        message_body += f"Upcoming Event(s):\n{details}\n\n"

    message_body += base_message_end

    return message_body

def notification_script():
    db_path = "subscriptions/subscribers.db"  # Path to your SQLite database
    login = "email"  # Replace with your email
    password = "password"      # Replace with your email's app password
    sender_email = "email"

    smtp_server = "smtp.gmail.com"
    port = 587
    # Fetch emails from database
    emails = fetch_emails_from_db(db_path)

    # Fetch astronomical event data
    event_data = fetch_event_data()

    # Generate the email content
    subject = "Upcoming Astronomical Events"
    body = generate_email_content(event_data)

    # Send emails
    for email in emails:
        send_email(smtp_server, port, login, password, sender_email, email, subject, body)

if __name__ == "__main__":
    notification_script()
