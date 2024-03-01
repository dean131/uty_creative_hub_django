


def name_formater(full_name):
    if not full_name:
        return ''
    full_name = full_name.split(' ')
    return full_name[1] if (len(full_name[0]) < 3 and len(full_name) > 1) else full_name[0]

