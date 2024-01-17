def prompt_and_validate(expected_type, prompt):
    while True:
        try:
            value = input(prompt)
            if expected_type == str:
                return value
            else:
                value = expected_type(value)
                if isinstance(value, expected_type):
                    return value
                else:
                    raise ValueError
        except (ValueError, SyntaxError):
            print(
                "Invalid input. Please enter a valid {}.".format(expected_type.__name__)
            )
