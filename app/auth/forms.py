from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Необходимо ввести логин')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Необходимо ввести пароль')
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Необходимо ввести email'),
        Length(5, 64),
        Email()
    ])
    username = StringField('Логин', validators=[
        DataRequired(message='Необходимо ввести логин'),
        Length(3, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Логин может состоять только из латинских букв, цифр, точек или подчеркиваний')
        ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Необходимо ввести пароль'),
        EqualTo('password2', message='Введенные пароли должны совпадать')
    ])
    password2 = PasswordField('Подтверждение', validators=[
        DataRequired(message='Необходимо ввести подтверждение пароля')
    ])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Такой email уже зарегистрирован')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Такой логин уже используется')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
