import threading
import time
import random
from tkinter import Tk, Canvas


class Philosopher(threading.Thread):
    def __init__(self, id, forks, canvas, root, philosophers, stop_event):
        threading.Thread.__init__(self)
        self.id = id
        self.forks = forks
        self.state = "thinking"
        self.left_fork = id
        self.right_fork = (id + 1) % len(forks)
        self.canvas = canvas
        self.root = root
        self.eat_count = 0
        self.philosophers = philosophers
        self.stats_tag = "stats_text"
        self.stop_event = stop_event
        self.update_ui()

    def run(self):
        while not self.stop_event.is_set():
            self.think()
            if not self.stop_event.is_set():
                self.eat()

    def think(self):
        self.state = "thinking"
        self.update_ui()
        time.sleep(random.uniform(1, 3))

    def eat(self):
        # Запрос вилок
        self.request_forks()

        # Филосовы кушают
        self.state = "eating"
        self.eat_count += 1
        self.update_ui()
        time.sleep(random.uniform(2, 4))

        # Освобождаем вилки
        self.release_forks()

    def request_forks(self):
        # Алгоритм Чанда-Мисра
        if self.id % 2 == 0:
            first, second = self.left_fork, self.right_fork
        else:
            first, second = self.right_fork, self.left_fork

        self.forks[first].acquire()
        self.forks[second].acquire()

    def release_forks(self):
        self.forks[self.left_fork].release()
        self.forks[self.right_fork].release()
        self.state = "thinking"
        self.update_ui()

    def update_ui(self):
        try:
            colors = {"thinking": "gray", "eating": "green", "waiting": "red"}
            x = 300 + 200 * (0.8 * (self.id % 5) - 1)
            y = 300 + 200 * (0.8 * (self.id // 5) - 1)

            # Удаляем предыдущие элементы философа
            self.canvas.delete(f"philosopher_{self.id}")

            # Рисуем
            self.canvas.create_oval(x - 30, y - 30, x + 30, y + 30,
                                    fill=colors[self.state],
                                    tags=f"philosopher_{self.id}")
            self.canvas.create_text(x, y, text=str(self.id),
                                    tags=f"philosopher_{self.id}")

            # Обновляем статистику (удаляем старую)
            self.canvas.delete(self.stats_tag)

            # Создаем новую статистику
            stats_text = "\n".join([f"Философ {p.id}: {p.eat_count} раз"
                                    for p in sorted(self.philosophers, key=lambda x_val: x_val.id)])
            self.canvas.create_text(700, 500, text=stats_text,
                                    anchor="se", tags=self.stats_tag)
        except:
            # Игнорируем ошибки, связанные с уничтожением canvas
            pass


def main():
    NUM_PHILOSOPHERS = 10  # Параметр количества философов

    root = Tk()
    root.title(f"Проблема философов (N={NUM_PHILOSOPHERS})")
    canvas = Canvas(root, width=800, height=600)
    canvas.pack()

    # Событие для остановки потоков
    stop_event = threading.Event()

    forks = [threading.Lock() for _ in range(NUM_PHILOSOPHERS)]
    philosophers = []

    # Создаем философов
    for i in range(NUM_PHILOSOPHERS):
        p = Philosopher(i, forks, canvas, root, philosophers, stop_event)
        philosophers.append(p)

    # Запускаем потоки
    for p in philosophers:
        p.start()

    # Обработчик закрытия окна
    def on_closing():
        stop_event.set()  # Сигнал остановки для всех потоков
        root.after(100, root.destroy)  # Даем время потокам на завершение

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
