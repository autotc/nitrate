#!/usr/bin/env bash

function logger
{
    local -r level=$1
    local -r msg=$2
    echo "[${level^^}] $msg"
}
logger info "Migrate database."
./src/manage.py migrate

logger info "Set default permissions to groups."
./src/manage.py setdefaultperms

logger info "Create a superuser if there is no one."
admin_exists=$(./src/manage.py shell -c "\
from django.contrib.auth.models import User
user = User.objects.filter(username='admin').first()



print(user.is_superuser if user is not None else False)
")

if [[ "$admin_exists" == "False" ]]; then
    logger info "Create a superuser with username and password admin:admin"
    ./src/manage.py createsuperuser --noinput --username admin --email admin@example.com
    ./src/manage.py shell -c "\
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.set_password('admin')
user.save()
"
fi

deactivate

profile=~/.bash_profile

if ! grep "cd ${code_dir}" "$profile" >/dev/null; then
    echo "cd ${code_dir}" >> "$profile"
fi

if ! grep ". ${venv_activate}" "$profile" >/dev/null; then
    echo ". ${venv_activate}" >> "$profile"
fi

