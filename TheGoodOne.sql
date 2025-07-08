/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.7.2-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: normalzone
-- ------------------------------------------------------
-- Server version	11.8.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Sequence structure for `global_seq`
--

DROP SEQUENCE IF EXISTS `global_seq`;
CREATE SEQUENCE `global_seq` start with 100000 minvalue 1 maxvalue 9223372036854775806 increment by 1 cache 1000 nocycle ENGINE=InnoDB;
DO SETVAL(`global_seq`, 100000, 0);

--
-- Table structure for table `agente`
--

DROP TABLE IF EXISTS `agente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `agente` (
  `id_agente` int(11) NOT NULL AUTO_INCREMENT,
  `id_entidad` int(11) DEFAULT NULL,
  `comision_venta` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id_agente`),
  KEY `id_entidad` (`id_entidad`),
  CONSTRAINT `agente_ibfk_1` FOREIGN KEY (`id_entidad`) REFERENCES `representante` (`id_entidad`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agente`
--

LOCK TABLES `agente` WRITE;
/*!40000 ALTER TABLE `agente` DISABLE KEYS */;
/*!40000 ALTER TABLE `agente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `almacen`
--

DROP TABLE IF EXISTS `almacen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `almacen` (
  `id_almacen` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `ubicacion` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id_almacen`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `almacen`
--

LOCK TABLES `almacen` WRITE;
/*!40000 ALTER TABLE `almacen` DISABLE KEYS */;
INSERT INTO `almacen` VALUES
(1,'1','Almacén Planta','Nave Industrial A, Monterrey'),
(2,'AE0511','Bodega Brasa (Agua Fria)','Veracruz');
/*!40000 ALTER TABLE `almacen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clasificacion`
--

DROP TABLE IF EXISTS `clasificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `clasificacion` (
  `id_clasificacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_tipo_clasificacion` int(11) DEFAULT NULL,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id_clasificacion`),
  KEY `id_tipo_clasificacion` (`id_tipo_clasificacion`),
  CONSTRAINT `clasificacion_ibfk_1` FOREIGN KEY (`id_tipo_clasificacion`) REFERENCES `tipo_clasificacion` (`id_tipo_clasificacion`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clasificacion`
--

LOCK TABLES `clasificacion` WRITE;
/*!40000 ALTER TABLE `clasificacion` DISABLE KEYS */;
INSERT INTO `clasificacion` VALUES
(1,1,'Premium'),
(2,1,'Estándar'),
(3,2,'Saco'),
(4,2,'Supersaco');
/*!40000 ALTER TABLE `clasificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id_cliente` int(11) NOT NULL AUTO_INCREMENT,
  `id_entidad` int(11) DEFAULT NULL,
  `limite_credito` decimal(15,2) DEFAULT NULL,
  `dias_credito` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  KEY `id_entidad` (`id_entidad`),
  CONSTRAINT `cliente_ibfk_1` FOREIGN KEY (`id_entidad`) REFERENCES `representante` (`id_entidad`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES
(1,1,50000.00,30),
(2,2,100000.00,45),
(3,1,50000.00,30),
(4,2,100000.00,45),
(5,1,50000.00,30),
(6,2,100000.00,45),
(7,1,50000.00,30),
(8,2,100000.00,45),
(9,1,50000.00,30),
(10,2,100000.00,45);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contacto`
--

DROP TABLE IF EXISTS `contacto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `contacto` (
  `id_contacto` int(11) NOT NULL AUTO_INCREMENT,
  `id_entidad` int(11) DEFAULT NULL,
  `nombre` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_contacto`),
  KEY `id_entidad` (`id_entidad`),
  CONSTRAINT `contacto_ibfk_1` FOREIGN KEY (`id_entidad`) REFERENCES `representante` (`id_entidad`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contacto`
--

LOCK TABLES `contacto` WRITE;
/*!40000 ALTER TABLE `contacto` DISABLE KEYS */;
/*!40000 ALTER TABLE `contacto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `direccion`
--

DROP TABLE IF EXISTS `direccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `direccion` (
  `id_direccion` int(11) NOT NULL AUTO_INCREMENT,
  `id_municipio` int(11) DEFAULT NULL,
  `calle` varchar(100) DEFAULT NULL,
  `numero_exterior` varchar(20) DEFAULT NULL,
  `colonia` varchar(100) DEFAULT NULL,
  `codigo_postal` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_direccion`),
  KEY `id_municipio` (`id_municipio`),
  CONSTRAINT `direccion_ibfk_1` FOREIGN KEY (`id_municipio`) REFERENCES `municipio` (`id_municipio`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `direccion`
--

LOCK TABLES `direccion` WRITE;
/*!40000 ALTER TABLE `direccion` DISABLE KEYS */;
INSERT INTO `direccion` VALUES
(1,1,'Av. Revolución','1500','Centro','64000'),
(2,3,'Blvd. Díaz Ordaz','220','Industrial','31000'),
(3,1,'Av. Revolución','1500','Centro','64000'),
(4,3,'Blvd. Díaz Ordaz','220','Industrial','31000'),
(5,1,'Av. Revolución','1500','Centro','64000'),
(6,3,'Blvd. Díaz Ordaz','220','Industrial','31000');
/*!40000 ALTER TABLE `direccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documento`
--

DROP TABLE IF EXISTS `documento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `documento` (
  `id_documento` int(11) NOT NULL AUTO_INCREMENT,
  `id_tipo_documento` int(11) DEFAULT NULL,
  `serie` varchar(20) DEFAULT NULL,
  `folio` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `id_entidad` int(11) DEFAULT NULL,
  `id_almacen` int(11) DEFAULT NULL,
  `total` decimal(15,4) NOT NULL,
  PRIMARY KEY (`id_documento`),
  KEY `id_tipo_documento` (`id_tipo_documento`),
  KEY `id_entidad` (`id_entidad`),
  KEY `id_almacen` (`id_almacen`),
  KEY `idx_documento_fecha` (`fecha`),
  CONSTRAINT `documento_ibfk_1` FOREIGN KEY (`id_tipo_documento`) REFERENCES `tipo_documento` (`id_tipo_documento`),
  CONSTRAINT `documento_ibfk_2` FOREIGN KEY (`id_entidad`) REFERENCES `representante` (`id_entidad`),
  CONSTRAINT `documento_ibfk_3` FOREIGN KEY (`id_almacen`) REFERENCES `almacen` (`id_almacen`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documento`
--

LOCK TABLES `documento` WRITE;
/*!40000 ALTER TABLE `documento` DISABLE KEYS */;
INSERT INTO `documento` VALUES
(1,NULL,'FAC',1001,'2023-01-15 00:00:00',1,NULL,24000.0000),
(2,NULL,'FAC',1002,'2023-02-20 00:00:00',1,NULL,48000.0000),
(3,1,'FAC',1001,'2023-01-15 00:00:00',1,1,24000.0000),
(4,1,'FAC',1002,'2023-02-20 00:00:00',2,1,48000.0000);
/*!40000 ALTER TABLE `documento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empresa`
--

DROP TABLE IF EXISTS `empresa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `empresa` (
  `id_empresa` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `rfc` varchar(20) DEFAULT NULL,
  `curp` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empresa`
--

LOCK TABLES `empresa` WRITE;
/*!40000 ALTER TABLE `empresa` DISABLE KEYS */;
/*!40000 ALTER TABLE `empresa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entidad_direccion`
--

DROP TABLE IF EXISTS `entidad_direccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `entidad_direccion` (
  `id_entidad_direccion` int(11) NOT NULL AUTO_INCREMENT,
  `id_entidad` int(11) DEFAULT NULL,
  `id_direccion` int(11) DEFAULT NULL,
  `tipo` enum('fiscal','envio','comercial') DEFAULT NULL,
  PRIMARY KEY (`id_entidad_direccion`),
  KEY `id_entidad` (`id_entidad`),
  KEY `id_direccion` (`id_direccion`),
  CONSTRAINT `entidad_direccion_ibfk_1` FOREIGN KEY (`id_entidad`) REFERENCES `representante` (`id_entidad`),
  CONSTRAINT `entidad_direccion_ibfk_2` FOREIGN KEY (`id_direccion`) REFERENCES `direccion` (`id_direccion`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entidad_direccion`
--

LOCK TABLES `entidad_direccion` WRITE;
/*!40000 ALTER TABLE `entidad_direccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `entidad_direccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estado`
--

DROP TABLE IF EXISTS `estado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `estado` (
  `id_estado` int(11) NOT NULL AUTO_INCREMENT,
  `id_pais` int(11) DEFAULT NULL,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id_estado`),
  KEY `id_pais` (`id_pais`),
  CONSTRAINT `estado_ibfk_1` FOREIGN KEY (`id_pais`) REFERENCES `pais` (`id_pais`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estado`
--

LOCK TABLES `estado` WRITE;
/*!40000 ALTER TABLE `estado` DISABLE KEYS */;
INSERT INTO `estado` VALUES
(1,1,'Nuevo León'),
(2,1,'Chihuahua'),
(3,1,'Veracruz');
/*!40000 ALTER TABLE `estado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `existencia`
--

DROP TABLE IF EXISTS `existencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `existencia` (
  `id_existencia` int(11) NOT NULL AUTO_INCREMENT,
  `id_almacen` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `cantidad` int(11) NOT NULL,
  `costo` decimal(15,4) DEFAULT NULL,
  PRIMARY KEY (`id_existencia`),
  KEY `id_almacen` (`id_almacen`),
  KEY `idx_existencia_producto` (`id_producto`),
  CONSTRAINT `existencia_ibfk_1` FOREIGN KEY (`id_almacen`) REFERENCES `almacen` (`id_almacen`),
  CONSTRAINT `existencia_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `existencia`
--

LOCK TABLES `existencia` WRITE;
/*!40000 ALTER TABLE `existencia` DISABLE KEYS */;
INSERT INTO `existencia` VALUES
(1,1,1,500,200.0000),
(2,1,2,200,800.0000);
/*!40000 ALTER TABLE `existencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `familia_producto`
--

DROP TABLE IF EXISTS `familia_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `familia_producto` (
  `id_familia` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `codigo` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_familia`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `familia_producto`
--

LOCK TABLES `familia_producto` WRITE;
/*!40000 ALTER TABLE `familia_producto` DISABLE KEYS */;
INSERT INTO `familia_producto` VALUES
(1,'Azúcares','AZU'),
(2,'Endulzantes','END'),
(3,'Servicios','SER'),
(4,'Aditivos','ADT'),
(5,'Embalaje','EMB');
/*!40000 ALTER TABLE `familia_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lote`
--

DROP TABLE IF EXISTS `lote`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lote` (
  `id_lote` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) DEFAULT NULL,
  `numero_lote` varchar(30) NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  PRIMARY KEY (`id_lote`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `lote_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lote`
--

LOCK TABLES `lote` WRITE;
/*!40000 ALTER TABLE `lote` DISABLE KEYS */;
INSERT INTO `lote` VALUES
(1,1,'LOTE-2023-001','2024-12-31'),
(2,2,'LOTE-2023-045','2024-10-15');
/*!40000 ALTER TABLE `lote` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `moneda`
--

DROP TABLE IF EXISTS `moneda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `moneda` (
  `id_moneda` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(3) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `simbolo` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id_moneda`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `moneda`
--

LOCK TABLES `moneda` WRITE;
/*!40000 ALTER TABLE `moneda` DISABLE KEYS */;
INSERT INTO `moneda` VALUES
(1,'MXN','Peso Mexicano','$'),
(2,'USD','Dólar Estadounidense','US$');
/*!40000 ALTER TABLE `moneda` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimiento_documento`
--

DROP TABLE IF EXISTS `movimiento_documento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimiento_documento` (
  `id_movimiento` int(11) NOT NULL AUTO_INCREMENT,
  `id_documento` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `cantidad` decimal(15,4) NOT NULL,
  `precio` decimal(15,4) NOT NULL,
  PRIMARY KEY (`id_movimiento`),
  KEY `id_documento` (`id_documento`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `movimiento_documento_ibfk_1` FOREIGN KEY (`id_documento`) REFERENCES `documento` (`id_documento`),
  CONSTRAINT `movimiento_documento_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimiento_documento`
--

LOCK TABLES `movimiento_documento` WRITE;
/*!40000 ALTER TABLE `movimiento_documento` DISABLE KEYS */;
INSERT INTO `movimiento_documento` VALUES
(1,1,1,100.0000,240.0000),
(2,2,2,50.0000,960.0000),
(3,1,1,100.0000,240.0000),
(4,2,2,50.0000,960.0000);
/*!40000 ALTER TABLE `movimiento_documento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `municipio`
--

DROP TABLE IF EXISTS `municipio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `municipio` (
  `id_municipio` int(11) NOT NULL AUTO_INCREMENT,
  `id_estado` int(11) DEFAULT NULL,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id_municipio`),
  KEY `id_estado` (`id_estado`),
  CONSTRAINT `municipio_ibfk_1` FOREIGN KEY (`id_estado`) REFERENCES `estado` (`id_estado`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `municipio`
--

LOCK TABLES `municipio` WRITE;
/*!40000 ALTER TABLE `municipio` DISABLE KEYS */;
INSERT INTO `municipio` VALUES
(1,1,'Monterrey'),
(2,1,'San Nicolás'),
(3,2,'Chihuahua'),
(4,3,'Veracruz');
/*!40000 ALTER TABLE `municipio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pais`
--

DROP TABLE IF EXISTS `pais`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `pais` (
  `id_pais` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `codigo_iso` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`id_pais`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pais`
--

LOCK TABLES `pais` WRITE;
/*!40000 ALTER TABLE `pais` DISABLE KEYS */;
INSERT INTO `pais` VALUES
(1,'México','MEX'),
(2,'Estados Unidos','USA');
/*!40000 ALTER TABLE `pais` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `precio_producto`
--

DROP TABLE IF EXISTS `precio_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `precio_producto` (
  `id_precio` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) DEFAULT NULL,
  `id_moneda` int(11) DEFAULT NULL,
  `tipo_precio` enum('compra','venta','especial') DEFAULT NULL,
  `precio` decimal(15,4) NOT NULL,
  `Fecha` date NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_precio`),
  KEY `id_producto` (`id_producto`),
  KEY `id_moneda` (`id_moneda`),
  CONSTRAINT `precio_producto_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`),
  CONSTRAINT `precio_producto_ibfk_2` FOREIGN KEY (`id_moneda`) REFERENCES `moneda` (`id_moneda`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `precio_producto`
--

LOCK TABLES `precio_producto` WRITE;
/*!40000 ALTER TABLE `precio_producto` DISABLE KEYS */;
INSERT INTO `precio_producto` VALUES
(1,1,1,'venta',110.0000,'2025-06-20');
/*!40000 ALTER TABLE `precio_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `id_familia` int(11) DEFAULT NULL,
  `id_unidad_medida` int(11) DEFAULT NULL,
  `peso` decimal(10,2) DEFAULT NULL,
  `clave_sat` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `id_familia` (`id_familia`),
  KEY `id_unidad_medida` (`id_unidad_medida`),
  KEY `idx_producto_codigo` (`codigo`),
  CONSTRAINT `producto_ibfk_1` FOREIGN KEY (`id_familia`) REFERENCES `familia_producto` (`id_familia`),
  CONSTRAINT `producto_ibfk_2` FOREIGN KEY (`id_unidad_medida`) REFERENCES `unidad_medida` (`id_unidad`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
INSERT INTO `producto` VALUES
(1,'AZ-EST-25KG','Azúcar Estandar Granulada Saco 25KG',1,1,25.00,'170199'),
(2,'AZ-REF-PULV-6x25KG','Azúcar Refinado Pulverizado 6x25KG',1,1,25.00,'170199'),
(3,'AZ-BRN-25KG','Azúcar Brown Dark Sugar Saco 25 KG',1,1,25.00,'170199'),
(4,'SERV-LOG','Servicio de Logística y Traslado',3,1,NULL,'851718');
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedor`
--

DROP TABLE IF EXISTS `proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor` (
  `id_proveedor` int(11) NOT NULL AUTO_INCREMENT,
  `id_entidad` int(11) DEFAULT NULL,
  `tiempo_entrega` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id_proveedor`),
  KEY `id_entidad` (`id_entidad`),
  CONSTRAINT `proveedor_ibfk_1` FOREIGN KEY (`id_entidad`) REFERENCES `representante` (`id_entidad`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor`
--

LOCK TABLES `proveedor` WRITE;
/*!40000 ALTER TABLE `proveedor` DISABLE KEYS */;
/*!40000 ALTER TABLE `proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `representante`
--

DROP TABLE IF EXISTS `representante`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `representante` (
  `id_entidad` int(11) NOT NULL AUTO_INCREMENT,
  `tipo` enum('cliente','proveedor','agente') NOT NULL,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `rfc` varchar(20) DEFAULT NULL,
  `contraseña` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_entidad`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `idx_entidad_tipo` (`tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `representante`
--

LOCK TABLES `representante` WRITE;
/*!40000 ALTER TABLE `representante` DISABLE KEYS */;
INSERT INTO `representante` VALUES
(1,'cliente','CLI-001','Comercializadora Dimafe',NULL,NULL),
(2,'proveedor','PROV-045','Productos Agrícolas Chihuahua',NULL,NULL),
(8,'cliente','C0003','PANADERIA Y PASTELERIA REGIONDNTANA','PPR969803857',NULL),
(9,'cliente','C0025','COMERCIAL TREVIÑO','CTR911104FBA',NULL),
(10,'proveedor','PROV-101','Alimentos Naturales Sabroza S.A. DE C.V.','AN59008284E9',NULL),
(11,'agente','AG01','JAMER ARROYO',NULL,NULL);
/*!40000 ALTER TABLE `representante` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_clasificacion`
--

DROP TABLE IF EXISTS `tipo_clasificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_clasificacion` (
  `id_tipo_clasificacion` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id_tipo_clasificacion`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_clasificacion`
--

LOCK TABLES `tipo_clasificacion` WRITE;
/*!40000 ALTER TABLE `tipo_clasificacion` DISABLE KEYS */;
INSERT INTO `tipo_clasificacion` VALUES
(1,'Calidad'),
(2,'Tipo Embalaje');
/*!40000 ALTER TABLE `tipo_clasificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_documento`
--

DROP TABLE IF EXISTS `tipo_documento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_documento` (
  `id_tipo_documento` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `afecta_existencia` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id_tipo_documento`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_documento`
--

LOCK TABLES `tipo_documento` WRITE;
/*!40000 ALTER TABLE `tipo_documento` DISABLE KEYS */;
INSERT INTO `tipo_documento` VALUES
(1,'Factura',1),
(2,'Orden de Compra',1),
(3,'Nota de Crédito',-1),
(4,'Albarán',1);
/*!40000 ALTER TABLE `tipo_documento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unidad_medida`
--

DROP TABLE IF EXISTS `unidad_medida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `unidad_medida` (
  `id_unidad` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `abreviatura` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_unidad`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidad_medida`
--

LOCK TABLES `unidad_medida` WRITE;
/*!40000 ALTER TABLE `unidad_medida` DISABLE KEYS */;
INSERT INTO `unidad_medida` VALUES
(1,'Kilogramo','KG'),
(2,'Gramo','GR'),
(3,'Litro','LT'),
(4,'Pieza','PZ'),
(5,'Tonelada','TON'),
(6,'Libra','LB');
/*!40000 ALTER TABLE `unidad_medida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `valor_clasificacion`
--

DROP TABLE IF EXISTS `valor_clasificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `valor_clasificacion` (
  `id_valor_clasificacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_clasificacion` int(11) DEFAULT NULL,
  `valor` varchar(100) NOT NULL,
  PRIMARY KEY (`id_valor_clasificacion`),
  KEY `id_clasificacion` (`id_clasificacion`),
  CONSTRAINT `valor_clasificacion_ibfk_1` FOREIGN KEY (`id_clasificacion`) REFERENCES `clasificacion` (`id_clasificacion`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `valor_clasificacion`
--

LOCK TABLES `valor_clasificacion` WRITE;
/*!40000 ALTER TABLE `valor_clasificacion` DISABLE KEYS */;
INSERT INTO `valor_clasificacion` VALUES
(1,1,'ISO 9001'),
(2,2,'Granel');
/*!40000 ALTER TABLE `valor_clasificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'normalzone'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-06-30  8:56:17
