import screeninfo

print(dir(screeninfo))

print(screeninfo.get_monitors())

for monitor in screeninfo.get_monitors():
    print(monitor.is_primary,monitor)