from tkinter import *
from tkinter import ttk
import tkintermapview
from utils import get_fuel_stations_near_city

station_markers = []
station_data = []

def find_stations():
    city = entry_city.get()

    if not city:
        label_info.config(text="❗ Podaj nazwę miejscowości")
        return

    listbox.delete(0, END)
    for m in station_markers:
        m.delete()
    station_markers.clear()
    station_data.clear()

    stations = get_fuel_stations_near_city(city)

    if not stations:
        label_info.config(text="⚠️ Nie znaleziono stacji w okolicy.")
        return

    for station in stations:
        marker = map_widget_mapa.set_marker(station["lat"], station["lon"], text=station["name"])
        station_markers.append(marker)
        station_data.append(station)
        listbox.insert(END, f"{station['name']} – {station['lat']:.5f}, {station['lon']:.5f}")

    map_widget_mapa.set_position(stations[0]["lat"], stations[0]["lon"])
    map_widget_mapa.set_zoom(13)
    label_info.config(text=f"✅ Znaleziono {len(stations)} stacji")

def on_listbox_click(event):
    try:
        index = listbox.curselection()[0]
        station = station_data[index]
        map_widget_mapa.set_position(station["lat"], station["lon"])
        map_widget_mapa.set_zoom(16)
    except IndexError:
        pass

root = Tk()
root.title("Zarządzanie siecią stacji paliw")
root.geometry("1200x700")

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

frame_map = Frame(notebook)
notebook.add(frame_map, text="Mapa")

frame_left = Frame(frame_map)
frame_left.pack(side=LEFT, fill=Y, padx=10, pady=10)

frame_right = Frame(frame_map)
frame_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

Label(frame_left, text="Miejscowość:").pack(pady=5)
entry_city = Entry(frame_left, width=30)
entry_city.pack(pady=5)

Button(frame_left, text="Szukaj stacji", command=find_stations).pack(pady=10)

# Nowe 3 przyciski – pod "Szukaj"
Button(frame_left, text="Przenieś stacje do zakładki").pack(pady=2, fill=X)
Button(frame_left, text="Przenieś pracowników do zakładki").pack(pady=2, fill=X)
Button(frame_left, text="Przenieś klientów do zakładki").pack(pady=2, fill=X)

label_info = Label(frame_left, text="", fg="blue")
label_info.pack(pady=5)

listbox = Listbox(frame_left, width=50)
listbox.pack(pady=10, fill=BOTH, expand=True)
listbox.bind("<<ListboxSelect>>", on_listbox_click)

map_widget_mapa = tkintermapview.TkinterMapView(frame_right, width=800, height=450)
map_widget_mapa.pack(fill=BOTH, expand=True)
map_widget_mapa.set_position(52.0, 19.0)
map_widget_mapa.set_zoom(6)

frame_stations = Frame(notebook)
notebook.add(frame_stations, text="Stacje")

Label(frame_stations, text="Lista wszystkich stacji (do uzupełnienia)", font=("Arial", 14)).pack(pady=20)

frame_employees = Frame(notebook)
notebook.add(frame_employees, text="Pracownicy")

Label(frame_employees, text="Moduł zarządzania pracownikami (w przygotowaniu)", font=("Arial", 14)).pack(pady=20)

frame_customers = Frame(notebook)
notebook.add(frame_customers, text="Klienci")

Label(frame_customers, text="Moduł zarządzania klientami (w przygotowaniu)", font=("Arial", 14)).pack(pady=20)

root.mainloop()