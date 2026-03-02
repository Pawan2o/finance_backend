# django-placeholder

Roles
- Superuser
- Backoffice
- User

Remember
- add new model in apps.py of app
- new seed file is must listed in seed_all file in sequence


django-placehoder includes
- .env (local, development, stage, production)
- requirements.txt
- Test api and address api both connected with FK
- filter
- swagger
- permissions, roles
- security app(for token and authentication)
- seed data and fakers
- display reference name for FK (code is in serializer)
- CORS header and pagination
- static files
- changeMyPassword
- forget password (some changes must requires, 1- settings.py change email id and application password. from that mail link will be sent. 2- view.py change server link http://127.0.0.1:8001/)
- checkUserUser
- userProfile with contact_no field which is associated with user model
- createUser without authentication
- websocket - django channels (base.py, asgi.py, api/websocket (routings.py works like urls.py and consumers.py works like views.py))


seed_files
- api/management/commands (python manage.py seed_test 3) <-- it will generate 3 records for test model. (python manage.py seed_all 5) <-- it will generate 5 records for all models.


