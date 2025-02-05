import tkinter as tk
from tkinter import ttk, messagebox
from conn import conecta_db 
import datetime
import requests
from decimal import Decimal

# Configurar la conexión a la base de datos
# Asegúrate de modificar los valores de conexión a tu base de datos
class ConsumoVIew:
    def __init__(self, root):
        self.root = root
        self.root.title("Actualiza Persona Indivual")
        self.root.iconbitmap("Logo-Grupo-Andes-Farms-50-Años.ico")
        
        # Variables y configuraciones iniciales
        self.arreglos_empleados = []
        self.hoy = datetime.datetime.now()
        self.link = "https://www.sinergylowellsprd.net:444/api/D_Employees_Fechas/Retrieve/7GkX7CIoEhMXw49Gx0Oh8ZDantU3Bcx7sbLR8ZAcWOPQetnLn2JonEtuVEAWQYWk44PqloJ7Z4GGQTPOu8ti57MXNy1RzjdncpSH/A"

        self.setup_ui()

    def setup_ui(self):
        # Etiqueta y campo de entrada para la cédula
        cedula_label = tk.Label(self.root, text="Ingrese la cédula:")
        cedula_label.pack(padx=10, pady=5)

        self.cedula_entry = tk.Entry(self.root)
        self.cedula_entry.pack(padx=10, pady=5)

        # Botones
        consultar_button = tk.Button(self.root, text="Consultar", command=self.obtener_datos)
        consultar_button.pack(pady=20)

        actualizar_boton = tk.Button(self.root, text="Actualizar Datos", command=self.actualiza_datos)
        actualizar_boton.pack(pady=20)

        # Grillas para mostrar los datos
        db_label = tk.Label(self.root, text="Datos de S48:")
        db_label.pack(padx=10, pady=5)

        self.tree_db = ttk.Treeview(self.root, columns=("PNOMBRE", "PAPELLIDO", "nomposicion", "NOMCARGEMPL", "CCOSTO3"), show="headings")
        self.tree_db.heading("PNOMBRE", text="PNOMBRE")
        self.tree_db.heading("PAPELLIDO", text="PAPELLIDO")
        self.tree_db.heading("nomposicion", text="Posición")
        self.tree_db.heading("NOMCARGEMPL", text="Cargo")
        self.tree_db.heading("CCOSTO3", text="Costo 3")
        self.tree_db.pack(padx=10, pady=10)

        api_label = tk.Label(self.root, text="Datos de Sinergy:")
        api_label.pack(padx=10, pady=5)

        self.tree_api = ttk.Treeview(self.root, columns=("Nombre", "Apellido", "Labor", "Cargo", "Centro3"), show="headings")
        self.tree_api.heading("Nombre", text="Nombre")
        self.tree_api.heading("Apellido", text="Apellido")
        self.tree_api.heading("Labor", text="Labor")
        self.tree_api.heading("Cargo", text="Cargo")
        self.tree_api.heading("Centro3", text="Centro 3")
        self.tree_api.pack(padx=10, pady=10)
    
    
    def obtener_datos(self):
        
        cedula = self.cedula_entry.get()
        conn = conecta_db()
        cursor = conn.cursor()
        if not cedula.isdigit():
            messagebox.showerror("Error", "Por favor ingrese una cédula válida.")
            return
        
        cedula = int(cedula)
        try:
            # Limpiar las grillas antes de insertar datos
            for row in self.tree_db.get_children():
                self.tree_db.delete(row)
            for row in self.tree_api.get_children():
                self.tree_api.delete(row)
            
            # Consultar la base de datos
            cursor.execute("SELECT PNOMBRE, PAPELLIDO, nomposicion, NOMCARGEMPL, CCOSTO3, fingreso FROM PERSONAL_SINERGY WHERE id = (%s)", (cedula,))
            resultado = cursor.fetchall()
            
            if not resultado:
                messagebox.showerror("Error", "No se encontró un empleado con esa cédula.")
                return
            
            # Mostrar datos en la primera grilla
            for x in resultado:
                self.tree_db.insert("", "end", values=(x['PNOMBRE'], x['PAPELLIDO'], x['nomposicion'], x['NOMCARGEMPL'], x['CCOSTO3'], x['fingreso']))
            
            # Procesar datos para la API
            fingreso = str(resultado[0]['fingreso'])
            fechaTratada = fingreso.replace("-", "/")
            linkFinal = self.link + '/' + str(cedula) + '/T/' + fechaTratada + '/' + fechaTratada
            
            # Consultar la API
            data = requests.get(linkFinal)
            if data.status_code == 200:
                empleados = data.json()
                
                # Mostrar resultados de la API en la segunda grilla
                for empleado in empleados:
                    self.tree_api.insert("", "end", values=(empleado['empleado_Pnombre'],empleado['empleado_Papellido'],empleado['horganizacional_Nom_Posicion'],empleado['horganizacional_Nom_Cargo'],empleado['empleado_Cen3']))
                    self.arreglos_empleados.append(empleado['empleado_Sucursal'])
                    self.arreglos_empleados.append(empleado['tipo_Empleado_Tipo'])
                    self.arreglos_empleados.append(empleado['empleado_Posicion'])
                    self.arreglos_empleados.append(empleado['horganizacional_Cargo'])
                    self.arreglos_empleados.append(empleado['horganizacional_Nom_Cargo'])
                    self.arreglos_empleados.append(empleado['empleado_Empleado'])
                    self.arreglos_empleados.append(empleado['horganizacional_Nom_Unidad'])
                    self.arreglos_empleados.append(empleado['horganizacional_Nom_Posicion'])
                    self.arreglos_empleados.append(empleado['empleado_Cen3'])
                    self.arreglos_empleados.append(empleado['centro_Costo3_Desc_Cen3'])
                    self.arreglos_empleados.append(empleado['tipo_Empleado_Desc_Tipo_Emp'])
                    self.arreglos_empleados.append(empleado['sucursal_Desc_Sucursal'])
                    self.arreglos_empleados.append(empleado['horganizacional_Nom_Emp'])

                messagebox.showinfo("Éxito", "Datos obtenidos correctamente.")
            else:
                messagebox.showerror("Error", f"Error en la solicitud: {data.status_code}")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
        return self.arreglos_empleados
    def actualiza_datos(self):
        try:
            conn = conecta_db()
            cursor = conn.cursor()
            #captura nuevamente la cedula para usarla de condicionals
            cedula = self.cedula_entry.get()
            cedula = str(cedula)
            #manda el update a sql local
            cursor.execute("exec [SP_ACTUALIZA_EMPLEADO] %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s",(str(self.arreglos_empleados[0]),str(self.arreglos_empleados[1]),str(self.arreglos_empleados[2]),str(self.arreglos_empleados[3]),str(self.arreglos_empleados[4]),cedula,str(self.arreglos_empleados[6]),str(self.arreglos_empleados[7]),str(self.arreglos_empleados[8]),str(self.arreglos_empleados[9]),str(self.arreglos_empleados[10]),str(self.arreglos_empleados[11]),str(self.arreglos_empleados[12])))
            #cursor.execute("update PERSONAL_SINERGY set CCOSTO3 = (%s),nomposicion = (%s),NOMCARGEMPL= (%s)  where id = (%s)",(str(self.arreglos_empleados[4]),str(self.arreglos_empleados[2]),str(self.arreglos_empleados[3]),cedula))
            # Confirma los cambios 
            cursor.connection.commit()
            #enviar a s48
            cedula = int(cedula)
            url_s48 = "https://cloud.s48.co:6060/sinergy/empleados"
            
            #captura los datos en 
            cursor.execute("exec SP_LLAMA_INFO %s", (cedula))
            resultadoSP = cursor.fetchall()
            #captura arreglo en limpio para no traer datos con formato
            datos_limpios = []
            #ciclo para limpiar los datos del retorno
            for fila in resultadoSP:
                fila_limpia = {
                    k: int(v) if k == 'cedula' else 
                    str(v) if isinstance(v, (Decimal, datetime.date)) else v
                    for k, v in fila.items()
            }
            datos_limpios.append(fila_limpia)
            cedula = str(cedula)
            response = requests.post(url=url_s48,json=datos_limpios)
            if response.status_code == 200:
                valida = "Enviado correctamente " + cedula
            else:
                valida = "Enviado con errores"  + cedula
            f = open('e:/log_prueba.txt','a+')
            f.write('--------------------------ejecucion' + str(valida) + ' ' +str(self.hoy) + '------------------------------------------ \n')
            f.write(str(datos_limpios)+ '\n')
            f.write('--------------------------ejecucion' + str(self.hoy) + '------------------------------------------ \n')
            f.close()
            
            conn.close()
                # Muestra un mensaje de éxito
            messagebox.showinfo("Éxito", "Datos actualizados correctamente.")
        except Exception as e:
            messagebox.showinfo("Falla", "Error: " + str(e))
            f = open('e:/log_prueba.txt','a+')
            f.write('--------------------------ejecucion fallida' + str(self.hoy) + '------------------------------------------ \n')
            f.write(str(e)+ '\n')
            f.write('--------------------------ejecucion' + str(self.hoy) + '------------------------------------------ \n')
            f.close()
    