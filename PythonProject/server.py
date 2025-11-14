import sqlite3
import hashlib
import socket
import threading
from datetime import datetime

currDate = datetime.now()
def setup_database():
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON;")

    #--- User Data ---#
    cur.execute("""
        CREATE TABLE IF NOT EXISTS userdata (
            id INTEGER PRIMARY KEY, 
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            registry TEXT NOT NULL     
        )
    """)

    #--- User Cart ---#
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            item_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL, 
            added_on TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES userdata (id)
        )
    """)

    #--- Vehicle ---#
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id INTEGER PRIMARY KEY,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)

    #--- Parts ---#
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            part_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            manufacturer TEXT,
            description TEXT,
            price REAL,
            category TEXT
        )
    """)
    # Look into part images (sqlite3 image storing)

    #--- Compatibility ---#
    cur.execute("""
        CREATE TABLE IF NOT EXISTS compatibility (
            compatibility_id INTEGER PRIMARY KEY,
            part_id INTEGER,
            vehicle_id INTEGER,
            FOREIGN KEY(part_id) REFERENCES parts(part_id),
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
        )
    """)

    #--- My Projects ---#
    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            date_created TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES userdata(id)
        )
    """)

    #--- Project Parts Link ---#
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_parts (
            link_id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            part_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
            FOREIGN KEY(part_id) REFERENCES parts(part_id)
        ) 
    """)

    #--- Messages ---#
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES userdata(id)
        )
    """)

    #--- Profile Pictures ---#
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profile_pictures(
                pic_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                image BLOB NOT NULL,
                FOREIGN KEY(user_id) REFERENCES userdata(id)
            )
        """)

    conn.commit()
    conn.close()

def add_project(c, user_id, project_name):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    try:
        if not project_name.strip():
            return c.send("Project name cannot be empty.".encode())

        r_date = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    
        cur.execute(
            "INSERT INTO projects (user_id, project_name, date_created) VALUES (?, ?, ?)", 
            (user_id, project_name, r_date)
        )
        conn.commit()
        c.send(f"Project '{project_name}' added successfully.".encode())
        
    except Exception as e:
        c.send(f"Error adding project: {e}".encode())
    finally:
        conn.close()
    
def add_part_to_project(c, project_id, part_id, quantity=1):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    try:
        if quantity <= 0:
            return c.send("Invalid number".encode())

        cur.execute("SELECT 1 FROM projects WHERE project_id = ?", (project_id,))
        if cur.fetchone() is None:
            return c.send(f"Project ID {project_id} does not exist.".encode())

        cur.execute("SELECT 1 FROM parts WHERE part_id = ?", (part_id,))
        if cur.fetchone() is None:
            return c.send(f"Part ID {part_id} does not exist.".encode())

        cur.execute(
            "SELECT link_id, quantity FROM project_parts WHERE project_id = ? AND part_id = ?", 
            (project_id, part_id)
        )

        existing = cur.fetchone()
        if existing:
            new_qty = existing[1] + quantity
            cur.execute(
                "UPDATE project_parts SET quantity = ? WHERE link_id = ?",
                (new_qty, existing[0])
            )
            c.send(f"Updated part {part_id} quantity to {new_qty} in project {project_id}.".encode())
        else:
            cur.execute(
                "INSERT INTO project_parts (project_id, part_id, quantity) VALUES (?, ?, ?)",
                (project_id, part_id, quantity)
            )
            c.send(f"Added part {part_id} with quantity {quantity} to project {project_id}.".encode())

        conn.commit()
    
    except Exception as e:
        c.send(f"Error adding project: {e}".encode())
    finally:
        conn.close()

        

def login_user(c, username, hashed_password):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, hashed_password))
    result = cur.fetchone()
    print(result)

    if result:
        c.send("login successful".encode())
        uId = str(result[0])
        registry_data = str(result[3])
        c.send(("Account Registered: "+registry_data).encode())
        c.send(("User ID: "+uId).encode())
    else:
        c.send("login failed".encode())
    
    conn.close()

def register_user(c, username, hashed_password):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()
    
    try:
        r_date = currDate.strftime("%m/%d/%Y %I:%M:%S %p")
        cur.execute("INSERT INTO userdata (id, username, password, registry) VALUES (?, ?, ?, ?)", (cur.lastrowid, username, hashed_password, r_date))
        conn.commit()
        c.send("Registration successful! You can now log in.".encode())
    except sqlite3.IntegrityError:
        c.send("Username already exists.".encode())
    finally:
        conn.close()

def handle_connection(c):
    try:
        msg = c.recv(1024).decode().strip()

        if msg.startswith("l:"):
            _, username, password = msg.split(":")
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            login_user(c, username, hashed_password)

        elif msg.startswith("r:"):
            _, username, password = msg.split(":")
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            register_user(c, username, hashed_password)

        elif msg.startswith("proj:"):
            try:
                _, user_id_str, project_name = msg.split(":", 2) 
                user_id = int(user_id_str)
                add_project(c, user_id, project_name) 
            except Exception as e:
                c.send(f"Error creating project: {e}".encode())

        elif msg.startswith("addprojpart:"):
            try:
                _, project_id_str, part_id_str, qty_str = msg.split(":")
                project_id = int(project_id_str)
                part_id = int(part_id_str)
                quantity = int(qty_str)
                add_part_to_project(c, project_id, part_id, quantity)
            except Exception as e:
                c.send(f"Invalid addprojpart command or data: {e}".encode())

        elif msg.startswith("add:"):
            _, user_id, part_id, qty = msg.split(":")
            add_to_cart(c, int(user_id), int(part_id), int(qty))

        else:
            c.send("Invalid command.".encode())

    except Exception as e:
        print(f"Client disconnected unexpectedly: {e}")
        c.send(f"Error: {e}".encode())
    finally:
        c.close()

def add_to_cart(c, user_id, part_id, qty):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()
    try:
        if qty <= 0:
            return c.send("Quantity must be positive.".encode())

        cur.execute("SELECT * FROM parts WHERE part_id = ?", (part_id,))
        if cur.fetchone() is None:
            return c.send("Part does not exist.".encode())

        cur.execute("SELECT quantity FROM cart_items WHERE user_id = ? AND item_id = ?", (user_id, part_id))
        existing = cur.fetchone()
        if existing:
            new_qty = existing[0] + qty
            cur.execute(
                "UPDATE cart_items SET quantity = ?, added_on = ? WHERE user_id = ? AND item_id = ?",
                (new_qty, datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"), user_id, part_id)
            )
        else:
            cur.execute(
                "INSERT INTO cart_items (user_id, item_id, quantity, added_on) VALUES (?, ?, ?, ?)",
                (user_id, part_id, qty, datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
            )

        conn.commit()
        c.send(f"Cart updated successfully for user {user_id}".encode())

    except Exception as e:
        c.send(f"Error adding to cart: {e}".encode())
    finally:
        conn.close()


setup_database()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9000))
server.listen()
print("Sever is listening: localhost:9000")


while True:
    client, addr = server.accept()
    threading.Thread(target=handle_connection, args=(client,)).start()