from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash # Generate Password and Check it
import flask_login
from datetime import datetime
from .model import photo_filename
import pathlib
import shutil

from . import db 
from . import model

bp = Blueprint("auth", __name__)

# AUTHENTICATION 

# - - - - - - - - -  SIGN UP - - - - - - - - - 

@bp.route("/signup")
def signup():
    return render_template("auth/signup.html")

@bp.route("/signup", methods =["POST"])
def signup_post():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")

   #  Check passwords are equal
    if password != request.form.get("password_repeat"):
        flash("Sorry, passwords are different")
        return redirect(url_for("auth.signup"))
    
   # Check if email is already in the database
    query = db.select(model.User).where(model.User.email == email)
    user = db.session.execute(query).scalar_one_or_none()
    if user:
        flash("Sorry, email provided is already registered")
        return redirect(url_for("auth.signup"))
    
    # Check if username already in use
    query = db.select(model.User).where(model.User.username == username)
    user = db.session.execute(query).scalar_one_or_none()
    if user:
        flash(f"{username} is already in use")
        return redirect(url_for("auth.signup"))

    # CREATE (SIGN UP) THE USER:
    
    password_hash = generate_password_hash(password)   # SECURITY CODIFICATION, HASH FUNCTION 

    new_user = model.User(email = email, username = username, password = password_hash)
    db.session.add(new_user)
    db.session.commit()

    # In order to store the user and use it in the next form, so we can update it with more info
    session["new_user_id"] = new_user.id
    
    flash("Now, provide a bit more information to complete your profile")  # Esto realmenteno loquiero flash, sino directamente texto displayed
    return redirect(url_for("auth.signup2"))


# SIGNUP STEP 2

@bp.route("/signup2")
def signup2():
    current_year = datetime.now().year
    return render_template("auth/signup2.html", current_year = current_year)

@bp.route("/signup2", methods=["POST"])
def signup2_post():
    # Obtain the user ID from the session
    user_id = session.get("new_user_id")
    if not user_id:
        flash("Your session has expired. Please start the signup process again.")
        return redirect(url_for("auth.signup"))
    
    # Obtain user from database
    query = db.select(model.User).where(model.User.id == user_id)
    user = db.session.execute(query).scalar_one_or_none()
    if not user:
        flash("An error occurred. Please try again.")
        return redirect(url_for("auth.signup"))

    # Get the Data from the FORM
    gender = request.form.get("gender")
    birth = int(request.form.get("birth"))
    bio = request.form.get("bio")
    name = request.form.get("name")
    lastname = request.form.get("lastname")

    if not gender or not birth:
        flash("Gender and year of birth are required.")
        return redirect(url_for("auth.signup2"))
    
    current_year = datetime.today().year
    user_age = current_year - birth

    if user_age < 18:
        flash("You must be over 18 to own an account.")
        return redirect(url_for("auth.signup"))

    min_age_diff = request.form.get("min_age_diff")
    max_age_diff = request.form.get("max_age_diff")
    gender_interest = request.form.getlist("gender_interest")  # Multiple Choice List

    if user_age-int(min_age_diff) < 18:
        flash("User must be over 18.")
        return redirect(url_for("auth.signup"))

    user.gender = gender
    user.year_of_birth = birth

    # Matching Preferences (gender and age range)
    user.matching_preferences = model.MatchingPreferences(
        interested_in_genders=gender_interest,  
        max_age_diff=max_age_diff,
        min_age_diff=min_age_diff
    )
    
    # CREATE THE PROFILE of the USER
    profile = model.Profile(user=user)
    profile.bio = bio
    profile.name = name
    profile.lastname = lastname

    db.session.add(profile)
    db.session.commit()

    # Get Profile Image
    profilepic = request.files['profilepic']

    if profilepic and profilepic.filename != '':
        # Check content type
        content_type = profilepic.content_type
        if content_type == "image/png":
            file_extension = "png"
        elif content_type in ["image/jpeg", "image/jpg"]:
            file_extension = "jpg"
        else:
            flash(f"Unsupported file type {content_type}.")
            return redirect(url_for("auth.signup2"))
        
        main_photo = model.Photo(file_extension=file_extension, is_profile_photo=True)
        profile.photos.append(main_photo)
        db.session.add(main_photo)
        db.session.commit()

        # Save the file in the static folder
        path = photo_filename(main_photo)
        profilepic.save(path)  # Saves FILE received in the form with enctype = multipart/form-data into the selected path

    # Clean session after completing the register
    session.pop("new_user_id", None)

    flash("You have successfully signed up!")
    return redirect(url_for("auth.login"))



# - - - - - - - - -  LOGIN - - - - - - - - - 

@bp.route("/login")
def login():
    return render_template("auth/login.html")

@bp.route("/login", methods = ["POST"])
def login_post():
    email = request.form.get("email")  
    password = request.form.get("password")

    # GET THE USER WITH GIVEN EMAIL
    query = db.select(model.User).where(model.User.email == email)
    user = db.session.execute(query).scalar_one_or_none()


    # CHECK PASSWORD
    if user and check_password_hash(user.password, password):  # If user exists & password correct:
        flask_login.login_user(user)
        return redirect(url_for("main.myprofile"))
        # return redirect(url_for("main.homepage"))  REALMENTE QUEREMOS QUE REDIRIJA AQUÍ
    else:
        flash("Wrong Password")
        return redirect(url_for("auth.login"))


# - - - - - - - - -  LOG OUT - - - - - - - - - 

@bp.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()    # It doesn't need an argument, it just closes actual user's session
    return redirect(url_for("auth.login")) 


# - - - - - - - - - CHANGE PASSWORD - - - - - - - - - 

@bp.route("/change_password")
@flask_login.login_required
def change_password():
    return render_template('auth/change_password.html')

@bp.route("/change_password", methods = ["POST"])
@flask_login.login_required
def change_password_post():
    if request.method == "POST":
        # Get the current user
        user = flask_login.current_user

        # Get form data
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Check if current password is correct
        if not check_password_hash(user.password, current_password):
            flash("Current password is incorrect.")
            return redirect(url_for("auth.change_password"))

        # Check if new passwords match
        if new_password != confirm_password:
            flash("Sorry, the new password does not match")
            return redirect(url_for("auth.change_password"))

        # Update the password and hash it
        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Password changed successfully.")
        return redirect(url_for("main.myprofile"))
        # return redirect(url_for("main.modify"))