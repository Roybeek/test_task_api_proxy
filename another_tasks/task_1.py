def simple_numbers(n: int):
    if n < 2:
        return
    for number in range(2, n):
        for i in range(2, number // 2 + 1):
            if number % i == 0:
                break
        else:
            print(number)

