class LocalConfig:
    """
    Configuration For Development
    """
    DEBUG =True
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'sqlite://../app.database.db'
    # SECRET_KEY = '382e54edbb6f2d734f9deca89ccbef2d1e8c277c71796c5504efef8ea28263aa'


class ProductionConfig:
    """
    Configuration For Production
    """

    DEBUG = False
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = 'sqlite://../app.database.db'
    # SECRET_KEY = '382e54edbb6f2d734f9deca89ccbef2d1e8c277c71796c5504efef8ea28263aa'
