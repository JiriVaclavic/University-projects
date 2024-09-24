
import tkinter as tk
from tkinter import *
import random
import time


class BeeAlgorithmGUI:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-zoomed', True)
        self.root.title("Bee Algorithm Visualization")
        self.root.wm_state('normal')

        # Ziskani rozmeru obrazovky
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Nastaveni vykreslovaciho okna
        window_width = 400
        window_height = 200

        # Vypocet pozice pro vycentrovani okna
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        # Nastaveni rozmeru okna a jeho pozice
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (width, height))

        self.canvas = tk.Canvas(self.root, width=400, height=screen_height * 0.5, bg='grey')
        self.canvas.pack(side=TOP, expand=YES, fill=X)

        # Pridani posuvniku pro nastaveni hodnoty space_range
        self.space_range_var = tk.IntVar()
        self.create_slider_box("Space distance:", self.space_range_var, 0, 500, self.update_space_range, resolution=1)

        # Pridani posuvniku pro nastaveni hodnoty max_iterations
        self.max_iterations_var = tk.IntVar()
        self.create_slider_box("Max Iterations:", self.max_iterations_var, 10, 1000, self.update_max_iterations,
                            resolution=10)

        # Pridani posuvniku pro nastaveni hodnoty scout_bees_ratio
        self.scout_bees_ratio_var = tk.DoubleVar()
        self.create_slider_box("Scout Bees ratio:", self.scout_bees_ratio_var, 0.1, 1.0, self.update_scout_bees_ratio,
                            resolution=0.01)

        # Pridani posuvniku pro nastaveni hodnoty colony_size
        self.colony_size_var = tk.IntVar()
        self.create_slider_box("Colony Size:", self.colony_size_var, 10, 500, self.update_colony_size)

        # Spustit algoritmus s vizualizaci po stisku tlacitka
        start_button = tk.Button(self.root, text="Start Bee Algorithm", bg='black', fg='white', height=20, width=20,
                                command=self.start_algorithm)
        start_button.pack(side="right", pady=25, padx=25)

        self.space_range_var.set(200)
        self.colony_size_var.set(50)
        self.scout_bees_ratio_var.set(0.5)
        self.max_iterations_var.set(500)

    def create_slider_box(self, label, variable, from_value, to_value, command, resolution=1):
        frame = tk.Frame(self.root)
        frame.pack(side="left", pady=25, padx=25)
        label_widget = tk.Label(frame, text=label)
        label_widget.pack(side="left")
        scale = tk.Scale(frame, from_=from_value, to=to_value, orient="horizontal", variable=variable, command=command,
                        resolution=resolution)
        scale.pack()
        return frame, scale

    def update_space_range(self, value):
        self.space_range_var.set(int(value))
        self.root.delete("info")  # Odstraneni predchozich textovych znacek

    def update_max_iterations(self, value):
        self.max_iterations_var.set(int(value))
        self.root.delete("info")  # Odstraneni predchozich textovych znacek

    def update_scout_bees_ratio(self, value):
        self.scout_bees_ratio_var.set(float(value))
        self.root.delete("info")  # Odstraneni predchozich textovych znacek

    def update_colony_size(self, value):
        self.colony_size_var.set(int(value))
        self.root.delete("info")  # Odstraneni predchozich textovych znacek

    def start_algorithm(self):
        bee_algorithm_with_visualization(
            max_iterations=self.max_iterations_var.get(),
            colony_size=self.colony_size_var.get(),
            scout_bees_ratio=self.scout_bees_ratio_var.get(),  # skauti
            other_bees_ratio=1 - self.scout_bees_ratio_var.get(),
            dimension=2,
            space_range=(-self.space_range_var.get(), self.space_range_var.get()),
            canvas=self.canvas,
            func=0
        )


def fitness_function(x, func=0):
    if func == 0:
        return -((x[0] - 3) ** 2 + (x[1] - 5) ** 2)  # Minimalizace kvadraticke funkce
    else:
        return sum(xi ** 2 for xi in x)


def initialize_colony(colony_size, dimension, space_range=(-200, 200)):
    colony = []
    for _ in range(colony_size):
        bee_position = [random.uniform(space_range[0], space_range[1]) for _ in range(dimension)]
        colony.append(bee_position)
    return colony


def visualize_colony(canvas, colony, color, radius=10):
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    for bee in colony:
        x, y = bee
        x += (canvas_width / 2)
        y += (canvas_height / 2)

        canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, tags="bees")


def visualize_progress(canvas, iteration, best_solution, best_fitness):
    canvas.delete("info")  # Odstraneni predchozich hodnot gui
    canvas.create_text(150, 20, text="Iteration: {}".format(iteration + 10), anchor="w", justify="center", tags="info")
    canvas.create_text(150, 40, text="Best Solution: {}".format(best_solution), anchor="w", justify="center", tags="info")
    canvas.create_text(150, 60, text="Best Fitness: {}".format(best_fitness), anchor="w", justify="center", tags="info")
    canvas.update()


def bee_algorithm_with_visualization(max_iterations, colony_size, scout_bees_ratio, other_bees_ratio, dimension, canvas,
                                    space_range, func=0):
    scout_bees = int(colony_size * scout_bees_ratio)
    other_bees = int(colony_size * other_bees_ratio)

    colony = initialize_colony(colony_size, dimension, space_range)

    for iteration in range(max_iterations):
        # Hledani skaut vcel
        for i in range(scout_bees):
            current_bee = colony[i]
            candidate_solution = [current_bee[j] + random.uniform(-1, 1) for j in range(dimension)]
            candidate_fitness = fitness_function(candidate_solution, func)

            # Aktualizace polohy vcely na zaklade kvality noveho reseni
            if candidate_fitness > fitness_function(current_bee, func):
                colony[i] = candidate_solution

        # Hledani ostatnich vcel
        total_fitness = sum(fitness_function(bee, func) for bee in colony[:scout_bees])
        for i in range(scout_bees, scout_bees + other_bees):
            # Vyber vcely na zaklade pravdepodobnosti vyberu
            selected_bee_index = probabilistic_selection(colony[:scout_bees], total_fitness, func)
            current_bee = colony[i]
            
            # Ostatni vcely hledaji s ohledem na informace poskytnute skauty
            direction_to_scout = [colony[selected_bee_index][j] - current_bee[j] for j in range(dimension)]
            candidate_solution = [current_bee[j] + 1 * direction_to_scout[j] + random.uniform(-1, 1) for j in range(dimension)]
            candidate_fitness = fitness_function(candidate_solution, func)

            # Aktualizace polohy vcely na zaklade kvality noveho reseni
            if candidate_fitness > fitness_function(current_bee, func):
                colony[i] = candidate_solution

        # Vizualizace prubehu algoritmu
        if iteration % 10 == 0:
            best_solution = max(colony, key=lambda bee: fitness_function(bee, func))
            best_fitness = fitness_function(best_solution, func)
            canvas.delete("bees")  # Odstraneni predchozich vcel
            visualize_colony(canvas, colony, "blue", radius=10)
            visualize_colony(canvas, [best_solution], "red", radius=10)

            visualize_progress(canvas, iteration, best_solution, best_fitness)
            time.sleep(0.05)  # Kratka pauza pro vizualizaci

    best_solution = max(colony, key=lambda bee: fitness_function(bee, func))
    return best_solution, fitness_function(best_solution, func)

# Pravdepodobnosti vyber jedince na zaklade jeho fitness funkce
def probabilistic_selection(scout_bees, total_fitness, func):
    selection_point = random.uniform(0, total_fitness)
    cumulative_fitness = 0
    for i, bee in enumerate(scout_bees):
        cumulative_fitness += fitness_function(bee, func)
        if cumulative_fitness >= selection_point:
            return i

    # Pokud nedojde k vyberu zadne vcely, vrati se posledni skaut
    return len(scout_bees) - 1



def main():
    try:
        root = tk.Tk()
        app = BeeAlgorithmGUI(root)
        root.mainloop()
    except Exception as error:
        print(error)
        input()


if __name__ == "__main__":
    main()
