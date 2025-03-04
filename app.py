from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, login_required, current_user
# Import the app instance along with other objects from your database_models.py
from models.database_models import app, db, bcrypt, login_manager, User, Admin, subject, chapter, quiz, question

@app.route('/', methods=['GET', 'POST'])
def login_signup():
    if request.method == "POST":
        print("Form is submitted")
        # Get form type from the submitted form data
        form_type = request.form.get("form_type")
        print("Form type:", form_type)
        
        if form_type == "login":
            username = request.form.get("username")
            password = request.form.get("password")
            
            # Check if the user is an admin (using username field)
            admin = Admin.query.filter_by(username=username).first()
            if admin and bcrypt.check_password_hash(admin.password, password):
                login_user(admin)
                return redirect(url_for("admin_dashboard"))
            
            # Check for a regular user (using username field)
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("user_dashboard"))
            
            flash("Invalid credentials, if new user please signup", "danger")
        
        elif form_type == "signup":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            
            # Check if a user with this email already exists
            user = User.query.filter_by(email=email).first()
            if user:
                flash("User already exists, please login", "danger")
            else:
                # Hash the password and create a new user
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                new_user = User(username=username, email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                print("User created successfully")
                flash("User created, please login", "success")
                
    return render_template("login.html")

# Admin Dashboard
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html", role="admin")

# User Dashboard
@app.route("/user_dashboard")
@login_required
def user_dashboard():
    return render_template("user_dashboard.html", role="user")

# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_signup"))

if __name__ == "__main__":
    app.run(debug=True)