import os
import numpy as np
from datetime import datetime
import csv
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk  # installed via pillow not PIL
import time

# GLOBALS --------------------------------------------------------------------------------------------------------------
row_dict = {}
config_dict = {}
config_data_dict = {}
math_dict = {}
data_dict = {}
math_sum = {}
math_operand1 = {}
math_operator = {}
math_operand2 = {}
math_operand3 = {}
math_operand4 = {}
data_actual_dict = {}
variable_dict = {}
type_of_data = ""
config_file_path = ""
data_in_file_name = ""
output_file_path = ""
num_data_pts = -1
image_data_yn = False
busy = False


def resetStatus():
    label_status.configure(text="", fg="#FFFFFF")


def browseForInput():
    global data_in_file_name
    resetStatus()
    data_in_file_name = filedialog.askopenfilename(initialdir="/",
                                                   title="Choose Source File",
                                                   filetypes=(("Text Files", "*.txt*"),
                                                              ("All Files", "*.*")))
    if data_in_file_name != "":
        label_input_path.configure(text="File Opened: " + data_in_file_name)


def browseForOutput():
    global output_file_path
    resetStatus()
    output_file_path = filedialog.askdirectory(mustexist=True,
                                             title="Choose Output Directory")
    if output_file_path != "":
        label_output_path.configure(text="Directory Opened: " + output_file_path)


def confirmAttachmentSelection():
    global type_of_data
    resetStatus()
    label_attachmentoptions.configure(text="Attachment Chosen: " + variable.get())
    type_of_data = variable.get()


def confirmNumDataPoints():
    global num_data_pts
    resetStatus()                               #changed 6/19/2022 by @dawsonxbancroft to fix -1 in data
    num_data_pts = int(entry_numDataPoints.get())
    label_numDataPoints.configure(text="Number Data Points: " + str(num_data_pts))


def read_config_file(file_path):
    #  Open File
    fp = open(file_path, "r")

    #  Create Dictionaries
    global row_dict, config_dict, data_dict, math_sum, math_operand1, math_operator, \
        math_operand2, math_operand3, math_operand4

    #  Get row labels for csv file
    line = fp.readline()
    arr = line.split("\"")
    rowLabels = np.empty(len(arr) - 3, dtype=object)
    i = 3
    while i < len(arr) - 1:
        rowLabels[i - 3] = arr[i]
        i += 1

    #  get the variables for the csv file
    line = fp.readline()
    arr = line.split("\"")
    rowVars = np.empty(len(arr) - 4, dtype=object)
    i = 3
    while i < len(arr) - 1:
        rowVars[i - 3] = arr[i]
        i += 1

    #  convert the row info into dictionary
    for var in range(len(rowLabels) - 1):
        row_dict[rowLabels[var]] = rowVars[var]

    #  image data?
    line = fp.readline()
    arr = line.split("\"")
    if arr[1] == 1:
        image_data_yn_func = True
    else:
        image_data_yn_func = False

    #  number of config blocks
    line = fp.readline()
    arr = line.split("\"")
    num_config_blocks_func = int(arr[1])

    #  read config blocks
    if num_config_blocks_func == 0:
        fp.readline()
        fp.readline()
        fp.readline()
    for i in range(num_config_blocks_func):
        line = fp.readline()
        arr = line.split("\"")
        num_config_bytes = int(arr[1])
        for j in range(num_config_bytes):
            line = fp.readline()
            arr = line.split("\"")
            address_label = "block" + str(i) + "byte" + str(j)
            config_dict[address_label] = arr[1]

    #  read number of data blocks
    line = fp.readline()
    arr = line.split("\"")
    num_data_blocks_func = int(arr[1])

    #  read data blocks
    for i in range(num_data_blocks_func):
        line = fp.readline()
        arr = line.split("\"")
        num_data_bytes = int(arr[1])
        for j in range(num_data_bytes):
            line = fp.readline()
            arr = line.split("\"")
            address_label = "block" + str(i) + "byte" + str(j)
            data_dict[address_label] = arr[1]
    line = fp.readline()
    arr = line.split("\"")
    if arr[1] != "null":
        print("ERROR in CONFIG")

    line = fp.readline()
    arr = line.split("\"")
    if arr[1] != "MATH":
        print("ERROR in CONFIG")

    #  read math
    checker = True
    cnt = 0
    while checker:
        line = fp.readline()
        arr = line.split("\"")
        if len(arr) == 3 and arr[1] == "null":
            checker = False
        else:
            math_sum[cnt] = arr[1]
            math_operand1[cnt] = arr[3]
            math_operator[cnt] = arr[4]
            math_operand2[cnt] = arr[5]
            if len(arr) > 6:
                math_operand3[cnt] = arr[6]
            if len(arr) > 7:
                math_operand4[cnt] = arr[7]
        cnt += 1

    line = fp.readline()
    arr = line.split("\"")
    if arr[1] != "eom":
        print("ERROR in CONFIG")

    line = fp.readline()
    arr = line.split("\"")
    if arr[1] != "eof":
        print("ERROR in CONFIG")

    return image_data_yn_func, num_data_blocks_func, num_config_blocks_func


def convert_line(linefunc):
    arr = linefunc.split(" ")
    arr_out = np.empty(16)
    address = int(arr[0], 16) >> 4
    for i in range(8):
        arr_out[i] = int(arr[i + 2], 16)
        arr_out[i + 8] = int(arr[i + 11], 16)
    return address, arr_out


def read_block(fo, last_ptr):
    data_out = np.zeros(512)
    line_cnt = 0
    curr_ptr = fo.tell()
    while line_cnt <= 31:
        curr_ptr = fo.tell()
        line = fo.readline()
        if line[0] == "*":
            fo.seek(last_ptr)
            last_addr_func, last_arr_func = convert_line(fo.readline())
            fo.readline()
            next_addr_func, next_arr_func = convert_line(fo.readline())
            delta_addr = (next_addr_func - last_addr_func) - 2
            if 32 - line_cnt < delta_addr:
                delta_addr = 32 - line_cnt
            for j in range(delta_addr):
                for byte in range(16):
                    data_out[((line_cnt * 16) + byte)] = last_arr_func[byte]
                line_cnt += 1
            fo.seek(last_ptr)
            fo.readline()
            fo.readline()
            line_cnt += 1
        else:
            curr_addr, curr_arr = convert_line(line)
            for byte in range(16):
                data_out[((line_cnt * 16) + byte)] = curr_arr[byte]
            line_cnt += 1
        last_ptr = curr_ptr
    data_out[511] = 0
    return curr_ptr, data_out


def operator_math(op1, op2, op3, op4, operator):
    final = "null"
    if operator == "<<":
        op1 = int(op1)
        op2 = int(op2)
        final = op1 << op2
    elif operator == ">>":
        op1 = int(op1)
        op2 = int(op2)
        final = op1 >> op2
    elif operator == "+":
        try:
            op1 = float(op1)
        except ValueError:
            op1 = 0
        op2 = float(op2)
        final = op1 + op2
    elif operator == "-":
        try:
            op1 = float(op1)
        except ValueError:
            op1 = 0
        op2 = float(op2)
        final = op1 - op2
    elif operator == "x":
        try:
            op1 = float(op1)
        except ValueError:
            op1 = 0
        op2 = float(op2)
        final = op1 * op2
    elif operator == 'div':
        try:
            op1 = float(op1)
        except ValueError:
            op1 = 0
        op2 = float(op2)
        final = op1 / op2
    elif operator == "strApp":
        op1 = str(op1)
        op2 = str(op2)
        final = op1 + op2
    elif operator == "rot":
        op1 = str(op1)
        op2 = int(op2)
        if op2 < 0:
            final = "0"
        else:
            Lfirst = op1[0:op2]
            Lsecond = op1[op2:]
            final = Lsecond + Lfirst
    elif operator == "convertStrToChrs":
        stringList = op1.split(".")
        newString = ""
        for i in stringList:
            newChr = int(i)
            newChr = chr(newChr)
            newString = newString + newChr
        final = newString
    elif operator == "ind":
        op1 = str(op1)
        try:
            op2 = int(op2)
        except ValueError:
            op2 = 0
        try:
            final = op1[op2]
        except IndexError:
            final = 0
        final = str(final)
    elif operator == "inds":
        op1 = str(op1)
        # x = list(op1) # debug
        try:
            op2 = int(op2)
        except ValueError:
            op2 = 0
        try:
            op3 = int(op3)
        except ValueError:
            op3 = 0
        deltaInd = op3 - op2
        final = ""
        for i in range(deltaInd + 1):
            try:
                final += str(op1[op2 + i])
            except IndexError:
                final = 0
        final = str(final)
    elif operator == "checkInd":
        op1 = list(op1)
        op2 = int(op2)
        # op4 = chr(int(op4))
        if len(op1) != 0:
            # op3 = op1[1]
            if op1[op2] == op3:
                op1[op2] = op4
        else:
            op1 = "null"
        final = "".join(op1)
    elif operator == "cast":
        op2 = str(op2)
        if op2 == "str":
            op1 = str(op1)
        elif op2 == "float":
            op1 = str(op1)
            op1 = op1.replace(".", "0")
            op1 = op1.replace(",", "0")
            try:
                op1 = float(op1)
            except ValueError:
                op1 = 0
        elif op2 == "int":
            op1 = int(op1)
        elif op2 == "chr":
            op1 = chr(op1)
        final = op1
    elif operator == "2comp":
        op1 = float(op1)
        op2 = int(op2)
        if op1 > op2:
            op1 -= op2 * 2
        final = op1
    elif operator == "findInString":
        op1 = str(op1)
        # x = list(op1)       # debug
        op2 = str(op2)  # find this
        op3 = str(op3)  # if you cant find that, find this
        if str(op4) != "null":  # after index op4
            op4 = int(op4)
            temp = int(op1.find(op2, op4))
            if temp < 0 and op3 != "0":
                temp = int(op1.find(op3, op4))
            if temp < 0:
                temp = -1
        else:
            temp = int(op1.find(op2))
            if temp < 0 and op3 != "0":
                temp = int(op1.find(op3))
            if temp < 0:
                temp = -1
        final = temp
    else:
        print("OPERATOR " + operator + " UNKNOWN")
    return final


def do_math():
    global math_dict
    op2 = "null"
    list_of_sums = math_sum.keys()
    for sum_key in list_of_sums:
        final_var = math_sum.get(sum_key)
        operand1 = math_operand1.get(sum_key)
        operand2 = math_operand2.get(sum_key)
        if sum_key in math_operand3:
            operand3 = math_operand3[sum_key]
        else:
            operand3 = "null"
        if sum_key in math_operand4:
            operand4 = math_operand4[sum_key]
        else:
            operand4 = "null"
        operator = math_operator.get(sum_key)
        if operand1[0] == "#":
            operand1 = list(operand1)
            operand1[0] = ""
            op1 = "".join(operand1)
        else:
            if operand1 in math_dict:
                op1 = math_dict.get(operand1)
            elif operand1 in config_data_dict:
                op1 = config_data_dict.get(operand1)
            elif operand1 in variable_dict:
                op1 = variable_dict.get(operand1)
            else:
                math_dict[operand1] = ""
                op1 = ""
        if operand2[0] == "#":
            if str(operand2) == "#quotes":
                operand2 = "#\""
            if str(operand2) == "#degreeSym":
                operand2 = "#°"
            operand2 = list(operand2)
            operand2[0] = ""
            op2 = "".join(operand2)
        else:
            if operand2 in math_dict:
                op2 = math_dict.get(operand2)
            elif operand2 in config_data_dict:
                op2 = config_data_dict.get(operand2)
            elif operand2 in variable_dict:
                op2 = variable_dict.get(operand2)
            elif operand2 == "str":
                op2 = "str"
            elif operand2 == "\n":
                op2 = "null"
            else:
                print("ERROR, variable " + str(operand2) + " not found")
        if operand3[0] == "#":
            operand3 = list(operand3)
            operand3[0] = ""
            op3 = "".join(operand3)
        else:
            if operand3 in math_dict:
                op3 = math_dict.get(operand3)
            elif operand3 in config_data_dict:
                op3 = config_data_dict.get(operand3)
            elif operand3 in variable_dict:
                op3 = variable_dict.get(operand3)
            else:
                op3 = "null"
        if operand4[0] == "#":
            operand4 = list(operand4)
            operand4[0] = ""
            op4 = "".join(operand4)
        else:
            if operand4 in math_dict:
                op4 = math_dict.get(operand4)
            elif operand4 in config_data_dict:
                op4 = config_data_dict.get(operand4)
            elif operand4 in variable_dict:
                op4 = variable_dict.get(operand4)
            else:
                op4 = "null"
        value = operator_math(op1, op2, op3, op4, operator)
        math_dict[final_var] = value
    return


def read_data_file(input_file_path, output_file_path_func, num_data_pts_func, num_config_blocks_func,
                   num_data_blocks_func):
    global image_data_yn, data_actual_dict, variable_dict, math_dict
    now = datetime.now()
    timedate = now.strftime("%Y%m%d_%H%M%S")
    out = open((output_file_path_func + "\\" + timedate + ".csv"), "w", newline='')
    if image_data_yn:
        os.mkdir(output_file_path_func + "\\images")
    csvwriter = csv.writer(out)
    csvwriter.writerow(row_dict.keys())
    ptr = 0
    inp = open(input_file_path, "r")
    for i in range(num_config_blocks_func):
        ptr, config_data = read_block(inp, ptr)
    for i in range(num_data_pts_func):
        for j in range(num_data_blocks_func):
            ptr, data = read_block(inp, ptr)
            for k in range(512):
                data_actual_dict["block" + str(j) + "byte" + str(k)] = data[k]
            list_of_keys = data_actual_dict.keys()
            for key in list_of_keys:
                if key in data_dict:
                    variable_dict[data_dict.get(key)] = data_actual_dict.get(key)
        #  do math
        #  print(data_actual_dict)
        #  print(variable_dict)
        do_math()
        #  print on csv or other files
        output_dict = {}
        list_of_values = row_dict.values()
        for val in list_of_values:
            if val in math_dict:
                output_dict[val] = math_dict[val]
            else:
                print("\"" + val + "\" output value not found")
        for key in output_dict.keys():
            output_dict[key] = str(output_dict.get(key))
        csvwriter.writerow(output_dict.values())
        #  clear dictionary for next time
        math_dict.clear()
    out.close()
    return


def startConversion():
    global cwd, image_data_yn, config_file_path, busy
    error = False
    if busy is True:
        label_status.configure(text="Error 0xEE: busy", fg="#FF0000")
        error = True
    if data_in_file_name == "" and output_file_path == "":
        label_status.configure(text="Error 0x00: no input file or output directory", fg="#FF0000")
        error = True
    elif data_in_file_name == "":
        label_status.configure(text="Error 0x01: no input file", fg="#FF0000")
        error = True
    elif output_file_path == "":
        label_status.configure(text="Error 0x02: no output directory", fg="#FF0000")
        error = True
    elif type_of_data == "":
        label_status.configure(text="Error 0x03: please confirm attachements", fg="#FF0000")
        error = True
    try:
        int(num_data_pts)
    except ValueError:
        label_status.configure(text="Error 0x04: number of data points entered must be an integer", fg="#FF0000")
        error = True

    if error:
        return

    if type_of_data == 'No Attachments':
        config_file_path = "config\\nAconfig.txt"
    elif type_of_data == 'LANL NEMO Device (old)':
        config_file_path = "config\\NEMOconfig_old.txt"
    elif type_of_data == "LANL NEMO Device":
        config_file_path = 'config\\NEMOconfig.txt'
    elif type_of_data == "BakTrack Data":
        config_file_path = 'config\\bakTrackConfig.txt'
    config = cwd + "\\" + config_file_path
    if not os.path.isfile(config):
        print("Fatal Error 0x10: No config file found, please ensure config directory is upto date")
        exit()

    busy = True
    label_status.configure(text="Fetching Config Data", fg="#FFFFFF")
    image_data_yn, num_data_blocks, num_config_blocks = read_config_file(config_file_path)
    label_status.configure(text="Config Data Retreived", fg="#FFFFFF")
    time.sleep(1)
    label_status.configure(text="Converting Hexdump File", fg="#FFFFFF")
    read_data_file(data_in_file_name, output_file_path, num_data_pts, num_config_blocks, num_data_blocks)
    label_status.configure(text="Conversion Complete", fg="#00FF00")
    busy = False
    return


#  MAIN ----------------------------------------------------------------------------------------------------------------
cwd = os.getcwd()

window = tk.Tk()

window.title('Raw to File Converter')

window.geometry("925x700")
window.config(background="#23272A")

label_file_explorer = tk.Label(window,
                               text="Raw to File Converter GUI v1.0.1",
                               width=30, height=4,
                               fg="#FFFFFF", bg="#2C2F33")

logo = Image.open("images\\msgc_logo.png")
logo = logo.resize((85, 60), Image.ANTIALIAS)
logo = ImageTk.PhotoImage(logo)
label_logo = tk.Label(window, image=logo, width=700, anchor="e", bg="#23272A")

button_startConversion = tk.Button(window,
                                   text="Start Conversion",
                                   command=startConversion)

label_input_path = tk.Label(window,
                            text="",
                            width=100, height=4,
                            fg="#FFFFFF", bg="#23272A")

label_output_path = tk.Label(window,
                             text="",
                             width=100, height=4,
                             fg="#FFFFFF", bg="#23272A")

button_explore_input = tk.Button(window,
                                 text="Get Text File for Input",
                                 command=browseForInput)

button_explore_output = tk.Button(window,
                                  text="Get Directory for Output",
                                  command=browseForOutput)

OPTIONS_ATTACH = [
    "No Attachments",
    "LANL NEMO Device (old)",
    "LANL NEMO Device",
    "BakTrack Data"
]
# add other[beta] at some point using a text file to direct formatting
# also add IR attachement after config is written and tested

variable = tk.StringVar(window)
variable.set(OPTIONS_ATTACH[0])  # default value
dropMenu_attachementoptions = tk.OptionMenu(window, variable, *OPTIONS_ATTACH)

label_attachmentoptions = tk.Label(window,
                                   text="Attachment Chosen: " + variable.get(),
                                   fg="#FFFFFF", bg="#23272A",
                                   height=4)

button_confirmAttachment = tk.Button(window,
                                     text="Confirm Attachement",
                                     command=confirmAttachmentSelection)

label_numDataPoints = tk.Label(window,
                               text="Number of Data Points: 0",
                               fg="#FFFFFF", bg="#23272A",
                               height=4)

entry_numDataPoints = tk.Entry(window)

button_confirmNumDataPoints = tk.Button(window,
                                        text="Confirm Number of Data Points",
                                        command=confirmNumDataPoints)

label_statusHeader = tk.Label(window,
                              text="Status : ",
                              bg="#23272A",
                              fg="#FFFFFF",
                              height=4)

label_status = tk.Label(window,
                        text="",
                        bg="#23272A",
                        fg="#FFFFFF",
                        height=4)

button_exit = tk.Button(window,
                        text="Exit",
                        command=exit)

placeholder_height4 = tk.Label(window,
                               bg="#23272A",
                               height=4)

placeholder_height4_attachButton = tk.Label(window,
                                            bg="#23272A",
                                            height=4)

placeholder_height4_conversionButton = tk.Label(window,
                                                bg="#23272A",
                                                height=4)

placeholder_height4_numDataPoints = tk.Label(window,
                                             bg="#23272A",
                                             height=4)

label_file_explorer.grid(column=1, row=1)
label_logo.grid(column=2, row=1)
button_explore_input.grid(column=1, row=2)
label_input_path.grid(column=2, row=2)
button_explore_output.grid(column=1, row=3)
label_output_path.grid(column=2, row=3)
dropMenu_attachementoptions.grid(column=1, row=4)
label_attachmentoptions.grid(column=2, row=4)
button_confirmAttachment.grid(column=1, row=5)
placeholder_height4_attachButton.grid(column=2, row=5)
entry_numDataPoints.grid(column=1, row=6)
label_numDataPoints.grid(column=2, row=6)
button_confirmNumDataPoints.grid(column=1, row=7)
placeholder_height4_numDataPoints.grid(column=2, row=7)
label_statusHeader.grid(column=1, row=9)
label_status.grid(column=2, row=9)
button_startConversion.grid(column=1, row=10)
placeholder_height4_conversionButton.grid(column=1, row=10)
button_exit.grid(column=1, row=16)
placeholder_height4.grid(column=2, row=16)

window.mainloop()
