from flask import Flask
app = Flask(__name__)
# foo
@app.route("/")
def hello():
    return "<html><body><h1>Hello Best Bike App!</h1></body></html>\n"