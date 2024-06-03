# Using flask to make an api 
# import necessary libraries and functions 
from flask import Flask, jsonify 

# creating a Flask app 
app = Flask(__name__) 

# on the terminal type: curl http://127.0.0.1:5000/ 
# creating login route
@app.route('/login/<username>,<password>', methods = ['GET', 'POST']) 
def login(username, password):
    
    # checking hardcoded User ID and Password
    if username == "mohsin" and password == "admin123":
        return jsonify({'prompt': "Access Granted"})
    elif username == "tabrez" and password == "admin456":
        return jsonify({'prompt': "Access Granted"})
    elif username == "yasir" and password == "admin789":
        return jsonify({'prompt': "Access Granted"})
    elif username == "ahsan" and password == "admin0":
        return jsonify({'prompt': "Access Granted"})
    else:
        return jsonify({'prompt': "User not found"})

  
# driver function 
if __name__ == '__main__': 

# to enable flask debugging
    app.run(debug = True) 