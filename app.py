from flask import Flask
from application.database import *
from flask_migrate import Migrate


app =Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tony.db'
app.config['SECRET_KEY'] = 'tony123'


db.init_app(app)    
migrate = Migrate(app, db)  

with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(email='admin@gmail.com',password='admin143', role='admin',name="admin", phone_number="123")
        db.session.add(admin)
        db.session.commit()
        print("admin created")

from application.controllers import routes
routes(app)


if __name__ == '__main__':
    app.run(debug=True)
