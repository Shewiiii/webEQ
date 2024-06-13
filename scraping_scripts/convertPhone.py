import numpy as np
from constants import delta


def convert_phone(
    name: str,
    phone: np.ndarray | list,
    compensation: np.ndarray = delta,
) -> np.ndarray:
    '''
    delta: from 5128 to 711
    -delta: from 711 to 5128
    '''
    assert len(phone) == 480, "Phone must have a length of 480."
    if type(phone) == list:
        np.array(phone)

    delta_phone = phone + compensation
    string = ''
    for fr, gain in delta_phone:
        string += f'{fr}    {gain}\n'

    open(f'Δ {name}.txt', 'w').write(string)
    return delta_phone
