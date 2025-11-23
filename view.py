class TaskView: # Интерфейс
    def show_tasks(self, tasks):
        print("\nYour Tasks:")
        for index, task in enumerate(tasks):
            print(f"{index + 1}. {task}")

        # В классе Тасквью создаем метод шоу_таскс в котором на следующей строке выводим текст цикла  начиная с цифры 1 список таскс

    def show_message(self, message):
        print(message)
        # Выводим атрибут мессадж




