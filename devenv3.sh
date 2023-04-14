#!/usr/bin/env bash

function logger
{
    local -r level=$1
    local -r msg=$2
    echo "[${level^^}] $msg"
}

venv_dir=$HOME/nitrate-env
venv_activate="${venv_dir}/bin/activate"
code_dir=/code



if [[ -e "$venv_dir" ]]; then
    logger info "Virtual environment ${venv_dir} exists already."
else
    logger info "Create Python virtual environment."
    python3 -m venv "$venv_dir"
fi

. "$venv_activate"

cd $code_dir

deactivate

profile=~/.bash_profile

if ! grep "cd ${code_dir}" "$profile" >/dev/null; then
    echo "cd ${code_dir}" >> "$profile"
fi

if ! grep ". ${venv_activate}" "$profile" >/dev/null; then
    echo ". ${venv_activate}" >> "$profile"
fi
