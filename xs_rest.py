from flask import Flask, make_response, request, jsonify
import json
import XenAPI
# Create settings.py with the host, username and password of the host you want to connect to
from settings import host, username, password
app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return make_response(json.dumps({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(json.dumps({'error': str(error)}), 500)

@app.route('/api/<object>', methods=['GET'])
def get_objects(object):
    # curl -X GET http://127.0.0.1:5000/api/VDI
    # Return all objects of type object
    objects = getattr(session.xenapi, object)
    return jsonify({str(object): objects.get_all()})

@app.route('/api/<object>/<uuid>', methods=['GET'])
def get_object_by_uuid(object, uuid):
    # curl -X GET http://127.0.0.1:5000/api/VDI/<uuid>
    # Return an object ref from a uuid
    objects = getattr(session.xenapi, object)
    return jsonify({str(object): objects.get_by_uuid(uuid)})

@app.route('/action/<object>/<action>', methods=['POST', 'GET'])
def get_post_object_action(object, action):
    # curl -X POST "http://localhost:5000/action/VDI/set_name_label?ref=OpaqueRef:006182f6-9efd-4240-96c4-15ed2adf2257&name_label=test"
    # curl -X POST "http://localhost:5000/action/VDI/get_SR?ref=OpaqueRef:006182f6-9efd-4240-96c4-15ed2adf2257"
    # Perform an action on a given object
    arg = request.args
    try:
        options = ()
        for key, value in arg.items():
            options += (str(value),)
        objects = getattr(session.xenapi, object)
        action = getattr(objects, action)(*options)

    except Exception as e:
        # If the previous command failed due to incorrect data structure than put parameters in dict instead
        if ("bad __structure" or "PARAMETER_COUNT_MISMATCH") in str(e):
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
