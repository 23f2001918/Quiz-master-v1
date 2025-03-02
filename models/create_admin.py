from database_models import db, app, Admin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def create_database():
    with app.app_context():
        db.create_all()

        # Add a default admin if not exists
        if not Admin.query.first():
            hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
            admin = Admin(username="admin", password=hashed_password)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created with username: admin and password: admin123")

        print("Database tables created successfully!")

if __name__ == "__main__":
    create_database()
