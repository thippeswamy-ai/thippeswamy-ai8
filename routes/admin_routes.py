from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models.db_helper import (
    verify_admin, get_dashboard_stats, get_all_lost_items, get_all_found_items,
    get_all_claims, get_lost_item_by_id, get_found_item_by_id, update_lost_item,
    update_found_item, delete_lost_item, delete_found_item, get_claim_by_id,
    update_claim_status, delete_claim, add_found_item,
    get_admin_by_id, get_all_admins, add_admin, update_admin_profile, delete_admin
)
from routes.main_routes import save_uploaded_file

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as Administrator to access this page.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as Administrator to access this page.', 'error')
            return redirect(url_for('admin.login'))
        if session.get('admin_role') != 'super_admin':
            flash('Super Administrator privileges required to access this page.', 'error')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        admin = verify_admin(username, password)
        if admin:
            session['admin_logged_in'] = True
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            session['admin_role'] = admin['role'] if 'role' in admin.keys() and admin['role'] else 'admin'
            flash(f'Welcome back, Administrator {admin["username"]} ({session["admin_role"]})!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('You have logged out of Admin Panel.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = get_dashboard_stats()
    recent_lost = get_all_lost_items(search=None)[:5]
    recent_found = get_all_found_items(search=None)[:5]
    recent_claims = get_all_claims()[:5]
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_lost=recent_lost,
        recent_found=recent_found,
        recent_claims=recent_claims
    )

@admin_bp.route('/lost')
@admin_required
def view_lost():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    items = get_all_lost_items(status=status if status else None, search=search)
    return render_template('admin/lost_list.html', items=items, search=search, status=status)

@admin_bp.route('/found')
@admin_required
def view_found():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    items = get_all_found_items(status=status if status else None, search=search)
    return render_template('admin/found_list.html', items=items, search=search, status=status)

@admin_bp.route('/claims')
@admin_required
def view_claims():
    status = request.args.get('status', '').strip()
    claims = get_all_claims(status=status if status else None)
    return render_template('admin/claims_list.html', claims=claims, status=status)

@admin_bp.route('/claim/<int:claim_id>/action', methods=['POST'])
@admin_required
def claim_action(claim_id):
    action = request.form.get('action') # 'Approved' or 'Rejected'
    admin_notes = request.form.get('admin_notes', '').strip()

    if action in ['Approved', 'Rejected']:
        update_claim_status(claim_id, action, admin_notes)
        flash(f'Claim #{claim_id} has been {action.lower()} successfully.', 'success')
    else:
        flash('Invalid action requested.', 'error')

    return redirect(url_for('admin.view_claims'))

@admin_bp.route('/item/edit/<item_type>/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit_item(item_type, item_id):
    if item_type == 'lost':
        item = get_lost_item_by_id(item_id)
        if not item:
            flash('Lost record not found.', 'error')
            return redirect(url_for('admin.view_lost'))

        if request.method == 'POST':
            item_name = request.form.get('item_name', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            location_lost = request.form.get('location_lost', '').strip()
            date_lost = request.form.get('date_lost', '').strip()
            status = request.form.get('status', 'Active').strip()

            update_lost_item(item_id, item_name, category, description, location_lost, date_lost, status)
            flash(f'Lost Item #{item_id} updated successfully.', 'success')
            return redirect(url_for('admin.view_lost'))

        return render_template('admin/item_edit.html', item=item, item_type='lost')

    elif item_type == 'found':
        item = get_found_item_by_id(item_id)
        if not item:
            flash('Found item record not found.', 'error')
            return redirect(url_for('admin.view_found'))

        if request.method == 'POST':
            item_name = request.form.get('item_name', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            place_found = request.form.get('place_found', '').strip()
            date_found = request.form.get('date_found', '').strip()
            status = request.form.get('status', 'Available').strip()

            update_found_item(item_id, item_name, category, description, place_found, date_found, status)
            flash(f'Found Item #{item_id} updated successfully.', 'success')
            return redirect(url_for('admin.view_found'))

        return render_template('admin/item_edit.html', item=item, item_type='found')

    flash('Invalid item type specified.', 'error')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/item/delete/<item_type>/<int:item_id>', methods=['POST'])
@admin_required
def delete_item(item_type, item_id):
    next_url = request.form.get('next') or request.referrer
    if item_type == 'lost':
        delete_lost_item(item_id)
        flash(f'Lost Item record #{item_id} has been deleted.', 'info')
        return redirect(next_url or url_for('admin.view_lost'))
    elif item_type == 'found':
        delete_found_item(item_id)
        flash(f'Found Item record #{item_id} has been deleted.', 'info')
        return redirect(next_url or url_for('main.found_items'))
    elif item_type == 'claim':
        delete_claim(item_id)
        flash(f'Claim record #{item_id} has been deleted.', 'info')
        return redirect(next_url or url_for('admin.view_claims'))

    flash('Invalid delete operation.', 'error')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/found/upload', methods=['GET', 'POST'])
@admin_required
def upload_found_admin():
    if request.method == 'POST':
        finder_name = request.form.get('finder_name', 'Admin Officer').strip()
        department = request.form.get('department', 'Security / Admin').strip()
        mobile = request.form.get('mobile', '0000000000').strip()
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        place_found = request.form.get('place_found', '').strip()
        date_found = request.form.get('date_found', '').strip()

        file = request.files.get('image')
        image_path = save_uploaded_file(file)

        if not (item_name and category and description and place_found and date_found):
            flash('Please fill in all required fields.', 'error')
            return render_template('admin/upload_found.html')

        add_found_item(finder_name, department, mobile, item_name, category, description, place_found, date_found, image_path)
        flash(f'New Found Item "{item_name}" added to database.', 'success')
        return redirect(url_for('admin.view_found'))

    return render_template('admin/upload_found.html')

@admin_bp.route('/profile', methods=['GET', 'POST'])
@admin_required
def profile():
    admin_id = session.get('admin_id')
    admin = get_admin_by_id(admin_id)
    if not admin:
        flash('Admin record not found.', 'error')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()

        # Verify current password
        verified = verify_admin(admin['username'], current_password)
        if not verified:
            flash('Incorrect current password. Profile update failed.', 'error')
            return render_template('admin/profile.html', admin=admin)

        if not username:
            flash('Username cannot be empty.', 'error')
            return render_template('admin/profile.html', admin=admin)

        try:
            update_admin_profile(admin_id, username, email, new_password if new_password else None)
            session['admin_username'] = username
            flash('Admin credentials updated successfully!', 'success')
            admin = get_admin_by_id(admin_id)
        except Exception as e:
            flash('Username or email already exists in system.', 'error')

    return render_template('admin/profile.html', admin=admin)

@admin_bp.route('/manage-admins', methods=['GET', 'POST'])
@super_admin_required
def manage_admins():
    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()
        new_role = request.form.get('role', 'admin').strip()

        if not (new_username and new_password):
            flash('Username and Password are required to create a new administrator.', 'error')
        else:
            try:
                add_admin(new_username, new_password, new_email, new_role)
                flash(f'New Administrator account "{new_username}" ({new_role}) created successfully!', 'success')
                return redirect(url_for('admin.manage_admins'))
            except Exception as e:
                flash('Administrator username or email already exists.', 'error')

    admins = get_all_admins()
    return render_template('admin/manage_admins.html', admins=admins)

@admin_bp.route('/delete-admin/<int:admin_id>', methods=['POST'])
@super_admin_required
def delete_admin_route(admin_id):
    current_admin_id = session.get('admin_id')
    if admin_id == current_admin_id:
        flash('You cannot delete your own active administrator account.', 'error')
        return redirect(url_for('admin.manage_admins'))

    admins = get_all_admins()
    if len(admins) <= 1:
        flash('Cannot delete the last remaining administrator account.', 'error')
        return redirect(url_for('admin.manage_admins'))

    delete_admin(admin_id)
    flash(f'Administrator ID #{admin_id} has been deleted.', 'info')
    return redirect(url_for('admin.manage_admins'))
