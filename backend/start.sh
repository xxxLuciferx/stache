#! /bin/sh
# if [ -d ".venv" ]; then
#     echo "env exist"
#     source .venv/bin/activate
# else
#     python3 -m venv .venv
#     source .venv/bin/activate
#     pip3 install -r authentication/requirement_home.txt
# fi

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
    sleep 1
done

python3 authentication/manage.py makemigrations

python3 authentication/manage.py migrate
echo "database gote migrate successfly..."

python3 authentication/manage.py  runserver 0.0.0.0:8000

