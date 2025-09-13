set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

if [ "$CREATE_SUPERUSER" == "True" ]; then
    python manage.py createsuperuser \
        --no-input \
        --username $CREATE_SUPERUSER_USERNAME \
        --email $CREATE_SUPERUSER_EMAIL
fi
