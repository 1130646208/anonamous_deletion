di1 = {
    "d": 2,
    "f": 3,
    "g": 4,
    "a": 2
}

di2 = {
    "d": 12,
    "f": 3,
    "g": 4,
    "a": 2
}

di3 = {
    "d": 3,
    "f": 3,
    "g": 4,
    "a": 2
}

sdi = sorted([di1, di2, di3], key=lambda x: x["d"])
print(sdi)
