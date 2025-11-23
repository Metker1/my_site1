# 1 Задание
# Я не понял, что я написал , дз совсем не понял :)

# def sort_list(lst):
#     n = len(lst)
#     avg = sum(lst) / n
#     if avg > 0:
#         lst[:2*n//3] = sorted(lst[:2*n//3])
#     else:
#         lst[:n//3] = sorted(lst[:n//3])
#         lst[n//3:] = lst[n//3:][::-1]
#     return lst
#
# lst = input('Введите числа').split()
# lst = [int(x) for x in lst]
# print('Sorted list',end='')
# print(sort_list(lst))


# 2 Задание
# grades = []
# for i in range(10):
#     while True:
#         grade = int(input(f"Введите оценку {i + 1} (1-12): "))
#         if 1 <= grade <= 12:
#             grades.append(grade)
#             break
#         else:
#             print("Неверная оценка. Пожалуйста, попробуйте снова.")
#
#
#
#
# def calculate_average():
#     return sum(grades) / len(grades)
#
# def is_scholarship_eligible():
#     return calculate_average() >= 10.7
#
#
# def sort_grades(order):
#     if order == "asc":
#         return sorted(grades)
#     elif order == "desc":
#         return sorted(grades, reverse=True)
#     else:
#         print("Недействительный заказ. Пожалуйста, попробуйте снова.")
#
# while True:
#     print("\nАкадемическое меню выступлений:")
#     print("1. Просмотр оценок")
#     print("2. Пересдать экзамен")
#     print("3. Проверьте право на получение стипендии")
#     print("4. Сортировка оценок")
#     print("5. Выход")
#     choice = input("Введите свой выбор: ")
#     if choice == "1":
#         print("Оценки:", grades)
#     elif choice == "2":
#         index = int(input("Введите номер экзамена для пересдачи (1-10): ")) - 1
#         if 0 <= index < 10:
#             new_grade = int(input("Введите новую оценку (1-12): "))
#             grades[index] = new_grade
#             print("Оценка успешно обновлена!")
#         else:
#             print("Неверный номер экзамена. Пожалуйста, попробуйте снова.")
#     elif choice == "3":
#         if is_scholarship_eligible():
#             print("Студент имеет право на получение стипендии!")
#         else:
#             print("Студент не имеет права на получение стипендии.")
#     elif choice == "4":
#         order = input("Введите порядок сортировки (asc/desc): ")
#         sorted_grades = sort_grades(order)
#         print("Отсортированные сорта:", sorted_grades)
#     elif choice == "5":
#         print("До свидания!")
#         break
#     else:
#         print("Неверный выбор. Пожалуйста, попробуйте снова.")















# 3 Задание

# Пузырьковый
# import random
# def bubble_sort(lst):
#     n = len(lst)
#     for i in range(n - 1):
#         count = 0
#         for j in range(n - i - 1):
#             if lst[j] > lst[j + 1]:
#                 lst[j], lst[j + 1] = lst[j + 1], lst[j]
#                 count += 1
#         if count == 0:
#             break
#     return lst
#
#
#
#
# lst = []
# for i in range(500):
#     lst.append(random.randint(1,500))
#
# bubble_sort(lst)
#
# print(lst)

