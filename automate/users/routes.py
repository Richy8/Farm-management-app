import os
from datetime import datetime, date
from flask import Blueprint, render_template, flash, request, redirect, url_for, abort, jsonify, current_app
from automate import db, mail, bcrypt
from flask_mail import Message
from flask_login import login_required, login_user, logout_user, current_user
from automate.users.forms import SignupForm, LoginForm, ForgetPasswordForm, PasswordResetForm, NewUserForm, ProfileForm
from automate.models import User, Activitylog, Feeditem, Feedtype, Vendor, Farmitem, Pen, Customer
from automate.users.utils import save_picture, send_reset_email
from automate.feedmill.utils import numberMonth

users = Blueprint('users', __name__)

# Template Filter
@users.app_template_filter()
def extractTwoWords(value):
    new_list = value.split()
    return new_list[0] +' '+ new_list[1]

# Login Route
@users.route('/', methods=['GET', 'POST'])
@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.portal'))
    form = LoginForm()
    if form.validate_on_submit():
        theuser = User.query.filter_by(email=form.email.data).first()
        if theuser and bcrypt.check_password_hash(theuser.password, form.password.data):
            login_user(theuser, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('users.portal'))
        else:
            flash('Invalid Login Credentials!', 'danger')
            return redirect(url_for('users.login'))

    return render_template("main/index.html", title = "Login", form = form)


# NewUser Route
@users.route('/users', methods=['GET', 'POST'])
def user():
    form = NewUserForm()
    if form.validate_on_submit():
        email = form.email.data
        user_row = User.query.filter_by(email=email).first()
        if user_row:
            flash('Email already Exist', 'danger')
        else:
            user = User(email=form.email.data, role=form.role.data)

            try:
                #Send email
                msg = Message(subject='Management system', sender=('County Choice Farms', 'menaelvisjones@gmail.com'), recipients=[email])
                msg.body = f'''Hi, Welcome to County Choice Management System, to complete user registration, kindly follow the link below:\n{ url_for('users.signup', email=email, _external = True) }
                
Ignore, if you didn't request for management portal role. 
                '''
                mail.send(msg)

            except:
                flash('Problem Sending Mail, check internet connection!', 'warning')
                return (redirect(url_for('users.user')))
                
            db.session.add(user)
            db.session.commit()
            flash('User added successfully', 'success')


    # Handle update user role form processing
    if request.method == 'POST' and request.form.get('check') == 'edit_user':
        userId = request.form.get('userId')
        userEmail = request.form.get('userEmail')
        userRole = request.form.get('role')

        checkemail = User.query.filter(User.email == userEmail).first()
        if checkemail:
            _ = User.query.filter(User.id == userId).update({'role': userRole})
            db.session.commit()

            flash('User role updated successfully', 'success')
            return redirect(url_for('users.user'))
        
        else:
            flash('Please check user email', 'warning')

    
     # Handle Delete user form processing
    if request.method == 'POST' and request.form.get('check') == 'delete_user':
        delete_id = request.form.get('delete_user_id')
        user_password = request.form.get('password')

        user_row = User.query.filter(User.id == delete_id).first()
        if user_row and bcrypt.check_password_hash(current_user.password, user_password):
            db.session.delete(user_row)
            db.session.commit()

            flash('User deleted successfully', 'success')
            return redirect(url_for('users.user'))            
        else:
            flash('Please check your password and try again', 'warning')
            return redirect(url_for('users.user')) 

    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch All Users
    users = User.query.filter(User.username != None).all()
    # Fetch User Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template("main/users.html", title = "Users", form = form, ficon = "users", date = datetime.now(), 
            image_file=image_file, users=users, all_activities=all_activities, user_activities=user_activities)


# Handle update user role form population
@users.route('/update_userrole', methods=['POST'])
def update_user():
    user_id = request.get_data('id').decode('utf-8')
    user_id = int(user_id)
    user_row = User.query.filter(User.id == user_id).first()

    userList = []
    userDict = {}

    userDict['id'] = user_row.id
    userDict['email'] = user_row.email
    userList.append(userDict)

    return jsonify({'userData': userList})


# Handle update user role form population
@users.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.get_data('id').decode('utf-8')
    user_id = int(user_id)
    user_row = User.query.filter(User.id == user_id).first()

    userList = []
    userDict = {}

    userDict['id'] = user_row.id
    userDict['username'] = user_row.username
    userList.append(userDict)

    return jsonify({'user_data': userList})


# Signup Route
@users.route('/signup/<email>', methods=['GET', 'POST'])
def signup(email):
    if current_user.is_authenticated:
        return redirect(url_for('users.portal'))
    form = SignupForm()
    form.email.data = email
    if form.validate_on_submit():
        check_email = User.query.filter(User.email==form.email.data).first()
        if check_email:
            hash_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            check_email.username = form.username.data
            check_email.password = hash_pwd
            db.session.commit()
            flash('SignUp was successful. Please Login!', 'success')
            return redirect(url_for('users.login'))
        else:
            flash('Please check the email link', 'danger')
    return render_template("main/wt_signup.html", title="Signup", form=form)


# ForgetPassword Route
@users.route('/forgetpassword', methods=['GET', 'POST'])
def forgetPassword():
    if current_user.is_authenticated:
        return redirect(url_for('users.portal'))
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to you, with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template("main/wt_forget_password.html", title = "Forget Password", form = form)


# ResetPassword Route
@users.route('/resetpassword/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.portal'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Email reset token has expired or is invalid, reset again!', 'warning')
        return redirect(url_for('users.forgetPassword'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hash_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hash_pwd
        db.session.commit()
        flash('Password Reset Successful', 'success')
        return redirect(url_for('users.login'))
    return render_template("main/wt_password_reset.html", title = "Reset Password", form = form)


# Profile Route
@users.route('/user_profile', methods=['GET', 'POST'])
@login_required
def profile():
    c_user = current_user.username
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)
    form = ProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.picture = picture_file
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.username = form.username.data
        db.session.commit()

        flash('Profile Updated Successfully', 'success')
        return redirect(url_for('users.profile'))

    if request.method =='GET':
        if current_user.firstname is None:
            pass
        else:
            form.firstname.data = current_user.firstname

        if current_user.lastname is None:
            pass
        else:
            form.lastname.data = current_user.lastname
        
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.role.data = current_user.role

    return render_template("main/profile.html", title = c_user, ficon = "user", form=form, date = datetime.now(), image_file=image_file)


# ManagementPortal Route
@users.route('/management_portal')
@login_required
def portal():
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)
    return render_template("main/portal.html", title = "Portal", image_file=image_file)


# Notification Route
@users.route('/notifications', methods=['GET', 'POST'])
def notifications():

    # Handle Request Authorization Processing
    if request.method == 'POST' and request.form.get('check') == 'authorize':
        request_id = request.form.get('request_id')
        request_row = Activitylog.query.filter(Activitylog.id == request_id).first()

        # Change the status to replied
        request_row.status = 'replied'
        db.session.commit()

        # Check if requested item still exists
        getRequestedItem = request_row.activity.split()[-2]
        request_list = request_row.request.split()
        if request_list[0] == 'Feeditem':
            # Check if Item Exists in db
            checkItem = Feeditem.query.filter(Feeditem.id == request_list[-1]).first()
            if checkItem:
                # Delete the feeditem from db
                deleteItem = Feeditem.query.filter(Feeditem.id == request_list[-1]).first()
            else:
                flash('Feeditem does no longer exist in db', 'warning')
                return redirect(url_for('users.notifications'))

        elif request_list[0] == 'Feedtype':
            # Check if Item Exists in db
            checkItem = Feedtype.query.filter(Feedtype.id == request_list[-1]).first()
            if checkItem:
                # Delete the feedtype from db
                deleteItem = Feedtype.query.filter(Feedtype.id == request_list[-1]).first()
            else:
                flash('Feedtype does no longer exist in db', 'warning')
                return redirect(url_for('users.notifications'))

        elif request_list[0] == 'Vendor':
            # Check if Item Exists in db
            checkItem = Vendor.query.filter(Vendor.id == request_list[-1]).first()
            if checkItem:
                # Delete the Vendor from db
                deleteItem = Vendor.query.filter(Vendor.id == request_list[-1]).first()
            else:
                flash('Vendor does no longer exist in db', 'warning')
                return redirect(url_for('users.notifications'))

        elif request_list[0] == 'Farmitem':
            # Check if Item Exists in db
            checkItem = Farmitem.query.filter(Farmitem.id == request_list[-1]).first()
            if checkItem:
                # Delete the Farmitem from db
                deleteItem = Farmitem.query.filter(Farmitem.id == request_list[-1]).first()
            else:
                flash('Farmitem does no longer exist in db', 'warning')
                return redirect(url_for('users.notifications'))

        elif request_list[0] == 'Pen':
            # Check if Item Exists in db
            checkItem = Pen.query.filter(Pen.id == request_list[-1]).first()
            if checkItem:
                # Delete the Pen from db
                deleteItem = Pen.query.filter(Pen.id == request_list[-1]).first()
            else:
                flash('Pen does no longer exist in db', 'warning')
                return redirect(url_for('users.notifications'))

        elif request_list[0] == 'Customer':
            # Check if Item Exists in db
            checkItem = Customer.query.filter(Customer.id == request_list[-1]).first()
            if checkItem:
                # Delete the Customer from db
                deleteItem = Customer.query.filter(Customer.id == request_list[-1]).first()
            else:
                flash('Customer does no longer exist in db', 'warning')
                return redirect(url_for('users.notifications'))

        else:
            pass

        db.session.delete(deleteItem)
        db.session.commit()

        # Change the activity info
        request_row.activity = 'Request to delete '+getRequestedItem+' has been authorized'
        db.session.commit()

        flash('Request authorization was successful', 'success')
        return redirect(url_for('users.notifications'))

        
    # Handle Request Decline Processing
    if request.method == 'POST' and request.form.get('check') == 'decline':
        request_id = request.form.get('request_id')
        request_row = Activitylog.query.filter(Activitylog.id == request_id).first()

        # Change the status to replied
        request_row.status = 'replied'
        db.session.commit()

        # Get Requested item
        getRequestedItem = request_row.activity.split()[-2]

        # Change the activity info
        request_row.activity = 'Request to delete '+getRequestedItem+' has been declined'
        db.session.commit()

        flash('Request has been successfully declined', 'success')
        return redirect(url_for('users.notifications'))

    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific pending notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()


    # Get current month and ywar to query with
    year = date.today().strftime('%Y')
    month = date.today().strftime('%m')

    # Fetch all Notifications
    page = request.args.get('page', 1, type=int)

    all_notifications = Activitylog.query.filter(db.extract('year', Activitylog.date) == year).\
                                filter(db.extract('month', Activitylog.date) == month).order_by(Activitylog.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)

    # Fetch all user Notifications
    user_notifications = Activitylog.query.filter(db.extract('year', Activitylog.date) == year).\
                                filter(db.extract('month', Activitylog.date) == month).\
                                filter(Activitylog.user_id == current_user.id).order_by(Activitylog.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)


    # Populate filter select tag with year and month from activitylog db
    notifications_db = Activitylog.query.all()
    year_list = []
    month_list = []

    for log in notifications_db:
        year_log = log.date.strftime('%Y')
        month_log = log.date.strftime('%m')

        if year_log in year_list:
            pass
        else:
            year_list.append(year_log)

        if month_log in month_list:
            pass
        else:
            month_list.append(month_log)


    # Hamdle processing of filter button click
    if request.method == 'POST' and request.form.get('check') == 'filter':
        month_select = request.form.get('month')
        year_select = request.form.get('year')

        if month_select and year_select:
            # Fetch all Notifications
            page = request.args.get('page', 1, type=int)

            all_notifications = Activitylog.query.filter(db.extract('year', Activitylog.date) == year_select).\
                                        filter(db.extract('month', Activitylog.date) == month_select).order_by(Activitylog.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)
            # Fetch all user Notifications
            user_notifications = Activitylog.query.filter(db.extract('year', Activitylog.date) == year_select).\
                                        filter(db.extract('month', Activitylog.date) == month_select).\
                                        filter(Activitylog.user_id == current_user.id).order_by(Activitylog.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)

            flash('Notifications for '+numberMonth(month_select)+' '+year_select+' selected', 'success')
        else:
            flash('Please make a selection', 'warning')


    # User Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template("main/notifications.html", title = "Notifications", ficon = "bell", date = datetime.now(),
                         image_file=image_file, all_activities=all_activities, user_activities=user_activities, 
                         all_notifications=all_notifications, user_notifications=user_notifications, year_list=year_list, month_list=month_list)


# Logout Route
@users.route('/logout')
def logout():
    logout_user()
    flash('Logout Successful', 'success')
    return redirect(url_for('users.login'))