
ps_value = [0]
if (1000.0 - ps_value[0]) < 0.0:
    ps_value[0] = 0
else:
    ps_value[0] = 1000.0  - ps_value[0]

print(ps_value[0])