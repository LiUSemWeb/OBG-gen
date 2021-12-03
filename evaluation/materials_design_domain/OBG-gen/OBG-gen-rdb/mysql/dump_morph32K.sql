/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP TABLE IF EXISTS `mp_32K_calculation`;
CREATE TABLE `mp_32K_calculation` (
  `material_id` varchar(50) NOT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `mp_32K_structure`;
CREATE TABLE `mp_32K_structure` (
  `material_id` varchar(50) NOT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `mp_32K_composition`;
CREATE TABLE `mp_32K_composition` (
  `material_id` varchar(50) NOT NULL,
  `formula_pretty` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `mp_32K_formationenergy`;
CREATE TABLE `mp_32K_formationenergy` (
  `material_id` varchar(50) NOT NULL,
  `energy` float NOT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `mp_32K_spacegroup`;
CREATE TABLE `mp_32K_spacegroup` (
  `material_id` varchar(50) NOT NULL,
  `spacegroup` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `mp_32K_bandgap`;
CREATE TABLE `mp_32K_bandgap` (
  `material_id` varchar(50) NOT NULL,
  `band_gap` float NOT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `oqmd_32K_calculation`;
CREATE TABLE `oqmd_32K_calculation` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `oqmd_32K_structure`;
CREATE TABLE `oqmd_32K_structure` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `oqmd_32K_composition`;
CREATE TABLE `oqmd_32K_composition` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `oqmd_32K_bandgap`;
CREATE TABLE `oqmd_32K_bandgap` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  `band_gap` float NOT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `oqmd_32K_spacegroup`;
CREATE TABLE `oqmd_32K_spacegroup` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  `spacegroup` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `oqmd_32K_formationenergy`;
CREATE TABLE `oqmd_32K_formationenergy` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  `delta_e` float NOT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
