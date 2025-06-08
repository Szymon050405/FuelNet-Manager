from tkinter import *
from utils import get_coordinates


def fetch_coordinates():
    location = entry_location.get()
    if not location:
        label_result.config(text="❗ Podaj nazwę miejscowości")
        return
    coords = get_coordinates(location)
    label_result.config(text=f"Szerokość: {coords[0]:.5f}, Długość: {coords[1]:.5f}")

# Konfiguracja GUI
root = Tk()
root.title("Pobieranie współrzędnych z Wikipedii")
root.geometry("400x200")

# Pole do wpisania miejscowości
Label(root, text="Podaj nazwę miejscowości (Wikipedia):").pack(pady=10)
entry_location = Entry(root, width=40)
entry_location.pack()

# Przycisk do pobrania danych
Button(root, text="Pobierz współrzędne", command=fetch_coordinates).pack(pady=10)

# Etykieta na wynik
label_result = Label(root, text="Współrzędne pojawią się tutaj")
label_result.pack(pady=10)

# Uruchomienie GUI
root.mainloop()