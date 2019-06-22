import os
import secrets
from flask import url_for, current_app
from flask_login import current_user
from PIL import Image
from automate import mail
from flask_mail import Message


# Send Email
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject='Password Reset Request', sender=('County Choice Farms', 'menaelvisjones@gmail.com'), recipients=[user.email])
    msg.body = f'''Hi, to reset your password, please follow the link below:\n
{ url_for('resetPassword', token=token, _external=True) }

If you didn't request for a password change, please ignore, thank you!
    '''
    mail.send(msg)


# Save Picture
def save_picture(form_picture):
    img_list = []
    old_image = current_user.picture
    img_list.append(old_image)

    old_image_copy = img_list.copy()

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    file_name = random_hex + f_ext
    file_path = os.path.join(current_app.root_path, 'static/wt-profile-pics', file_name)

    # Compress Image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(file_path)

    if old_image_copy[0] == 'avatar.png':
        pass
    else:
        delete_picture_path = os.path.join(current_app.root_path, 'static/wt-profile-pics', old_image_copy[0])
        os.remove(delete_picture_path)

    return file_name

