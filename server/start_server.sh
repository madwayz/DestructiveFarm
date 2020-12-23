#!/bin/sh

# Use FLASK_DEBUG=True if needed

<<<<<<< HEAD
FLASK_APP=__init__.py flask run --host 0.0.0.0 --with-threads
=======
FLASK_APP=standalone.py python3 -m flask run --host 0.0.0.0 --with-threads
>>>>>>> upstream/master
