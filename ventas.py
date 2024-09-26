import os
import mysql.connector
from mysql.connector import Error, InterfaceError, DatabaseError, OperationalError
from dotenv import load_dotenv

class Venta:
    def __init__(self, producto, cantidad, precio, nombre_cliente, apellido_cliente, vendedor, n_local):
        self.__producto = producto
        self.__cantidad = cantidad
        self.__precio = precio
        self.__nombre_cliente = nombre_cliente
        self.__apellido_cliente = apellido_cliente
        self.__n_local = n_local
        self.__vendedor = vendedor
        self.__n_venta = int(0)

    @property
    def n_venta(self):
        return self.__n_venta

    @property
    def producto(self):
        return self.__producto

    @property
    def cantidad(self):
        return self.__cantidad

    @property
    def precio(self):
        return self.__precio

    @property
    def apellido_cliente(self):
        return self.__apellido_cliente.capitalize()

    @property
    def nombre_cliente(self):
        return self.__nombre_cliente.capitalize()

    @property
    def vendedor(self):
        return self.__vendedor

    @property
    def n_local(self):
        return self.__n_local

    @precio.setter
    def precio(self, nuevo_precio):
        self.__precio = self.validar_positivo(nuevo_precio)

    @cantidad.setter
    def cantidad(self, nueva_cantidad):
        self.__cantidad = self.validar_positivo(nueva_cantidad)

    @n_venta.setter
    def n_venta(self, n_venta):
        self.__n_venta = n_venta

    def validar_positivo(self, valor):
        try:
            valor = float(valor)
            if valor <= 0:
                raise ValueError(f"debe ser numérico positivo. ({valor}: valor incorrecto)")
            return valor
        except ValueError:
            raise ValueError("debe ser un número válido.")

    def to_dict(self):
        return {
            "n_venta": int(self.n_venta),
            "producto": self.producto,
            "cantidad": self.cantidad,
            "precio": self.precio,
            "apellido_cliente": self.apellido_cliente,
            "nombre_cliente": self.nombre_cliente,
            "vendedor": self.vendedor,
            "n_local": self.n_local
        }

    def __str__(self):
        return f"Número de venta: {self.n_venta} producto: {self.producto} vendedor: {self.vendedor}"

# Clase VentaTarjetaCredito
class VentaTarjetaCredito(Venta):
    def __init__(self, producto, cantidad, precio, nombre_cliente, apellido_cliente, vendedor, n_local, marca_tarjeta, n_cuotas):
        super().__init__(producto, cantidad, precio, nombre_cliente, apellido_cliente, vendedor, n_local)
        self.__marca_tarjeta = marca_tarjeta
        self.__n_cuotas = n_cuotas

    @property
    def marca_tarjeta(self):
        return self.__marca_tarjeta

    @property
    def n_cuotas(self):
        return self.__n_cuotas

    def to_dict(self):
        data = super().to_dict()
        data["marca_tarjeta"] = self.marca_tarjeta
        data["n_cuotas"] = self.n_cuotas
        return data

    def __str__(self):
        return f"{super().__str__()} - En cuotas con tarjeta de crédito: {self.n_cuotas}"

# Clase VentaCreditoCasa
class VentaCreditoCasa(Venta):
    def __init__(self, producto, cantidad, precio, nombre_cliente, apellido_cliente, vendedor, local, n_cuotas):
        super().__init__(producto, cantidad, precio, nombre_cliente, apellido_cliente, vendedor, local)
        self.__n_cuotas = n_cuotas

    @property
    def n_cuotas(self):
        return self.__n_cuotas

    def to_dict(self):
        data = super().to_dict()
        data["n_cuotas"] = self.n_cuotas
        return data

    def __str__(self):
        return f"{super().__str__()} - En cuotas con crédito de la casa: {self.n_cuotas}"

# Clase GestionVentas
class GestionVentas:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        self.port = os.getenv('DB_PORT')
        self.connection = None

    def connect_db(self):
        '''Establecer una conexión con la base de datos'''        
        try:            
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            if self.connection.is_connected():
                print("Conexión a la base de datos establecida.")
        except (InterfaceError, DatabaseError, OperationalError, Error) as e:
            print(f"Error al conectar a MySQL: {e}")
            self.connection = None

    def crear_venta(self, venta):
        self.connect_db()
        if not self.connection:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return
        
        try:
            with self.connection.cursor() as cursor:
                # Lógica común para insertar en la tabla "venta"
                query = ''' 
                    INSERT INTO venta (producto, cantidad, precio, nombre_cliente, apellido_cliente, vendedor, n_local)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) 
                ''' 
                cursor.execute(query, (venta.producto, venta.cantidad, venta.precio, venta.nombre_cliente, venta.apellido_cliente, venta.vendedor, venta.n_local))
                
                # Obtener el ID de la venta creada
                venta.n_venta = cursor.lastrowid
                
                # según el tipo de venta
                if isinstance(venta, VentaTarjetaCredito):
                    query = ''' 
                        INSERT INTO VentaTarjetaCredito (n_cuotas, marca_tarjeta, n_venta)
                        VALUES (%s, %s, %s) 
                    ''' 
                    cursor.execute(query, (venta.n_cuotas, venta.marca_tarjeta, venta.n_venta))

                elif isinstance(venta, VentaCreditoCasa):
                    query = ''' 
                        INSERT INTO VentaCreditoCasa (n_cuotas, n_venta)
                        VALUES (%s, %s) 
                    ''' 
                    cursor.execute(query, (venta.n_cuotas, venta.n_venta))

                # Commit de la transacción
                self.connection.commit()
                print(f"Venta N°: {venta.n_venta} creada correctamente.")

        except Exception as error:
            print(f'Error inesperado al crear la venta: {error}')
        finally:
            if self.connection.is_connected():
                self.cerrar_conexion()

    def leer_venta(self, n_venta):
        self.connect_db()
        if not self.connection:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return        
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                
                cursor.execute('''SELECT * FROM venta WHERE n_venta = %s''', (n_venta,))
                venta_data = cursor.fetchone()
                if venta_data:
                    print(f"Venta n° {venta_data['n_venta']} | producto: {venta_data['producto']} | cantidad: {venta_data['cantidad']} | precio: {venta_data['precio']} | cliente: {venta_data['nombre_cliente']} {venta_data['apellido_cliente']} \n vendedor: {venta_data['vendedor']} | n_local: {venta_data['n_local']}")
                    
                    cursor.execute('''SELECT * FROM VentaCreditoCasa WHERE n_venta = %s''', (n_venta,))
                    venta_credito_casa = cursor.fetchone()
                    if venta_credito_casa:                                             
                        print(f"Número de cuotas de la casa: {venta_credito_casa['n_cuotas']}")
                    
                    cursor.execute('''SELECT * FROM VentaTarjetaCredito WHERE n_venta = %s''', (n_venta,))
                    venta_tarjeta = cursor.fetchone()   
                    if venta_tarjeta:
                        print(f"Marca de la tarjeta: {venta_tarjeta['marca_tarjeta']} | Número de cuotas: {venta_tarjeta['n_cuotas']}")
                else:
                    print(f'No se encontró la venta {n_venta}')

        except Error as e:
            print(f'Error al leer la venta: {e}')
        finally:
            self.cerrar_conexion()

    def modificar_venta(self, n_venta, nuevo_precio):
        self.connect_db()
        if not self.connection:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('''SELECT * FROM venta WHERE n_venta = %s''', (n_venta,)) 
                if cursor.fetchone():   
                    cursor.execute('''UPDATE venta SET precio = %s WHERE n_venta = %s''', (nuevo_precio, n_venta))
                    self.connection.commit()
                    print(f'Se modificó el precio de la venta N°: {n_venta} a {nuevo_precio}')
                else:
                    print(f'No existe la venta N°: {n_venta}')
        except Error as e:
            print(f'Error al modificar la venta: {e}')
        finally:
            self.cerrar_conexion()

    def eliminar_venta(self, n_venta):
        self.connect_db()
        if not self.connection:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('''SELECT * FROM venta WHERE n_venta = %s''', (n_venta,)) 
                if cursor.fetchone():
                    # Eliminar entradas relacionadas en ventacreditocasa
                    cursor.execute('''DELETE FROM ventacreditocasa WHERE n_venta = %s''', (n_venta,))
                    
                    # Eliminar entradas relacionadas en ventatarjetacredito
                    cursor.execute('''DELETE FROM ventatarjetacredito WHERE n_venta = %s''', (n_venta,))
                    
                    # Finalmente eliminar la venta
                    cursor.execute('''DELETE FROM venta WHERE n_venta = %s''', (n_venta,))
                    
                    self.connection.commit()
                    print(f'La venta N°: {n_venta} se eliminó correctamente')
                else:
                    print(f'No existe la venta N°: {n_venta}')
        except Error as e:
            print(f'Error al eliminar la venta: {e}')
        finally:
            self.cerrar_conexion()

    def imprimir_todas_las_ventas(self):
        self.connect_db()
        if not self.connection:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return

        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute('''
                    SELECT v.*, 
                        cc.n_cuotas AS n_cuotas, 
                        tc.marca_tarjeta AS marca_tarjeta 
                    FROM venta v
                    LEFT JOIN VentaCreditoCasa cc ON v.n_venta = cc.n_venta
                    LEFT JOIN VentaTarjetaCredito tc ON v.n_venta = tc.n_venta
                ''')
                ventas = cursor.fetchall()

                print('=============== Listado completo de Ventas ==============')    
                for venta in ventas:
                    detalles_venta = f"Venta n° {venta['n_venta']} - producto: {venta['producto']} - cantidad: {venta['cantidad']} - precio: {venta['precio']} - vendedor: {venta['vendedor']}\n"

                    if 'marca_tarjeta' in venta and venta['marca_tarjeta']:
                        detalles_venta += f" - compra con tarjeta de crédito: {venta['marca_tarjeta']} en: {venta['n_cuotas']} cuotas"
                    elif 'n_cuotas' in venta and venta['n_cuotas']:
                        detalles_venta += f" - compra con crédito de la casa en: {venta['n_cuotas']} cuotas"
                    else:
                        detalles_venta += " - compra al contado"
                    
                    print(detalles_venta)
        except Error as e:
            print(f'Error al imprimir las ventas: {e}')
        finally:
            self.cerrar_conexion()
            
    def mejor_vendedor(self):
        self.connect_db()
        if not self.connection:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return

        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute('''
                    SELECT v.vendedor, SUM(v.precio * v.cantidad) AS total_ingresos
                    FROM venta v
                    GROUP BY v.vendedor
                    ORDER BY total_ingresos DESC
                    LIMIT 1
                ''')
                mejor_vendedor = cursor.fetchone()

                if mejor_vendedor:
                    print(f"Mejor Vendedor: {mejor_vendedor['vendedor']} - Total Ingresos: {mejor_vendedor['total_ingresos']}")
                else:
                    print("No se encontraron ventas.")

        except Error as e:
            print(f'Error al buscar el mejor vendedor: {e}')
        finally:
            self.cerrar_conexion()

    def cerrar_conexion(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a la base de datos cerrada.")