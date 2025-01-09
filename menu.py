import tkinter as tk
from tkinter import PhotoImage
from consumo import ConsumoVIew
from actualiza_mes import ActualizaMesView 
def abrir_personal():
    # Crear una nueva ventana para ConsumoVIew
    consumo_window = tk.Toplevel()  # Crear una ventana secundaria
    ConsumoVIew(consumo_window)     # Pasar la ventana como argumento a la clase

def abrir_mensual():
    Actualiza_Mes = tk.Toplevel()
    ActualizaMesView(Actualiza_Mes)
# Crear la ventana principal
root = tk.Tk()
root.title("Actualiza personal S48")
root.geometry("300x200")  # Tamaño de la ventana (ancho x alto)
root.iconbitmap("Logo-Grupo-Andes-Farms-50-Años.ico")
root.iconphoto(True, PhotoImage(file="Logo.png"))
# Etiqueta descriptiva
label = tk.Label(root, text="Seleccione una opción:", font=("Arial", 14))
label.pack(pady=20)  # Espaciado vertical

# Botón para "Personal"
btn_personal = tk.Button(root, text="Personal", font=("Arial", 12), width=15, command=abrir_personal)
btn_personal.pack(pady=10)

# Botón para "Mensual"
btn_mensual = tk.Button(root, text="Mensual", font=("Arial", 12), width=15, command=abrir_mensual)
btn_mensual.pack(pady=10)

# Ejecutar la aplicación
root.mainloop()