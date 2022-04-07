from pgmles import bcrypt, db, models

db.session.add(models.User(type='admin', username='admin', email='admin@email.com',
               password=bcrypt.generate_password_hash('password').decode('utf-8')))
