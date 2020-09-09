from py_ecc.fields import FQ, bn128_FQ
from py_ecc.fields.field_properties import field_properties
bn128_FQ.field_modulus = field_properties["bn128"]["field_modulus"]
a = bn128_FQ(19969813732963974350542270771558874737889757243987466590255542594953650591601)

