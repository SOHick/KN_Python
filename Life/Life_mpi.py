from mpi4py import MPI
import numpy as np
import sys
import time

def read_grid(filename):
    """Загрузка начальной конфигурации из файла"""
    with open(filename, 'r') as f:
        grid = np.array([list(line.strip()) for line in f], dtype=np.int8)
    return grid


def save_grid(grid, filename):
    """Сохранение конфигурации в файл"""
    np.savetxt(filename, grid, fmt='%d', delimiter='')


def evolve_subgrid(subgrid, steps, comm, rank, size):
    """Выполнение шагов эволюции для подгрида"""
    rows, cols = subgrid.shape
    padded = np.zeros((rows + 2, cols + 2), dtype=np.int8)

    for _ in range(steps):
        padded[1:-1, 1:-1] = subgrid

        # Соседи для всех клеток (без границ)
        neighbors = (
                padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
                padded[1:-1, :-2] + padded[1:-1, 2:] +
                padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]
        )

        # Правила игры "Жизнь"
        birth = (neighbors == 3) & (subgrid == 0)
        survive = ((neighbors == 2) | (neighbors == 3)) & (subgrid == 1)
        subgrid[:] = np.where(birth | survive, 1, 0)

        # Обмен граничными строками между процессами
        comm.Barrier()
        if rank > 0:
            comm.Send(subgrid[0, :], dest=rank - 1, tag=0)
            comm.Recv(subgrid[-1, :], source=rank - 1, tag=1)
        if rank < size - 1:
            comm.Recv(subgrid[0, :], source=rank + 1, tag=0)
            comm.Send(subgrid[-1, :], dest=rank + 1, tag=1)


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if len(sys.argv) != 4:
        if rank == 0:
            print("Использование: mpiexec -n <процессы> python life_mpi.py <входной файл> <шаги> <выходной файл>")
        sys.exit()

    input_file = sys.argv[1]
    steps = int(sys.argv[2])
    output_file = sys.argv[3]

    if rank == 0:
        # Главный процесс загружает и распределяет данные
        full_grid = read_grid(input_file)
        rows, cols = full_grid.shape

        # Разделение грида между процессами
        chunk_size = rows // size
        remainder = rows % size

        # Отправка данных другим процессам
        for i in range(1, size):
            start = i * chunk_size + min(i, remainder)
            end = start + chunk_size + (1 if i < remainder else 0)
            comm.send((full_grid[start:end, :], steps), dest=i)

        # Обработка своей части
        subgrid = full_grid[:chunk_size + (1 if 0 < remainder else 0), :]
    else:
        # Получение данных от главного процесса
        subgrid, steps = comm.recv(source=0)

    # Замер времени выполнения
    start_time = time.time()
    evolve_subgrid(subgrid, steps, comm, rank, size)
    elapsed_time = time.time() - start_time

    # Сбор результатов на главном процессе
    if rank == 0:
        result = np.zeros((rows, cols), dtype=np.int8)
        result[:subgrid.shape[0], :] = subgrid

        for i in range(1, size):
            start = i * chunk_size + min(i, remainder)
            end = start + (chunk_size + (1 if i < remainder else 0))
            comm.Recv(result[start:end, :], source=i)

        save_grid(result, output_file)

        # Вывод статистики
        print(f"Размер грида: {rows}x{cols}")
        print(f"Шагов: {steps}")
        print(f"Процессов: {size}")
        print(f"Время выполнения: {elapsed_time:.4f} сек")
    else:
        comm.Send(subgrid, dest=0)

    MPI.Finalize()