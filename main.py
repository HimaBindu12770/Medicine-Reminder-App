import threading
import time
import schedule
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from plyer import notification
from twilio.rest import Client

# --------------------
# Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

# --------------------
# DB Model
class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine = db.Column(db.String(100))
    time = db.Column(db.String(100))


# --------------------
# Twilio SMS Function
def send_sms_twilio(medicine, time):
    # 👉 Paste your Twilio credentials here
    account_sid = 'ACcdd64ab1d3a5770a19ff3558f6afc9ec'   # Your Twilio SID
    auth_token = '5b2ddc0cb744614dc796e84bef752447'                      # Your Twilio Auth Token
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f'💊 Reminder: Take your {medicine} at {time}',
        from_='+15158543443',   # Your Twilio Number
        to='+919347399688'      # Your Phone +91
    )
    print(f"✅ SMS Sent Successfully: {message.sid}")


# --------------------
# PC Notification + SMS Both
def send_notification():
    with app.app_context():
        medicines = Medicine.query.all()
        for med in medicines:
            # PC Notification
            notification.notify(
                title='💊 Medicine Reminder 💊',
                message=f'Take your {med.medicine} at {med.time}',
                timeout=10
            )
            # Twilio SMS Notification
            send_sms_twilio(med.medicine, med.time)
            print(f"🔔 Reminder: Take your {med.medicine} at {med.time}")


# --------------------
# Routes
@app.route('/')
def home():
    medicines = Medicine.query.all()
    return render_template('index.html', medicines=medicines)


@app.route('/add', methods=['POST'])
def add():
    med = request.form['medicine']
    time_str = request.form['time']
    new_medicine = Medicine(medicine=med, time=time_str)
    db.session.add(new_medicine)
    db.session.commit()
    return redirect('/')


# --------------------
# Scheduler
def scheduler_thread():
    schedule.every(10).seconds.do(send_notification)
    while True:
        schedule.run_pending()
        time.sleep(1)


# --------------------
# Run App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    threading.Thread(target=scheduler_thread, daemon=True).start()
    app.run(debug=True)
