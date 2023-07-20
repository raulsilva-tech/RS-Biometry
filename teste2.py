from DKFP import *

init_status, ret = initialize(False, False, True, 1)
# terminate_func()
#init_status, ret = initialize(False, False, True, 1)
if ret != 0:
    print("Initialize Error: {}".format(ret))
else:

    total = 2

    dktemplate_list = []

    for i in range(total):

        ret, dktemplate = get_dktemplate_from_fp(1)
        if ret == 0 and dktemplate is not None:
            dktemplate["UserId"] = i+1
            dktemplate_list.append(dktemplate)

    # print("Digitais capturadas: ")
    # print(str(dktemplate_list))
    # for template in dktemplate_list:
    #     print(template)

    # json_list = json.dumps(dktemplate_list)

    if len(dktemplate_list) > 0:
        if update_user_list(dktemplate_list):

            for x in range(100):
                success = identify()

    terminate_func()


