from tkinter import *
from tkinter import ttk
import tkintermapview
from utils import get_fuel_stations_near_city

# === GLOBALNE DANE ===

station_markers = []
station_data = []

stations_tab_data = []
stations_tab_markers = []

employees_data = []

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

def update_employee_table():
    for row in tree_employees.get_children():
        tree_employees.delete(row)
    for i, e in enumerate(employees_data):
        tree_employees.insert("", "end", values=(e['name'], e['surname'], e['role'], e['station']))

def add_employee():
    name = entry_employee_name.get().strip()
    surname = entry_employee_surname.get().strip()
    role = entry_employee_role.get().strip()
    station_name = entry_station_name.get().strip()

    if name and surname and role and station_name:
        employees_data.append({
            "name": name,
            "surname": surname,
            "role": role,
            "station": station_name
        })

        entry_employee_name.delete(0, END)
        entry_employee_surname.delete(0, END)
        entry_employee_role.delete(0, END)
        entry_station_name.delete(0, END)

        update_employee_table()
        label_employees_info.config(text="✅ Dodano pracownika")
    else:
        label_employees_info.config(text="❗ Uzupełnij wszystkie pola")

def update_station_combobox():
    pass

def move_selected_station_to_tab():
    try:
        index = listbox.curselection()[0]
        station = station_data[index]
        if station not in stations_tab_data:
            stations_tab_data.append(station)
            marker = map_widget_stations.set_marker(station["lat"], station["lon"], text=station["name"])
            stations_tab_markers.append(marker)
        notebook.select(frame_stations)
    except IndexError:
        label_info.config(text="❗ Zaznacz stację na liście")

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
Button(frame_left, text="➡️ Przenieś zaznaczoną stację do zakładki: STACJE", command=move_selected_station_to_tab).pack(pady=2, fill=X)
Button(frame_left, text="➡️ Przejdź do zakładki: PRACOWNICY", command=lambda: notebook.select(frame_employees)).pack(pady=2, fill=X)
Button(frame_left, text="➡️ Przejdź do zakładki: KLIENCI", command=lambda: notebook.select(frame_customers)).pack(pady=2, fill=X)

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

frame_stations = Frame(notebook)
notebook.add(frame_stations, text="Stacje")

frame_stations_left = Frame(frame_stations)
frame_stations_left.pack(side=LEFT, fill=Y, padx=10, pady=10)

frame_stations_right = Frame(frame_stations)
frame_stations_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

listbox_stations = Listbox(frame_stations_left, width=45, height=25)
listbox_stations.pack(pady=10, fill=Y)

map_widget_stations = tkintermapview.TkinterMapView(frame_stations_right, width=800, height=450)
map_widget_stations.pack(fill=BOTH, expand=True)
map_widget_stations.set_position(52.0, 19.0)
map_widget_stations.set_zoom(6)

# === ZAKŁADKA PRACOWNICY ===

frame_employees = Frame(notebook)
notebook.add(frame_employees, text="Pracownicy")

frame_employees_left = Frame(frame_employees)
frame_employees_left.pack(side=LEFT, fill=Y, padx=10, pady=10)

frame_employees_right = Frame(frame_employees)
frame_employees_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

Label(frame_employees_left, text="Imię: ").pack()
entry_employee_name = Entry(frame_employees_left, width=30)
entry_employee_name.pack(pady=2)

Label(frame_employees_left, text="Nazwisko: ").pack()
entry_employee_surname = Entry(frame_employees_left, width=30)
entry_employee_surname.pack(pady=2)

Label(frame_employees_left, text="Stanowisko: ").pack()
entry_employee_role = Entry(frame_employees_left, width=30)
entry_employee_role.pack(pady=2)

Label(frame_employees_left, text="Stacja: ").pack()
entry_station_name = Entry(frame_employees_left, width=30)
entry_station_name.pack(pady=2)

Button(frame_employees_left, text="Dodaj pracownika", command=add_employee).pack(pady=5)

label_employees_info = Label(frame_employees_left, text="Brak akcji", fg="blue")
label_employees_info.pack(pady=5)

columns = ("Imię", "Nazwisko", "Stanowisko", "Stacja")
tree_employees = ttk.Treeview(frame_employees_right, columns=columns, show='headings')
for col in columns:
    tree_employees.heading(col, text=col)
    tree_employees.column(col, width=150)
tree_employees.pack(fill=BOTH, expand=True, padx=10, pady=10)

# === ZAKŁADKA KLIENCI ===

frame_customers = Frame(notebook)
notebook.add(frame_customers, text="Klienci")
Label(frame_customers, text="Moduł zarządzania klientami (w przygotowaniu)", font=("Arial", 14)).pack(pady=20)

root.mainloop()
