import flask
from flask import current_app as app
import functools
from website.models import User

from wtforms import Form, BooleanField, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Required, Optional, Email, Length, EqualTo, ValidationError,\
    StopValidation, Regexp


class Unique(object):

    """ validator that checks field uniqueness """

    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = 'This element already exists'
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)
			


def stop_on_validation_error(f):
    ''' A decorator which will turn raised ValidationErrors into StopValidations '''
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            # Replace the error with a StopValidation to stop the validation chain
            raise StopValidation(*e.args) from e
    return decorator


_username_validator = Regexp(
    r'^[a-zA-Z0-9_\-]+$',
    message='Your username must only consist of alphanumerics and _- (a-zA-Z0-9_-)')

class SignupForm(Form):
	username = StringField('Enter desired username.', [
		DataRequired(), 
		Length(min=5, max=40), 
		Required(), 
		stop_on_validation_error(_username_validator), 
		Unique(User, User.username, 'Username not availiable')],
		render_kw = {'placeholder': 'Choose username.', 'class': 'form-control'})

	password = PasswordField('Enter password.', [
		DataRequired(), 
		Length(min=10, max=1000)],
		render_kw = {'placeholder': 'Choose password.', 'class': 'form-control'},
		description = 'Password must be at least 10 characters long.')
	
	password2 = PasswordField('Re-enter password.', [
		DataRequired(),
		Length(min=10, max=100),
		EqualTo('password', message='Passwords aren\'t equal!')], 
		render_kw = {'placeholder': 'Confirm password.', 'class': 'form-control'})

class LoginForm(Form):
	username = StringField('Enter your username.', [
		DataRequired(),
		Length(min=5, max=40)],  
		render_kw = {'placeholder': 'Username.', 'class': 'form-control'})

	password = PasswordField('Enter password.', [
		DataRequired(), 
		Length(min=10, max=1000)],
		render_kw = {'placeholder': 'Password.', 'class': 'form-control'},
		description = 'Password must be at least 10 characters long.')

class SubmitForm(Form):
	title = StringField('Title', [
		DataRequired(),
		Length(min=5, max=100), Required()],  
	render_kw = {'placeholder': 'The quick red fox.', 'class': 'form-control'})

	story = TextAreaField('Story', 
	[DataRequired(), Length(min=100, max=5000)],  
	render_kw = {
		'placeholder': 'Once upon a time there was a magical fox.', 'class': 'form-control', 'rows': 10, 'id': 'story-text'})

	synopsis = StringField('Synopsis', 
	[DataRequired(), Length(min=30, max=200)],  
	render_kw = {'placeholder': 'This is a story about a quick fox named Peter.', 'class': 'form-control'}, 
	description = 'Must be between 30-200 characters.')

class CommentForm(Form):
	comment = TextAreaField('Write a comment.', [
		DataRequired(),
		Length(max=1000),
		Required()],
		render_kw = {'class': 'form-control', 'rows': 5})