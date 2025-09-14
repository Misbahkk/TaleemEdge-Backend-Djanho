set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# if [ "$CREATE_SUPERUSER" == "True" ]; then
#   python manage.py shell < create_superuser.py
# fi
