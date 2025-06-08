from tkinter import *
from tkinter import ttk
import tkintermapview
from utils import get_fuel_stations_near_city

# === GLOBALNE ZMIENNE ===

station_markers = []
station_data = []

# === FUNKCJE MAPY ===

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

# === GUI APLIKACJI ===

root = Tk()
root.title("Zarządzanie siecią stacji paliw")
root.geometry("1200x750")

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

# === ZAKŁADKA MAPA ===

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

# NOWE PRZYCISKI PRZEŁĄCZAJĄCE ZAKŁADKI
Button(frame_left, text="➡️ Przenieś stacje do zakładki", command=lambda: notebook.select(frame_stations)).pack(pady=2, fill=X)
Button(frame_left, text="➡️ Przenieś pracowników do zakładki", command=lambda: notebook.select(frame_employees)).pack(pady=2, fill=X)
Button(frame_left, text="➡️ Przenieś klientów do zakładki", command=lambda: notebook.select(frame_customers)).pack(pady=2, fill=X)

label_info = Label(frame_left, text="", fg="blue")
label_info.pack(pady=5)

listbox = Listbox(frame_left, width=50)
listbox.pack(pady=10, fill=BOTH, expand=True)
listbox.bind("<<ListboxSelect>>", on_listbox_click)

map_widget_mapa = tkintermapview.TkinterMapView(frame_right, width=800, height=450)
map_widget_mapa.pack(fill=BOTH, expand=True)
map_widget_mapa.set_position(52.0, 19.0)
map_widget_mapa.set_zoom(6)

# === ZAKŁADKA STACJE ===

def update_station_listbox():
    listbox_stations.delete(0, END)
    for i, s in enumerate(station_data):
        listbox_stations.insert(i, f"{i+1}. {s['name']} – {s['lat']:.5f}, {s['lon']:.5f}")

def show_selected_station_on_map():
    try:
        index = listbox_stations.curselection()[0]
        station = station_data[index]
        map_widget_mapa.set_position(station["lat"], station["lon"])
        map_widget_mapa.set_zoom(15)
        label_stations_info.config(text=f"{station['name']} ({station['lat']:.4f}, {station['lon']:.4f})")
    except IndexError:
        label_stations_info.config(text="❗ Wybierz stację")

def delete_station():
    try:
        index = listbox_stations.curselection()[0]
        station_markers[index].delete()
        station_markers.pop(index)
        station_data.pop(index)
        update_station_listbox()
        label_stations_info.config(text="🗑️ Stacja usunięta")
    except IndexError:
        label_stations_info.config(text="❗ Nie wybrano stacji")

def edit_station():
    try:
        index = listbox_stations.curselection()[0]
        entry_station_name.delete(0, END)
        entry_station_name.insert(0, station_data[index]['name'])
        button_edit.config(text="Zapisz", command=lambda: save_station_name(index))
        label_stations_info.config(text="✏️ Edytuj nazwę i kliknij Zapisz")
    except IndexError:
        label_stations_info.config(text="❗ Wybierz stację do edycji")

def save_station_name(index):
    new_name = entry_station_name.get().strip()
    if not new_name:
        label_stations_info.config(text="❗ Nazwa nie może być pusta")
        return
    station_data[index]['name'] = new_name
    station_markers[index].set_text(new_name)
    update_station_listbox()
    entry_station_name.delete(0, END)
    button_edit.config(text="Edytuj", command=edit_station)
    label_stations_info.config(text="✅ Zmieniono nazwę stacji")

frame_stations = Frame(notebook)
notebook.add(frame_stations, text="Stacje")

left = Frame(frame_stations)
left.pack(side=LEFT, fill=Y, padx=10, pady=10)

right = Frame(frame_stations)
right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

Label(left, text="Nazwa stacji:").pack(pady=(5, 0))
entry_station_name = Entry(left, width=30)
entry_station_name.pack(pady=2)

button_edit = Button(left, text="Edytuj", command=edit_station)
button_edit.pack(pady=2)

Button(left, text="Usuń", command=delete_station).pack(pady=2)
Button(left, text="Pokaż na mapie", command=show_selected_station_on_map).pack(pady=2)

label_stations_info = Label(left, text="Brak akcji", fg="blue", wraplength=200)
label_stations_info.pack(pady=10)

listbox_stations = Listbox(left, width=45, height=25)
listbox_stations.pack(pady=10, fill=Y)

def on_stations_tab_selected(event):
    selected_tab = notebook.index("current")
    if notebook.tab(selected_tab, "text") == "Stacje":
        update_station_listbox()

notebook.bind("<<NotebookTabChanged>>", on_stations_tab_selected)

# === ZAKŁADKA PRACOWNICY ===

frame_employees = Frame(notebook)
notebook.add(frame_employees, text="Pracownicy")
Label(frame_employees, text="Moduł zarządzania pracownikami (w przygotowaniu)", font=("Arial", 14)).pack(pady=20)

# === ZAKŁADKA KLIENCI ===

frame_customers = Frame(notebook)
notebook.add(frame_customers, text="Klienci")
Label(frame_customers, text="Moduł zarządzania klientami (w przygotowaniu)", font=("Arial", 14)).pack(pady=20)

root.mainloop()
