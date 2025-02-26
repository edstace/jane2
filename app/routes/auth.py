from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app.services.user_service import UserService
from app import db
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == 'POST':
        # Validate form data
        data = request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        # Username validation
        if not re.match(r'^[A-Za-z0-9_]{3,20}$', username):
            flash('Username must be 3-20 characters and contain only letters, numbers, and underscores', 'error')
            return render_template('auth/register.html')
        
        # Email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Invalid email address', 'error')
            return render_template('auth/register.html')
        
        # Password validation
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('auth/register.html')
        
        try:
            # Create user
            user_data = {
                'username': username,
                'email': email,
                'password': password,
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'phone_number': data.get('phone_number', '')
            }
            
            user = UserService.create_user(user_data)
            
            # Log in the user
            login_user(user)
            
            # Redirect to profile or dashboard
            return redirect(url_for('main.home'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('auth/register.html')
    
    # GET request
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        # Validate form data
        data = request.form
        login_id = data.get('login', '').strip()  # can be username or email
        password = data.get('password', '')
        remember = data.get('remember', False) == 'on'
        
        # Validation
        if not login_id or not password:
            flash('Username/email and password are required', 'error')
            return render_template('auth/login.html')
        
        # Authenticate user
        user = UserService.authenticate_user(login_id, password)
        
        if not user:
            flash('Invalid username/email or password', 'error')
            return render_template('auth/login.html')
        
        # Log in the user
        login_user(user, remember=remember)
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.home'))
    
    # GET request
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out a user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile"""
    return render_template('auth/profile.html')

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        # Validate form data
        data = request.form
        email = data.get('email', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        
        # Email validation
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Invalid email address', 'error')
            return render_template('auth/edit_profile.html')
        
        try:
            # Update user
            user_data = {
                'email': email or current_user.email,
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number
            }
            
            UserService.update_user(current_user.id, user_data)
            
            flash('Profile updated successfully', 'success')
            return redirect(url_for('auth.profile'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('auth/edit_profile.html')
    
    # GET request
    return render_template('auth/edit_profile.html')

@auth_bp.route('/password/change', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        # Validate form data
        data = request.form
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 8:
            flash('New password must be at least 8 characters', 'error')
            return render_template('auth/change_password.html')
        
        # Verify current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'error')
            return render_template('auth/change_password.html')
        
        try:
            # Update password
            UserService.update_user(current_user.id, {'password': new_password})
            
            flash('Password changed successfully', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return render_template('auth/change_password.html')
    
    # GET request
    return render_template('auth/change_password.html')

@auth_bp.route('/conversations')
@login_required
def conversations():
    """Display user conversations"""
    from app.services.message_service import MessageService
    
    # Get user conversations
    conversations = MessageService.get_conversations(current_user.id)
    
    return render_template('auth/conversations.html', conversations=conversations)