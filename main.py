from tkinter import *
from tkinter import ttk
import tkintermapview

from utils import get_city_coordinates

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

# ----------------- STACJE ------------------

from utils import get_fuel_stations_near_city


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


def rename_selected_station():
    index = listbox_stations.curselection()
    if not index:
        return
    index = index[0]
    station = stations_tab_data[index]

    def apply_new_name():
        new_name = entry_new_name.get().strip()
        if new_name:
            station["name"] = new_name
            listbox_stations.delete(index)
            listbox_stations.insert(index, f"{station['name']} – {station['lat']:.5f}, {station['lon']:.5f}")
            stations_tab_markers[index].set_text(new_name)
            rename_window.destroy()

    rename_window = Toplevel()
    rename_window.title("Zmień nazwę stacji")
    Label(rename_window, text="Nowa nazwa stacji:").pack(pady=5)
    entry_new_name = Entry(rename_window, width=40)
    entry_new_name.pack(pady=5)
    entry_new_name.insert(0, station["name"])
    Button(rename_window, text="Zapisz", command=apply_new_name).pack(pady=10)


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


def delete_selected_station():
    try:
        index = listbox_stations.curselection()[0]
        stations_tab_data.pop(index)
        marker = stations_tab_markers.pop(index)
        marker.delete()
        listbox_stations.delete(index)
    except IndexError:
        pass


# ----------------- PRACOWNICY ------------------

def create_employee_table_for_station(station_name):
    label = Label(frame_employees_right, text=f"📍 Pracownicy stacji: {station_name}", font=("Arial", 12, "bold"))
    label.pack(pady=(10, 0))
    tree = ttk.Treeview(frame_employees_right, columns=("Imię", "Nazwisko", "Stanowisko", "Lokalizacja"),
                        show='headings')
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


# ----------------- KLIENCI ------------------

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
        editing_customer_index = None
        label_customers_info.config(text="✅ Zapisano zmiany")
    else:
        label_customers_info.config(text="❗ Uzupełnij wszystkie pola")


def create_customer_table_for_station(station_name):
    label = Label(frame_customers_right, text=f"📍 Klienci stacji: {station_name}", font=("Arial", 12, "bold"))
    label.pack(pady=(10, 0))
    tree = ttk.Treeview(frame_customers_right, columns=("Imię", "Nazwisko", "Email", "Telefon"), show='headings')
    for col in ("Imię", "Nazwisko", "Email", "Telefon"):
        tree.heading(col, text=col)
        tree.column(col, width=130)
    tree.pack(pady=5, fill=X)
    customers_by_station[station_name] = tree


def delete_selected_customer():
    global editing_customer_index
    for station, tree in customers_by_station.items():
        selected = tree.selection()
        if selected:
            index = tree.index(selected[0])
            customer = [c for c in customers_data if c["station"] == station][index]
            customers_data.remove(customer)
            update_customer_tables()
            editing_customer_index = None
            label_customers_info.config(text="🗑️ Usunięto klienta")
            break


# -------------------------- GUI --------------------------

root = Tk()
root.title("Zarządzanie siecią stacji paliw")
root.geometry("1200x750")
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

# --- Mapa ---
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
Button(frame_left, text="➡️ Przenieś zaznaczoną stację do zakładki: STACJE", command=move_selected_station_to_tab).pack(
    pady=2, fill=X)
Button(frame_left, text="➡️ Przejdź do zakładki: PRACOWNICY", command=lambda: notebook.select(frame_employees)).pack(
    pady=2, fill=X)
Button(frame_left, text="➡️ Przejdź do zakładki: KLIENCI", command=lambda: notebook.select(frame_customers)).pack(
    pady=2, fill=X)

label_info = Label(frame_left, text="", fg="blue")
label_info.pack(pady=5)
listbox = Listbox(frame_left, width=50)
listbox.pack(pady=10, fill=BOTH, expand=True)
listbox.bind("<<ListboxSelect>>", on_listbox_click)

map_widget_mapa = tkintermapview.TkinterMapView(frame_right, width=800, height=450)
map_widget_mapa.pack(fill=BOTH, expand=True)
map_widget_mapa.set_position(52.0, 19.0)
map_widget_mapa.set_zoom(6)

# --- Stacje ---
frame_stations = Frame(notebook)
notebook.add(frame_stations, text="Stacje")
frame_stations_left = Frame(frame_stations)
frame_stations_left.pack(side=LEFT, fill=Y, padx=10, pady=10)
frame_stations_right = Frame(frame_stations)
frame_stations_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

listbox_stations = Listbox(frame_stations_left, width=45, height=25)
listbox_stations.pack(pady=10, fill=Y)
Button(frame_stations_left, text="🗑️ Usuń zaznaczoną stację", command=delete_selected_station).pack(pady=2, fill=X)
Button(frame_stations_left, text="✏️ Zmień nazwę stacji", command=rename_selected_station).pack(pady=2, fill=X)

map_widget_stations = tkintermapview.TkinterMapView(frame_stations_right, width=800, height=450)
map_widget_stations.pack(fill=BOTH, expand=True)
map_widget_stations.set_position(52.0, 19.0)
map_widget_stations.set_zoom(6)

# --- Pracownicy ---
frame_employees = Frame(notebook)
notebook.add(frame_employees, text="Pracownicy")
frame_employees_left = Frame(frame_employees)
frame_employees_left.pack(side=LEFT, fill=Y, padx=10, pady=10)
canvas_employees = Canvas(frame_employees)
scrollbar_employees = Scrollbar(frame_employees, orient=VERTICAL, command=canvas_employees.yview)
scrollable_frame_employees = Frame(canvas_employees)
scrollable_frame_employees.bind(
    "<Configure>",
    lambda e: canvas_employees.configure(scrollregion=canvas_employees.bbox("all"))
)
canvas_employees.create_window((0, 0), window=scrollable_frame_employees, anchor="nw")
canvas_employees.configure(yscrollcommand=scrollbar_employees.set)
canvas_employees.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)
scrollbar_employees.pack(side=RIGHT, fill=Y)
frame_employees_right = scrollable_frame_employees

Label(frame_employees_left, text="Imię:").pack()
entry_employee_name = Entry(frame_employees_left, width=30)
entry_employee_name.pack()
Label(frame_employees_left, text="Nazwisko:").pack()
entry_employee_surname = Entry(frame_employees_left, width=30)
entry_employee_surname.pack()
Label(frame_employees_left, text="Stanowisko:").pack()
entry_employee_role = Entry(frame_employees_left, width=30)
entry_employee_role.pack()
Label(frame_employees_left, text="Stacja:").pack()
entry_station_name = Entry(frame_employees_left, width=30)
entry_station_name.pack()

Label(frame_employees_left, text="Szerokość (lat):").pack()
entry_employee_lat = Entry(frame_employees_left, width=30)
entry_employee_lat.pack(pady=2)
Label(frame_employees_left, text="Długość (lon):").pack()
entry_employee_lon = Entry(frame_employees_left, width=30)
entry_employee_lon.pack(pady=2)

Button(frame_employees_left, text="Dodaj pracownika", command=add_employee).pack(pady=5)
Button(frame_employees_left, text="✏️ Wczytaj do edycji", command=load_selected_employee).pack(pady=2)
Button(frame_employees_left, text="💾 Zapisz zmiany", command=edit_selected_employee).pack(pady=2)
Button(frame_employees_left, text="🗑️ Usuń zaznaczonego", command=delete_selected_employee).pack(pady=2)

label_employees_info = Label(frame_employees_left, text="Brak akcji", fg="blue")
label_employees_info.pack(pady=5)

tree_all_employees = ttk.Treeview(
    frame_employees_right,
    columns=("Imię", "Nazwisko", "Stanowisko", "Stacja", "Lokalizacja"),
    show='headings'
)
for col in ("Imię", "Nazwisko", "Stanowisko", "Stacja", "Lokalizacja"):
    tree_all_employees.heading(col, text=col)
    tree_all_employees.column(col, width=130)
tree_all_employees.pack(fill=BOTH, expand=True)

# --- Klienci ---
frame_customers = Frame(notebook)
notebook.add(frame_customers, text="Klienci")
frame_customers_left = Frame(frame_customers)
frame_customers_left.pack(side=LEFT, fill=Y, padx=10, pady=10)
canvas_customers = Canvas(frame_customers)
scrollbar_customers = Scrollbar(frame_customers, orient=VERTICAL, command=canvas_customers.yview)
scrollable_frame_customers = Frame(canvas_customers)
scrollable_frame_customers.bind(
    "<Configure>",
    lambda e: canvas_customers.configure(scrollregion=canvas_customers.bbox("all"))
)
canvas_customers.create_window((0, 0), window=scrollable_frame_customers, anchor="nw")
canvas_customers.configure(yscrollcommand=scrollbar_customers.set)
canvas_customers.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)
scrollbar_customers.pack(side=RIGHT, fill=Y)
frame_customers_right = scrollable_frame_customers
tree_all_customers = ttk.Treeview(
    frame_customers_right,
    columns=("Imię", "Nazwisko", "Email", "Telefon", "Stacja", "Lokalizacja"),
    show='headings'
)

for col in ("Imię", "Nazwisko", "Email", "Telefon", "Stacja", "Lokalizacja"):
    tree_all_customers.heading(col, text=col)
    tree_all_customers.column(col, width=120)
tree_all_customers.pack(fill=BOTH, expand=True, pady=10)
Label(frame_customers_left, text="Imię: ").pack()
entry_customer_name = Entry(frame_customers_left, width=30)
entry_customer_name.pack(pady=2)
Label(frame_customers_left, text="Nazwisko: ").pack()
entry_customer_surname = Entry(frame_customers_left, width=30)
entry_customer_surname.pack(pady=2)
Label(frame_customers_left, text="Email: ").pack()
entry_customer_email = Entry(frame_customers_left, width=30)
entry_customer_email.pack(pady=2)
Label(frame_customers_left, text="Telefon: ").pack()
entry_customer_phone = Entry(frame_customers_left, width=30)
entry_customer_phone.pack(pady=2)
Label(frame_customers_left, text="Stacja: ").pack()
entry_customer_station = Entry(frame_customers_left, width=30)
entry_customer_station.pack(pady=2)
Label(frame_customers_left, text="Szerokość (lat): ").pack()
entry_customer_lat = Entry(frame_customers_left, width=30)
entry_customer_lat.pack(pady=2)
Label(frame_customers_left, text="Długość (lon): ").pack()
entry_customer_lon = Entry(frame_customers_left, width=30)
entry_customer_lon.pack(pady=2)

Button(frame_customers_left, text="Dodaj klienta", command=add_customer).pack(pady=5)
Button(frame_customers_left, text="✏️ Wczytaj do edycji", command=load_customer_from_table).pack(pady=2)

Button(frame_customers_left, text="💾 Zapisz zmiany", command=edit_selected_customer).pack(pady=2)
Button(frame_customers_left, text="🗑️ Usuń zaznaczonego", command=delete_selected_customer).pack(pady=2)

label_customers_info = Label(frame_customers_left, text="Brak akcji", fg="blue")
label_customers_info.pack(pady=5)

# --- Mapa Pracownicy ---
frame_map_employees = Frame(notebook)
notebook.add(frame_map_employees, text="Mapa Pracownicy")

btn_refresh_employees_map = Button(frame_map_employees, text="🔄 Odśwież dane na mapie",
                                   command=lambda: show_employees_on_map())
btn_refresh_employees_map.pack(side=TOP, fill=X, pady=(10, 5))

map_widget_employees = tkintermapview.TkinterMapView(frame_map_employees, width=1150, height=700)
map_widget_employees.pack(fill=BOTH, expand=True)
map_widget_employees.set_position(52.0, 19.0)
map_widget_employees.set_zoom(6)


def show_employees_on_map():
    map_widget_employees.delete_all_marker()
    for emp in employees_data:
        loc = emp.get("location", "")
        if loc:
            try:
                lat, lon = map(float, loc.split(","))
                map_widget_employees.set_marker(lat, lon, text=f"👷 {emp['name']} {emp['surname']} ({emp['role']})")
                continue
            except Exception as e:
                print(f"Błąd lokalizacji pracownika: {e}")

        station = next((s for s in station_data if s["name"] == emp.get("station", "")), None)
        if station:
            try:
                map_widget_employees.set_marker(station["lat"], station["lon"],
                                                text=f"👷 {emp['name']} {emp['surname']} ({emp['role']})")
            except Exception as e:
                print(f"Błąd lokalizacji pracownika przez stację: {e}")


# --- Mapa Klienci ---
frame_map_customers = Frame(notebook)
notebook.add(frame_map_customers, text="Mapa Klienci")

btn_refresh_customers_map = Button(frame_map_customers, text="🔄 Odśwież dane na mapie",
                                   command=lambda: show_customers_on_map())
btn_refresh_customers_map.pack(side=TOP, fill=X, pady=(10, 5))

map_widget_customers = tkintermapview.TkinterMapView(frame_map_customers, width=1150, height=700)
map_widget_customers.pack(fill=BOTH, expand=True)
map_widget_customers.set_position(52.0, 19.0)
map_widget_customers.set_zoom(6)


def show_customers_on_map():
    map_widget_customers.delete_all_marker()
    for cust in customers_data:
        loc = cust.get("location", "")
        if loc:
            try:
                lat, lon = map(float, loc.split(","))
                map_widget_customers.set_marker(lat, lon, text=f"🧑‍💼 {cust['name']} {cust['surname']}")
                continue
            except Exception as e:
                print(f"Błąd lokalizacji klienta: {e}")

        station = next((s for s in station_data if s["name"] == cust.get("station", "")), None)
        if station:
            try:
                map_widget_customers.set_marker(station["lat"], station["lon"],
                                                text=f"🧑‍💼 {cust['name']} {cust['surname']}")
            except Exception as e:
                print(f"Błąd lokalizacji klienta przez stację: {e}")


root.mainloop()
