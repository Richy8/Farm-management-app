# Configuration settings
class Config:
    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:april2019@localhost/countymgtdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SINGLE_DATA_PER_PAGE = 11
    MULTIPLE_DATA_PER_PAGE = 15
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''