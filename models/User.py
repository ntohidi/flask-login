from flask import jsonify
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

import copy

users = db.users


class UserModel:
    def __init__(self, data=None):
        data = data or {}
        for k, v in data.items():
            setattr(self, k, v)

    def to_json(self, safe=True):
        if safe:
            res = copy.deepcopy(self.__dict__)
            res.pop('password', 0)
            return res
        return self.__dict__

    def save(self):
        try:
            res = users.insert_one(copy.deepcopy(self.__dict__))
            return res.acknowledged
        except Exception as err:
            return jsonify(status=500, error="Error in insertion of the user: {}".format(str(err)))

    def update(self, args, data):
        try:
            # res = users.update_one({'username': self.username}, {'$set': copy.deepcopy(self.__dict__)})
            res = users.update_one(args, {'$set': data})
            return res.acknowledged
        except Exception as err:
            return jsonify(status=500, error="Error in updating user: {}".format(str(err)))

    def get_id(self):
        user = users.find_one({"email": self.email}, {"id": 1})
        return str(user['_id'])

    def verify_password(self, pwd):
        if not check_password_hash(self.password, pwd):
            return jsonify(status=403, error="wrong password")
        return jsonify(status=200)

    @staticmethod
    def return_all():
        try:
            return [UserModel(user) for user in users.find({}, {'_id': 0})]
        except Exception as err:
            print("[UserModel Get All Error]: " + str(err))
            return []

    @staticmethod
    def delete_one(args):
        try:
            users.remove(args)
            return True
        except Exception as err:
            print("[UserModel Delete Error]: " + str(err))
            return False

    @staticmethod
    def generate_hash(password):
        return generate_password_hash(password, method='sha256')

    @staticmethod
    def get_one(args, filters=None):
        try:
            user = users.find_one(args, filters)
            if user:
                return UserModel(user)
            return None
        except Exception as err:
            print("[UserModel Get User Error]: " + str(err))
            return None

    @staticmethod
    def check_for_conflict(args):
        try:
            user = users.find_one(args, {'_id': 1})
            if user:
                return jsonify(status=409, message="user exists", user=True)
            return jsonify(status=200, user=False)
        except Exception as err:
            print("[UserModel Check for User Conflict Error]: " + str(err))
            return jsonify(status=500, error="Error: {}".format(str(err)))
