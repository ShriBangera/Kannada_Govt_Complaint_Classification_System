import mysql.connector
from mysql.connector import Error

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # Update with your MySQL password if needed
    'database': 'kannada_complaints',
    'auth_plugin': 'mysql_native_password'
}


def get_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        # If the database doesn't exist (error 1049), try connecting without specifying a database
        err_no = getattr(e, 'errno', None)
        print(f"Error while connecting to MySQL: {e}")
        if err_no == 1049:
            cfg = db_config.copy()
            cfg.pop('database', None)
            try:
                connection = mysql.connector.connect(**cfg)
                return connection
            except Error as e2:
                print(f"Error connecting without database: {e2}")
                return None
        return None


def create_tables():
    """Create all required tables"""
    connection = get_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS kannada_complaints")
        cursor.execute("USE kannada_complaints")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citizens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                department_name VARCHAR(50) NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                password VARCHAR(255) NOT NULL,
                department VARCHAR(50),
                role VARCHAR(20),
                FOREIGN KEY (department) REFERENCES departments(department_name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INT AUTO_INCREMENT PRIMARY KEY,
                citizen_name VARCHAR(100),
                phone VARCHAR(20),
                complaint_text TEXT,
                predicted_department VARCHAR(50),
                confidence FLOAT,
                status VARCHAR(30) DEFAULT 'Pending',
                remarks TEXT,
                assigned_employee_id INT,
                citizen_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (predicted_department) REFERENCES departments(department_name),
                FOREIGN KEY (assigned_employee_id) REFERENCES employees(id),
                FOREIGN KEY (citizen_id) REFERENCES citizens(id)
            )
        """)

        cursor.execute("SHOW COLUMNS FROM complaints LIKE %s", ('remarks',))
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE complaints ADD COLUMN remarks TEXT")

        cursor.execute("SHOW COLUMNS FROM complaints LIKE %s", ('updated_at',))
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE complaints ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")

        cursor.execute("SHOW COLUMNS FROM complaints LIKE %s", ('citizen_id',))
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE complaints ADD COLUMN citizen_id INT")
            cursor.execute("ALTER TABLE complaints ADD CONSTRAINT fk_complaints_citizen FOREIGN KEY (citizen_id) REFERENCES citizens(id)")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaint_updates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                complaint_id INT NOT NULL,
                updated_by INT,
                status VARCHAR(50),
                remarks TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
                FOREIGN KEY (updated_by) REFERENCES employees(id)
            )
        """)

        connection.commit()
        print("✓ All tables created successfully!")
        return True

    except Error as e:
        print(f"Error creating tables: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_tables()


def insert_complaint(complaint_text, predicted_department, confidence, citizen_name=None, phone=None, citizen_id=None, status='Pending'):
    """Insert a complaint and return the new complaint id, or None on error"""
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor()
    try:
        cursor.execute("USE kannada_complaints")
        sql = ("INSERT INTO complaints (citizen_name, phone, complaint_text, predicted_department, confidence, status, citizen_id) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(sql, (citizen_name, phone, complaint_text, predicted_department, float(confidence), status, citizen_id))
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error inserting complaint: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


def register_citizen(name, phone, email, password):
    connection = get_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("INSERT INTO citizens (name, phone, email, password) VALUES (%s, %s, %s, %s)", (name, phone, email, password))
        connection.commit()
        return True
    except Error as e:
        print(f"Error registering citizen: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_citizen_by_credentials(email, password):
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("SELECT * FROM citizens WHERE email = %s AND password = %s LIMIT 1", (email, password))
        return cursor.fetchone()
    except Error as e:
        print(f"Error fetching citizen by credentials: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def get_citizen_by_id(citizen_id):
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("SELECT * FROM citizens WHERE id = %s LIMIT 1", (citizen_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error fetching citizen by id: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def get_citizen_complaints(citizen_id):
    connection = get_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute(
            "SELECT id, complaint_text, predicted_department, status, remarks, created_at, updated_at FROM complaints WHERE citizen_id = %s ORDER BY created_at DESC",
            (citizen_id,)
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching citizen complaints: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def find_employee_for_department(department_name):
    """Return a single employee row (dict) for the given department, or None if none found"""
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("SELECT * FROM employees WHERE department = %s LIMIT 1", (department_name,))
        row = cursor.fetchone()
        return row
    except Error as e:
        print(f"Error finding employee: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def assign_complaint(complaint_id, employee_id):
    """Assign an employee to a complaint and set status to 'Accepted'"""
    connection = get_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("UPDATE complaints SET assigned_employee_id = %s, status = %s WHERE id = %s", (employee_id, 'Accepted', complaint_id))
        connection.commit()
        return True
    except Error as e:
        print(f"Error assigning complaint: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_employee_by_credentials(email, password):
    """Return employee dict if credentials match, else None"""
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("SELECT * FROM employees WHERE email = %s AND password = %s LIMIT 1", (email, password))
        return cursor.fetchone()
    except Error as e:
        print(f"Error fetching employee: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def get_employee_by_email(email):
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("SELECT * FROM employees WHERE email = %s LIMIT 1", (email,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error fetching employee by email: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def ensure_department_exists(department_name):
    connection = get_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("INSERT IGNORE INTO departments (department_name) VALUES (%s)", (department_name,))
        connection.commit()
        return True
    except Error as e:
        print(f"Error ensuring department exists: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def register_employee(name, email, password, department, role='staff'):
    connection = get_connection()
    if connection is None:
        return False

    if not ensure_department_exists(department):
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute(
            "INSERT INTO employees (name, email, password, department, role) VALUES (%s, %s, %s, %s, %s)",
            (name, email, password, department, role)
        )
        connection.commit()
        return True
    except Error as e:
        print(f"Error registering employee: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_employee_by_id(emp_id):
    connection = get_connection()
    if connection is None:
        return None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("SELECT * FROM employees WHERE id = %s LIMIT 1", (emp_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error fetching employee by id: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def get_complaint_by_id(complaint_id):
    connection = get_connection()
    if connection is None:
        return None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("SELECT * FROM complaints WHERE id = %s LIMIT 1", (complaint_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error fetching complaint by id: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def get_complaints_for_department(department_name, status=None):
    """Return list of complaints for a department, optionally filtered by status"""
    connection = get_connection()
    if connection is None:
        return []
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("USE kannada_complaints")
        if status:
            cursor.execute("SELECT * FROM complaints WHERE predicted_department = %s AND status = %s ORDER BY created_at DESC", (department_name, status))
        else:
            cursor.execute("SELECT * FROM complaints WHERE predicted_department = %s ORDER BY created_at DESC", (department_name,))
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching complaints: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def update_complaint_status(complaint_id, status, employee_id=None, remarks=None):
    """Update complaint status and optionally assigned employee and remarks"""
    connection = get_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute("USE kannada_complaints")
        if employee_id and remarks is not None:
            cursor.execute("UPDATE complaints SET status = %s, assigned_employee_id = %s, remarks = %s WHERE id = %s", (status, employee_id, remarks, complaint_id))
        elif employee_id:
            cursor.execute("UPDATE complaints SET status = %s, assigned_employee_id = %s WHERE id = %s", (status, employee_id, complaint_id))
        elif remarks is not None:
            cursor.execute("UPDATE complaints SET status = %s, remarks = %s WHERE id = %s", (status, remarks, complaint_id))
        else:
            cursor.execute("UPDATE complaints SET status = %s WHERE id = %s", (status, complaint_id))
        connection.commit()
        return True
    except Error as e:
        print(f"Error updating complaint status: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def add_complaint_update(complaint_id, updated_by, status, remarks=None):
    """Insert a record into complaint_updates"""
    connection = get_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute("USE kannada_complaints")
        cursor.execute("INSERT INTO complaint_updates (complaint_id, updated_by, status, remarks) VALUES (%s, %s, %s, %s)",
                       (complaint_id, updated_by, status, remarks))
        connection.commit()
        return True
    except Error as e:
        print(f"Error adding complaint update: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()
