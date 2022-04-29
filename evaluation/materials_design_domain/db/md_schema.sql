DROP DATABASE IF EXISTS ODGSG_MP;
CREATE DATABASE ODGSG_MP;
USE ODGSG_MP;

DROP TABLE IF EXISTS `Calculation1K`;
CREATE TABLE `Calculation1K` (
  `material_id` varchar(50) NOT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `Structure1K`;
CREATE TABLE `Structure1K` (
  `material_id` varchar(50) NOT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `Composition1K`;
CREATE TABLE `Composition1K` (
  `material_id` varchar(50) NOT NULL,
  `formula_pretty` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `FormationEnergy1K`;
CREATE TABLE `FormationEnergy1K` (
  `material_id` varchar(50) NOT NULL,
  `energy` float NOT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `SpaceGroup1K`;
CREATE TABLE `SpaceGroup1K` (
  `material_id` varchar(50) NOT NULL,
  `spacegroup` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `BandGap1K`;
CREATE TABLE `BandGap1K` (
  `material_id` varchar(50) NOT NULL,
  `band_gap` float NOT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP DATABASE IF EXISTS ODGSG_OQMD;
CREATE DATABASE ODGSG_OQMD;
USE ODGSG_OQMD;

DROP TABLE IF EXISTS `Calculation1K`;
CREATE TABLE `Calculation1K` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `Structure1K`;
CREATE TABLE `Structure1K` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `Composition1K`;
CREATE TABLE `Composition1K` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `BandGap1K`;
CREATE TABLE `BandGap1K` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  `band_gap` float NOT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `SpaceGroup1K`;
CREATE TABLE `SpaceGroup1K` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  `spacegroup` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `FormationEnergy1K`;
CREATE TABLE `FormationEnergy1K` (
  `entry_id` varchar(50) NOT NULL,
  `calculation_id` varchar(50) NOT NULL,
  `delta_e` float NOT NULL,
  PRIMARY KEY (`calculation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
