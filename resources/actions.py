from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import actionsDb
from schemas import ActionsSchema, ActionSchema
from sqlalchemy.exc import SQLAlchemyError
from models.person import PersonModel
from models.action import ActionModel
from models.tag import TagModel
from flask_sqlalchemy import SQLAlchemy
from flask_cors import cross_origin

db = SQLAlchemy()

blp = Blueprint('actions', __name__, description="Operation on actions")


@blp.route('/allActions')
class Actions(MethodView):
    @cross_origin()
    @blp.response(201, ActionsSchema(many=True))
    def get(self):
        return jsonify(list(actionsDb.values()))

    # @blp.arguments(ActionSchema)
    # @blp.response(201, ActionSchema(many=True))
    # def post(self, request_data):
    #     action_id = request_data['id']
    #     actionsDb[action_id] = request_data
    #     return jsonify(list(actionsDb.values()))

    @blp.arguments(ActionSchema)
    @blp.response(201, ActionSchema(many=True))
    def post(self, request_data):
        print(1)
        print(request_data)
        action = ActionModel(
            id=request_data['id'],
            action=request_data['action'],
            category=request_data['category'],
            description=request_data['description'],
            persons=[PersonModel(name='', last_name='', id=0)],
            tag=[TagModel(name=t['name'], id=request_data['id'])
                 for t in request_data['tag']]
        )

        # try:
        #     db.session.add(action)
        #     db.session.commit()
        # except SQLAlchemyError:
        #     abort(500,message='An error occured while adding action')

        return action
        # return action

    @blp.arguments(ActionsSchema(many=True))
    def put(self, request_data):
        print(request_data)
        request_dict = {d['id']: d for d in request_data}
        try:
            for key, value in actionsDb.items():
                if key in request_dict:
                    for k, v in value.items():
                        if v != request_dict[key][k]:
                            actionsDb[key][k] = request_dict[key][k]
            return jsonify(actionsDb)
        except KeyError:
            abort(404, message='Update not done')


@blp.route('/action/<string:actionId>')
class SingleActionUpdate(MethodView):

    @blp.response(201, ActionsSchema)
    def get(self, actionId):
        action_id = int(actionId)
        if action_id not in actionsDb:
            abort(400, message='Bad request, not such action id')
        try:
            action = actionsDb[action_id]
            return jsonify(action)
        except KeyError:
            abort(404, message='Action not found')

    @blp.arguments(ActionsSchema)
    @blp.response(201, ActionsSchema(many=True))
    def put(self, request_data, actionId):
        request_data = request.get_json(silent=True)
        action_id = int(actionId)

        try:
            if action_id in actionsDb:
                actionsDb[action_id] = request_data
            return actionsDb
        except KeyError:
            abort(404, message='Update not done')

    @blp.response(201, ActionsSchema(many=True))
    def delete(self, actionId):
        action_id = int(actionId)
        try:
            actionsDb.pop(action_id)
            return actionsDb
        except KeyError:
            abort(404, message='Delete not done')