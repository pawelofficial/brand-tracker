from flask import Flask
app = Flask(__name__)
# foo
@app.route("/")
def hello():
    return "<html><body><h1>Hello Best Bike App!</h1></body></html>\n"

@app.route("/endpoint")
def endpoint():
    return "<html><body><h1>Hello there my friend !</h1></body></html>\n"

if __name__ == '__main__':
    app.run(port=80)