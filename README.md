# django-placeholder

Roles
- Superuser
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


finance_backend/
├─ .git/
├─ .gitignore
├─ README.md
└─ backend/
   ├─ .env
   ├─ .venv/                  # local Python virtual environment
   ├─ _requirements.txt
   ├─ requirements.txt
   ├─ manage.py               # Django entry point
   ├─ Dockerfile
   ├─ build.sh
   ├─ docker-compose.yaml     # app + database
   ├─ db-docker-compose.yaml  # database only
   │
   ├─ backend/                # Django project config
   │  ├─ __init__.py
   │  ├─ asgi.py              # ASGI / websocket entry
   │  ├─ urls.py              # top-level routes
   │  ├─ wsgi.py
   │  ├─ settings/
   │  │  ├─ __init__.py
   │  │  ├─ base.py
   │  │  ├─ local.py
   │  │  ├─ development.py
   │  │  ├─ stage.py
   │  │  └─ production.py
   │  └─ staticfiles/         # collected static files
   │
   ├─ api/                    # main business app
   │  ├─ __init__.py
   │  ├─ admin.py
   │  ├─ apps.py
   │  ├─ models.py
   │  ├─ permissions.py
   │  ├─ response_formatter.py
   │  ├─ tests.py
   │  ├─ urls.py              # API routes under /api/v1/
   │  ├─ views.py
   │  ├─ migrations/
   │  ├─ management/
   │  │  └─ commands/         # seed scripts
   │  │     ├─ seed_all.py
   │  │     ├─ seed_categories.py
   │  │     ├─ seed_permissions.py
   │  │     ├─ seed_roles.py
   │  │     └─ seed_types.py
   │  │
   │  ├─ User/
   │  │  ├─ model.py
   │  │  ├─ serializers.py
   │  │  └─ view.py
   │  ├─ UserProfile/
   │  │  ├─ model.py
   │  │  └─ serializers.py
   │  ├─ Role/
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ Permission/
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ Type/
   │  │  ├─ model.py
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ Category/
   │  │  ├─ model.py
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ PaymentMethod/
   │  │  ├─ model.py
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ Transactions/
   │  │  ├─ model.py
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ RecurringTransaction/
   │  │  ├─ model.py
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ Budget/
   │  │  ├─ model.py
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ SavingsGoals/
   │  │  ├─ model.py
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ Greeting/
   │  │  ├─ model.py
   │  │  ├─ serializer.py
   │  │  └─ view.py
   │  ├─ AuditLog/
   │  │  ├─ middleware.py
   │  │  ├─ model.py
   │  │  ├─ serializers.py
   │  │  └─ view.py
   │  ├─ ChangeMyPassword/
   │  │  └─ view.py
   │  ├─ ForgetPassword/
   │  │  └─ view.py
   │  ├─ CreateUser/
   │  │  └─ views.py
   │  ├─ IsSuperUser/
   │  │  └─ view.py
   │  ├─ CustomApi/
   │  │  ├─ deleteUser.py
   │  │  └─ emailotp.py
   │  └─ Websocket/
   │     ├─ consumers.py
   │     └─ routings.py
   │
   └─ security/               # auth/JWT app
      ├─ __init__.py
      ├─ admin.py
      ├─ apps.py
      ├─ models.py
      ├─ serializers.py
      ├─ tests.py
      ├─ urls.py              # /auth/token, /auth/token/refresh
      ├─ views.py
      └─ migrations/
