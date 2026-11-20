CREATE DATABASE  IF NOT EXISTS `soai` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `soai`;
-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: soai
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('166a24a783a8');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Muletas',1),(2,'Bastones',1),(3,'Andadores',1),(4,'Sillas de ruedas',1),(5,'Rodilleras',1),(6,'Tobilleras',1),(7,'Fajas',1),(8,'Plantillas',1),(9,'Otros',1);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `name` varchar(200) NOT NULL,
  `category_id` int NOT NULL,
  `description` text,
  `price` decimal(12,2) NOT NULL,
  `stock` int NOT NULL DEFAULT '0',
  `min_stock` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_products_code` (`code`),
  KEY `ix_products_category_id` (`category_id`),
  KEY `ix_products_name` (`name`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `ck_products_min_stock_nonneg` CHECK ((`min_stock` >= 0)),
  CONSTRAINT `ck_products_price_nonneg` CHECK ((`price` >= 0)),
  CONSTRAINT `ck_products_stock_nonneg` CHECK ((`stock` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'MUL-001','Muleta axilar de aluminio regulable',1,NULL,28500.00,12,4,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(2,'MUL-002','Muleta canadiense con apoyo de antebrazo',1,NULL,34900.00,3,5,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(3,'MUL-003','Par de gomas para muleta',1,NULL,3200.00,40,10,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(4,'BAS-001','Bastón de aluminio regulable',2,NULL,14500.00,18,5,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(5,'BAS-002','Bastón tetrápode',2,NULL,22900.00,0,3,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(6,'BAS-003','Bastón plegable',2,NULL,17800.00,7,4,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(7,'AND-001','Andador fijo de aluminio',3,NULL,49500.00,6,2,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(8,'AND-002','Andador con ruedas delanteras',1,NULL,58900.00,7,3,1,'2026-11-19 21:11:19','2026-11-19 21:13:27'),(9,'AND-003','Andador rollator de cuatro ruedas',3,NULL,129000.00,4,2,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(10,'SIL-001','Silla de ruedas plegable estándar',4,NULL,215000.00,3,1,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(11,'SIL-002','Silla de ruedas liviana de aluminio',4,NULL,289000.00,1,2,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(12,'SIL-003','Silla de baño con respaldo',4,NULL,68500.00,5,NULL,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(13,'ROD-001','Rodillera elástica talle M',5,NULL,19800.00,15,5,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(14,'ROD-002','Rodillera elástica talle L',5,NULL,19800.00,4,5,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(15,'ROD-003','Rodillera con ortesis de rótula',5,NULL,38500.00,8,3,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(16,'ROD-004','Rodillera articulada con barras laterales',5,NULL,72000.00,0,2,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(17,'TOB-001','Tobillera elástica talle M',6,NULL,12500.00,20,6,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(18,'TOB-002','Tobillera con ajuste de velcro',6,NULL,18900.00,9,4,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(19,'TOB-003','Tobillera estabilizadora rígida',6,NULL,31500.00,5,NULL,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(20,'FAJ-001','Faja lumbar elástica talle M',7,NULL,26500.00,10,4,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(21,'FAJ-002','Faja lumbar con varillas talle L',7,NULL,39800.00,3,4,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(22,'FAJ-003','Faja postural para espalda',7,NULL,33900.00,7,3,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(23,'PLA-001','Plantillas ortopédicas de silicona',8,NULL,9800.00,25,8,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(24,'PLA-002','Plantillas para pie plano',8,NULL,15500.00,14,5,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(25,'PLA-003','Taloneras de gel',8,NULL,6900.00,30,10,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(26,'OTR-001','Cuello ortopédico blando',9,NULL,11900.00,11,4,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(27,'OTR-002','Cabestrillo para brazo',9,NULL,13400.00,9,3,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(28,'OTR-003','Almohadón antiescaras',9,NULL,42500.00,4,2,1,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(29,'OTR-004','Collar cervical rígido (discontinuado)',9,NULL,28700.00,0,NULL,0,'2026-11-19 21:11:19','2026-11-19 21:11:19'),(30,'OTR-005','Bolsa de gel frío/calor',9,NULL,8700.00,16,5,1,'2026-11-19 21:11:19','2026-11-19 21:11:19');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'soai'
--

--
-- Dumping routines for database 'soai'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-20  3:48:08
