
def get_all_pks(pks):
    pks_in_str = ''
    temp = []
    for pk in pks:
        for xy in pk:
            temp.append(str(xy))
        print(temp)
        pks_in_str += ','.join(temp)
        pks_in_str += ';'
        temp.clear()

    return pks_in_str


pks = set()
pks.add((112441254, 35444656))
pks.add((456889799, 46767422))
pks.add((986855858, 53937376))
print(get_all_pks(pks))
