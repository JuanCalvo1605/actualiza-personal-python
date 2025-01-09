import pymssql

def conecta_db():
    try:
        conn = pymssql.connect(
            server = '10.238.1.19',
            user= 'consulta',
            password= 'Consulta_2017',
            database = 'PERSONAL',
            as_dict= True
        )
        f = open('e:/log_prueba.txt','a+')
        f.write('inicia proceso -- conexion Exitosa \n')
        f.close()
        return conn
    except NameError as e:
        f = open('e:/log_prueba.txt','a+')
        f.write(f'conexion fallida'+ e.name + '\n')
        f.close()