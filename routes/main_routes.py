import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from models.db_helper import (
    add_lost_item, get_all_lost_items, add_found_item, get_all_found_items, count_found_items,
    get_found_item_by_id, add_claim, get_dashboard_stats
)

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage):
    if file_storage and file_storage.filename != '':
        if allowed_file(file_storage.filename):
            ext = file_storage.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex[:10]}_{secure_filename(file_storage.filename)}"
            upload_dir = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file_storage.save(filepath)
            return filename
    return None

@main_bp.route('/')
def index():
    stats = get_dashboard_stats()
    recent_found = get_all_found_items(status='Available', limit=6)
    recent_lost = get_all_lost_items(status='Active')[:6]
    return render_template('index.html', stats=stats, recent_found=recent_found, recent_lost=recent_lost)

@main_bp.route('/lost/new', methods=['GET', 'POST'])
def report_lost():
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        department = request.form.get('department', '').strip()
        mobile = request.form.get('mobile', '').strip()
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        location_lost = request.form.get('location_lost', '').strip()
        date_lost = request.form.get('date_lost', '').strip()
        
        file = request.files.get('image')
        image_path = save_uploaded_file(file)

        if not (student_name and roll_number and department and mobile and item_name and category and description and location_lost and date_lost):
            flash('Please fill in all required fields.', 'error')
            return render_template('lost_form.html')

        item_id = add_lost_item(
            student_name, roll_number, department, mobile,
            item_name, category, description, location_lost, date_lost, image_path
        )

        flash(f'Your lost report for "{item_name}" has been recorded successfully! Reference ID: #{item_id}', 'success')
        return redirect(url_for('main.index'))

    return render_template('lost_form.html')

@main_bp.route('/found/new', methods=['GET', 'POST'])
def upload_found():
    if request.method == 'POST':
        finder_name = request.form.get('finder_name', '').strip()
        department = request.form.get('department', '').strip()
        mobile = request.form.get('mobile', '').strip()
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        place_found = request.form.get('place_found', '').strip()
        date_found = request.form.get('date_found', '').strip()
        
        file = request.files.get('image')
        image_path = save_uploaded_file(file)

        if not (finder_name and department and mobile and item_name and category and description and place_found and date_found):
            flash('Please fill in all required fields.', 'error')
            return render_template('found_form.html')

        item_id = add_found_item(
            finder_name, department, mobile, item_name,
            category, description, place_found, date_found, image_path
        )

        flash(f'Found item "{item_name}" uploaded successfully! Thank you for helping.', 'success')
        return redirect(url_for('main.found_items'))

    return render_template('found_form.html')

@main_bp.route('/found')
def found_items():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', 'All').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 9

    offset = (page - 1) * per_page
    total_count = count_found_items(category=category, search=search)
    items = get_all_found_items(category=category, search=search, limit=per_page, offset=offset)

    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

    categories = ['All', 'Electronics', 'Personal Accessories', 'Wallets & Cards', 'Stationery & Books', 'Keys', 'Clothing', 'Documents', 'Other']

    return render_template(
        'found_items.html',
        items=items,
        categories=categories,
        current_category=category,
        search_query=search,
        page=page,
        total_pages=total_pages,
        total_count=total_count
    )

@main_bp.route('/lost')
def lost_items():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', 'All').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 9

    offset = (page - 1) * per_page
    all_lost = get_all_lost_items(status='Active', search=search)
    if category and category != 'All':
        all_lost = [i for i in all_lost if i['category'] == category]

    total_count = len(all_lost)
    items = all_lost[offset:offset + per_page]
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

    categories = ['All', 'Electronics', 'Personal Accessories', 'Wallets & Cards', 'Stationery & Books', 'Keys', 'Clothing', 'Documents', 'Other']

    return render_template(
        'lost_items.html',
        items=items,
        categories=categories,
        current_category=category,
        search_query=search,
        page=page,
        total_pages=total_pages,
        total_count=total_count
    )

@main_bp.route('/found/<int:item_id>')
def item_detail(item_id):
    item = get_found_item_by_id(item_id)
    if not item:
        flash('Requested item was not found.', 'error')
        return redirect(url_for('main.found_items'))
    
    return render_template('item_detail.html', item=item)

@main_bp.route('/found/<int:item_id>/claim', methods=['POST'])
def claim_item(item_id):
    item = get_found_item_by_id(item_id)
    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('main.found_items'))

    claimant_name = request.form.get('claimant_name', '').strip()
    roll_number = request.form.get('roll_number', '').strip()
    department = request.form.get('department', '').strip()
    mobile = request.form.get('mobile', '').strip()
    proof_ownership = request.form.get('proof_ownership', '').strip()
    description = request.form.get('description', '').strip()

    file = request.files.get('proof_image')
    proof_image = save_uploaded_file(file)

    if not (claimant_name and roll_number and department and mobile and proof_ownership):
        flash('Please fill in all required fields for claiming.', 'error')
        return redirect(url_for('main.item_detail', item_id=item_id))

    claim_id = add_claim(
        found_item_id=item_id,
        claimant_name=claimant_name,
        roll_number=roll_number,
        department=department,
        mobile=mobile,
        proof_ownership=proof_ownership,
        description=description,
        proof_image=proof_image
    )

    flash('Your claim request has been submitted to college admin for verification!', 'success')
    return redirect(url_for('main.item_detail', item_id=item_id))

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')
