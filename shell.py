import kumo


while True:
    text = input('kumo > ')
    result, error = kumo.run('<stdin>', text)

    if error: print(error.as_string())
    else: print(result)
