#!/bin/bash

# Configura o Pyenv corretamente
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

# Ativa o ambiente virtual (se estiver usando venv)
source /home/herman/Projects/automated-payment-verification/venv/bin/activate

# Executa o script Python
# /home/herman/Projects/automated-payment-verification/venv/bin/python /home/herman/Projects/automated-payment-verification/main.py >> /home/herman/Projects/automated-payment-verification/log.txt 2>&1
/home/herman/Projects/automated-payment-verification/venv/bin/python /home/herman/Projects/automated-payment-verification/main.py >> /home/herman/Projects/automated-payment-verification/logs/cron.log 2>&1