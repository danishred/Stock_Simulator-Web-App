# Using flask to make an api 
# import necessary libraries and functions 
from flask import Flask, jsonify, request

# creating a Flask app 
app = Flask(__name__) 


# on the terminal type: curl http://127.0.0.1:5000/ 
# returns hello world when we use GET. 
# returns the data that we send when we use POST. 
@app.route('/') 
def index(): 
    return "The server is running"
  

# on the terminal type: curl http://127.0.0.1:5000/login/userid,password
# creating login route

# Use POST if user reached route via POST (as by submitting a form via POST)
# Use GET or nothing if user reached route via GET (as by clicking a link 
# or via redirect)
# Data sent through link is not considered as POST but GET as in below example
@app.route('/login/<username>,<password>', methods=["GET"]) 
def login(username, password):
    
    # checking hardcoded User ID and Password
    if username == "mohsin" and password == "admin123":
        return jsonify({"Prompt":"Access Granted"})
    elif username == "tabrez" and password == "admin456":
        return jsonify({"Prompt":"Access Granted"})
    elif username == "yasir" and password == "admin789":
        return jsonify({"Prompt":"Access Granted"})
    elif username == "ahsan" and password == "admin0":
        return jsonify({"Prompt":"Access Granted"})
    else:
        return jsonify({"Prompt":'User not found or wrong password'})

if __name__ == '__main__': 
    app.run(debug = True) 