

### This file is extracted from DOCS SOME ISSUES MAY OCCUR
### Original file will be updated soon.


import mysql.connector
from tabulate import tabulate

DB_HOST = 'localhost'
DB_NAME = 'complaint_system_24x7'
DB_USER = 'root'
DB_PASS = ''
# L_USER: Logged in User
conn = cursor = L_USER = None
def intro():
    print("\nWelcome To COMPLAINT SYSTEM 24x7\nMade By: Arpit Patel & Dilip\n")
    connect_db()
    main_menu()
def connect_db():
    global conn, cursor
    try:
        conn = mysql.connector.connect(host = DB_HOST, user = DB_USER, password = DB_PASS)
        cursor = conn.cursor(dictionary = True)
        cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}';")
        if cursor.fetchone():
            cursor.execute(f"USE {DB_NAME};")
        else:
            create_db()
            insert_data()
    except mysql.connector.Error as err:
        closeApp(error = f"Database connection error: {err}")
    except Exception as e:
        closeApp(error = f"Error: {e}")
def create_db():
    cursor.execute(f"CREATE DATABASE {DB_NAME};")
    cursor.execute(f"USE {DB_NAME};")
    cursor.execute("""
        CREATE TABLE users (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            mobile VARCHAR(15) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            address TEXT,
            user_type ENUM('User','Worker','Manager','Admin') DEFAULT 'User',
            manager_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES users(user_id)
        );
    """)
    cursor.execute("""
        CREATE TABLE complaints (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT,
            worker_id INT DEFAULT NULL,
            service_id INT DEFAULT NULL,
            details TEXT,
            status ENUM('Pending','In Progress','Completed','Rated','Rejected') DEFAULT
            'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE
            CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (worker_id) REFERENCES users(user_id),
            INDEX (status)
        );
    """)
    cursor.execute("""
        CREATE TABLE complaint_history (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT,
            complaint_id INT,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (complaint_id) REFERENCES complaints(id)
        );
    """)
    cursor.execute("""
        CREATE TABLE services (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
def insert_table(table, data = {}):
    values = list(data.values())
    cursor.execute(f"INSERT INTO {table} (" + ",".join(list(data.keys())) + ") VALUES ( " + ",".join(["%s"] * len(values)) + ")", values)
    conn.commit()
    return cursor.lastrowid
def update_table(table, data = {}, where = {}):
    cursor.execute(f"UPDATE {table} SET " + ",".join([field + "=%s" for field in
    data.keys()]) + " WHERE " + " AND ".join([key + "=%s" for key in where.keys()]), list(data.values()) + list(where.values()))
    conn.commit()
    return cursor.rowcount
def insert_data():
    insert_table('users', { 'name': 'Admin', 'mobile': '1234567890', 'email':"admin@complaint_system_24x7.com", 'password': "Password@123", 'address': 'Admin Address', 'user_type': 'Admin' })
    
    manager_id = insert_table('users', { 'name': 'Manager', 'mobile': '9876543210', 'password': "Password@123", 'user_type': 'Manager' })

    insert_table('users', {'name': 'Worker', 'mobile': '1111111111', 'password':"Password@1111111111", 'user_type': 'Worker', 'manager_id': manager_id})

    user_id = insert_table('users', {'name': 'User', 'mobile': '2222222222', 'password':"Password@2222222222", 'user_type': 'User'})
 
    for name, description in [
        ('Electrician', 'Electrician service.'),
        ('Plumber', 'Plumber service.'),
        ('Fan Repair', 'Fan repair service.'),
        ('Fan Installation', 'Fan installation service.'),
        ('Other', 'Other service.'),
    ]:
        service_id = insert_table('services', {'name': name, 'description': description})
        insert_table('complaints', {'user_id': user_id, 'service_id': service_id, 'details': 'Test Complaint for ' + name})

    conn.commit()
def main_menu():
    while True:
        try:
            L_USER and user_menu()
            valid_input('option', 'Choose an option:', options = {'Register': register, 'Login': login, 'Exit': closeApp}, title = 'Main Menu')()
        except KeyboardInterrupt:
            closeApp()
        except mysql.connector.Error as err:
            closeApp('MySQL error: ' + str(err))
        except Exception as err:
            closeApp('Error: ' + str(err))
def register():
    global L_USER
    print("\nEnter your details to register: ")
    user_id = add_update_user(success_msg = 'Registration successful!', error_msg = 'Registration failed. Please try again.')
    if user_id:
        return login(user_id)
    else:
        return False
def login(user_id = None):
    global L_USER
    if user_id:
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    else:
        mobile = valid_input('text', "Enter your mobile number", required = True)
        password = valid_input('text', 'Enter your password', required = True)
        cursor.execute("SELECT * FROM users WHERE mobile=%s AND password=%s", (mobile, password))
        user = cursor.fetchone()
    if not user:
        print("\nLogin failed. Please try again.")
        return False
    del user['password']
    L_USER = user
    print("\nWelcome,", L_USER['name'], " !\n")
    return True
def refresh_db_connection():
    global conn, cursor
    try:
        cursor.close()
        conn.close()
        conn.connect()
        cursor = conn.cursor(dictionary = True)
        cursor.execute(f"USE {DB_NAME};")
    except mysql.connector.Error as err:
        closeApp(error = f"Database connection refresh error: {err}")


#### USER MENU ####
def user_menu():
    refresh_db_connection()
    if not L_USER:
        return False
    options = {
        'User': {
            'New Complaint': new_complaint,
            'Rate/Feedback Complaint': rate_complaint,
        },
        'Worker': {
            'Complete Complaint': complete_complaint,
            'Reject Complaint': reject_complaint,
        },
        'Manager': {
            'Assign Complaint': assign_complaint,
            'Complete Complaint': complete_complaint,
            'Reject Complaint': reject_complaint,
            'Add Worker': add_worker,
            'View Users/Workers': view_users_by_type,
        },
        'Admin': {
            'Add Manager': add_manager,
            'Add Service': add_service,
            'Update Service': update_service,
            'View Services': view_services,
            'View Users/Workers/Managers': view_users_by_type,
        },
    }[L_USER['user_type']]
    options.update({
        'View Complaints': view_complaints,
        'View Complaint History': view_complaint_history,
        'View Profile': view_profile,
        'Update Profile': update_profile,
        'Logout': logout,
    })
    valid_input('option', 'Choose an option:', options = options, title = L_USER['user_type'] + ' Menu')()
    user_menu()


#### USER ####
def new_complaint():
    cursor.execute("SELECT * FROM services")
    list_data(cursor.fetchall(), 'No services found.', 'SERVICES')
    services = {service['id']: service['name'] for service in services}
    while True:
        service_id = valid_input('digits', 'Enter service ID', required = True)
        if service_id in services.keys():
            break
        print("\nInvalid service ID. Please try again.")
    complaint_id = insert_table('complaints', {
    'user_id': L_USER['user_id'],
    'service_id': service_id,
    'details': valid_input('text', 'Enter your complaint details', required = True),
    })
    print("\nComplaint submitted successfully!")
    add_complaint_history(complaint_id = complaint_id, remarks = 'Complaint submitted for ' + services[service_id])
def rate_complaint(complaint_id = None):
    complaint = get_complaint_details(complaint_id)
    if not complaint:
        return False
    if complaint['status'] in ['Rated', 'Rejected']:
        print(f"\nComplaint already {complaint['status']}.")
        return False
    if complaint['status'] not in ['Completed']:
        print("\nComplaint not completed yet.")
        return False
    while True:
        rating = valid_input('digits', "Enter rating (1-5)", required = True)
        if rating in range(1, 6):
            break
        print("\nInvalid rating. Please enter a number between 1 and 5.")
    update_complaint_status(complaint, 'Rated', f"Complaint rated: {rating}")


#### MANAGER ####
def assign_complaint():
    complaint = get_complaint_details()
    if not complaint:
        return False
    if complaint['worker_id']:
        print("\nComplaint already assigned to a Worker.")
        return False
    print("\nSelect a Worker to assign the complaint: ")
    view_users(user_type = 'Worker')
    worker_id = valid_input('digits', "Enter Worker ID", required = True)
    cursor.execute("SELECT * FROM users WHERE user_id=%s AND user_type='Worker' AND manager_id=%s",(worker_id, L_USER['user_id']))
    if not cursor.fetchone():
        print("\nWorker not found or not assigned to you. Please try again.")
        return False
    update_table('complaints', {'worker_id': worker_id}, {'id': complaint['id']})
    update_complaint_status(complaint, 'In Progress', 'Complaint assigned to Worker ID:' + worker_id)
def add_worker():
    user_id = add_update_user('Worker', manager_id = L_USER['user_id'])
    user_id and print("\nWorker Id: ", user_id)


#### WORKER/MANAGER ####
def complete_complaint():
    complaint = get_complaint_details()
    if not complaint:
        return False
    if not complaint['worker_id']:
        print("\nComplaint not assigned to any Worker.")
        return False
    if complaint['status'] not in ['Pending', 'In Progress']:
        print("\nComplaint already " + complaint['status'] + ". Cannot complete again.")
        return False
    update_complaint_status(complaint, 'Completed', 'Complaint completed')
def reject_complaint():
    complaint = get_complaint_details()
    if not complaint:
        return False
    if complaint['status'] not in ['Pending', 'In Progress']:
        print("\nComplaint already resolved.")
        return False
    update_complaint_status(complaint, 'Rejected', 'Complaint rejected')
    
    
#### ADMIN ####
def add_manager():
    user_id = add_update_user('Manager', manager_id = L_USER['user_id'])
    user_id and print("\nManager Id: ", user_id)
def add_service():
    service_id = insert_table('services', {
        'name': valid_input('text', 'Enter service name', required = True),
        'description': valid_input('text', 'Enter service description'),
    })
    print("\nService added successfully!\nService ID: ", service_id)
    view_services()
def view_services():
    cursor.execute("SELECT * FROM services")
    list_data(cursor.fetchall(), 'No services found.')
def update_service():
    view_services()
    service_id = valid_input('digits', "Enter service ID", required = True)
    cursor.execute("SELECT * FROM services WHERE id=%s",(service_id,))
    service = cursor.fetchone()
    if not service:
        print("\nService not found.")
        return False
    service_name = valid_input('text', "Enter new service name", default = service['name'])
    service_description = valid_input('text', "Enter new service description", default = service['description'])
    update_table('services', {'name': service_name, 'description': service_description}, {'id': service_id})
    print("\nService updated successfully!\nService ID: ", service_id)
    view_services()


#### ADMIN/MANAGER ####
def view_users_by_type():
    option_names = ['All', 'User', 'Worker']
    if L_USER['user_type'] == 'Admin':
        option_names.append('Manager')
    view_users(valid_input('option', 'Select a user type to view', 'User', 
        option_names = option_names,
        title = 'VIEW DETAILS',
    ))


#### COMMON ####
def add_update_user(user_type = 'User', user_id = None, manager_id = None, success_msg = None, error_msg = None):
    try:
        if bool(user_id):
            cursor.execute('SELECT * FROM users WHERE user_id=%s', (user_id,))
            user = cursor.fetchone()
            value_error_if(not user, f"{user_type} not found.")
            field = valid_input('option', 'Select a field to update:', options = {
                'Name': 'name',
                'Mobile': 'mobile',
                'Password': 'password',
                'Email': 'email',
                'Address': 'address',
            }, required = True, title = 'UPDATE ' + user_type.upper())
            if field == 'password':
                value = valid_input(field, 'Enter new password') or user[field]
            else:
                value = valid_input(field, f"Enter new {field}", user[field])
            update_table('users', {field: value}, {'user_id': user_id})
            success_msg = success_msg or f"{user_type} updated successfully!"
        else:
            user_id = insert_table(table = 'users', data = {
                'name': valid_input('name', 'Enter name', required = True),
                'mobile': valid_input('mobile', 'Enter mobile number', required = True),
                'password': valid_input('password', 'Enter password', required = True),
                'email': valid_input('email', 'Enter email (optional)'),
                'address': valid_input('address', 'Enter address (optional)'),
                'user_type': user_type,
                'manager_id': manager_id,
            })
            success_msg = success_msg or f"{user_type} added successfully!"
        conn.commit()
        print("\n", success_msg)
        return user_id
    except Exception as e:
        error_msg = error_msg or 'Operation failed. Please try again.'
        print("\n", error_msg, "\nError: ", e)
        return None
def view_complaints():
    searching = valid_input('text', 'Do you want to search for a specific complaint? (y/n)')
    where = "1 "
    data = ()
    if searching == 'y':
        field = valid_input('option', 'Search Using Field:', options = {
            'Complaint ID': 'id',
            'User ID': 'user_id',
            'Worker ID': 'worker_id',
            'Service ID': 'service_id',
            'Status': 'status',
            'Details': 'details',
        }, title = 'SEARCH COMPLAINTS')
        if field == 'id':
            complaint = get_complaint_details()
            list_data(complaint, 'Complaint not found.', 'COMPLAINT DETAILS')
            print("\nComplaint History: ")
            return view_complaint_history(complaint['id'])
        if field in ['user_id', 'worker_id', 'service_id']:
            search_value = valid_input('digits', f"Enter the {field} to search")
        else:
            search_value = valid_input('text', 'Enter the value to search')
        if field == 'details':
            where += f" AND c.details LIKE %s"
            search_value = f"%{search_value}%"
        else:
            where += f" AND c.{field} = %s"
        data = (search_value,)
    if L_USER['user_type'] in ['User', 'Worker']:
        where += f" AND c.{L_USER['user_type'].lower()}_id = {L_USER['user_id']}"
    cursor.execute(f"""
        SELECT
            c.id,c.details,c.status,
            u.name AS user_name,
            u.mobile AS user_mobile,
            s.name AS service_name,
            w.name AS worker_name,
            w.mobile AS worker_mobile,
            updated_at
        FROM complaints c
        LEFT JOIN users u ON c.user_id = u.user_id
        LEFT JOIN users w ON c.worker_id = w.user_id
        LEFT JOIN services s ON c.service_id = s.id
        WHERE {where}
        ORDER BY status ASC,updated_at DESC
    """, data)
    complaints = cursor.fetchall()
    list_data(complaints, 'No complaints found.')
    if not complaints:
        L_USER['user_type'] == 'Worker' and print('Any complaints assigned to you will be shown here.')
    return False
def view_complaint_history(complaint_id = None):
    complaint = get_complaint_details(complaint_id)
    if not complaint:
        return False
    list_data({
        'id': complaint['id'],
        'details': complaint['details'],
        'status': complaint['status'],
        'created_at': complaint['created_at'],
        'updated_at': complaint['updated_at'],
    }, title = "Complaint Details: ")
    cursor.execute("""
        SELECT ch.id,ch.user_id,u.name AS name,u.mobile AS mobile,u.user_type,ch.remarks,ch.created_at
        FROM complaint_history ch,users u
        WHERE ch.complaint_id=%s AND ch.user_id = u.user_id
        ORDER BY ch.created_at DESC
    """,(complaint['id'],))
    list_data(cursor.fetchall(), 'No history found.')
def view_profile():
    list_data(L_USER, title = 'Profile Details: ')
    if L_USER['manager_id']:
        cursor.execute('SELECT name,mobile,email FROM users WHERE user_id =' + L_USER['manager_id'])
    list_data(cursor.fetchone(), 'Manager not found.', 'Manager Details: ')
def update_profile():
    global L_USER
    view_profile()
    add_update_user(user_id = L_USER['user_id'], success_msg = 'Profile updated successfully!', error_msg = 'Profile update failed. Please try again.')
    refresh_db_connection()
    login(L_USER['user_id'])
def logout():
    global L_USER
    L_USER = None
    print("\nLogged out successfully!")


#### FUNCTIONS ####
def view_users(user_type = 'User'):
    if user_type == 'All':
        user_type = None
        where = '1 '
    if user_type in ['User', 'Worker', 'Manager']:
        where += f" AND user_type='{user_type}'"
    if user_type in ['Worker', 'Manager']:
        where += f" AND manager_id = {L_USER['user_id']}"


    columns = 'user_id AS id, name, mobile, email, address'
    if where.find('user_type') == -1:
        columns += ',user_type'
    cursor.execute('SELECT ' + columns + ' FROM users WHERE ' + where)
    list_data(cursor.fetchall(), 'No ' + user_type + 's found.')
def get_complaint_details(complaint_id = None):
    if complaint_id is None:
        complaint_id = valid_input('digits', 'Enter complaint ID', required = True)
    sql = "SELECT * FROM complaints WHERE id=%s"
    if L_USER['user_type'] in ['User', 'Worker']:
        sql += f" AND {L_USER['user_type'].lower()}_id = {L_USER['user_id']}"
        cursor.execute(sql, (complaint_id,))
        complaint = cursor.fetchone()
    not complaint and print("\n",{
        'User': 'Complaint not found or not submitted by you.',
        'Worker': 'Complaint not found or not assigned to you.',
        'Manager': 'Complaint not found.',
    }[L_USER['user_type']])
    return complaint or False
def update_complaint_status(complaint, new_status, remarks):
    update_table('complaints', {'status': new_status}, {'id': complaint['id']})
    add_complaint_history(complaint, remarks = remarks)
    if cursor.rowcount > 0:
        print(f"\nComplaint {new_status.lower()} successfully!")
    else:
        print(f"\nComplaint {new_status.lower()} failed. Please try again.")
def add_complaint_history(complaint = None, complaint_id = None, remarks = None):
    complaint = complaint or get_complaint_details(complaint_id)
    if not complaint:
        return False
    insert_table('complaint_history', {
        'complaint_id': complaint['id'],
        'user_id': L_USER['user_id'],
        'remarks': valid_input('text', 'Enter remarks', required = remarks is None, default = remarks),
    })
    return cursor.rowcount > 0
def list_data(data, nodata = 'No data found.', title = None):
    if type(data) not in [list, dict] or len(data) == 0:
        print("\n", nodata)
        return
    title and print(title)
    headers = 'keys'
    if type(data) == list and all([type(item) == dict for item in data]):
        pass
    elif type(data) == dict:
        data = data.items()
        headers = ['-', '-']
    else:
        print("\nInvalid data format.")
        return
    print(tabulate(data, headers, tablefmt = 'grid'))
def closeApp(error = None):
    try:
        error and print("\nError: ", error)
        if error or input("\nAre you sure you want to exit application? (Enter 'y' to exit):") == 'y':
            pass # Continue closing the app
        else:
            return
        cursor and cursor.close()
        conn and conn.close()
        print("\n\nThank you for using COMPLAINT SYSTEM 24x7. We are glad to help you.\n\n")
        exit()
    except KeyboardInterrupt:
        closeApp()

    
#### VALIDATIONS ####
def valid_input(type, text, default = None, required = False, options = {}, option_names=[], title = None):
    while True:
        try:
            if not text.endswith(':'):
                if default:
                    text += f" [{default}]"
                text += ':'

            title and print(f"\n{title}\n")
            if type == 'option':
                return input_options(text, options, option_names, default, required)
            value = input_value = input(text + ' ')
            if not value:
                value_error_if(required, "This field is required.")
                return default
            types = {
                'mobile': validate_mobile,
                'email': validate_email,
                'name': validate_name,
                'password': validate_password,
                'digits': validate_digits,
            }
            if type in types.keys():
                return (types[type])(value)
            return input_value
        except ValueError as e:
            print("\nError: ", e, "\n")
        except Exception as e:
            print("\nError: ", e, "\n")
def input_options(text = 'Select an option: ', options = {}, option_names = [], default = None, required = False):
    if not option_names and options:
        option_names = list(options.keys())
    i = 1
    for name in option_names:
        print(f"{i}. {name}")
        i += 1
    print()
    value = input(text + ' ')
    if value:
        value_error_if((not value.isdigit() or 1 < int(value) > len(option_names)) and not value in option_names, 'Invalid choice. Please try again.')
        option_name = option_names[int(value) - 1]
    elif default:
        option_name = default
    else:
        value_error_if(True, 'Option is required.')
    if options:
        return options[option_name]
    else:
        return option_name
def validate_mobile(value):
    for char in [' ', '-', '+91', '+']:
        value = value.replace(char, "")
    if value[:3] == '091' and len(value) == 13:
        value = value[3:]
    if value[:2] == '91' and len(value) == 12:
        value = value[2:]
    len(value) > 0 and validate_digits(value, 'Mobile number must contain only digits.')
    value_error_if(len(value) != 10, 'Mobile number must be 10 digits long.')
    
    cursor.execute("SELECT * FROM users WHERE mobile=%s", (value,))
    value_error_if(cursor.fetchone(), 'Mobile number already registered with us.')


    return value
def validate_email(value):
    username, *rest = value.strip().split('@')
    value_error_if(value.count('@') != 1, 'Email must contain @ symbol and only once.')
    value_error_if(len(username) == 0, 'Email must contain username.')
    domain = rest[0] or ''
    value_error_if(len(domain) == 0, 'Email must contain domain.')
    value_error_if(domain.count('.') == 0 or '.' in [domain[0], domain[-1]], 'Invalid domain in email.')
    return value
def validate_name(value):
    value_error_if(not value.replace(' ', '').isalpha(), 'Name must contain only alphabets.')
    value_error_if(len(value) < 3, 'Name must be at least 3 characters long.')
    return value
def validate_password(value):
    value_error_if(len(value) < 8, 'Password must be at least 8 characters long.')
    value_error_if(not any(char.isdigit() for char in value), 'Password must contain at least one digit.')
    value_error_if(not any(char.isupper() for char in value), 'Password must contain at least one uppercase letter.')
    value_error_if(not any(char.islower() for char in value), 'Password must contain at least one lowercase letter.')
    return value
def validate_digits(value, msg = 'It must contain only digits.'):
    value_error_if(not value.isdigit(), msg)
    return int(value)
def value_error_if(condition, error):
    if condition:
        raise ValueError(error)


#### MAIN PROGRAM ####
intro() 
