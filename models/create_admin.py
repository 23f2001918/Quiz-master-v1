from database_models import db, app, Admin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def create_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()  # Ensures all tables are created

        # Ensure the Admin table exists and create a default admin
        admin = Admin.query.first()
        if not admin:
            hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
            admin = Admin(username="admin", password=hashed_password)
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created (username: admin, password: admin123)")
        else:
            print("⚠️ Admin user already exists.")

        print("✅ Database tables created successfully!")

if __name__ == "__main__":
    create_database()
