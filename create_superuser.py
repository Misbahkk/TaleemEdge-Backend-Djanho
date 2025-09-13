import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("CREATE_SUPERUSER_USERNAME")
email = os.environ.get("CREATE_SUPERUSER_EMAIL")
password = os.environ.get("CREATE_SUPERUSER_PASSWORD")
full_name = os.environ.get("CREATE_SUPERUSER_FULLNAME", "Admin User")  # default agar env me na ho

if username and email and password:
    if not User.objects.filter(username=username).exists():
        print("Creating superuser...")
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
    else:
        print("Superuser already exists. Skipping...")
