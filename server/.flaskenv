# Automatically read by Flask if python-dotenv is installed
# https://flask.palletsprojects.com/en/2.1.x/cli/
# Syntax is liberal, closer to Python and INI, but keep it source-able by bash

# Development settings.
# Production should use .env, which takes precedence, with a template in repo,
#   or preferably not run Flask directly at all.

# Python module and instance var / factory function to run
# Default: {app,wsgi}{,.py}:{app,application,*,create_app(),make_app()}
export FLASK_APP=server

# Changes many behaviours, including enabling debugging
export FLASK_ENV=development

# Enabled if development
#export FLASK_DEBUG=1

# Enabled if debug
#export FLASK_RUN_RELOAD=1

# Default 5000
#export FLASK_RUN_PORT=5000

# Default 127.0.0.1 (== localhost only)
export FLASK_RUN_HOST=0.0.0.0

# SSL Certificates. Automatically enable HTTPS handling when set
export FLASK_RUN_CERT=fullchain.pem
export FLASK_RUN_KEY=privkey.pem
