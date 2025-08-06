set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py create_ebooklets
python manage.py setup_static_pdfs

# if [[ $CREATE_SUPERUSER ]]; then
#     python manage.py createsuperuser --no-input
# fi
