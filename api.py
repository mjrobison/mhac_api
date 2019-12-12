from flask import Blueprint, request, abort, jsonify, g
from app import db

api = Blueprint('api', __name__)

@api.route('/teams', methods=['POST'])
def teams():
    return jsonify(['Matt Did it']), 200
