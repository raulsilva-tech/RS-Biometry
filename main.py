import time
from flask import Flask, request, Response, send_file
import logging
from logging.handlers import RotatingFileHandler
# import traceback
# from waitress import serve
from DKFP import *

# iniciando a api rest
app = Flask(__name__)


@app.route('/allow_next_operation')
def app_allow_next_operation():
    result = allow_next_operation()
    return {"result": str(result), "desc": ""}, 200


@app.route('/cancel')
def app_cancel():
    cancel()
    return "", 200


@app.route('/enroll/<int:num_fingers>')
def app_enroll(num_fingers):
    enroll_error, dktemplate = get_dktemplate_from_fp(num_fingers)
    status = get_read_fingerprint_status()
    return {"result": status, "desc": dktemplate}, 200


@app.route('/get_general_status')
def app_get_general_status():
    general_status, ret_code, ret_code_desc = get_general_status()

    return {"generalStatus": general_status,
            "retCode": ret_code,
            "retCodeDesc": ret_code_desc
            }, 200


@app.route('/set_read_fingerprint_status/<string:value>')
def app_set_read_fingerprint_status(value):
    set_read_fingerprint_status(value)
    return "", 200


@app.route('/get_processor_status')
def app_get_processor_status():
    return {"result": get_processor_status(), "desc": ""}, 200


@app.route('/set_processor_status/<string:value>')
def app_set_processor_status(value):
    set_processor_status(value)
    return "", 200


@app.route('/get_identify_status')
def app_get_identify_status():
    ret_code, current_user_id, fp_identified, ret_code_desc = get_identify_status()

    result = {
        "retCode": ret_code,
        "retCodeDesc": ret_code_desc,
        "currentUserId": current_user_id,
        "isFPIdentified": fp_identified
    }

    return result, 200


@app.route('/get_ret_code')
def app_get_ret_code():
    ret_code, ret_code_desc = get_ret_code()
    return {"result": str(ret_code), "desc": ret_code_desc}, 200


@app.route('/identify')
def app_identify():
    process_fp = identify()
    return {"result": str(process_fp), "desc": ""}


@app.route('/initialize/<int:fake_finger>/<int:emulate>/<int:log>/<int:far>')
def app_initialize(fake_finger, emulate, log, far):
    init_status, ret = initialize(fake_finger, emulate, log, far)

    return {
               "result": str(ret),
               "desc": init_status
           }, 200


@app.route('/set_terminate_and_cancel/<int:terminate>')
def app_set_terminate_and_cancel(terminate):
    set_terminate_and_cancel(terminate)
    return "", 200


@app.route('/terminate')
def app_terminate():
    terminate_func()
    return "",200


@app.route('/get_msg_and_status')
def app_get_msg_and_status():
    msg, status = get_msg_and_status()

    return {
               "result": status,
               "desc": msg
           }, 200


@app.route('/update_user_list', methods=['POST'])
def app_update_user_list():
    user_list = request.json


    # print(user_list)
    result = update_user_list(user_list)
    print(result)

    return {"result": str(result), "desc": "what"}, 200


# iniciando em modo debug
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)

# serve(app, host='0.0.0.0', port=5001) #WAITRESS!
