import base64 as b64


data = b64.b64encode(b'secret1: wangshuangxing')
print(data)


missing_padding = 4 - len(data) % 4
if missing_padding:
    print(missing_padding)
    data += b'=' * missing_padding

print(data)

print(b64.b64decode(data))
