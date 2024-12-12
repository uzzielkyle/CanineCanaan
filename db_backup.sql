-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: dog_breeding
-- ------------------------------------------------------
-- Server version	8.0.37

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
-- Table structure for table `dog`
--

DROP TABLE IF EXISTS `dog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `litter_id` int DEFAULT NULL,
  `name` varchar(45) NOT NULL,
  `gender` tinyint NOT NULL,
  `breed` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_dog_litter1_idx` (`litter_id`),
  CONSTRAINT `fk_dog_litter1` FOREIGN KEY (`litter_id`) REFERENCES `litter` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dog`
--

LOCK TABLES `dog` WRITE;
/*!40000 ALTER TABLE `dog` DISABLE KEYS */;
/*!40000 ALTER TABLE `dog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `health_problem`
--

DROP TABLE IF EXISTS `health_problem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `health_problem` (
  `id` int NOT NULL AUTO_INCREMENT,
  `health_record_id` int NOT NULL,
  `problem` varchar(135) NOT NULL,
  `date` date NOT NULL,
  `treatment` varchar(135) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_health_problem_health_record1_idx` (`health_record_id`),
  CONSTRAINT `fk_health_problem_health_record1` FOREIGN KEY (`health_record_id`) REFERENCES `health_record` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `health_problem`
--

LOCK TABLES `health_problem` WRITE;
/*!40000 ALTER TABLE `health_problem` DISABLE KEYS */;
/*!40000 ALTER TABLE `health_problem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `health_record`
--

DROP TABLE IF EXISTS `health_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `health_record` (
  `id` int NOT NULL AUTO_INCREMENT,
  `dog_id` int NOT NULL,
  `vet_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_health_record_dog1_idx` (`dog_id`),
  KEY `fk_health_record_vet1_idx` (`vet_id`),
  CONSTRAINT `fk_health_record_dog1` FOREIGN KEY (`dog_id`) REFERENCES `dog` (`id`),
  CONSTRAINT `fk_health_record_vet1` FOREIGN KEY (`vet_id`) REFERENCES `vet` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `health_record`
--

LOCK TABLES `health_record` WRITE;
/*!40000 ALTER TABLE `health_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `health_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `litter`
--

DROP TABLE IF EXISTS `litter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `litter` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sire_id` int NOT NULL,
  `dam_id` int NOT NULL,
  `birthdate` date NOT NULL,
  `birthplace` varchar(135) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_litter_dog_idx` (`sire_id`),
  KEY `fk_litter_dog1_idx` (`dam_id`),
  CONSTRAINT `fk_litter_dog` FOREIGN KEY (`sire_id`) REFERENCES `dog` (`id`),
  CONSTRAINT `fk_litter_dog1` FOREIGN KEY (`dam_id`) REFERENCES `dog` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `litter`
--

LOCK TABLES `litter` WRITE;
/*!40000 ALTER TABLE `litter` DISABLE KEYS */;
/*!40000 ALTER TABLE `litter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vet`
--

DROP TABLE IF EXISTS `vet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vet` (
  `id` int NOT NULL AUTO_INCREMENT,
  `firstname` varchar(45) NOT NULL,
  `lastname` varchar(45) NOT NULL,
  `email` varchar(45) DEFAULT NULL,
  `phone` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vet`
--

LOCK TABLES `vet` WRITE;
/*!40000 ALTER TABLE `vet` DISABLE KEYS */;
/*!40000 ALTER TABLE `vet` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-12 21:57:49
