n_ventan_venta
create database ventas_db;
use ventas_db;
create table venta (
	n_venta INT AUTO_INCREMENT PRIMARY KEY,
	producto VARCHAR(255) not null,
	cantidad INT not null,
	precio DECIMAL(10, 2) not null,
	nombre_cliente VARCHAR(255) not null,
	apellido_cliente VARCHAR(255) not null,
	vendedor VARCHAR(255) not null,
	n_local VARCHAR(255) not null
	);
create table VentaCreditoCasa (
	n_venta INT AUTO_INCREMENT PRIMARY KEY,
    n_cuotas INT not null,
    FOREIGN KEY (n_venta) REFERENCES venta(n_venta)
	);
create table VentaTarjetaCredito (
	n_venta INT AUTO_INCREMENT PRIMARY KEY,
    n_cuotas INT not null,
    marca_tarjeta VARCHAR(255) not null,
    FOREIGN KEY (n_venta) REFERENCES venta(n_venta)
	);
-- modificar

ALTER TABLE venta
MODIFY COLUMN precio FLOAT not null;

ALTER TABLE venta
ADD lugar_de_venta FLOAT not null;

ALTER TABLE venta
DROP COLUMN lugar_de_venta;

SELECT * FROM venta;

