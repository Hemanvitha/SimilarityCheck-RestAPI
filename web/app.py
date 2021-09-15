from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db['users']

def UserExist(username):
    if users.find({"Username" : username}).count() != 0:
        return True
    else:
        return False
class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        if UserExist(username):
            retJson = {
                "status" : 301,
                "msg"    : "User already exists"  
            }
            return jsonify(retJson)

        hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.insert({
            "Username" : username,
            "Password" : hashed_pwd,
            "Tokens"   : 5 #default chances given to each user for similarity check
        })

        ret = {
            "status" : 200,
            "msg"    : "success"
        }
        return jsonify(ret)
def verifyPw(username, password):
    pass
def countTokens(username):
    pass
    # if not UserExist(username):
    #     return False
    # else:
    #     return True

class Detect(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        text1 = postedData["text1"]
        text2 = postedData["text2"]

        if not UserExist(username):
            retJson = {
                "status" : 301,
                "message" : "Invalid username"
            }
            return jsonify(retJson)
            #step 4 verify user has enough tokens
            num_tokens = countTokens(username)
            if num_tokens <=0 :
                retJson = {
                    "status" : 303,
                    "message" : "you are out of tokens"
                }
                return jsonify(retJson)
            
            # calculate the similarity between text 1 and text2
            import spacy
            nlp = spacy.load('en_core_web_sm')
            text1 = nlp(text1)
            text2 = nlp(text2)

            score = text1.similairty(text2)
            ratio = score * 100
            retJson = {
                "status": 200,
                "ratio" : ratio,
                "msg" : "Simialirty between two texts"

            }
            current_tokens = countTokens(username)
            users.update({
                "Username" : username},
                {
                    "$Set" : {
                        "Tokens" : current_tokens-1
                    }
            })
            return jsonify(retJson)

class Refill(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["admin_pw"]
        refill_amount = postedData["refill"]

        if not UserExist(username):
            retJson = {
                "statue" : 301,
                "msg" : "Invalid username"
            }
            return jsonify(retJson)
            correct_pw = "abc123"
            if not password == correct_pw:
                retJson = {
                    "status" : 304,
                    "msg" : "Invalid Admin Password"
                }
                return jsonify(retJson)
            users.update({
                "Username" : username
            },
            {
                "$Set" : {
                    "Tokens : refill_amount"
                }
            }
            )
            retJson = {
                "status" : 200,
                "msg" : "Refilled successfully"
            }
            return jsonify(retJson)
api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')

if __name__ == "__main__":
    app.run(host = '0.0.0.0')
         
