# This Flask project is set up in the packages format, meaning we can
# separate our application into multiple modules that are then imported
# into __init__.py here

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Module imports
import EsportsManagementTool.exampleModule

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/test")
def test():
    return "<p> This is a test </p>"
