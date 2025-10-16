from EsportsManagementTool import app
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import MySQLdb.cursors
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta

mysql = MySQL()


"""DISCLAIMER: THIS CODE WAS GENERATED USING CLAUDE AI"""
# UC-13: ChooseEventNotice - User Notification Preferences
@app.route('/eventnotificationsettings', methods=['GET', 'POST'])
def notification_settings():
    """Allow users to configure their event notification preferences"""
    if 'loggedin' not in session:
        flash('Please log in to access notification settings.', 'warning')
        return redirect(url_for('login'))

    user_id = session['loggedin']

    if request.method == 'POST':
        enable_notifications = request.form.get('enable_notifications') == 'on'
        advance_notice_days = int(request.form.get('advance_notice_days', 1))
        advance_notice_hours = int(request.form.get('advance_notice_hours', 0))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            # Check if preferences exist
            cursor.execute("""
                           SELECT id
                           FROM notification_preferences
                           WHERE user_id = %s
                           """, (user_id,))

            exists = cursor.fetchone()

            if exists:
                # Update existing preferences
                cursor.execute("""
                               UPDATE notification_preferences
                               SET enable_notifications = %s,
                                   advance_notice_days  = %s,
                                   advance_notice_hours = %s,
                                   updated_at           = NOW()
                               WHERE user_id = %s
                               """, (enable_notifications, advance_notice_days,
                                     advance_notice_hours, user_id))
            else:
                # Insert new preferences
                cursor.execute("""
                               INSERT INTO notification_preferences
                               (user_id, enable_notifications, advance_notice_days,
                                advance_notice_hours, created_at, updated_at)
                               VALUES (%s, %s, %s, %s, NOW(), NOW())
                               """, (user_id, enable_notifications, advance_notice_days,
                                     advance_notice_hours))

            mysql.connection.commit()
            flash('Notification preferences saved successfully!', 'success')

        finally:
            cursor.close()

        return redirect(url_for('notification_settings'))

    # GET request - fetch current preferences
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    preferences = None

    try:
        cursor.execute("""
                       SELECT *
                       FROM notification_preferences
                       WHERE user_id = %s
                       """, (user_id,))
        preferences = cursor.fetchone()
    finally:
        cursor.close()

    return render_template('eventnotificationsettings.html', preferences=preferences)


# UC-14: SendEventNotice - Automated Email Notifications
def send_event_notification(user_email, user_name, event_type, event_details):
    """Send email notification to user about upcoming event"""
    try:
        subject = f"Reminder: Upcoming {event_type}"

        body = f"""
        Hello {user_name},

        This is a reminder about your upcoming {event_type.lower()}:

        Event: {event_details['title']}
        Date: {event_details['date'].strftime('%B %d, %Y')}
        Time: {event_details['time'].strftime('%I:%M %p')}
        Location: {event_details['location']}

        {'Match Details:' if event_type == 'Match' else 'Event Details:'}
        {event_details.get('description', 'No additional details')}

        We look forward to seeing you there!

        Best regards,
        Esports Management Tool
        """

        msg = Message(subject=subject, recipients=[user_email], body=body)
        mail.send(msg)

        return True
    except Exception as e:
        print(f"Error sending email to {user_email}: {e}")
        return False


def check_and_send_notifications():
    """
    Background task to check for upcoming events and send notifications
    based on user preferences (FREQ24, FREQ25)
    """

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Get all users with notifications enabled
        cursor.execute("""
                       SELECT u.id as user_id,
                              u.email,
                              u.name,
                              u.user_type,
                              np.advance_notice_days,
                              np.advance_notice_hours
                       FROM users u
                                JOIN notification_preferences np ON u.id = np.user_id
                       WHERE np.enable_notifications = TRUE
                       """)

        users = cursor.fetchall()

        for user in users:
            # Calculate notification window
            advance_time = timedelta(
                days=user['advance_notice_days'],
                hours=user['advance_notice_hours']
            )
            notification_time = datetime.now() + advance_time

            # FREQ24: Send Players reminders about upcoming matches
            if user['user_type'] == 'player':
                cursor.execute("""
                               SELECT m.id,
                                      m.title,
                                      m.match_date as date,
                        m.match_time as time,
                        m.location,
                        m.description
                               FROM matches m
                                   JOIN match_participants mp
                               ON m.id = mp.match_id
                               WHERE mp.user_id = %s
                                 AND m.match_date = DATE (%s)
                                 AND m.match_time BETWEEN %s
                                 AND %s
                                 AND NOT EXISTS (
                                   SELECT 1 FROM sent_notifications sn
                                   WHERE sn.user_id = %s
                                 AND sn.event_id = m.id
                                 AND sn.event_type = 'match'
                                 AND sn.sent_at >= DATE_SUB(NOW()
                                   , INTERVAL 1 DAY)
                                   )
                               """, (user['user_id'], notification_time.date(),
                                     notification_time.time(),
                                     (notification_time + timedelta(minutes=30)).time(),
                                     user['user_id']))

                matches = cursor.fetchall()

                for match in matches:
                    if send_event_notification(
                            user['email'],
                            user['name'],
                            'Match',
                            match
                    ):
                        # Log sent notification
                        cursor.execute("""
                                       INSERT INTO sent_notifications
                                           (user_id, event_id, event_type, sent_at)
                                       VALUES (%s, %s, 'match', NOW())
                                       """, (user['user_id'], match['id']))

            # FREQ25: Send Community Members reminders for upcoming events
            if user['user_type'] in ['community_member', 'player', 'admin']:
                cursor.execute("""
                               SELECT e.id,
                                      e.title,
                                      e.event_date as date,
                        e.event_time as time,
                        e.location,
                        e.description
                               FROM events e
                                   JOIN event_registrations er
                               ON e.id = er.event_id
                               WHERE er.user_id = %s
                                 AND e.event_date = DATE (%s)
                                 AND e.event_time BETWEEN %s
                                 AND %s
                                 AND NOT EXISTS (
                                   SELECT 1 FROM sent_notifications sn
                                   WHERE sn.user_id = %s
                                 AND sn.event_id = e.id
                                 AND sn.event_type = 'event'
                                 AND sn.sent_at >= DATE_SUB(NOW()
                                   , INTERVAL 1 DAY)
                                   )
                               """, (user['user_id'], notification_time.date(),
                                     notification_time.time(),
                                     (notification_time + timedelta(minutes=30)).time(),
                                     user['user_id']))

                events = cursor.fetchall()

                for event in events:
                    if send_event_notification(
                            user['email'],
                            user['name'],
                            'Event',
                            event
                    ):
                        # Log sent notification
                        cursor.execute("""
                                       INSERT INTO sent_notifications
                                           (user_id, event_id, event_type, sent_at)
                                       VALUES (%s, %s, 'event', NOW())
                                       """, (user['user_id'], event['id']))

        mysql.connection.commit()

    finally:
        cursor.close()


# Initialize scheduler for background notifications
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=check_and_send_notifications,
    trigger="interval",
    minutes=60
)
scheduler.start()

import atexit
atexit.register(lambda: scheduler.shutdown())
"""DISCLAIMER: THIS CODE WAS GENERATED USING CLAUDE AI"""