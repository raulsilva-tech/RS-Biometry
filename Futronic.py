from ctypes import *
from operator import is_
from sys import platform
import base64

# constants
FTR_STATE_FRAME_PROVIDED = 1
FTR_STATE_SIGNAL_PROVIDED = 2
FTR_PURPOSE_ENROLL = 1
FSD_FUTRONIC_USB = 1
FTR_PARAM_IMAGE_WIDTH = 1
FTR_PARAM_IMAGE_HEIGHT = 2
FTR_PARAM_IMAGE_SIZE = 3
FTR_PARAM_CB_FRAME_SOURCE = 4
FTR_PARAM_CB_CONTROL = 5
FTR_PARAM_MAX_MODELS = 10
FTR_PARAM_MAX_TEMPLATE_SIZE = 6
FTR_PARAM_MAX_FAR_REQUESTED = 7
FTR_PARAM_MAX_FARN_REQUESTED = 13
FTR_PARAM_SYS_ERROR_CODE = 8
FTR_PARAM_FAKE_DETECT = 9
FTR_PARAM_FFD_CONTROL = 11
FTR_PARAM_MIOT_CONTROL = 12
FTR_RETCODE_OK = 0
FTR_RETCODE_NO_MEMORY = 2
FTR_RETCODE_INVALID_ARG = 3
FTR_RETCODE_ALREADY_IN_USE = 4
FTR_RETCODE_INVALID_PURPOSE = 5
FTR_RETCODE_INTERNAL_ERROR = 6
FTR_RETCODE_UNABLE_TO_CAPTURE = 7
FTR_RETCODE_CANCELED_BY_USER = 8
FTR_RETCODE_NO_MORE_RETRIES = 9
FTR_RETCODE_INCONSISTENT_SAMPLING = 11
FTR_RETCODE_FRAME_SOURCE_NOT_SET = 201
FTR_RETCODE_DEVICE_NOT_CONNECTED = 202
FTR_RETCODE_DEVICE_FAILURE = 203
FTR_RETCODE_EMPTY_FRAME = 204
FTR_RETCODE_FAKE_SOURCE = 205
FTR_RETCODE_INCOMPATIBLE_HARDWARE = 206
FTR_RETCODE_INCOMPATIBLE_FIRMWARE = 207
FTR_CANCEL = 1


class FTR_DATA(Structure):
    _fields_ = [("Size", c_int),
                ("pData", POINTER(c_char_p * 0))]


class FTR_DATA_PTR(Structure):
    _fields_ = [("pFtrData", FTR_DATA * 0)]


class PBITMAP(Structure):
    _fields_ = [("Width", c_int),
                ("Height", c_int),
                ("Bitmap", FTR_DATA)]


# definindo nome correto da lib de acordo com o S.O.
shared_lib_path = "./lib/"
is_linux = None

try:

    if platform.startswith('win32'):
        shared_lib_path += "DankfpAPI.dll"
        callback_function = WINFUNCTYPE(None, POINTER(c_int), c_int, POINTER(c_int), c_int, POINTER(PBITMAP))
        dankfpapi = WinDLL(shared_lib_path)
        is_linux = False
    else:
        shared_lib_path += "DankfpAPI.so"
        callback_function = CFUNCTYPE(None, POINTER(c_int), c_int, POINTER(c_int), c_int, POINTER(PBITMAP))
        dankfpapi = CDLL(shared_lib_path)
        is_linux = True

    print("Successfully loaded : ", dankfpapi)
except Exception as e:
    print("Exception: "+e)

status_msg = ""

def FTR_load_library():
    # definindo nome correto da lib de acordo com o S.O.
    shared_lib_path = "./lib/"

    global dankfpapi

    try:

        if platform.startswith('win32'):
            shared_lib_path += "DankfpAPI.dll"
            dankfpapi = WinDLL(shared_lib_path)
        else:
            shared_lib_path += "DankfpAPI.so"
            dankfpapi = CDLL(shared_lib_path)

        print("Successfully loaded ", dankfpapi)
    except Exception as e:
        print("Exception: "+e)


@callback_function
def callback_py(context, statemask, response, signal, Bitmap):
    # print("invoke")

    global status_msg

    # print("signal: ", signal)
    if (statemask & FTR_STATE_SIGNAL_PROVIDED) != 0:

        if signal == 1:
            status_msg = "Posicione o dedo sobre o leitor biometrico"
            print(status_msg)
        elif signal == 2:
            status_msg = "Retire o dedo do leitor"
            print(status_msg)
        elif signal == 3:
            status_msg = "Dedo falso detectado. Tente novamente."
            print(status_msg)


def FTR_set_callback_function():
    print("set_callback_function")

    func = dankfpapi.SetCallbackFunction
    func.restype = None
    func.argtypes = [callback_function]

    func(callback_py)


def FTR_get_status_msg():
    global status_msg
    return status_msg

def FTR_initialize(fake_detect, emulate, log):
    c_fake_detect = c_bool(fake_detect)
    c_emulate = c_bool(emulate)
    c_log = c_bool(log)
    dankfpapi.Initialize.restype = c_int
    return dankfpapi.Initialize(c_fake_detect, c_emulate, c_log)


def FTR_terminate():
    dankfpapi.Terminate.restype = None
    dankfpapi.Terminate()


def FTR_set_max_fingers(max):
    c_max = c_int(max)
    dankfpapi.SetMaxFingers.restype = c_int
    return dankfpapi.SetMaxFingers(c_max)


def FTR_start_identify_data(num):
    c_num = c_int(num)
    dankfpapi.StartIndentifyData.restype = c_int
    result = dankfpapi.StartIndentifyData(c_num)
    print("Start_Identify_Data: ", result)
    return result


def FTR_add_identify_data(pos, id, pData_memory, size):
    c_size = c_int(size)
    c_pos = c_int(pos)
    c_id = c_int32(id)
    # c_pData = c_char * size
    # buffer = c_pData.from_buffer(pData_memory)
    dankfpapi.AddIdentifyData.restype = c_int

    result = dankfpapi.AddIdentifyData(c_pos, c_id, pData_memory, c_size)
    # print("Add_Identify_Data: ", result)


def FTR_finish_identify_data():
    dankfpapi.FinishIdentifyData.restype = None
    dankfpapi.FinishIdentifyData()
    print("Finish_Identify_Data")


def FTR_identify():
    # int  Identify(IntByReference IsIdentified, LongByReference FARLevel)
    c_is_identified = c_int(0)
    c_is_identified_p = pointer(c_is_identified)
    c_far_level = c_long(0)
    c_far_level_p = pointer(c_far_level)

    global is_linux

    if is_linux:
        dankfpapi.DKIdentify.restype = c_int
        c_result = dankfpapi.DKIdentify(c_is_identified_p, c_far_level_p)
    else:
        dankfpapi.Identify.restype = c_int
        c_result = dankfpapi.Identify(c_is_identified_p, c_far_level_p)

    return c_result, c_is_identified_p.contents.value, c_far_level_p.contents.value


def FTR_set_far_level(far_level):
    dankfpapi.SetFARLevel.restype = None
    c_far_level = c_int(far_level)
    dankfpapi.SetFARLevel(c_far_level)


def FTR_set_visual_state(green, red):
    dankfpapi.SetVisualState.restype = None
    c_green = c_int(green)
    c_red = c_int(red)
    dankfpapi.SetVisualState(c_green, c_red)


def FTR_cancel():
    dankfpapi.Cancel.restype = None
    dankfpapi.Cancel()


def FTR_is_identify_running():
    dankfpapi.IsIdentifyRunning.restype = c_int
    return dankfpapi.IsIdentifyRunning()


def FTR_is_operation_running():
    dankfpapi.IsOperationRunning.restype = c_int
    return dankfpapi.IsOperationRunning()


def FTR_enroll():
    c_enroll_error = c_int(0)
    c_enroll_error_p = pointer(c_enroll_error)

    dankfpapi.Enroll.restype = POINTER(FTR_DATA)

    FTR_DATA_p = dankfpapi.Enroll(c_enroll_error_p)

    contents = FTR_DATA_p.contents  # Dereference it.

    # Cast a pointer to the zero-sized array to the correct size and dereference it.
    fp_array = cast(byref(contents.pData.contents), POINTER(c_char * contents.Size)).contents

    # print("EnrolError: ", c_enroll_error_p.contents.value)
    # print("Size: {}".format(FTR_DATA_p.contents.Size))
    # print("fp_array: {}".format(list(fp_array)))
    # print("sizeof: {}".format(sizeof(fp_array)))


    return c_enroll_error_p.contents.value, fp_array


#
# ret = FTR_initialize(False, False, True)
# if ret != 0:
#     print("Initialize Error: {}".format(ret))
# else:
#
#     FTR_set_callback_function()
#     print("SetMaxFingers: {}".format(FTR_set_max_fingers(1)))
#
#     FTR_set_far_level(1)
#     # set_visual_state(100, 100)
#
#     # print("IsIdentifyRunning? : {}".format(is_identify_running()))
#     # print("IsOperationRunning? : {}".format(is_operation_running()))
#     fp_array = [None] * 5
#     for i in range(5):
#         error, fp_array[i] = FTR_enroll()
#         if error != 0:
#             break
#
#     # string = "nQIDAwAhEhkid3d3d3d3d3d3d3d3d3d3d3d3d3d3d3c2Nzg2MjExd3d3d3d3d3d3ODc2Nzc3NTIxd3d3d3d3d3c7OTk4NzU0NTQyMS4ud3d3d3c7Ojk5ODY0NTU0My4uLXd3dwIBOzo5ODc1NTU0NDExMXd3dwMBADo5OTg3NjU0MzIxMDF3dwMCADo5ODc3NjU0NDAuLi93dwMCATs5Nzc2NTQ0NDEuMDF3dwUEAgA5Nzc2NTMzMjEyMTF3dwkFAwA5ODg3NTMyMDAxMS93dwsHAwA7Ojk3NTIwLy8vLy53dw0JBQMAOjg2NDIwLi0sLS13dxALCAUBOjY0MjEvLSsqKyx3dxIOCgcDOjYyMC4tKykpKip3dxUSDwsFOjMwLisqKCcnKSl3dxkYFhILOi8sKyopJyUkJiZ3dx0dHBkVHiYmJSgpJiUlJSV3dyAiISEeHR8hIiMkIyIjJCR3dyQlJykgFxsdHx8gICEhIiJ3dycoKy86DRYaHB0eHx8gISB3dycpLC83CBMYGhwcHR4fHx53dygqLC83BA8WGBoaHBwcGxt3dykrKy42AgsTFRcZGRoZGBp3d3d3d3d3d3d3d3d3d3d3d3d3Ugg8C3pMVW5BJg0zG0BTN0EOb2R0e3BEHjB3RHI2HDcILgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADdnbXB8hoqNkqeoqbO5ER4vNzs8PUxOUlRZY4yNjqi0u74AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABCAwUBAQEEQYBBAsECQ0NDQAQDQIOAg0ADAMFBQUDCwQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
#     # fp_array = base64.b64decode(string)
#
#     FTR_start_identify_data(5)
#
#     for i in range(len(fp_array)):
#         FTR_add_identify_data(i, i + 1, fp_array[i], len(fp_array[i]))
#
#     FTR_finish_identify_data()
#
#     for x in range(1):
#         print("Identify: {}".format(FTR_identify()))
#
#     FTR_terminate()
