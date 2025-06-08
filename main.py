from tkinter import *
from tkinter import ttk
import tkintermapview
from utils import get_city_coordinates, get_fuel_stations_near_city

# Globalne zmienne
station_markers = []
station_data = []
stations_tab_data = []
stations_tab_markers = []
employees_data = []
employees_by_station = {}
customers_data = []
customers_by_station = {}
editing_employee_index = None
editing_customer_index = None

# ------------------ FUNKCJE STACJE ------------------

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
        try:
            marker = map_widget_mapa.set_marker(station["lat"], station["lon"], text=station["name"])
            station_markers.append(marker)
            station_data.append(station)
            listbox.insert(END, f"{station['name']} – {station['lat']:.5f}, {station['lon']:.5f}")
        except KeyError as e:
            print(f"Błąd w danych stacji: {e}")

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

def move_selected_station_to_tab():
    try:
        index = listbox.curselection()[0]
        station = station_data[index]
        if station not in stations_tab_data:
            stations_tab_data.append(station)
            marker = map_widget_stations.set_marker(station["lat"], station["lon"], text=station["name"])
            stations_tab_markers.append(marker)
            listbox_stations.insert(END, f"{station['name']} – {station['lat']:.5f}, {station['lon']:.5f}")
        notebook.select(frame_stations)
    except IndexError:
        label_info.config(text="❗ Zaznacz stację na liście")

def rename_selected_station():
    index = listbox_stations.curselection()
    if not index:
        label_info.config(text="❗ Zaznacz stację do zmiany nazwy")
        return
    index = index[0]
    station = stations_tab_data[index]

    def apply_new_name():
        new_name = entry_new_name.get().strip()
        if new_name:
            station["name"] = new_name
            listbox_stations.delete(index)
            listbox_stations.insert(index, f"{new_name} – {station['lat']:.5f}, {station['lon']:.5f}")
            stations_tab_markers[index].set_text(new_name)
            rename_window.destroy()

    rename_window = Toplevel()
    rename_window.title("Zmień nazwę stacji")
    Label(rename_window, text="Nowa nazwa stacji:").pack(pady=5)
    entry_new_name = Entry(rename_window, width=40)
    entry_new_name.pack(pady=5)
    entry_new_name.insert(0, station["name"])
    Button(rename_window, text="Zapisz", command=apply_new_name).pack(pady=10)

def delete_selected_station():
    try:
        index = listbox_stations.curselection()[0]
        stations_tab_data.pop(index)
        marker = stations_tab_markers.pop(index)
        marker.delete()
        listbox_stations.delete(index)
    except IndexError:
        pass

# ------------------ PRACOWNICY ------------------

def create_employee_table_for_station(station_name):
    label = Label(frame_employees_right, text=f"📍 Pracownicy stacji: {station_name}", font=("Arial", 12, "bold"))
    label.pack(pady=(10, 0))
    tree = ttk.Treeview(frame_employees_right, columns=("Imię", "Nazwisko", "Stanowisko", "Lokalizacja"), show='headings')
    for col in ("Imię", "Nazwisko", "Stanowisko", "Lokalizacja"):
        tree.heading(col, text=col)
        tree.column(col, width=130)
    tree.pack(pady=5, fill=X)
    employees_by_station[station_name] = tree

def update_employee_tables():
    for tree in employees_by_station.values():
        tree.delete(*tree.get_children())
    for emp in employees_data:
        station = emp["station"]
        if station not in employees_by_station:
            create_employee_table_for_station(station)
        location = emp.get("location", "")
        employees_by_station[station].insert("", END, values=(
            emp["name"], emp["surname"], emp["role"], location
        ))

def add_employee():
    global editing_employee_index
    name = entry_employee_name.get().strip()
    surname = entry_employee_surname.get().strip()
    role = entry_employee_role.get().strip()
    station = entry_station_name.get().strip()
    lat = entry_employee_lat.get().strip()
    lon = entry_employee_lon.get().strip()

    if name and surname and role and station:
        location = f"{lat},{lon}" if lat and lon else ""
        employees_data.append({
            "name": name,
            "surname": surname,
            "role": role,
            "station": station,
            "location": location
        })
        for entry in [entry_employee_name, entry_employee_surname, entry_employee_role,
                      entry_station_name, entry_employee_lat, entry_employee_lon]:
            entry.delete(0, END)
        editing_employee_index = None
        update_employee_tables()
        label_employees_info.config(text="✅ Dodano pracownika")
    else:
        label_employees_info.config(text="❗ Uzupełnij wszystkie pola")

def load_selected_employee():
    global editing_employee_index
    for station, tree in employees_by_station.items():
        selected = tree.selection()
        if selected:
            index = tree.index(selected[0])
            emp = [e for e in employees_data if e["station"] == station][index]
            entry_employee_name.delete(0, END)
            entry_employee_name.insert(0, emp["name"])
            entry_employee_surname.delete(0, END)
            entry_employee_surname.insert(0, emp["surname"])
            entry_employee_role.delete(0, END)
            entry_employee_role.insert(0, emp["role"])
            entry_station_name.delete(0, END)
            entry_station_name.insert(0, emp["station"])
            if "location" in emp and "," in emp["location"]:
                lat, lon = emp["location"].split(",")
                entry_employee_lat.delete(0, END)
                entry_employee_lat.insert(0, lat)
                entry_employee_lon.delete(0, END)
                entry_employee_lon.insert(0, lon)
            else:
                entry_employee_lat.delete(0, END)
                entry_employee_lon.delete(0, END)
            editing_employee_index = employees_data.index(emp)
            label_employees_info.config(text="✏️ Edytuj dane i kliknij ZAPISZ")
            break

def edit_selected_employee():
    global editing_employee_index
    if editing_employee_index is None:
        label_employees_info.config(text="❗ Wybierz pracownika do edycji")
        return
    name = entry_employee_name.get().strip()
    surname = entry_employee_surname.get().strip()
    role = entry_employee_role.get().strip()
    station = entry_station_name.get().strip()
    lat = entry_employee_lat.get().strip()
    lon = entry_employee_lon.get().strip()

    if name and surname and role and station:
        location = f"{lat},{lon}" if lat and lon else ""
        emp = employees_data[editing_employee_index]
        emp.update({
            "name": name,
            "surname": surname,
            "role": role,
            "station": station,
            "location": location
        })
        update_employee_tables()
        editing_employee_index = None
        label_employees_info.config(text="✅ Zapisano zmiany")
    else:
        label_employees_info.config(text="❗ Uzupełnij wszystkie pola")

def delete_selected_employee():
    global editing_employee_index
    for station, tree in employees_by_station.items():
        selected = tree.selection()
        if selected:
            index = tree.index(selected[0])
            emp = [e for e in employees_data if e["station"] == station][index]
            employees_data.remove(emp)
            update_employee_tables()
            editing_employee_index = None
            label_employees_info.config(text="🗑️ Usunięto pracownika")
            break

# ------------------ KLIENCI ------------------

def create_customer_table_for_station(station_name):
    label = Label(frame_customers_right, text=f"📍 Klienci stacji: {station_name}", font=("Arial", 12, "bold"))
    label.pack(pady=(10, 0))
    tree = ttk.Treeview(frame_customers_right, columns=("Imię", "Nazwisko", "Email", "Telefon"), show='headings')
    for col in ("Imię", "Nazwisko", "Email", "Telefon"):
        tree.heading(col, text=col)
        tree.column(col, width=130)
    tree.pack(pady=5, fill=X)
    customers_by_station[station_name] = tree

def update_customer_tables():
    for tree in customers_by_station.values():
        tree.delete(*tree.get_children())
    for customer in customers_data:
        station = customer["station"]
        if station not in customers_by_station:
            create_customer_table_for_station(station)
        customers_by_station[station].insert("", END, values=(
            customer["name"], customer["surname"], customer["email"], customer["phone"]
        ))

def update_all_customers_table():
    tree_all_customers.delete(*tree_all_customers.get_children())
    for cust in customers_data:
        location = cust.get("location", "")
        tree_all_customers.insert("", END, values=(
            cust["name"], cust["surname"], cust["email"],
            cust["phone"], cust["station"], location
        ))

def add_customer():
    global editing_customer_index
    name = entry_customer_name.get().strip()
    surname = entry_customer_surname.get().strip()
    email = entry_customer_email.get().strip()
    phone = entry_customer_phone.get().strip()
    station = entry_customer_station.get().strip()
    lat = entry_customer_lat.get().strip()
    lon = entry_customer_lon.get().strip()

    if name and surname and email and phone and station:
        location = f"{lat},{lon}" if lat and lon else ""
        customers_data.append({
            "name": name,
            "surname": surname,
            "email": email,
            "phone": phone,
            "station": station,
            "location": location
        })
        update_customer_tables()
        update_all_customers_table()
        for entry in [entry_customer_name, entry_customer_surname, entry_customer_email,
                      entry_customer_phone, entry_customer_station, entry_customer_lat, entry_customer_lon]:
            entry.delete(0, END)
        editing_customer_index = None
        label_customers_info.config(text=f"✅ Dodano klienta do stacji: {station}")
    else:
        label_customers_info.config(text="❗ Uzupełnij wszystkie pola")

def load_customer_from_table():
    global editing_customer_index
    selected = tree_all_customers.selection()
    if not selected:
        return
    index = tree_all_customers.index(selected[0])
    customer = customers_data[index]

    entry_customer_name.delete(0, END)
    entry_customer_name.insert(0, customer["name"])
    entry_customer_surname.delete(0, END)
    entry_customer_surname.insert(0, customer["surname"])
    entry_customer_email.delete(0, END)
    entry_customer_email.insert(0, customer["email"])
    entry_customer_phone.delete(0, END)
    entry_customer_phone.insert(0, customer["phone"])
    entry_customer_station.delete(0, END)
    entry_customer_station.insert(0, customer["station"])

    if "location" in customer and "," in customer["location"]:
        lat, lon = customer["location"].split(",")
        entry_customer_lat.delete(0, END)
        entry_customer_lat.insert(0, lat)
        entry_customer_lon.delete(0, END)
        entry_customer_lon.insert(0, lon)
    else:
        entry_customer_lat.delete(0, END)
        entry_customer_lon.delete(0, END)

    editing_customer_index = index
    label_customers_info.config(text="✏️ Edytuj dane i kliknij ZAPISZ")

def edit_selected_customer():
    global editing_customer_index
    if editing_customer_index is None:
        label_customers_info.config(text="❗ Wybierz klienta do edycji")
        return

    name = entry_customer_name.get().strip()
    surname = entry_customer_surname.get().strip()
    email = entry_customer_email.get().strip()
    phone = entry_customer_phone.get().strip()
    station = entry_customer_station.get().strip()
    lat = entry_customer_lat.get().strip()
    lon = entry_customer_lon.get().strip()

    if name and surname and email and phone and station:
        location = f"{lat},{lon}" if lat and lon else ""
        customer = customers_data[editing_customer_index]
        customer.update({
            "name": name,
            "surname": surname,
            "email": email,
            "phone": phone,
            "station": station,
            "location": location
        })
        update_customer_tables()
        update_all_customers_table()
        editing_customer_index = None
        label_customers_info.config(text="✅ Zapisano zmiany")
    else:
        label_customers_info.config(text="❗ Uzupełnij wszystkie pola")

def delete_selected_customer():
    global editing_customer_index
    for station, tree in customers_by_station.items():
        selected = tree.selection()
        if selected:
            index = tree.index(selected[0])
            customer = [c for c in customers_data if c["station"] == station][index]
            customers_data.remove(customer)
            update_customer_tables()
            update_all_customers_table()
            editing_customer_index = None
            label_customers_info.config(text="🗑️ Usunięto klienta")
            break

# ------------------ GUI ------------------

# (GUI kod poniżej dodałbyś zgodnie z tym co już masz — jeśli chcesz, mogę też dodać cały kod interfejsu)

