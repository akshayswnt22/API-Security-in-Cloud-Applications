from app import db, app
from app import Feedback, Inquiry  # Import models

with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("Tables created successfully!")

    # Insert test data
    test_feedback = Feedback(name="John Doe", email="john@example.com", message="This is a test message.")
    test_inquiry = Inquiry(name="Jane Doe", email="jane@example.com", question="This is a test question.")
    db.session.add(test_feedback)
    db.session.add(test_inquiry)
    db.session.commit()
    print("Test data inserted successfully!")