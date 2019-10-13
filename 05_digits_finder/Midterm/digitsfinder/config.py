import os
import psycopg2



class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    if os.environ.get('ENV') == 'dev': # local machine setting
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    else: # heroku postgres production env variable name
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(SQLALCHEMY_DATABASE_URI, sslmode='require')

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
