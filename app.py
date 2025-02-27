from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, Column, Integer, String, DateTime,Float,ForeignKey,func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session,relationship,backref
from datetime import datetime
import re
import random
from collections import defaultdict


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine("postgresql://postgres:hello123@localhost:5432/mybank")  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = scoped_session(SessionLocal)  

#Users model
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    card_number= Column(String,unique=True, nullable=False)
    expiry_date=Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
     

# Beneficiary model
class Beneficiary(Base):
    __tablename__ = 'beneficiaries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_number = Column(String(20), nullable=False)
    bank_name = Column(String(50), nullable=False)
    account_holder_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())

#Transactions model 
class Transaction(Base):
    __tablename__ = 'transactions'

    trans_id = Column(Integer, primary_key=True)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Reference to Users table
    amount = Column(Float, nullable=False)
    remarks = Column(String(255), nullable=True)
    transaction_date = Column(DateTime, default=func.now())
  
    # Relationships
    beneficiary = relationship('Beneficiary', backref=backref('transactions', lazy=True))
    user = relationship('Users', backref=backref('transactions', lazy=True))

# Create tables
Base.metadata.create_all(engine)

#Routes

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Collect form data
        full_name = request.form.get("full_name").strip()
        phone_number = request.form.get("phone_number").strip()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        # Input validations
        if not full_name or not phone_number or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("signup.html")

        # Validate phone number format
        if not re.match(r"^\d{11}$", phone_number):
            flash("Invalid phone number. Enter a 11-digit number.", "danger")
            return render_template("signup.html")

        # Validate email format
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            flash("Invalid email address format.", "danger")
            return render_template("signup.html")

        # Validate password length
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("signup.html")

        # Check if email already exists
        existing_user = db.query(Users).filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('login'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

     

# Generating Card Number and Expiry
        def generate_card_number():
          return f"4562 {' '.join(str(random.randint(1000, 9999)) for _ in range(3))}"


        card_number=generate_card_number()
       
        def generate_expiry_date():
            today = datetime.now()
            expiry_date = today.replace(year=today.year + 10)
            return expiry_date.strftime("%m/%Y")
 
        expiry_date=generate_expiry_date()
        # Create a new user
        new_user = Users(
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            password=hashed_password,
            card_number=card_number,
            expiry_date=expiry_date,

        )

        # Add to the database
        db.add(new_user)
        db.commit()

        #flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")








@app.route("/")
def home():
    return render_template("home.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/language")
def language():
    return render_template("language.html")

@app.route("/contact-us")
def contact_us():
    return render_template("contact_us.html")


@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@app.route("/continue", methods=["GET"])
def continue_to_screen2():
    return render_template("home2.html")

@app.route("/continue/3", methods=["GET"])
def continue_to_screen3():
    return render_template("home3.html")


@app.route("/send-money")
def send_money():
    return render_template("send_money.html")


@app.route("/continue/login", methods=["GET"])
def continue_to_login():
    return redirect(url_for('login'))

#LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        usern = request.form.get("username").lower()
        passw = request.form.get("password")

        # Query database for the user
        user = db.query(Users).filter_by(email=usern).one_or_none()
  

        if user and bcrypt.check_password_hash(user.password, passw):
            session['user_id'] = user.id
           
            return redirect(url_for('dashboard'))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


#TRANSACTION HISTORY
@app.route("/history")
def transaction_history():
    if 'user_id' not in session:
        flash("Please log in to view your transaction history.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch the transactions for the logged-in user
    transactions = db.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.transaction_date.desc()).all()

    # Group transactions by date
    grouped_transactions = defaultdict(list)
    for transaction in transactions:
        # Extract just the date (YYYY-MM-DD)
        transaction_date = transaction.transaction_date.strftime("%Y-%m-%d")
        
        # Append the transaction details to the corresponding date
        grouped_transactions[transaction_date].append({
            'trans_id': transaction.trans_id,
            'beneficiary_name': transaction.beneficiary.account_holder_name,
            'bank_name': transaction.beneficiary.bank_name,
            'amount': transaction.amount,
            'remarks': transaction.remarks,
           
        })

    # Convert defaultdict to a regular dictionary for Jinja2 compatibility
    grouped_transactions = dict(grouped_transactions)

    # Get today's date for comparison in the template
    today_date = datetime.today().strftime("%Y-%m-%d")

    return render_template("history.html", grouped_transactions=grouped_transactions, today_date=today_date)


#USER DASHBOARD
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))

    # Fetch user details from the database using user_id stored in session
    user = db.query(Users).filter_by(id=session['user_id']).one_or_none()

    if not user:
        session.pop('user_id', None)
        flash("User not found. Please log in again.", "danger")
        return redirect(url_for('login'))

    user_data = {
        "name": user.full_name,
        "card_number": user.card_number,
        "expiry_date": user.expiry_date
    }

    return render_template("dashboard.html", user=user_data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/select_bank")
def select_bank():
    return render_template("select_bank.html")


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if 'user_id' not in session:
        flash("Please log in to edit your profile.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db.query(Users).filter_by(id=user_id).first()

    if request.method == "POST":
        new_name = request.form.get("name")
        new_email = request.form.get("email")

        if user:
            user.full_name = new_name
            user.email = new_email
            db.commit()
            session['name'] = new_name
            flash("Profile updated successfully.", "success")
        else:
            flash("Error updating profile.", "danger")

    return render_template("edit_profile.html", user=user)


#CHANGE PASSWORD
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if 'user_id' not in session:
        flash("Please log in to change your password.", "warning")
        return redirect(url_for('login'))

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        user_id = session['user_id']
        user = db.query(Users).filter_by(id=user_id).first()

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('change_password'))

        if not bcrypt.check_password_hash(user.password, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for('change_password'))

        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.commit()

        flash("Password updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template("change_password.html")

#ADD BENEFICIARY
@app.route("/add_beneficiary", methods=["GET", "POST"])
def add_beneficiary():
    if 'user_id' not in session:
        flash("Please log in to add a beneficiary.", "warning")
        return redirect(url_for('login'))

    if request.method == "POST":
        account_number = request.form.get("account_number")
        account_holder_name = request.form.get("account_holder_name")
        bank_name = request.form.get("bank_name", "Unknown Bank")

        user_id = session['user_id']

        if not account_number or not account_holder_name:
            flash("All fields are required!", "error")
            return render_template("add_beneficiary.html")

        new_beneficiary = Beneficiary(
            user_id=user_id,
            account_number=account_number,
            bank_name=bank_name,
            account_holder_name=account_holder_name
        )
        db.add(new_beneficiary)
        db.commit()
        #flash("Beneficiary added successfully!", "success")
        return redirect(url_for("beneficiaries_added"))

    return render_template("add_beneficiary.html")

@app.route("/beneficiaries-success")
def beneficiaries_added():
     return render_template("beneficiary_added.html")


#BENEFICIARIES LIST
@app.route("/beneficiaries")
def beneficiaries():
    if 'user_id' not in session:
        flash("Please log in to view your beneficiaries.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    beneficiary_list = db.query(Beneficiary).filter_by(user_id=user_id).all()

    return render_template("beneficiary_list.html", beneficiaries=beneficiary_list)


#SEND MONEY
@app.route('/transfer_money/<int:beneficiary_id>', methods=['GET', 'POST'])
def transfer_money(beneficiary_id):
    # Fetch the beneficiary from the database
    beneficiary = db.query(Beneficiary).filter_by(id=beneficiary_id).first()
    
    if not beneficiary:
        flash("Beneficiary not found.", "error")
        return redirect(url_for('beneficiaries'))

    if request.method == 'POST':
        transfer_amount = request.form.get("amount")
        transfer_note = request.form.get("remarks")

        # Validation of the transfer amount
        if not transfer_amount or float(transfer_amount) <= 0:
            flash("Invalid amount entered.", "error")
            return redirect(url_for('transfer_money', beneficiary_id=beneficiary_id))

        # Store the transfer data temporarily in session
        session['transfer_data'] = {
            'beneficiary_id': beneficiary_id,
            'amount': transfer_amount,
            'note': transfer_note
        }

        # Redirect to the confirmation page where the user will review and confirm the transfer
        return redirect(url_for('transfer_confirmation', beneficiary_id=beneficiary_id))

    return render_template('transfer_funds.html', beneficiary=beneficiary)

#CONFIRM PAYMENT
@app.route('/transfer_confirmation/<int:beneficiary_id>', methods=['GET', 'POST'])
def transfer_confirmation(beneficiary_id):
    # Fetch the beneficiary from the database
    beneficiary = db.query(Beneficiary).filter_by(id=beneficiary_id).first()
    
    if not beneficiary:
        abort(404, description="Beneficiary not found")

    # Get the transfer details from the session
    transfer_data = session.get('transfer_data')

    if not transfer_data or transfer_data['beneficiary_id'] != beneficiary_id:
        flash("Invalid transfer data.", "error")
        return redirect(url_for('transfer_money', beneficiary_id=beneficiary_id))

    # If the user confirms the payment, save the transaction to the database
    if request.method == 'POST':
        transfer_amount = transfer_data['amount']
        transfer_note = transfer_data['note']

        # Save the transaction in the database
        new_transaction = Transaction(
            beneficiary_id=beneficiary.id,
            user_id=session['user_id'],  
            amount=transfer_amount,
            remarks=transfer_note
        )
        db.add(new_transaction)
        db.commit()

        # Clear the session data after the transaction
        session.pop('transfer_data', None)

        # Redirect to the success page
        return redirect(url_for('transfer_successful'))

    return render_template(
        'transfer_funds_confirmation.html',
        beneficiary=beneficiary,
        transfer_details=transfer_data
    )

@app.route("/transfer-success")
def transfer_successful():
    return render_template("transfer_successful.html")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()  # Automatically removes session after each request


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True) 