import numpy as np

def ra(h,m,s):
    mi=float(m)+(float(s)/60)
    hora = float(h)+mi/60
    deg = hora*15
    sec = deg*3600
    return sec
def dec(d,m,s):
    if d[0] != '-':
        mi = float(d)*60+float(m)
        sec = mi*60+float(s)
    if d[0] == '-':
        mi = float(d)*60-float(m)
        sec = mi*60-float(s)
    return sec



