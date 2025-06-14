import time
import os


def clear_console():
    """Очистка консоли (кросс-платформенный способ)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_grid(grid_new, alive_char='.', dead_char='#'):
    """Вывод грида в консоль с заданными символами"""
    for row in grid_new:
        print(''.join([alive_char if cell == 1 else dead_char for cell in row]))
    print()


def evolve(grid_new):
    """Один шаг эволюции игры 'Жизнь'"""
    rows = len(grid_new)
    cols = len(grid_new[0]) if rows > 0 else 0
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]

    for i in range(rows):
        for j in range(cols):
            neighbors = sum(
                grid_new[x][y]
                for x in range(max(0, i - 1), min(rows, i + 2))
                for y in range(max(0, j - 1), min(cols, j + 2))
                if (x != i or y != j)
            )
            if grid_new[i][j] == 1:
                grid_new[i][j] = 1 if neighbors in (2, 3) else 0
            else:
                grid_new[i][j] = 1 if neighbors == 3 else 0
    return new_grid


def load_grid(filename):
    """Загрузка грида из текстового файла"""
    with open(filename, 'r') as f:
        grid_new = []
        for line in f:
            line = line.strip()
            if not line:
                continue  # Пропускаем пустые строки
            row = []
            for char in line:
                if char == '1':
                    row.append(1)
                else:
                    row.append(0)
            grid_new.append(row)
    return grid_new


# Загрузка начальной конфигурации из файла
input_file = "random_input.txt"  # Укажите путь к вашему файлу
try:
    grid_new = load_grid(input_file)
except FileNotFoundError:
    print(f"Файл {input_file} не найден!")
    exit()

# Проверка, что грид не пустой
if not grid_new or not any(any(row) for row in grid_new):
    print("Ошибка: грид пустой или содержит только нули!")
    exit()

# Запуск анимации на 50 шагов
for step in range(1):
    clear_console()
    print(f"Шаг {step + 1}:\n")
    print_grid(grid_new, alive_char='.', dead_char='#')
    grid_new = evolve(grid_new)
    time.sleep(2)