import re

while True:

    num = input("please enter the car number ")
    cn1 = bool(re.match(r"^[456]\d{15}$", num))       # if starting with 4,5,6 and total 15 digits
    cn2 = bool(re.match(r"^[456]\d{3}\-\d{4}\-\d{4}\-\d{4}$", num))   # if starting with 4,5,6 and total 15 digits if there is a divider as "-"
    num = num.replace("-", "")
    cn3 = bool(re.match(r"(?!.*(\d)(-?\1){3})", num)) # no integer should be repeated more then 4 times
    if (cn1 or cn2) and cn3:
         print("Valid")
    else:
         print("Invalid")
