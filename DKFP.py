import json
import time

from Futronic import *
import logging
from logging.handlers import RotatingFileHandler
import traceback
import base64

logger = logging.getLogger("BIOMETRY PYTHON LOG")
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler("BIO_Log.txt", maxBytes=10000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# status de initialize
init_status = ""

# status geral
general_status = ""

# indicador para finalizar enroll
terminate = None

# status digital do enroll
read_fingerprint_status = ""

# ultimo retorno de identify executado
ret_code = 0

# status do elemento que processa a digital no identify
processor_status = ""

# indicador de identificação da ultima digital lida no Identify
fp_identified = False

# id do ultimo usuário reconhecido no identify
current_user_id = 0

# false accept ratio level
far_level = 1


# retornando mensagem atual do leitor biometrico
def get_status_msg():
    global status_msg
    status_msg = FTR_get_status_msg()
    return status_msg


def get_general_status():
    global general_status
    return general_status


def get_processor_status():
    global processor_status
    return processor_status


def set_processor_status(value):
    global processor_status
    processor_status = value


def get_read_fingerprint_status():
    global read_fingerprint_status
    return read_fingerprint_status


def initialize(fake_finger, emulate, log, far):
    global init_status
    global general_status
    global terminate
    global far_level
    global status_msg

    print("DKFP Version 1.1 Build 220915")
    print("Se Windows: é preciso que ftrScanAPI.dll esteja na raiz do environment do python. Ex: C:\\ProgramData\\Miniconda3\\envs\\Biometry\\ftrScanAPI.dll")

    try:

        ret = 0

        # if general_status == "TERMINATE":
        #     FTR_load_library()

        if init_status != "S":

            # iniciando comunicação
            ret = FTR_initialize(fake_finger, emulate, log)

            print("1")
            # HOUVE ERRO?
            if ret != 0:

                init_status = "E"
                general_status = "ERROR"
                logger.error("Erro {} ao inicializar o leitor.".format(ret))
            else:
                status_msg = "Posicione o dedo sobre o leitor biométrico"
                init_status = "S"
                general_status = "READY"
                terminate = False
                far_level = far

                # iniciando função que captura as mensagem do leitor (coloque/retire o dedo)
                FTR_set_callback_function()

                FTR_set_far_level(far_level)

                print("Comunicação Leitor Biométrico Inicializada.")

        else:
            status_msg = "Posicione o dedo sobre o leitor biométrico"
            init_status = "S"
            general_status = "READY"
            terminate = False
            far_level = far

    except Exception as e:

        init_status = "E"
        logger.error(str(e))
        logger.error(traceback.format_exc())

    return init_status, ret


def allow_next_operation():
    allow = False

    for i in range(5):

        if FTR_is_operation_running() == 1:
            print("Ainda há uma operação em execução. Aguarde 1s.")
            time.sleep(1)
        else:
            allow = True
            print("Nova operação permitida.")
            break

    return allow


def cancel():
    if FTR_is_operation_running() == 1:
        FTR_cancel()
        allow_next_operation()


def get_dktemplate_from_fp(num_fingers):
    global read_fingerprint_status
    global terminate
    global general_status

    try:

        terminate = False

        if general_status == "READY" or general_status == "ERROR":

            general_status = "ENROLL"

            ret = FTR_set_max_fingers(num_fingers)
            if ret == 0:

                read_fingerprint_status = "N"

                while read_fingerprint_status != "S" and not terminate:

                    time.sleep(0.5)

                    enroll_error, fp_array = FTR_enroll()
                    # print(enroll_error)

                    if enroll_error != 0:

                        if enroll_error == 4:
                            read_fingerprint_status = "E"
                            logger.error("Erro {} em FTR_enroll. ".format(enroll_error))
                            FTR_cancel()

                        elif enroll_error == 205:
                            read_fingerprint_status = "E"
                            logger.error("Erro {} em FTR_enroll. ".format(enroll_error))

                        else:
                            general_status = "ERROR"
                            logger.error("Erro {} em FTR_enroll. ".format(enroll_error))

                    else:
                        read_fingerprint_status = "S"
                        print("Digital válida!")

                if len(fp_array) == 0:
                    read_fingerprint_status = "E"
                    logger.error("Erro no Enroll: Template da digital está vazio(0 bytes).")
                    return 1, {}
                else:
                    # SUCESSO

                    encoded = base64.b64encode(fp_array)
                    encoded = encoded.decode('ascii')

                    if general_status != "ERROR":
                        general_status = "READY"

                    dktemplate = {"size": len(fp_array), "UserId": 0, "pDataBase64": encoded}

                    print(dktemplate)

                    return enroll_error, dktemplate

            else:
                logger.error("Erro {} em FRT_set_max_fingers.".format(ret))
                return ret, {}

    except Exception as e:
        print(e)
        logger.error(e)
        general_status = "ERROR"
        return 1, {}


def get_general_status():
    global general_status
    global ret_code

    return general_status, ret_code, get_ret_code_desc(ret_code)


def get_ret_code_desc(code):
    desc = ""

    if code == 0:
        desc = "OK"
    elif code == 2:
        desc = "NO_MEMORY"
    elif code == 3:
        desc = "INVALID_ARG"
    elif code == 4:
        desc = "ALREADY_IN_USE"
    elif code == 5:
        desc = "INVALID_PURPOSE"
    elif code == 6:
        desc = "INTERNAL_ERROR"
    elif code == 7:
        desc = "UNABLE_TO_CAPTURE"
    elif code == 8:
        desc = "CANCELED_BY_USER"
    elif code == 9:
        desc = "NO_MORE_RETRIES"
    elif code == 11:
        desc = "INCONSISTENT_SAMPLING"
    elif code == 201:
        desc = "FRAME_SOURCE_NOT_SET"
    elif code == 202:
        desc = "DEVICE_NOT_CONNECTED"
    elif code == 203:
        desc = "DEVICE_FAILURE"
    elif code == 204:
        desc = "EMPTY_FRAME"
    elif code == 205:
        desc = "FAKE_SOURCE"
    elif code == 206:
        desc = "INCOMPATIBLE_HARDWARE"
    elif code == 207:
        desc = "INCOMPATIBLE_FIRMWARE"

    return desc


def set_read_fingerprint_status(status):
    global read_fingerprint_status
    read_fingerprint_status = status


def set_processor_status(status):
    global processor_status
    processor_status = status


def get_identify_status():
    global processor_status
    global ret_code
    global fp_identified
    global current_user_id

    processor_status = "S"

    if fp_identified:
        desc = ""
    else:
        desc = get_ret_code_desc(ret_code)

    return ret_code, current_user_id, fp_identified, desc


def get_ret_code():
    global ret_code
    return ret_code, get_ret_code_desc(ret_code)


def identify():
    global general_status
    global current_user_id
    global far_level
    global ret_code
    global fp_identified

    if allow_next_operation() == True:

        process_fp = False

        if general_status == "READY" or general_status == "ERROR":

            general_status = "IDENTIFY"
            current_user_id = 0

            try:

                ret_code = 0
                FTR_FAR_level = 0

                FTR_set_far_level(far_level)

                print("Inicio verificação 1xn")
                ret_code, int_identified, FTR_FAR_level = FTR_identify()

                if ret_code != 0 and int_identified == 1:

                    print("Digital encontrada com sucesso! UserId: {}".format(ret_code))
                    current_user_id = ret_code
                    fp_identified = True

                    FTR_set_visual_state(255, 0)

                    process_fp = True

                else:
                    current_user_id = 0
                    fp_identified = False

                    if ret_code > 0:

                        # print("Ret identify: {} ".format(ret_code))

                        if ret_code == 205:

                            FTR_set_visual_state(255, 255)
                            process_fp = True

                        elif ret_code == 8:  # identify cancelado
                            pass
                        elif ret_code == 6: # internal error
                            general_status = "ERROR"
                            FTR_set_visual_state(255,255)
                            process_fp = True
                        elif ret_code == 9: # too many tries
                            general_status = "ERROR"
                            FTR_set_visual_state(255,255)
                            process_fp = True
                        else:
                            general_status = "ERROR"

                    else:
                        print("Usuário não encontrado.")
                        FTR_set_visual_state(0, 255)
                        process_fp = True

                if general_status != "ERROR":
                    general_status = "READY"

            except Exception as e:
                print(e)
                logger.error(e)
                general_status = "ERROR"

            return process_fp


def set_terminate_and_cancel(value):
    global terminate

    terminate = value

    if FTR_is_operation_running():
        FTR_cancel()


def terminate_func():
    FTR_terminate()
    global general_status
    general_status = "TERMINATE"


def get_msg_and_status():
    global read_fingerprint_status

    msg = get_status_msg()

    return msg, read_fingerprint_status


def update_user_list(json_list):
    global general_status

    try:

        for i in range(3):
            print("UpdateuserList General_Status: " + general_status)
            if general_status == "READY" or general_status == "ERROR":
                break
            else:
                logger.error("UpdateUserList general Status: " + general_status)

            time.sleep(1)


        if general_status == "READY" or  general_status == "ERROR":

            general_status = "UPDATING"

            # fp_list = json.loads(json_list)
            fp_list = json_list
            # print(fp_list)
            list_size = len(fp_list)
            print(list_size)

            if list_size > 0:

                ret = FTR_start_identify_data(list_size)

                if ret == 0:
                    i = 0

                    for fp in fp_list:
                        # {"size": len(fp_array), "UserId": 0, "pDataBase64": encoded}
                        pDataBase64 = fp["pDataBase64"]
                        UserId = fp["UserId"]
                        size = fp["size"]
                        # print(fp)

                        byte_array = base64.b64decode(pDataBase64)

                        FTR_add_identify_data(i, UserId, byte_array, size)

                        i += 1

                    FTR_finish_identify_data()

                    general_status = "READY"

                    return True

                else:
                    logger.error("Erro {} no FTR_start_identify_data.".format(ret))
                    return False


    except Exception as e:

        print(e)
        logger.error(e)
        general_status = "ERROR"
        return False
