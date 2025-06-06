/*!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.8-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: lab_commanddeck
-- ------------------------------------------------------
-- Server version	10.11.8-MariaDB-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `buttons`
--

DROP TABLE IF EXISTS `buttons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `buttons` (
  `button_id` int(4) NOT NULL,
  `button_name` varchar(50) NOT NULL,
  `button_command` varchar(100) NOT NULL,
  `button_color` varchar(7) NOT NULL,
  `sort_order` int(3) NOT NULL,
  UNIQUE KEY `button_id` (`button_id`),
  UNIQUE KEY `sort_order` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buttons`
--

LOCK TABLES `buttons` WRITE;
/*!40000 ALTER TABLE `buttons` DISABLE KEYS */;
INSERT INTO `buttons` VALUES
(1111,'Button 2','echo button2','#ff0400',2),
(3333,'Button 1','echo button1','#757575',1),
(3374,'Test response','ssh -i /root/.ssh/commanddeck -p 22 root@10.10.70.103 \"cat test.test\"','#3498db',5),
(4772,'button 3','echo button3','#590d68',3),
(9652,'Remote  SSH Test','ssh root@10.10.70.103 -i /root/.ssh/commanddeck -t \"echo \"remote ssh test  worked!\" > test.test\"','#3498db',4);
/*!40000 ALTER TABLE `buttons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_buttons`
--

DROP TABLE IF EXISTS `user_buttons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_buttons` (
  `user_id` int(11) NOT NULL,
  `button_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`button_id`),
  KEY `button_id` (`button_id`),
  CONSTRAINT `user_buttons_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_buttons_ibfk_2` FOREIGN KEY (`button_id`) REFERENCES `buttons` (`button_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_buttons`
--

LOCK TABLES `user_buttons` WRITE;
/*!40000 ALTER TABLE `user_buttons` DISABLE KEYS */;
INSERT INTO `user_buttons` VALUES
(25,3333),
(25,4772),
(26,1111),
(26,3333),
(26,4772);
/*!40000 ALTER TABLE `user_buttons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `permission_level` varchar(10) NOT NULL DEFAULT 'user',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(24,'admin','$2b$12$20PMbK2knh5JZPNTJMxQyeyxjXyIyFAdKD5aakJjmaBt8PgzxSCNu','admin'),
(25,'user','$2b$12$CM6teb6pTyksf3htKHWLP./d58AKjLLMApLFWnPgYdzIzv3fQF3ia','user'),
(26,'silvan','(\"(\'$2b$12$PoIyVb9rSYOsCZUDSOYlQOlO.8pcIxTfWEQjZ8q4w6WhmOie4z9dC\',)\",)','user');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-06 20:33:52
