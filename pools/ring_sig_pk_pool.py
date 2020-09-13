
MAX_PK_NUM_LIMIT = 1000


class RingSigPKPool:

    def __init__(self):
        self.pks = set()
        # self.pks looks like {(int1, int2), (int3, int4)}

        self.max_pk_num_limit = MAX_PK_NUM_LIMIT

    def get_all_pks(self):
        pks_in_str = ''
        temp = []
        for pk in self.pks:
            for xy in pk:
                temp.append(str(xy))
            print(temp)
            pks_in_str += ','.join(temp)
            pks_in_str += ';'
            temp.clear()

        return pks_in_str

    def add_pk(self, pk: tuple):
        if not len(pk) == 2:
            raise ValueError("Error1: please add a valid pk(curve point).")

        for xy in pk:
            if not type(xy) == int:
                raise ValueError("Error2: please add a valid int pk.")

        self.pks.add(pk)

    def submit_pk(self, pk: tuple):
        if self.pk_num < self.max_pk_num_limit:
            self.add_pk(pk)
            return True

        return False

    @property
    def pk_num(self):
        # len() returns tuple number in set 'pks'
        return len(self.pks)
