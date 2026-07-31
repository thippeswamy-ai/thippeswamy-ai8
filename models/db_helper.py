import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "database.db"

def get_db_path(app=None):
    if app and app.config.get("DATABASE"):
        return app.config["DATABASE"]
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, DB_NAME)

def get_db_connection(db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None, schema_path=None):
    if db_path is None:
        db_path = get_db_path()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if schema_path is None:
        schema_path = os.path.join(base_dir, "schema.sql")

    conn = get_db_connection(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    
    # Migration: Ensure role column exists in Admin table
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Admin)")
    columns = [col[1] for col in cursor.fetchall()]
    if "role" not in columns:
        cursor.execute("ALTER TABLE Admin ADD COLUMN role TEXT DEFAULT 'admin'")

    # Create or update default Super Admin
    cursor.execute("SELECT id, role FROM Admin WHERE username = ?", ("admin",))
    row = cursor.fetchone()
    if not row:
        hashed = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO Admin (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
            ("admin", hashed, "admin@college.edu", "super_admin")
        )
    else:
        # Upgrade existing admin user to super_admin
        cursor.execute("UPDATE Admin SET role = 'super_admin' WHERE username = ?", ("admin",))
        
    conn.commit()
    conn.close()

def seed_sample_data(db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Check if sample found items already exist
    cursor.execute("SELECT COUNT(*) FROM Found_Items")
    if cursor.fetchone()[0] == 0:
        sample_found = [
            ("Alex Johnson", "Computer Science", "9876543210", "Blue Water Bottle", "Personal Accessories",
             "Stainless steel hydro flask with college stickers.", "Central Library 2nd Floor", "2026-07-28", "sample_bottle.svg", "Available"),
            ("Priya Sharma", "Electronics", "9876543211", "Scientific Calculator FX-991EX", "Electronics",
             "Casio calculator in black color with name tag.", "Lab 3, Academic Block", "2026-07-27", "sample_calc.svg", "Available"),
            ("Rahul Verma", "Mechanical Eng", "9876543212", "Leather Wallet with ID", "Wallets & Cards",
             "Brown leather wallet containing college ID and library card.", "College Canteen Ground Floor", "2026-07-26", "sample_wallet.svg", "Available"),
            ("Sneha Patel", "Civil Eng", "9876543213", "Engg Drawing Tool Set", "Stationery & Books",
             "Compass set with scales in blue plastic container.", "Auditorium Hall B", "2026-07-25", "sample_tools.svg", "Available")
        ]
        cursor.executemany(
            """INSERT INTO Found_Items 
               (finder_name, department, mobile, item_name, category, description, place_found, date_found, image_path, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            sample_found
        )

    # Check if sample lost items exist
    cursor.execute("SELECT COUNT(*) FROM Lost_Items")
    if cursor.fetchone()[0] == 0:
        sample_lost = [
            ("Rohan Das", "CS-2023-045", "Computer Science", "9123456789", "Black Wireless Earbuds", "Electronics",
             "Sony WF-1000XM4 in black charging case.", "Near Sports Complex", "2026-07-27", None, "Active"),
            ("Ananya Roy", "EC-2022-089", "Electronics", "9123456788", "Data Structures Textbook", "Stationery & Books",
             "Tanenbaum book with green cover highlighting on chapter 4.", "Seminar Hall 1", "2026-07-26", None, "Active")
        ]
        cursor.executemany(
            """INSERT INTO Lost_Items
               (student_name, roll_number, department, mobile, item_name, category, description, location_lost, date_lost, image_path, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            sample_lost
        )

    conn.commit()
    conn.close()

# --- ADMIN FUNCTIONS ---
def verify_admin(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Admin WHERE username = ?", (username,))
    admin = cursor.fetchone()
    conn.close()
    if admin and check_password_hash(admin["password_hash"], password):
        return admin
    return None

def get_admin_by_id(admin_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Admin WHERE id = ?", (admin_id,))
    admin = cursor.fetchone()
    conn.close()
    return admin

def get_all_admins():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role, created_at FROM Admin ORDER BY id ASC")
    admins = cursor.fetchall()
    conn.close()
    return admins

def add_admin(username, password, email=None, role="admin"):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO Admin (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
        (username, hashed, email, role)
    )
    conn.commit()
    admin_id = cursor.lastrowid
    conn.close()
    return admin_id

def update_admin_profile(admin_id, username, email=None, new_password=None, role=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if new_password:
        hashed = generate_password_hash(new_password)
        if role:
            cursor.execute(
                "UPDATE Admin SET username = ?, email = ?, password_hash = ?, role = ? WHERE id = ?",
                (username, email, hashed, role, admin_id)
            )
        else:
            cursor.execute(
                "UPDATE Admin SET username = ?, email = ?, password_hash = ? WHERE id = ?",
                (username, email, hashed, admin_id)
            )
    else:
        if role:
            cursor.execute(
                "UPDATE Admin SET username = ?, email = ?, role = ? WHERE id = ?",
                (username, email, role, admin_id)
            )
        else:
            cursor.execute(
                "UPDATE Admin SET username = ?, email = ? WHERE id = ?",
                (username, email, admin_id)
            )
    conn.commit()
    conn.close()

def delete_admin(admin_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Admin WHERE id = ?", (admin_id,))
    conn.commit()
    conn.close()

# --- LOST ITEMS FUNCTIONS ---
def add_lost_item(student_name, roll_number, department, mobile, item_name, category, description, location_lost, date_lost, image_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Lost_Items 
           (student_name, roll_number, department, mobile, item_name, category, description, location_lost, date_lost, image_path)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (student_name, roll_number, department, mobile, item_name, category, description, location_lost, date_lost, image_path)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id

def get_all_lost_items(status=None, search=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Lost_Items WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (item_name LIKE ? OR description LIKE ? OR location_lost LIKE ? OR category LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])
        
    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()
    return items

def get_lost_item_by_id(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lost_Items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item

def update_lost_item(item_id, item_name, category, description, location_lost, date_lost, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Lost_Items 
           SET item_name=?, category=?, description=?, location_lost=?, date_lost=?, status=?
           WHERE id=?""",
        (item_name, category, description, location_lost, date_lost, status, item_id)
    )
    conn.commit()
    conn.close()

def delete_lost_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Lost_Items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

# --- FOUND ITEMS FUNCTIONS ---
def add_found_item(finder_name, department, mobile, item_name, category, description, place_found, date_found, image_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Found_Items 
           (finder_name, department, mobile, item_name, category, description, place_found, date_found, image_path)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (finder_name, department, mobile, item_name, category, description, place_found, date_found, image_path)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id

def get_all_found_items(status=None, category=None, search=None, limit=None, offset=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Found_Items WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if category and category != 'All':
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (item_name LIKE ? OR description LIKE ? OR place_found LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
        
    query += " ORDER BY created_at DESC"
    
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
        if offset is not None:
            query += " OFFSET ?"
            params.append(offset)
            
    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()
    return items

def count_found_items(status=None, category=None, search=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM Found_Items WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if category and category != 'All':
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (item_name LIKE ? OR description LIKE ? OR place_found LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
        
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_found_item_by_id(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Found_Items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item

def update_found_item(item_id, item_name, category, description, place_found, date_found, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Found_Items 
           SET item_name=?, category=?, description=?, place_found=?, date_found=?, status=?
           WHERE id=?""",
        (item_name, category, description, place_found, date_found, status, item_id)
    )
    conn.commit()
    conn.close()

def delete_found_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Found_Items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

# --- CLAIMS FUNCTIONS ---
def add_claim(found_item_id, claimant_name, roll_number, department, mobile, proof_ownership, description=None, proof_image=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Claims 
           (found_item_id, claimant_name, roll_number, department, mobile, proof_ownership, description, proof_image)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (found_item_id, claimant_name, roll_number, department, mobile, proof_ownership, description, proof_image)
    )
    conn.commit()
    claim_id = cursor.lastrowid
    conn.close()
    return claim_id

def get_all_claims(status=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT c.*, f.item_name, f.category, f.image_path as found_image, f.place_found
        FROM Claims c
        JOIN Found_Items f ON c.found_item_id = f.id
    """
    params = []
    if status:
        query += " WHERE c.status = ?"
        params.append(status)
        
    query += " ORDER BY c.created_at DESC"
    cursor.execute(query, params)
    claims = cursor.fetchall()
    conn.close()
    return claims

def get_claim_by_id(claim_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, f.item_name, f.category, f.image_path as found_image, f.place_found, f.finder_name, f.mobile as finder_mobile
        FROM Claims c
        JOIN Found_Items f ON c.found_item_id = f.id
        WHERE c.id = ?
    """, (claim_id,))
    claim = cursor.fetchone()
    conn.close()
    return claim

def update_claim_status(claim_id, status, admin_notes=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Claims SET status=?, admin_notes=? WHERE id=?", (status, admin_notes, claim_id))
    
    # If approved, update the corresponding found item status to 'Claimed'
    if status == 'Approved':
        cursor.execute("SELECT found_item_id FROM Claims WHERE id=?", (claim_id,))
        res = cursor.fetchone()
        if res:
            found_item_id = res['found_item_id']
            cursor.execute("UPDATE Found_Items SET status='Claimed' WHERE id=?", (found_item_id,))
            # Reject other pending claims for this item
            cursor.execute("UPDATE Claims SET status='Rejected', admin_notes='Item claimed by another verified owner.' WHERE found_item_id=? AND id!=? AND status='Pending'", (found_item_id, claim_id))

    conn.commit()
    conn.close()

def delete_claim(claim_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Claims WHERE id = ?", (claim_id,))
    conn.commit()
    conn.close()

# --- DASHBOARD METRICS ---
def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Lost_Items WHERE status='Active'")
    total_lost = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Found_Items WHERE status='Available'")
    total_found = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Claims WHERE status='Pending'")
    pending_claims = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Claims WHERE status='Approved'")
    reunited_count = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_lost": total_lost,
        "total_found": total_found,
        "pending_claims": pending_claims,
        "reunited_count": reunited_count
    }
