from flask import Flask, abort, make_response, request, jsonify
import json
from datetime import datetime
import XenAPI
from settings import host, username, password
app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return make_response(json.dumps({'error': 'Not found'}), 404)

@app.route('/VDI', methods=['GET'])
def get_VDIs():
    # curl -X GET http://127.0.0.1:5000/VDI
    # Return all VDIs
    VDIs = session.xenapi.VDI.get_all()
    return jsonify({"VDIs": VDIs})

@app.route('/api/<object>', methods=['GET'])
def get_objects(object):
    # curl -X GET http://127.0.0.1:5000/api/VDI
    # Return all VDIs
    objects = getattr(session.xenapi, object)
    return jsonify({str(object): objects.get_all()})

@app.route('/api/<object>/<uuid>', methods=['GET'])
def get_object_by_uuid(object, uuid):
    # curl -X GET http://127.0.0.1:5000/api/VDI/<uuid>
    # Return all VDIs
    objects = getattr(session.xenapi, object)
    return jsonify({str(object): objects.get_by_uuid(uuid)})

@app.route('/action/<object>/<action>', methods=['POST', 'GET'])
def get_post_object_action(object, action):
    # curl -X POST "http://localhost:5000/action/VDI/get_SR?tom=test"
    # curl -X POST "http://localhost:5000/action/VDI/get_SR?ref=OpaqueRef:006182f6-9efd-4240-96c4-15ed2adf2257"

    # Need to work out whether params should be dict or list of params
    action_param_type = {"set_name_label": "list"}
    arg = request.args
    if len(arg) == 1:
        options = request.args.get('ref')
    else:
        options = {}
        for key, value in arg.items():
            options[key] = value

    objects = getattr(session.xenapi, object)
    action = getattr(objects, action)(options)
    return jsonify({str(object): action})


if __name__ == '__main__':
    try:
        session = XenAPI.Session("http://%s/" % host, ignore_ssl=True)
        session.login_with_password(username, password, '1.0', 'rest_api')
        app.run()
    finally:
        session.xenapi.logout()
