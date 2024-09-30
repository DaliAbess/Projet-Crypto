from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room
import os
from db import *
import hashlib

database = "data.db"
app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = '123456789AZERTYUIOP'
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
resetKEY=app.secret_key

#):

print(f'to reset your password please visit this link : http://192.168.1.17/reset?id={resetKEY}\nYour link will expire in 15 Min')
def calculate_sha256(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()
    return sha256_hash

@app.route('/')
def index():
    #Query = request.args.get('data', default='', type=str)
    return render_template('./index.html')


#signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'id' not in list(session.keys()):
        if request.method == 'POST':
            fname = request.form.get('first-name')
            lname = request.form.get('last-name')
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            copassword = request.form.get('copassword')

            if len(fname) > 0 and len(lname) > 0 and  len(username) > 0 and len(email) > 0:
                if len(password) >= 8:
                    if password == copassword:
                        if check_email_exists(database, email) is None and check_username_exists(database, username) is None:
                            session['id'] = insert_user(database, fname, lname, username, email, calculate_sha256(password))
                            return redirect(url_for('index'))
                        else:
                            return render_template('./signup.html', result='L\'utilisateur existe déjà', fname=fname, lname=lname, username=username, email=email)
                    else:
                        return render_template('./signup.html', result='Veuillez vérifier votre mot de passe', fname=fname, lname=lname, username=username, email=email)
                else:
                    return render_template('./signup.html', result='La longueur du mot de passe doit être >= 8', fname=fname, lname=lname, username=username, email=email)
            else:
                return render_template('./signup.html', result='Assurez-vous de remplir tous les champs et d\'accepter les conditions.', fname=fname, lname=lname, username=username, email=email)
        else:
            return render_template('./signup.html')
    else:
        return redirect(url_for('index'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'id' not in list(session.keys()):
        if request.method == 'POST':
            usernameORemail = request.form.get('UsernameOrEmail')
            password = request.form.get('password')
            user = check_user_exists(database, usernameORemail, calculate_sha256(password))
            if user is not None:
                session['id'] = user[0]
                return redirect(url_for('index'))
            else:
                return render_template('./login.html', result='User Not Exist')
        else:
            return render_template('./login.html')
    else:
        return redirect(url_for('index'))

#forget password
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        usernameOrEmail = request.form.get('UsernameOrEmail')
        if usernameOrEmail:
            emailExist = check_email_exists(database, usernameOrEmail)
            usernameExist = check_username_exists(database, usernameOrEmail)
            if emailExist is not None:
                userResetID = emailExist[0]
                userEmail = emailExist[4]
                fullName = f'{emailExist[1]} {emailExist[2]}'
                resetKEY = createResetPasswordRequest(database, userResetID)
                sendResetEmail(userEmail, fullName, resetKEY)
                #sendEmail(userEmail, 'Password Reset', f'to reset your password please visit this link : http://192.168.1.17/reset?id={resetKEY}\nYour link will expire in 15 Min')
                return render_template('./resetPassword.html', resp='Instructions de réinitialisation du mot de passe envoyées à votre e-mail', col='green')
            elif usernameExist is not None:
                userResetID = usernameExist[0]
                userEmail = usernameExist[4]
                fullName = f'{usernameExist[1]} {usernameExist[2]}'
                resetKEY = createResetPasswordRequest(database, userResetID)
                sendResetEmail(userEmail, fullName, resetKEY)
                #sendEmail(userEmail, 'Password Reset', f'to reset your password please visit this link : http://192.168.1.17/reset?id={resetKEY}\nYour link will expire in 15 Min')
                return render_template('./resetPassword.html', resp='Instructions de réinitialisation du mot de passe envoyées à votre e-mail', col='green')
            else:
                return render_template('./resetPassword.html', resp='Nom d\'utilisateur ou e-mail introuvable', col='red')
        else:
            newPassword = request.form.get('newPassword')
            confirmPassword = request.form.get('confirmPassword')
            resetQuery = request.args.get('id', default='', type=str)
            if newPassword and confirmPassword:
                if len(newPassword) >= 8 and len(confirmPassword) >= 8:
                    if newPassword == confirmPassword:
                        newPassword = calculate_sha256(newPassword)
                        if resetPasswordRequestExist(database, resetQuery):
                            resetPasswordRequestClose(database, resetQuery, newPassword)
                            return redirect(url_for('login'))
                        else:
                            return render_template('./resetPassword.html', resp='Expiré', col='red')
                    else:
                        return render_template('./confirmResetPassword.html', resp='Les mots de passe ne correspondent pas', col='red')
                else:
                    return render_template('./confirmResetPassword.html', resp='La longueur du mot de passe doit être >= 8', col='red')
            else:
                return render_template('./confirmResetPassword.html', resp='Le mot de passe ne doit pas être vide', col='red')
    else:
        resetQuery = request.args.get('id', default='', type=str)
        isResetStillValid = resetPasswordRequestExist(database, resetQuery)
        if len(resetQuery) > 0 and isResetStillValid:
            return render_template('./confirmResetPassword.html')
        elif not isResetStillValid and resetQuery != '':
            return render_template('./resetPassword.html', resp='Expiré', col='red')
        else:
            return render_template('./resetPassword.html')


@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))


@app.route('/offers', methods=['GET', 'POST'])
def offers():
    offers = GetOffers(database)
    if request.method == 'POST':
        #productName = request.form.get('product-name')
        return redirect(url_for('index'))
    else:
        if 'id' in list(session.keys()):
            myID = session['id']
        else:
            myID = -1
        return render_template('./offers.html', offers=offers, myID=myID)


@app.route('/addoffer', methods=['GET', 'POST'])
def addoffer():
    if 'id' in list(session.keys()):
        if request.method == 'POST':
            uid = session['id']
            type = request.form.get('type')
            coin = request.form.get('coin')
            Amount = request.form.get('Amount')
            insertOffer(database, type, coin, Amount, uid)
            return redirect(url_for('myOffers'))
        else:
            return render_template('./addOffer.html')
    else:
        return redirect(url_for('index'))

@app.route('/editOffer/<offerID>', methods=['GET', 'POST'])
def editOffer(offerID):
    if 'id' in list(session.keys()):
        userID = session['id']
        iOwnIt = False
        offerData = None
        myOffers = GetMyOffers(database, userID)
        for offer in myOffers:
            if offerID == str(offer[0]):
                iOwnIt = True
                offerData = offer
                break
        if iOwnIt:
            if request.method == 'POST':
                type = request.form.get('type')
                coin = request.form.get('coin')
                Amount = request.form.get('Amount')
                editOfferDB(database, offerID, type, coin, Amount)
                return redirect(url_for('myOffers'))
            else:
                return render_template('./editOffer.html', offer = offerData)
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/deleteOffer/<offerID>', methods=['GET'])
def deleteOffer(offerID):
    if 'id' in list(session.keys()):
        userID = session['id']
        iOwnIt = False
        myOffers = GetMyOffers(database, userID)
        for offer in myOffers:
            if offerID == str(offer[0]):
                iOwnIt = True
                break
        if iOwnIt:
            deleteOfferDB(database, offerID)
            return redirect(url_for('myOffers'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/myOffers', methods=['GET', 'POST'])
def myOffers():
    if 'id' in list(session.keys()):
        userID = session['id']
        myOffers = GetMyOffers(database, userID)
        if request.method == 'POST':
            #productName = request.form.get('product-name')
            return redirect(url_for('index'))
        else:
            return render_template('./myOffers.html', offers=myOffers)
    else:
        return redirect(url_for('index'))

@app.route('/contact/<offerID>', methods=['GET', 'POST'])
def contact(offerID):
    if 'id' in list(session.keys()):
        userID = session['id']
        print(f'{userID} - {offerID}')
        insertOrder(database, offerID, userID)
        return redirect(url_for('orders'))
    else:
        return redirect(url_for('login'))


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if 'id' in list(session.keys()):
        orders_List = []
        closed_orders = []

        for order in GetOrders(database, session['id']):
            Offer = GetOffer(database, order[1])
            User = GetUser(database, Offer[0][1])
            if order[3] == 'New':
                orders_List.append((order[0], Offer, User, order[3], order[4]))
            else:
                closed_orders.append((order[0], Offer[0], User, order[3], order[4]))

        incoming_orders = []
        myOffers = GetMyOffers(database, session['id'])
        for myOffer in myOffers:
            id_offer = myOffer[0]
            orders = GetOrderByOfferID(database, id_offer)
            for order in orders:
                User = GetUser(database, order[2])
                if order[3] == 'New':
                    incoming_orders.append((order[0], myOffer, User, order[3], order[4]))
                else:
                    closed_orders.append((order[0], myOffer, User, order[3], order[4]))
        return render_template('./orders.html', my_orders=orders_List, incoming_orders=incoming_orders, closed_orders=closed_orders)
    else:
        return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'id' in list(session.keys()):
        if GetIsAdmin(database, session['id'])[0][0] == 1:
            orders_List = []
            closed_orders = []
            for order in GetAllOrders(database):
                Offer = GetOffer(database, order[1])
                User = GetUser(database, order[2])
                OfferOwner = GetUser(database, Offer[0][1])
                if order[3] == 'New':
                    orders_List.append((order[0], Offer, User, order[3], order[4], OfferOwner))
                else:
                    closed_orders.append((order[0], Offer, User, order[3], order[4], OfferOwner))
            return render_template('./admin.html', orders_List=orders_List, closed_orders=closed_orders)
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/Closed/<orderID>', methods=['GET', 'POST'])
def Closed(orderID):
    if 'id' in list(session.keys()):
        if GetIsAdmin(database, session['id'])[0][0] == 1:
            editOrderStatusDB(database, orderID, 'Closed')
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

#user must be logged in & the order id exist & load all the messages
@app.route('/<room_id>')
def room(room_id):
    if 'id' in list(session.keys()):
        order = GetOrderByID(database, room_id)
        print(order)
        if order:
            Offer = GetOffer(database, order[0][1])
            creatorID = order[0][2]
            ownerID  = Offer[0][1]
            if session['id'] in [1, creatorID, ownerID]:
                messages = GetOrderMessagesByID(database, room_id)
                return render_template('room.html', room_id=room_id, offer=Offer[0], myID=session['id'], messages=messages)
            else:
                return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@socketio.on('connect')
def handle_connect():
    room_id = request.path[1:]  # Extract room ID from the URL
    join_room(room_id)
    #socketio.emit('message', {'msg': 'Welcome to the chat!', 'room': room_id}, room=room_id)

@socketio.on('join')  # Handle the 'join' event
def handle_join(data):
    room_id = data.get('room')
    join_room(room_id)
    #socketio.emit('message', {'msg': 'Welcome to the chat!', 'room': room_id}, room=room_id)

@socketio.on('message')
def handle_message(data):
    room_id = data.get('room')
    message = data.get('msg')
    date = data.get('date')
    sender = data.get('sender')
    socketio.emit('message', {'msg': message, 'room': room_id, 'date': date, 'sender':sender}, room=room_id)
    insertMessage(database, room_id, sender, message, date)

@socketio.on('disconnect')
def handle_disconnect():
    room_id = request.path[1:]
    leave_room(room_id)
    print(f"User disconnected from room: {room_id}")




if __name__ == '__main__':
    if not os.path.exists(database):
        createDatabase(database)
        insert_user(database, 'Admin', 'Admin', 'Admin', 'admin@gmail.com', calculate_sha256('12345678'), True)
    socketio.run(app, host='0.0.0.0', port=80, debug=True, allow_unsafe_werkzeug=True)