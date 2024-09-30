import sqlite3
from datetime import datetime, timedelta
import uuid

def createDatabase(database):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Create the 'users' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            idUser INTEGER PRIMARY KEY,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            pwd TEXT NOT NULL,
            isAdmin BOOLEAN NOT NULL DEFAULT FALSE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            idOffer INTEGER PRIMARY KEY,
            idUser INTEGER NOT NULL,
            status TEXT CHECK(status IN ('buy', 'sell')) NOT NULL DEFAULT 'buy',
            coin TEXT NOT NULL,
            ammount float NOT NULL,
            FOREIGN KEY (idUser) REFERENCES users (idUser)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            idOrder INTEGER PRIMARY KEY,
            idOffer INTEGER NOT NULL,
            idUser INTEGER NOT NULL,
            status TEXT CHECK(status IN ('New', 'Pending', 'In Progress', 'Confirmed', 'Closed')) NOT NULL DEFAULT 'New',
            ammount float NOT NULL,
            FOREIGN KEY (idOffer) REFERENCES offers (idOffer),
            FOREIGN KEY (idUser) REFERENCES users (idUser)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            idMessage INTEGER PRIMARY KEY,
            idOrder INTEGER NOT NULL,
            idSender INTEGER NOT NULL,
            message TEXT NOT NULL,
            sendingTime TEXT NOT NULL,
            FOREIGN KEY (idOrder) REFERENCES orders (idOrder),
            FOREIGN KEY (idSender) REFERENCES users (idUser)
        )
    ''')

    # Create the 'reset Password Request' table with foreign keys
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resetPasswordRequest (
            requestID INTEGER PRIMARY KEY,
            requestKey TEXT NOT NULL,
            idUser INTEGER NOT NULL,
            expDate TEXT NOT NULL,
            used BOOLEAN NOT NULL DEFAULT FALSE,
            FOREIGN KEY (idUser) REFERENCES users (idUser)
        )
    ''')


def check_email_exists(database, email):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))

    # Fetch the result
    user = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if the user exists

    return user if user is not None else None

def check_username_exists(database, username):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))

    # Fetch the result
    user = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if the user exists

    return user if user is not None else None

def insert_user(database, fname, lname, username, email, password, isAdmin = False):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Insert a new user into the 'users' table
    cursor.execute('''
        INSERT INTO users (firstName, lastName, username, email, pwd, isAdmin)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (fname, lname, username, email, password, isAdmin))

    # Commit the changes to the database
    conn.commit()

    # Get the last inserted row ID (user ID)
    user_id = cursor.lastrowid

    # Close the connection
    conn.close()

    return user_id

def check_user_exists(database, usernameORemail, password):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM users WHERE (username = ? or email = ?) and pwd = ?', (usernameORemail, usernameORemail, password))

    # Fetch the result
    user = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if the user exists

    return user if user is not None else None

def createResetPasswordRequest(database, idUser):
    # Connect to the SQLite database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    current_timestamp = datetime.now()

    cursor.execute('SELECT * FROM resetPasswordRequest WHERE idUser = ? and expDate > ? and used = FALSE', (idUser, str(current_timestamp)))

    # Fetch the result
    haveActiveRequest = cursor.fetchone()

    if haveActiveRequest is not None:
        conn.close()
        return haveActiveRequest[1]
    else:
        requestKey = str(uuid.uuid4())
        new_timestamp = current_timestamp + timedelta(minutes=15)
        cursor.execute('''
            INSERT INTO resetPasswordRequest (requestKey, idUser, expDate)
            VALUES (?, ?, ?)
        ''', (requestKey, idUser, str(new_timestamp)))
        conn.commit()
        conn.close()
        return requestKey

def resetPasswordRequestExist(database, requestKEY):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    current_timestamp = datetime.now()
    cursor.execute('SELECT * FROM resetPasswordRequest WHERE requestKey = ? and expDate > ? and used = FALSE', (requestKEY, str(current_timestamp)))
    requestExistAndActive = cursor.fetchone()
    if requestExistAndActive is None:
        conn.close()
        return False
    else:
        conn.close()
        return True

def resetPasswordRequestClose(database, requestKEY, newPassword):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resetPasswordRequest WHERE requestKey = ?', (requestKEY, ))
    requestdata = cursor.fetchone()
    userID = requestdata[2]
    cursor.execute('''UPDATE users SET pwd = ? WHERE idUser = ?''', (newPassword, userID))
    conn.commit()
    cursor.execute('UPDATE resetPasswordRequest SET used = TRUE WHERE requestKey = ?', (requestKEY, ))
    conn.commit()
    conn.close()
    return userID




def insertOffer(database, offerType, offerCoin, ammount, idUser):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Insert a new user into the 'users' table
    cursor.execute('''
        INSERT INTO offers (status, coin, ammount, idUser)
        VALUES (?, ?, ?, ?)
    ''', (offerType, offerCoin, ammount, idUser))

    # Commit the changes to the database
    conn.commit()

    # Get the last inserted row ID (user ID)
    odderID = cursor.lastrowid

    # Close the connection
    conn.close()

    return odderID

def GetMyOffers(database, userID):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM offers WHERE idUser = ?', (userID, ))

    # Fetch the result
    offers = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return offers if offers is not None else None


def GetOffers(database):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM offers')

    # Fetch the result
    offers = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return offers if offers is not None else None

def GetOffer(database, idOffer):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM offers where idOffer = ?', (idOffer, ))

    # Fetch the result
    offers = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return offers if offers is not None else None

def GetIsAdmin(database, idUser):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT isAdmin FROM users where idUser = ?', (idUser, ))

    # Fetch the result
    user = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return user if user is not None else None

def GetUser(database, idUser):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT firstName, lastName FROM users where idUser = ?', (idUser, ))

    # Fetch the result
    user = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return user if user is not None else None

def editOfferDB(database, offerID, offerType, offerCoin, ammount):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Insert a new user into the 'users' table
    cursor.execute('''
        UPDATE offers SET status = ?, coin = ?, ammount = ? WHERE idOffer = ?
    ''', (offerType, offerCoin, ammount, offerID))

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()

    return True


def editOrderStatusDB(database, idOrder, status):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Insert a new user into the 'users' table
    cursor.execute('''
        UPDATE orders SET status = ? WHERE idOrder = ?
    ''', (status, idOrder))

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()

    return True

def deleteOfferDB(database, offerID):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Insert a new user into the 'users' table
    cursor.execute('''
        DELETE FROM offers WHERE idOffer = ?
    ''', (offerID,))

    # Commit the changes to the database
    conn.commit()


    # Close the connection
    conn.close()

    return True


def GetOrderByID(database, idOrder):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM orders where idOrder = ?', (idOrder, ))

    # Fetch the result
    orders = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return orders if orders is not None else None

def GetOrderByOfferID(database, idOffer):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM orders where idOffer = ?', (idOffer, ))

    # Fetch the result
    orders = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return orders if orders is not None else None

def GetOrders(database, idUser):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM orders where idUser = ?', (idUser, ))

    # Fetch the result
    orders = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return orders if orders is not None else None


def GetAllOrders(database):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM orders')

    # Fetch the result
    orders = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return orders if orders is not None else None

def insertOrder(database, idOffer, idUser):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Insert a new user into the 'users' table
    cursor.execute('''
        INSERT INTO orders (idOffer, idUser, status, ammount)
        VALUES (?, ?, ?, ?)
    ''', (idOffer, idUser, 'New', 0))

    # Commit the changes to the database
    conn.commit()

    # Get the last inserted row ID (user ID)
    orderID = cursor.lastrowid

    # Close the connection
    conn.close()

    return orderID




def GetOrderMessagesByID(database, idOrder):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM messages where idOrder = ?', (idOrder, ))

    # Fetch the result
    orders = cursor.fetchall()

    # Close the connection
    conn.close()

    # Check if the user exists

    return orders if orders is not None else None



def insertMessage(database, idOrder, idSender, message, sendingTime):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Insert a new user into the 'users' table
    cursor.execute('''
        INSERT INTO messages (idOrder, idSender, message, sendingTime)
        VALUES (?, ?, ?, ?)
    ''', (idOrder, idSender, message, sendingTime))

    # Commit the changes to the database
    conn.commit()

    # Get the last inserted row ID (user ID)
    messageID = cursor.lastrowid

    # Close the connection
    conn.close()

    return messageID
