from flask_app import app
from flask import render_template,redirect,request,session,flash
from flask_app.models.user_model import User
from flask_app.models.message_model import Message
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import datetime
DEFAULT_VIEW = 'wall.html'

# what happens when 2 controllers register the same route route?
@app.route('/wall')
def home():
    if 'logged_in' not in session:
        return redirect('/')
    
    id = session['user_id']
    data = {'id': id}

    user = User.get_by_id(data)
    user.sent_count = Message.get_sent_message_count_for_user(data)
    received_messages = Message.get_all_by_recipient_id(data)
    recipients_list = User.get_all(data)

    return render_template(DEFAULT_VIEW, user=user, messages=received_messages, recipients=recipients_list)

@app.route('/send', methods=['POST'])
def new_message():
    if 'logged_in' not in session:
        return redirect('/')
    
    addressee = request.form['sendTo']
    data = getFormValues(request.form, addressee)

    if not Message.validate(data):
        return redirect('/wall')

    r = Message.save(data)
    return redirect('/wall')


# @app.route('/new')
# @app.route('/new/message')
# def add_new():
#     if 'logged_in' not in session:
#         return redirect('/')
    
#     reporter = User.get_by_id(session['user_id'])
#     return render_template('new.html', reporter=reporter)

# @app.route('/add', methods=['POST'])
# def create_message():
#     if 'logged_in' not in session:
#         return redirect('/')

#     data = getFormValues(request.form, None)
#     data['reported_by_id'] = session['user_id']

#     if not Message.validate(data):
#         return redirect('/new')
    
#     _id = Message.save(data)

#     return redirect('/dashboard')

def getFormValues(form, receiver_id):
    user_id = session['user_id']
    msg_key = 'msg_to_' + receiver_id
    data = {
        'sender_id': user_id,
        'receiver_id': receiver_id,
        'message': form[msg_key]
    }
    # print(f'getFormValues({receiver_id}) => ', data)
    
    return data

# @app.route('/show/<int:id>')
# def show_message_by_id(id):
#     if 'logged_in' not in session:
#         return redirect('/')

#     message = Message.get_by_message_id({'id': id})
#     print('\n\n\n\n---------------')
#     print(message)

#     # messages from the db best be valid
#     # if not Message.validate(data):
#     #     return redirect('/new')
    
#     # We need the current user && the name of the reporting user
#     user = User.get_by_id(session['user_id'])

#     return render_template('show.html', message=message, user=user)



# # Attribution: https://codereview.stackexchange.com/questions/41298/producing-ordinal-numbers
# @staticmethod
# def ordinalize(n):
#     return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(10<=n%100<=20 and n or n % 10, 'th')


    # @app.route('/edit/<int:id>')
    # def edit_message(id):
    #     if 'logged_in' not in session:
    #         return redirect('/')

    #     message = Message.get_by_message_id({'id': id})
    #     if not message:
    #         redirect('/dashboard')
    #     uid = {'id': session['user_id']}
    #     user = User.get_by_id(uid)

    #     return render_template('edit.html', message = message, user=user )

    # @app.route('/update/<int:id>', methods=['POST'])
    # def update_message(id):
    #     if 'logged_in' not in session:
    #         return redirect('/')

    #     data = getFormValues(request.form, id)

    #     #validate or redirect
    #     if not Message.validate(data):
    #         print ('\n\n\nValidation failed')
    #         return redirect(f'/edit/{id}')
        
    #     Message.update(data)
        
    #     return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    if 'logged_in' not in session:
        return redirect('/')
    
    # Need to protect against hacker delete attempts
    user_id = session['user_id']

    Message.delete({'id':id, 'user_id':user_id})
    return redirect('/wall')
