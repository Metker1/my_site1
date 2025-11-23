import pytest
import math

# def calculator(a,b):
#     if b == 0:
#         raise ZeroDivisionError("Деление на ноль")
#     return a / b
#
#
# def test_calculator():
#     with pytest.raises(ZeroDivisionError):
#         calculator(10,0)



# class Calculator:
#     def add(self, a, b):
#         return a + b
#
#     def subtract(self, a, b):
#         return a - b
#
#     def multiply(self, a, b):
#         return a * b
#
#     def divide(self, a, b):
#         if b == 0:
#             raise ZeroDivisionError("Деление на ноль невозможно.")
#         return a / b
#
#
# calc = Calculator()
#
#
# def test_add():
#     assert calc.add(3, 4) == 7
#     assert calc.add(-1, 5) == 4
#
#
#
# def test_substract():
#     assert calc.subtract(10, 4) == 6
#     assert calc.subtract(-3, -6) == 3
#
#
#
# def test_multiply():
#     assert calc.multiply(3, 5) == 15
#     assert calc.multiply(-2, 4) == -8
#
#
# def test_devide():
#     with pytest.raises(ZeroDivisionError):
#         calc.divide(10,0)




# class BankAccount:
#     def __init__(self, initial_balance):
#         self.balance = initial_balance
#
#     def add(self, amount):
#         amount + self.balance
#
#
#     def minus(self, amount):
#         self.balance - amount
#
#
#
#     def get_balance(self):
#         return self.balance
#
#
# account = BankAccount(5000)
#
# def test_add():
#     account.add(100) == 5100
#
#
# def test_minus():
#     account.add(100) == 4900
#
# def test_get_balance():
#     account.get_balance() == 5000







# class Shape:
#
#     def area(self):
#         pass
#
#
# class Rectangle(Shape):
#     def __init__(self, width, height):
#         self.width = width
#         self.height = height
#
#     def area(self):
#         return self.width * self.height
#
# class Circle(Shape):
#     def __init__(self, radius):
#         self.radius = radius
#
#     def area(self):
#         return math.pi * self.radius ** 2
#
#
# rect = Rectangle(4, 5)
# circle = Circle(3)
#
# def test_area():
#     assert rect.area() == 20
#
# def test_area1():
#     assert circle.area() == 28.274333882308138







# def chet(n):
#     return n % 2 == 0
#
#
# def test_chet():
#     assert chet(2) is True