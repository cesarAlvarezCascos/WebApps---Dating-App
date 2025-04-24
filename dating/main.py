import datetime
import dateutil.tz
from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, current_app, jsonify
import flask_login
# from flask_login import current_user
from datetime import datetime
from .model import photo_filename
import os
from . import model
from . import db 
from sqlalchemy import func

bp = Blueprint("main", __name__)


# MAIN VIEW  ( HOMEPAGE )

@bp.route("/")
@flask_login.login_required
def homepage():
    user = flask_login.current_user
    show_all = request.args.get('showAll', 'false').lower() == 'true'
    if show_all:
        # Fetch all users without applying preferences
        query = db.select(model.User).where(
            model.User.id != user.id,
            model.User.year_of_birth.isnot(None)
        )
    else:    
        # Fetch matching preferences
        query_preferences = db.select(model.MatchingPreferences).where(model.MatchingPreferences.user_id == user.id)
        matching = db.session.execute(query_preferences).scalar_one_or_none()

        if not matching:
            return render_template("main/homepage.html", matches=[])

        min_year = user.year_of_birth - matching.max_age_diff  # Younger bound
        max_year = user.year_of_birth + matching.min_age_diff  # Older bound

        liked_genders = matching.interested_in_genders


        # Fetch potential matches
        query = db.select(model.User).join(model.MatchingPreferences).where(
            model.User.id != user.id,
            model.MatchingPreferences.user_id == model.User.id,
            model.User.gender.in_(liked_genders),
            model.User.year_of_birth.isnot(None),
            model.User.year_of_birth.between(min_year, max_year),
            model.User.id.notin_([u.id for u in user.liking]),
            model.User.id.notin_([u.id for u in user.blocking]),
            model.User.id.notin_([u.id for u in user.blockers]),
            # Check the preferences of the potential match   
            func.json_contains(model.MatchingPreferences.interested_in_genders, f'"{user.gender.value}"'),
            user.year_of_birth >= model.User.year_of_birth - model.MatchingPreferences.max_age_diff,
            user.year_of_birth <= model.User.year_of_birth + model.MatchingPreferences.min_age_diff
        )

    potential_matches = db.session.execute(query).scalars().all()

    return render_template("main/homepage.html", matches=potential_matches, show_all=show_all)


# - - - - - - - - -  CURRENT USER PROFILE - - - - - - - - - 


@bp.route('/profile')   # es necesario /<int:current_user.id> ? Ya que no va a ser la misma url para esta pagina sin importar que usuario sea el current user
@flask_login.login_required
def myprofile():

    # Get current user and info from that user
    user = flask_login.current_user 
    
    # query = db.select(model.User).where(model.User.id != user.id).where(model.User in user.liking).where(model.User in user.likers)
    # matches = db.session.execute(query).scalars().all
    matches = [u for u in user.likers if u in user.liking]

    return render_template('main/myprofile.html', user = user , matches = matches) 



@bp.route('/modify')  # No hay que poner id en la url? Cuando sí?
@flask_login.login_required
def modify():
    # user = flask_login.current_user 
    current_year = datetime.now().year

    return render_template('main/modify.html', current_year = current_year)

@bp.route("/modify", methods=["POST"])
@flask_login.login_required
def modify_post():
    user = flask_login.current_user

    # GET VARIABLES
    name = request.form.get("name")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    username = request.form.get("username")
    gender = request.form.get("gender")
    birth = int(request.form.get("birth"))
    bio = request.form.get("bio")
    min_age_diff = request.form.get("min_age_diff")
    max_age_diff = request.form.get("max_age_diff")
    gender_interest = request.form.getlist("gender_interest")

    uploaded_photo = request.files['profilepic']
    if uploaded_photo.filename != '':
        # Check content type
        content_type = uploaded_photo.content_type
        if content_type == "image/png":
            file_extension = "png"
        elif content_type in ["image/jpeg", "image/jpg"]:
            file_extension = "jpg"
        else:
            flash(f"Unsupported file type {content_type}")
            return redirect(url_for("main.modify"))

    # CONSTRAINTS
    # Check if email is already in the database
    query = db.select(model.User).where(model.User.email == email, model.User.id != user.id)
    user2 = db.session.execute(query).scalar_one_or_none()
    if user2:
        flash("Sorry, email provided is already registered")
        return redirect(url_for("main.modify"))

    # Check if username already in use
    query = db.select(model.User).where(model.User.username == username, model.User.id != user.id)
    user2 = db.session.execute(query).scalar_one_or_none()
    if user2:
        flash(f"{username} is already in use")
        return redirect(url_for("main.modify"))

    if not gender or not birth:
        flash("Gender and year of birth are required.")
        return redirect(url_for("main.modify"))

    current_year = datetime.today().year
    user_age = current_year - birth

    if user_age < 18:
        flash("You must be over 18 to own an account")
        return redirect(url_for("main.modify"))


    # ASSIGN VARIABLES
    user.profile.name = name
    user.profile.lastname = lastname
    user.profile.bio = bio
    user.email = email
    user.username = username
    user.year_of_birth = birth
    user.gender = gender
    user.matching_preferences.interested_in_genders = gender_interest
    user.matching_preferences.max_age_diff = max_age_diff
    user.matching_preferences.min_age_diff = min_age_diff

    if uploaded_photo.filename != '':
        # Handle profile photo
        current_main_photo = next((photo for photo in user.profile.photos if photo.is_profile_photo), None)

        if current_main_photo:
            # Delete current main profile photo
            path = photo_filename(current_main_photo)
            if path.exists():
                path.unlink()
            db.session.delete(current_main_photo)

        # Add new main profile photo
        new_photo = model.Photo(file_extension=file_extension, is_profile_photo=True)
        user.profile.photos.append(new_photo)  # Append photo to the photos list in the profile
        db.session.add(new_photo)
        db.session.commit()  # So the photo.id is created, in order to create an adequate path

        # Save the file in the static folder
        path = photo_filename(new_photo)
        uploaded_photo.save(path)

    db.session.commit()
    return redirect(url_for("main.myprofile"))




@bp.route("/add_photo")
@flask_login.login_required
def add_photo():
    return render_template("main/add_photo.html")   


@bp.route("/add_photo", methods=["POST"])
@flask_login.login_required
def add_photo_post():
    user = flask_login.current_user
    profile = user.profile

    # Get photo from form
    uploaded_photo = request.files.get("photo")
    if uploaded_photo and uploaded_photo.filename != "":
        # Determine file extension
        content_type = uploaded_photo.content_type
        if content_type == "image/png":
            file_extension = "png"
        elif content_type in ["image/jpeg", "image/jpg"]:
            file_extension = "jpg"
        else:
            flash(f"Unsupported file type: {content_type}")
            return redirect(url_for("main.add_photo"))

        # Create photo entry
        new_photo = model.Photo(profile=profile, file_extension=file_extension)
        db.session.add(new_photo)
        db.session.commit()

        # Save photo to static folder
        path = photo_filename(new_photo)
        uploaded_photo.save(path)
    else:
        flash("Please select a valid photo.")

    return redirect(url_for("main.myprofile"))


@bp.route('/delete_photo/<int:photo_id>', methods=["POST"])
@flask_login.login_required
def delete_photo(photo_id):
    
    user = flask_login.current_user
    photo = db.session.get(model.Photo, photo_id)

    if not photo:
        abort(404, "Photo not found.")

    # Check if the photo belongs to the current user
    if photo not in user.profile.photos:
        abort(403, "You do not have permission to delete this photo.")

    # Delete the photo from the database
    db.session.delete(photo)
    db.session.commit()

    # Remove the photo file from the file system
    photo_path = photo_filename(photo)
    if os.path.exists(photo_path):
        os.remove(photo_path)

    return jsonify({"success": True})



# - - - - - - - - -  OTHER USER'S PROFILES - - - - - - - - - 

@bp.route('/other_profile/<int:user_id>')
@flask_login.login_required
def other_profile(user_id):
    user = flask_login.current_user

    if user_id == user.id: 
        return redirect(url_for('main.myprofile')) # Redirect to the user's own profile


    # Query the user by ID
    query = db.select(model.User).where(model.User.id == user_id)
    other_user = db.session.execute(query).scalar_one_or_none()

    # Check if the user exists
    if not other_user:
        abort(404, "User not found.")

    # Check if the current user has blocked this user
   # if other_user in user.blocking:
   #     abort(403, "You cannot view this profile.")

    # Check if the other user has blocked the current user
    if user in other_user.blocking:
        abort(403, "You cannot view this profile.")

    # Parameters needed to send to the rendered page:
    liked_user_ids = [u.id for u in user.liking] # List of IDs of users that current user likes 
    blocked_user_ids = [u.id for u in user.blocking] # List of blocked user IDs (blocked from current user)
    other_user_liking_ids = [u.id for u in other_user.liking]
    query = db.select(model.DateProposal).where( ((model.DateProposal.proposer_id == user.id) & (model.DateProposal.recipient_id == other_user.id)) | ((model.DateProposal.proposer_id == other_user.id) & (model.DateProposal.recipient_id == user.id)) ) 
    existing_proposals = db.session.execute(query).scalars().all() # If there are proposals, allow only if the most recent one has a status of reschedule requested 
    latest_proposal = None
    for p in existing_proposals:
        if latest_proposal is None or p.created_at > latest_proposal.created_at:
            latest_proposal = p 

    # Render the profile page for the other user
    return render_template("main/other_profile.html", user=other_user, logged_user = user, liked_user_ids =liked_user_ids , blocked_user_ids =blocked_user_ids, other_user_liking_ids = other_user_liking_ids , latest_proposal = latest_proposal)


# LIKING A USER

@bp.route('/like/<int:user_id>', methods=['POST'])
@flask_login.login_required
def like_user(user_id):
    current_user = flask_login.current_user

    # Check if the user is trying to like themselves
    if user_id == current_user.id:
        return jsonify({"error": "You cannot like yourself."}), 400

    # Query the user by ID
    liked_user = db.session.get(model.User, user_id)

    if not liked_user:
        return jsonify({"error": "User not found."}), 404

    if liked_user in current_user.blocking:
        return jsonify({"error": "You cannot like a user you have blocked."}), 409

    # Handle liking/unliking logic
    if liked_user in current_user.liking:
        current_user.liking.remove(liked_user)  # UNLIKE USER
        db.session.commit()
        return jsonify({"success": True, "liked": False}), 200
    else:
        current_user.liking.append(liked_user)  # LIKE USER
        db.session.commit()
        return jsonify({"success": True, "liked": True}), 200


# BLOCKING A USER

@bp.route('/block/<int:user_id>', methods=['POST'])
@flask_login.login_required
def block_user(user_id):
    current_user = flask_login.current_user

    # Check if the user is trying to block themselves
    if user_id == current_user.id:
        return jsonify({"error": "You cannot block yourself."}), 400
    
    # Change the block status
    # Query the user by ID
    query = db.select(model.User).where(model.User.id == user_id)
    blocked_user = db.session.execute(query).scalar_one_or_none()

    if not blocked_user:
        abort(404, description="User not found.")
    elif blocked_user in current_user.liking : 
        return jsonify({"error": "You cannot block a user you have liked."}), 400
    else:
        if blocked_user in current_user.blocking:
            current_user.blocking.remove(blocked_user)  # UNBLOCK USER
            db.session.commit()
            return jsonify({"success": True, "blocked": False}), 200
        else:
            query = db.select(model.DateProposal).where(
                ((model.DateProposal.proposer_id == current_user.id) & (model.DateProposal.recipient_id == blocked_user.id)) | ((model.DateProposal.proposer_id == blocked_user.id) & (model.DateProposal.recipient_id == current_user.id)))
            proposals = db.session.execute(query).scalars().all()

            for proposal in proposals:
                if proposal.status != model.ProposalStatus.ignored:
                    proposal.status = model.ProposalStatus.ignored
                    proposal.responded_at = datetime.utcnow()

            current_user.blocking.append(blocked_user)  # BLOCK USER

            if current_user in blocked_user.liking:
                blocked_user.liking.remove(current_user)  # Blocked User stops Liking 

            db.session.commit()
            return jsonify({"success": True, "blocked": True}),200
        

# - - - - - - - SCHEDULE DATES - - - - - - -

@bp.route('/schedule_date/<int:other_user_id>')
@flask_login.login_required
def schedule_date(other_user_id):

    current_user = flask_login.current_user

    # Check if the liking association is bidirectional
    other_user = db.session.execute(
        db.select(model.User).where(model.User.id == other_user_id)
    ).scalar_one_or_none()

    if not other_user:
        abort(404, "User not found.")
    if current_user.id == other_user_id:
        abort(403, "You cannot schedule a date with yourself!?")
    # Ensure mutual liking
    if (current_user.id not in [u.id for u in other_user.liking]) or \
       (other_user_id not in [u.id for u in current_user.liking]):
        abort(403, "You can only schedule a date with someone who mutually likes you.")

   # if (other_user_id in [p.recipient_id for p in current_user.sent_proposals]) or \
   #    (other_user_id in [p.proposer_id for p in current_user.received_proposals]):
   #     abort(403, "You cannot schedule a date with a user you already scheduled a date with.")
        
    # Check existing proposals 
    query = db.select(model.DateProposal).where( ((model.DateProposal.proposer_id == current_user.id) & (model.DateProposal.recipient_id == other_user_id)) | ((model.DateProposal.proposer_id == other_user_id) & (model.DateProposal.recipient_id == current_user.id)) ) 
    existing_proposals = db.session.execute(query).scalars().all() # If there are proposals, allow only if the most recent one has a status of reschedule requested 
    if existing_proposals: 
        latest_proposal = None
        for p in existing_proposals:
            if latest_proposal is None or p.created_at > latest_proposal.created_at:
                latest_proposal = p 
        if latest_proposal.status != model.ProposalStatus.reschedule : 
            abort(403, "You cannot schedule a new date unless the status of the latest proposal is 'reschedule requested'.") 


    # Render the schedule date view
    return render_template('main/schedule_date.html', other_user=other_user)


@bp.route('/restaurants_availability/<string:selected_date>', methods=['GET'])
@flask_login.login_required
def restaurants_availability(selected_date):

    current_user = flask_login.current_user

    # Validate the date format
    try:
        date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    current_date = datetime.now().date()
    is_past = date_obj.date() < current_date
    
    # Query restaurants with availability on the selected date
    query = db.select(model.Restaurant,model.Availability.slots).join(model.Availability).where(model.Availability.date == date_obj).where(model.Availability.slots > 0)
    results = db.session.execute(query).all()
    restaurants = [ { "id": r.id, "name": r.name, "location": r.location, "description": r.description, "image_url": r.image_url, "slots": slots,} for r,slots in results ]
    
    # Return the available restaurants in JSON format
    
    return jsonify({"restaurants" :restaurants, "is_past" : is_past} ), 200


@bp.route('/schedule_date_action', methods=['POST'])
@flask_login.login_required
def schedule_date_action():
    current_user = flask_login.current_user

    # Extract form data
    restaurant_id = request.form.get('restaurant_id')
    proposed_date = request.form.get('proposed_date')
    message = request.form.get('message')
    other_user_id = request.form.get('other_user_id')

    if not (restaurant_id and proposed_date and other_user_id):
        flash("All fields are required.", "error")
        return redirect(url_for('main.schedule_date', other_user_id=other_user_id))

    # Validate the proposed date
    try:
        proposed_date_obj = datetime.strptime(proposed_date, '%Y-%m-%d')
    except ValueError:
        flash("Invalid date format. Use YYYY-MM-DD.", "error")
        return redirect(url_for('main.schedule_date', other_user_id=other_user_id))
    #Fetch other user
    query = db.select(model.User).where(model.User.id  == other_user_id)
    other_user = db.session.execute(query).scalar_one_or_none()
    if not other_user:
        flash("User not found", "error")
        return redirect(url_for('main.homepage'))
    if current_user in other_user.blocking:
        # Save the date proposal
        date_proposal = model.DateProposal(
            date=proposed_date_obj,
            status=model.ProposalStatus.proposed,
            proposer_id=current_user.id,
            recipient_id=other_user_id,
            proposal_message=message,
            restaurant_association=model.DateInRestaurant(
                restaurant_id=restaurant.id
            )
        )
        db.session.add(date_proposal)
        db.session.commit()
        flash("Ignored")
        return redirect(url_for('main.homepage'))

    # Fetch the restaurant
    query = db.select(model.Restaurant).where(model.Restaurant.id == restaurant_id)
    restaurant = db.session.execute(query).scalar_one_or_none()

    if not restaurant:
        flash("Restaurant not found.", "error")
        return redirect(url_for('main.schedule_date', other_user_id=other_user_id))

    # Check availability
    query = db.select(model.Availability).where(model.Availability.restaurant_id == restaurant_id).where(model.Availability.date == proposed_date_obj)
    
    availability = db.session.execute(query).scalar_one_or_none()

    if not availability or availability.slots <= 0:
        flash("No slots available for the selected date.", "error")
        return redirect(url_for('main.schedule_date', other_user_id=other_user_id))

    # Reduce slot count
    availability.slots -= 1

    # Save the date proposal
    date_proposal = model.DateProposal(
        date=proposed_date_obj,
        status=model.ProposalStatus.proposed,
        proposer_id=current_user.id,
        recipient_id=other_user_id,
        proposal_message=message,
        restaurant_association=model.DateInRestaurant(
            restaurant_id=restaurant.id
        )
    )
    db.session.add(date_proposal)
    db.session.commit()

    return redirect(url_for('main.homepage'))



# - - - - - - - MANAGE DATES - - - - - - -
@bp.route('/manage_dates')
@flask_login.login_required
def manage_dates():
    current_user = flask_login.current_user

    # Fetch proposed dates (dates sent by the current user)
    query = db.select(model.DateProposal).where(model.DateProposal.proposer_id == current_user.id)
    all_proposed_dates = db.session.execute(query).scalars().all()

    # Fetch received dates (dates received by the current user)
    query = db.select(model.DateProposal).where(model.DateProposal.recipient_id == current_user.id)
    all_received_dates = db.session.execute(query).scalars().all()

    # Combine both lists for processing
    all_dates = all_proposed_dates + all_received_dates

    # Dictionary to store the latest proposal for each user pair
    latest_proposals = {}

    for proposal in all_dates:
        # Create a pair identifier to handle both directions (proposer -> recipient and recipient -> proposer)
        pair_key = tuple(sorted([proposal.proposer_id, proposal.recipient_id]))

        if pair_key not in latest_proposals:
            # First proposal for this pair
            latest_proposals[pair_key] = proposal
        else:
            # Compare the existing proposal with the current one
            current_best = latest_proposals[pair_key]

            # Prioritize based on status
            if proposal.status != model.ProposalStatus.reschedule:
                if current_best.status == model.ProposalStatus.reschedule or proposal.created_at > current_best.created_at:
                    latest_proposals[pair_key] = proposal
            else:
                # Both are 'reschedule'; keep the latest one
                if proposal.created_at > current_best.created_at:
                    latest_proposals[pair_key] = proposal

    # Separate the proposals back into proposed and received for display
    proposed_dates = [p for p in latest_proposals.values() if p.proposer_id == current_user.id]
    received_dates = [p for p in latest_proposals.values() if p.recipient_id == current_user.id]

    return render_template(
        'main/manage_dates.html',
        proposed_dates=proposed_dates,
        received_dates=received_dates
    )




@bp.route('/respond_to_proposal/<int:proposal_id>', methods=['POST'])
@flask_login.login_required
def respond_to_proposal(proposal_id):
    current_user = flask_login.current_user

    # Fetch the date proposal
    query = db.select(model.DateProposal).where(model.DateProposal.id == proposal_id)

    proposal = db.session.execute(query).scalar_one_or_none()

    if not proposal:
        flash("Proposal not found.", "error")
        return redirect(url_for('main.manage_dates'))

    # Ensure the proposal is for the current user
    if proposal.recipient_id != current_user.id:
        abort(403, "You are not authorized to respond to this proposal.")

    # Get the response and response message
    response = request.form.get('response')
    response_message = request.form.get('response_message', '').strip()

    if response not in ['accepted', 'rejected', 'ignored', 'reschedule']:
        flash("Invalid response.", "error")
        return redirect(url_for('main.manage_dates'))

    # Increment the slots back if the status is changed to a non-accepted status
    if response != 'accepted' and proposal.status == model.ProposalStatus.proposed:
        if proposal.restaurant_association:
            availability = db.session.execute(
                db.select(model.Availability)
                .where(model.Availability.restaurant_id == proposal.restaurant_association.restaurant_id)
                .where(model.Availability.date == proposal.date)
            ).scalar_one_or_none()

            if availability:
                availability.slots += 1

    # Update the proposal status
    if response == 'accepted':
        proposal.status = model.ProposalStatus.accepted
    elif response == 'rejected':
        proposal.status = model.ProposalStatus.rejected
    elif response == 'ignored':
        proposal.status = model.ProposalStatus.ignored
    elif response == 'reschedule':
        proposal.status = model.ProposalStatus.reschedule

    # Save the response message
    proposal.response_message = response_message
    proposal.responded_at = datetime.utcnow()
    db.session.commit()
    flash(f"Proposal has been {response}.", "success")
    return redirect(url_for('main.manage_dates'))



