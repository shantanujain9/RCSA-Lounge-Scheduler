import webview
import os

os.system('python manage.py runserver')  # Start the Django server

webview.create_window('My App', 'http://127.0.0.1:8000/')
webview.start()
