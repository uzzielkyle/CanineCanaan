-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
-- ------------------------------------------------------
-- Server version	8.0.30

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'be2fcb50-b6d0-11ef-80c4-06aab8433371:1-39';

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
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dog`
--

LOCK TABLES `dog` WRITE;
/*!40000 ALTER TABLE `dog` DISABLE KEYS */;
INSERT INTO `dog` VALUES (1,18,'Princess',0,'Bulldog'),(2,14,'Queen',0,'Golden Retriever'),(3,7,'Pepper',1,'Labrador'),(4,21,'Brownie',1,'Dachshund'),(5,14,'Coco',0,'Shih Tzu'),(6,11,'Cookie',0,'Bulldog'),(7,8,'Toby',0,'Pomeranian'),(8,20,'Coco',1,'Dachshund'),(9,10,'Queen',1,'Beagle'),(10,18,'Cookie',0,'Aspin'),(11,24,'Mochi',1,'Chihuahua'),(12,22,'Sammy',1,'Doberman'),(13,9,'Cookie',0,'Maltese'),(14,12,'Bantay',0,'Bulldog'),(15,15,'Max',0,'Pomeranian'),(16,5,'Panda',1,'German Shepherd'),(17,12,'Bruno',0,'Rottweiler'),(18,21,'Chambe',0,'Pug'),(19,11,'Shadow',1,'Doberman'),(20,16,'Milo',0,'Dachshund'),(21,22,'Queen',1,'Doberman'),(22,16,'Bantay',1,'Chihuahua'),(23,16,'Bruno',0,'Bulldog'),(24,23,'Bruno',0,'German Shepherd'),(25,11,'Milo',0,'Pit Bull'),(26,20,'Sky',0,'German Shepherd'),(27,3,'Bella',1,'German Shepherd'),(28,7,'Pepper',1,'German Shepherd'),(29,4,'Angel',0,'Pomeranian'),(30,6,'Angel',0,'Aspin'),(31,19,'Sky',0,'Bulldog'),(32,7,'Chachi',1,'Beagle'),(33,22,'Shadow',0,'Maltese'),(34,4,'Shadow',0,'Labrador'),(35,1,'Brownie',1,'Chihuahua'),(36,2,'Queen',0,'Golden Retriever'),(37,13,'Buddy',1,'Pug'),(38,5,'Buddy',1,'Labrador'),(39,18,'Coco',1,'Dachshund'),(40,9,'Choco',1,'Siberian Husky'),(41,3,'Chambe',0,'Maltese'),(42,18,'Milo',0,'Siberian Husky'),(43,11,'Lucky',1,'Golden Retriever'),(44,11,'Brownie',0,'Maltese'),(45,2,'Coco',0,'Pit Bull'),(46,4,'Chambe',1,'Jack Russell Terrier'),(47,19,'Sky',1,'Jack Russell Terrier'),(48,10,'Lucky',0,'Beagle'),(49,1,'Toby',1,'Maltese'),(50,7,'Bantay',1,'Maltese');
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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `health_problem`
--

LOCK TABLES `health_problem` WRITE;
/*!40000 ALTER TABLE `health_problem` DISABLE KEYS */;
INSERT INTO `health_problem` VALUES (1,9,'Arthritis','2024-01-04','Non-steroidal Anti-inflammatory Drugs (NSAIDs), Joint Supplements, Physical Therapy, Acupuncture'),(2,2,'Ear Infection','2023-01-10','Antibiotics, Ear Drops, Antifungal Treatment, Steroid Therapy'),(3,13,'Kennel Cough','2022-01-20','Antibiotics, Cough Suppressants, Rest, Humidifier Use'),(4,11,'Hypothyroidism','2024-02-25','Thyroid Hormone Replacement, Regular Blood Tests, Diet Management'),(5,9,'Pancreatitis','2024-10-10','Fasting, Fluids and Electrolytes, Pain Relief, Antiemetic Drugs'),(6,2,'Diarrhea','2024-05-12','Hydration Therapy, Probiotics, Antidiarrheal Medications, Prescription Diet'),(7,6,'Kennel Cough','2024-05-16','Antibiotics, Cough Suppressants, Rest, Humidifier Use'),(8,22,'Heartworm Disease','2022-11-10','Heartworm Preventatives, Immiticide Injections, Corticosteroids, Antibiotics for secondary infections'),(9,3,'Heartworm Disease','2022-12-01','Heartworm Preventatives, Immiticide Injections, Corticosteroids, Antibiotics for secondary infections'),(10,6,'Heartworm Disease','2022-05-04','Heartworm Preventatives, Immiticide Injections, Corticosteroids, Antibiotics for secondary infections'),(11,18,'Heartworm Disease','2024-08-10','Heartworm Preventatives, Immiticide Injections, Corticosteroids, Antibiotics for secondary infections'),(12,15,'Arthritis','2024-01-29','Non-steroidal Anti-inflammatory Drugs (NSAIDs), Joint Supplements, Physical Therapy, Acupuncture'),(13,5,'Kennel Cough','2024-11-29','Antibiotics, Cough Suppressants, Rest, Humidifier Use'),(14,14,'Hypothyroidism','2024-03-02','Thyroid Hormone Replacement, Regular Blood Tests, Diet Management'),(15,18,'Obesity','2023-09-23','Calorie-Restricted Diet, Increased Exercise, Weight Management Medications, Behavioral Modifications'),(16,16,'Dental Disease','2024-02-05','Teeth Cleaning, Antibiotics, Dental Surgery, Dental Chews'),(17,20,'Ear Infection','2023-03-29','Antibiotics, Ear Drops, Antifungal Treatment, Steroid Therapy'),(18,14,'Hypothyroidism','2022-06-04','Thyroid Hormone Replacement, Regular Blood Tests, Diet Management'),(19,1,'Pancreatitis','2022-07-24','Fasting, Fluids and Electrolytes, Pain Relief, Antiemetic Drugs'),(20,14,'Pancreatitis','2023-10-02','Fasting, Fluids and Electrolytes, Pain Relief, Antiemetic Drugs'),(21,19,'Hypothyroidism','2024-05-07','Thyroid Hormone Replacement, Regular Blood Tests, Diet Management'),(22,18,'Pancreatitis','2023-09-26','Fasting, Fluids and Electrolytes, Pain Relief, Antiemetic Drugs'),(23,17,'Pancreatitis','2022-04-19','Fasting, Fluids and Electrolytes, Pain Relief, Antiemetic Drugs'),(24,7,'Obesity','2022-05-21','Calorie-Restricted Diet, Increased Exercise, Weight Management Medications, Behavioral Modifications'),(25,23,'Dental Disease','2023-09-16','Teeth Cleaning, Antibiotics, Dental Surgery, Dental Chews');
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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `health_record`
--

LOCK TABLES `health_record` WRITE;
/*!40000 ALTER TABLE `health_record` DISABLE KEYS */;
INSERT INTO `health_record` VALUES (1,6,8),(2,27,5),(3,10,1),(4,8,3),(5,9,19),(6,1,17),(7,19,22),(8,19,2),(9,34,25),(10,31,4),(11,16,24),(12,3,25),(13,2,7),(14,14,22),(15,22,25),(16,27,10),(17,11,14),(18,18,14),(19,26,18),(20,50,8),(21,42,1),(22,29,1),(23,33,1),(24,18,15),(25,33,15);
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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `litter`
--

LOCK TABLES `litter` WRITE;
/*!40000 ALTER TABLE `litter` DISABLE KEYS */;
INSERT INTO `litter` VALUES (1,48,27,'2023-12-10','Port Christopherton'),(2,46,23,'2022-03-23','East Billy'),(3,10,25,'2022-01-02','Riveraburgh'),(4,38,46,'2022-07-29','Schmitthaven'),(5,13,22,'2023-07-26','New Christopherhaven'),(6,8,47,'2024-06-29','Lake Ronaldborough'),(7,23,35,'2023-03-04','Petersenfort'),(8,9,41,'2023-08-05','Port Michelle'),(9,45,11,'2022-01-10','Lake Hunterhaven'),(10,46,43,'2024-05-13','Marvinfort'),(11,32,27,'2023-01-21','Kendrafurt'),(12,27,6,'2023-07-29','East Danielleberg'),(13,26,15,'2022-12-16','Jessicamouth'),(14,39,8,'2022-03-06','South Robertfort'),(15,42,15,'2024-07-02','Lake Hollystad'),(16,46,39,'2023-09-09','New Stevenmouth'),(17,34,20,'2022-02-21','South Kimberlytown'),(18,13,33,'2022-01-29','Lake Mario'),(19,40,38,'2024-12-01','Jamesfort'),(20,38,41,'2022-05-31','New Jaclynmouth'),(21,45,27,'2024-09-15','Lake Jenniferport'),(22,17,24,'2022-06-25','Lloydville'),(23,24,31,'2024-02-24','North Kimberly'),(24,41,32,'2023-10-31','Katherinemouth'),(25,21,3,'2023-06-16','North Rachelton');
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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vet`
--

LOCK TABLES `vet` WRITE;
/*!40000 ALTER TABLE `vet` DISABLE KEYS */;
INSERT INTO `vet` VALUES (1,'Carmela','Cruz','achang@example.org','487-364-7593x824'),(2,'Miguel','Ramos','vanessa89@example.org','911-957-8156x5938'),(3,'Carlos','Garcia','bryan80@example.org','001-460-997-5351x3933'),(4,'Carmela','Cruz','millerluke@example.net','614.984.1858x3989'),(5,'Carmela','Morales','carlsonpaul@example.net','342.332.0947'),(6,'Jasmine','Gomez','nancymclean@example.org','001-986-984-8339x694'),(7,'Maria','Morales','christopher91@example.com','001-453-730-4135'),(8,'Kyle','Garcia','gcabrera@example.org','001-330-898-9101x399'),(9,'Maria','Libao','woodtina@example.org','+1-303-621-7300x869'),(10,'Kyle','Morales','walkerdeborah@example.com','(420)587-0916x34579'),(11,'Juan','Heredero','kramereric@example.org','884-619-7207x69845'),(12,'Miguel','Garcia','annsmith@example.net','650-784-2375'),(13,'Miguel','Dela Cruz','jenniferhughes@example.com','+1-210-893-5233x7696'),(14,'Jasmine','Dela Cruz','tbarton@example.org','(271)242-7878'),(15,'Grace','Heredero','dnguyen@example.org','(338)512-0665x03008'),(16,'Maria','Santos','franklinjames@example.com','721-376-1047x142'),(17,'Maria','Santos','joshuasmith@example.org','948.855.9097'),(18,'Juan','Santos','monica23@example.com','001-340-722-4555'),(19,'Maria','Libao','williamsfrank@example.net','356-682-4173x0428'),(20,'Jose','Santos','thouston@example.com','318-977-5517'),(21,'Kyle','Morales','vjohnson@example.net','+1-822-696-1113x30601'),(22,'Maria','Gomez','ymora@example.net','001-336-315-3492x635'),(23,'Maria','Heredero','leachshannon@example.net','417.364.3039'),(24,'Kyle','Gomez','stephenward@example.org','797-929-6687'),(25,'Juan','Dela Cruz','mreid@example.net','+1-830-655-5082x492');
/*!40000 ALTER TABLE `vet` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-10 21:29:15
