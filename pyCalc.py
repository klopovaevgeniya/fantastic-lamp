import os
import math

number = 0
while number != 12:
    os.system('cls')

    print("1. Сложение")
    print("2. Вычитание")
    print("3. Умножение")
    print("4. Деление")
    print("5. Возведение в степень")
    print("6. Квадратный корень числа")
    print("7. Процент от числа")
    print("8. Факториал")
    print("9. Синус угла")
    print("10.Косинус угла")
    print("11. Тангенс угла")
    print("12. Выйти из калькулятора")

    number = int(input("\n---->"))
    print("")

    if number==1: # Сложение
        a = float(input('Введите слагаемое A: '))
        b = float(input('Введите слагаемое B: '))
        print("Результат: A+B = ", a+b)

    elif number==2: # Вычитание
        a = float(input('Введите уменьшаемое A: '))
        b = float(input('Введите вычитаемое B: '))
        print("Результат: A-B = ", a-b)

    elif number==3: # Умножение
        a = float(input('Введите множитель A: '))
        b = float(input('Введите множитель B: '))
        print("Результат: A*B = ", a*b)

    elif number==4: # Деление
        a = float(input('Введите делимое A: '))
        b = float(input('Введите делитель B: '))
        print("Результат: A/B = ", a/b)

    elif number==5: # Возведение в степень
        a = float(input('Введите основание A: '))
        b = float(input('Введите показатель степени B: '))
        print("Результат: A в степени B =", a**b)

    elif number==6: # Квадратный корень числа
        a = float(input('Введите число: '))
        print("Результат: Квадратный корень из ", a ," = ", round(math.sqrt(a), 3))

    elif number==7: # Процент от числа
        a = float(input('Введите число: '))
        b = float(input('Введите %: '))
        print("Результат: ", b, " процентов от ", a, " = ", a / 100 * b)

    elif number==8: # Факториал числа
        a = int(input('Введите число: '))
        b=1
        for i in range(1, a+1):
           b=b*i
        print("Результат: ", a, "! = ", b)

    elif number==9: # Синус угла
        a = float(input('Введите угол (в градусах): '))
        print("Результат: Синус ", a, "градусов = ", round(math.sin(math.pi*a/180), 3))

    elif number==10: # Косинус угла
        a = float(input('Введите угол (в градусах): '))
        print("Результат: Косинус ", a, "градусов = ", round(math.cos(math.pi*a/180), 3))

    elif number==11: # Тангенс угла
        a = float(input('Введите угол (в градусах): '))
        if round(math.cos(math.pi*a/180), 3) == 0:
            print("Результат: Тангенс ", a, "градусов не определен")
        else:
            print("Результат: Тангенс ", a, "градусов = ", round(math.tan(math.pi*a/180), 3))


    if number != 12: # Выход
        input("Нажмите Enter для продолжения...")



        


