-- MySQL Administrator dump 1.4
--
-- ------------------------------------------------------
-- Server version	5.0.18-nt


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


--
-- Create schema geanie
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ geanie;
USE geanie;

--
-- Table structure for table `geanie`.`namesakes`
--

DROP TABLE IF EXISTS `namesakes`;
CREATE TABLE `namesakes` (
  `Predecessor` int(10) unsigned NOT NULL default '0' COMMENT 'Person ID',
  `Successor` int(10) unsigned NOT NULL default '0' COMMENT 'Person ID',
  PRIMARY KEY  (`Predecessor`,`Successor`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `geanie`.`namesakes`
--

/*!40000 ALTER TABLE `namesakes` DISABLE KEYS */;
/*!40000 ALTER TABLE `namesakes` ENABLE KEYS */;


--
-- Table structure for table `geanie`.`offspring`
--

DROP TABLE IF EXISTS `offspring`;
CREATE TABLE `offspring` (
  `Parent` int(10) unsigned NOT NULL default '0' COMMENT 'Person ID',
  `Child` int(10) unsigned NOT NULL default '0' COMMENT 'Person ID',
  PRIMARY KEY  (`Parent`,`Child`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `geanie`.`offspring`
--

/*!40000 ALTER TABLE `offspring` DISABLE KEYS */;
/*!40000 ALTER TABLE `offspring` ENABLE KEYS */;


--
-- Table structure for table `geanie`.`people`
--

DROP TABLE IF EXISTS `people`;
CREATE TABLE `people` (
  `idPerson` int(10) unsigned NOT NULL default '0',
  `Name` varchar(66) NOT NULL default '',
  `Scion` int(10) unsigned NOT NULL default '0' COMMENT 'Scion level',
  `Qualifier` int(10) unsigned NOT NULL default '0' COMMENT 'Qualifier level',
  `Sex` char(1) default NULL,
  `BirthDate` datetime default NULL,
  `BirthPlace` text,
  `DeathDate` datetime default NULL,
  `DeathPlace` text,
  `idParents` int(10) unsigned default NULL COMMENT '1:1 Union ID',
  PRIMARY KEY  (`idPerson`,`Name`,`Scion`,`Qualifier`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `geanie`.`people`
--

/*!40000 ALTER TABLE `people` DISABLE KEYS */;
/*!40000 ALTER TABLE `people` ENABLE KEYS */;


--
-- Table structure for table `geanie`.`photoassociations`
--

DROP TABLE IF EXISTS `photoassociations`;
CREATE TABLE `photoassociations` (
  `idPhoto` int(10) unsigned NOT NULL default '0',
  `idPerson` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`idPhoto`,`idPerson`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `geanie`.`photoassociations`
--

/*!40000 ALTER TABLE `photoassociations` DISABLE KEYS */;
/*!40000 ALTER TABLE `photoassociations` ENABLE KEYS */;


--
-- Table structure for table `geanie`.`photos`
--

DROP TABLE IF EXISTS `photos`;
CREATE TABLE `photos` (
  `idPhoto` int(10) unsigned NOT NULL default '0',
  `Filename` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`idPhoto`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `geanie`.`photos`
--

/*!40000 ALTER TABLE `photos` DISABLE KEYS */;
/*!40000 ALTER TABLE `photos` ENABLE KEYS */;


--
-- Table structure for table `geanie`.`scions`
--

DROP TABLE IF EXISTS `scions`;
CREATE TABLE `scions` (
  `Predecessor` int(10) unsigned NOT NULL default '0' COMMENT 'Person ID',
  `Successor` int(10) unsigned NOT NULL default '0' COMMENT 'Person ID',
  PRIMARY KEY  (`Predecessor`,`Successor`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `geanie`.`scions`
--

/*!40000 ALTER TABLE `scions` DISABLE KEYS */;
/*!40000 ALTER TABLE `scions` ENABLE KEYS */;


--
-- Table structure for table `geanie`.`unions`
--

DROP TABLE IF EXISTS `unions`;
CREATE TABLE `unions` (
  `idUnion` int(10) unsigned NOT NULL default '0',
  `idPerson_A` int(10) unsigned NOT NULL default '0',
  `idPerson_B` int(10) unsigned NOT NULL default '0',
  `Date` datetime default NULL,
  `Dissolution` datetime default NULL,
  `Location` text,
  PRIMARY KEY  (`idUnion`,`idPerson_A`,`idPerson_B`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `geanie`.`unions`
--

/*!40000 ALTER TABLE `unions` DISABLE KEYS */;
/*!40000 ALTER TABLE `unions` ENABLE KEYS */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
