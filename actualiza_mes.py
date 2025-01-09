import tkinter as tk
from tkinter import ttk,messagebox
import datetime
from datetime import datetime as dt
import calendar
import locale
import requests
import json
from conn import conecta_db 
from decimal import Decimal

class ActualizaMesView():
    def __init__(self,root):
        self.root = root
        self.root.title("Actualiza Mes")
        self.root.iconbitmap("Logo-Grupo-Andes-Farms-50-Años.ico")
        self.meses_texto = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.link = "https://www.sinergylowellsprd.net:444/api/D_Employees_Fechas/Retrieve/7GkX7CIoEhMXw49Gx0Oh8ZDantU3Bcx7sbLR8ZAcWOPQetnLn2JonEtuVEAWQYWk44PqloJ7Z4GGQTPOu8ti57MXNy1RzjdncpSH/A/T/T"
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        self.hoy = datetime.datetime.now()
        
        self.setup_ui()
        
        
    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20)
        self.root.after(0,self.trae_fechas)

        # Combobox para el año
        ttk.Label(frame, text="Año:").grid(row=0, column=0, padx=5)
        self.combobox_anio = ttk.Combobox(frame, width=10)
        self.combobox_anio.grid(row=0, column=1, padx=5)

        # Botón "Actualizar"
        self.boton_actualizar = ttk.Button(frame, text="Actualizar", command=self.actualizar)
        self.boton_actualizar.grid(row=0, column=2, padx=5)

        # Combobox para el mes
        ttk.Label(frame, text="Mes:").grid(row=0, column=3, padx=5)
        self.combobox_mes = ttk.Combobox(frame, width=10)
        self.combobox_mes.grid(row=0, column=4, padx=5)

        # Llamar a la función actualiza_mes cada vez que se cambie el año
        self.combobox_anio.bind("<<ComboboxSelected>>", self.meses_segun_anio)
        
    def actualizar(self):
        conn = conecta_db()
        cursor = conn.cursor()
        anioElegido = self.combobox_anio.get()
        mesElegido = self.combobox_mes.get()
        #TODO 
        #1. armar la api con el mes elegido, desde el día 1 hasta la fecha final *
        mesNumero = dt.strptime(mesElegido, "%B").month #pone el mes numerico
        _, ultimoDia = calendar.monthrange(int(anioElegido),int(mesNumero))#numero del dia final mes
        linkFinal = self.link + '/' +  str(anioElegido) + '/' + str(mesNumero) + '/' + '1' + '/' + str(anioElegido) + '/' + str(mesNumero) + '/' + str(ultimoDia)
        #2. consume api *
        data = requests.get(linkFinal)
        arregloEmpleados = []
        if data.status_code == 200:
            empleados = data.json()
            
            for empleado in empleados:
                
                try:
                    #captura datos de la api
                    sucursal = empleado['empleado_Sucursal']
                    tipoEmpleado = empleado['tipo_Empleado_Tipo']
                    posicion = empleado['empleado_Posicion']
                    cargo = empleado['horganizacional_Cargo']
                    CargoEmple = empleado['horganizacional_Nom_Cargo']
                    cedula = empleado['empleado_Empleado']
                    unidad =  empleado['horganizacional_Nom_Unidad']
                    nombrePosicion = empleado['horganizacional_Nom_Posicion']
                    cen3 = empleado['empleado_Cen3']
                    descCen3 = empleado['centro_Costo3_Desc_Cen3']
                    descTipoEmpl = empleado['tipo_Empleado_Desc_Tipo_Emp']
                    departamento = empleado['sucursal_Desc_Sucursal']
                    nombreEmpresa = empleado['horganizacional_Nom_Emp']
                    #captura empleados y los envia al array
                    arregloEmpleados.append(cedula)
                    #envia datos a bd
                    cursor.execute("exec [SP_ACTUALIZA_EMPLEADO] %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s",(str(sucursal),str(tipoEmpleado),posicion,cargo,CargoEmple,cedula,unidad,nombrePosicion,cen3,descCen3,descTipoEmpl,departamento,nombreEmpresa))
                    #valida
                    cursor.connection.commit()
                    #messagebox.showinfo('Actualizado','Emplado: ' + cedula)
                except NameError as e:
                    messagebox.showinfo("Error:" + e)
        try:
            datos = []
            #4. al actualizar enviara todos los empleados del mes
            for cedula in arregloEmpleados:
                #crea el json para cargar a la apis  
                cursor.execute("exec SP_LLAMA_INFO %s", (cedula))  
                resultado = cursor.fetchall()
                
                for fila in resultado:
                    fila_limpia = { 
                        k: int(v) if k == 'cedula' else 
                        str(v) if isinstance(v, (Decimal, datetime.date)) else v
                        for k, v in fila.items()
                        
                    }
                    datos.append(fila_limpia)
            
            #convierte datos
            datos = json.dumps(datos, ensure_ascii=False, indent=4)
            #url s48
            url_s48 = "https://cloud.s48.co:6060/sinergy/empleados"
            #envia data
            response = requests.post(url=url_s48,json=datos)
            #validacion de ejecución
            if response.status_code == 200:
                valida = "ejecutado correctamente"
            else:
                valida = "fallas en los registros"
            f = open('e:/log_prueba.txt','a+')
            f.write('--------------------------ejecucion mensual' + str(valida) + ' ' +str(self.hoy) + '------------------------------------------ \n')
            f.write(datos)
            f.write('--------------------------ejecucion mensual' + str(self.hoy) + '------------------------------------------ \n')
            f.close()
            #mensaje informativo
            messagebox.showinfo("Éxito", "Datos actualizados correctamente.")
            conn.close()
        except Exception as e:
            messagebox.showinfo("Falla", "Error: " + e)
            f = open('e:/log_prueba.txt','a+')
            f.write('--------------------------ejecucion mensual fallida ' +str(self.hoy)  + '------------------------------------------ \n')
            f.write('falla ' + e)
            f.write('--------------------------ejecucion mensual fallida' + str(self.hoy) + '------------------------------------------ \n')
            f.close()
            

    #trae las fechas del minimo al maximo a las bases de datos
    def trae_fechas(self):
        
        conn = conecta_db()
        cursor = conn.cursor()
        cursor.execute("SELECT *from VIEW_MAX_MIN_DATES")
        resultado = cursor.fetchall()
        fecha_min = resultado[0]['fecha_min']
        fecha_max = resultado[0]['fecha_max']
        rangos = list(range(fecha_min,fecha_max + 1))
        self.combobox_anio['values'] = rangos
        self.combobox_anio.set(fecha_min)
        
        conn.close()
    #segun el anio elegido coloca los meses
    def meses_segun_anio(self,event):
        anio = self.combobox_anio.get()
        anio = int(anio)
        anio_actual = datetime.datetime.now().year
        hoy = datetime.datetime.today()
        if anio == anio_actual:
            meses = self.meses_texto[:hoy.month]
        else:
            meses = self.meses_texto
        
            
        self.combobox_mes['values'] = meses
        self.combobox_mes.set(meses[0])
        