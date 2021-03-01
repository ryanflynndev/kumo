import kumo


while True:
    text = input('kumo > ')
    result, error = kumo.run('<stdin>', text)

    #If there is an error we print it
    if error: print(error.as_string())
    #Otherwise we print the result
    else: print(result)
