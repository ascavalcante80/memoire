import pymysql
from ner.rule import Rule
from ner.potential_ne import PotentialNE

__author__ = 'alexandre s. cavalcante'


class MySQLConnector:

    def __init__(self, database, password, user, host='localhost', port=3306, charset="utf8"):

        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.charset = charset

        self.__conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.password,
                                      db=self.database, charset=self.charset, use_unicode=True, autocommit=True)

        # self.__conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='20060907jl', db=self.database_name,  charset="utf8", use_unicode=True, autocommit=True)

    def rebuild_db(self):
        try:
            try:
                query = """
       -- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema memoire
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `memoire` ;

-- -----------------------------------------------------
-- Schema memoire
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `memoire` DEFAULT CHARACTER SET utf8 ;
USE `memoire` ;

-- -----------------------------------------------------
-- Table `memoire`.`rules`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `memoire`.`rules` ;

CREATE TABLE IF NOT EXISTS `memoire`.`rules` (
  `idrules` INT NOT NULL AUTO_INCREMENT,
  `surface` VARCHAR(1000) NOT NULL,
  `orientation` VARCHAR(1) NOT NULL,
  `full_sentence` VARCHAR(1000) NULL,
  `treated` TINYINT(1) NULL DEFAULT 0,
  `lemmas` VARCHAR(1000) NULL,
  `POS` VARCHAR(45) NULL,
  `frequency` INT NULL DEFAULT 0,
  PRIMARY KEY (`idrules`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `memoire`.`potential_ne`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `memoire`.`potential_ne` ;

CREATE TABLE IF NOT EXISTS `memoire`.`potential_ne` (
  `idpotential_ne` INT NOT NULL AUTO_INCREMENT,
  `surface` VARCHAR(500) NOT NULL,
  `type` VARCHAR(1) NOT NULL,
  `treated` TINYINT(1) NULL DEFAULT 0,
  `frequency` INT NULL DEFAULT 0,
  PRIMARY KEY (`idpotential_ne`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `memoire`.`potential_ne_has_rules`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `memoire`.`potential_ne_has_rules` ;

CREATE TABLE IF NOT EXISTS `memoire`.`potential_ne_has_rules` (
  `potential_ne_idpotential_ne` INT NOT NULL,
  `rules_idrules` INT NOT NULL,
  PRIMARY KEY (`potential_ne_idpotential_ne`, `rules_idrules`),
  INDEX `fk_potential_ne_has_rules_rules1_idx` (`rules_idrules` ASC),
  INDEX `fk_potential_ne_has_rules_potential_ne_idx` (`potential_ne_idpotential_ne` ASC),
  CONSTRAINT `fk_potential_ne_has_rules_potential_ne`
    FOREIGN KEY (`potential_ne_idpotential_ne`)
    REFERENCES `memoire`.`potential_ne` (`idpotential_ne`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_potential_ne_has_rules_rules1`
    FOREIGN KEY (`rules_idrules`)
    REFERENCES `memoire`.`rules` (`idrules`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

                """

                cur = self.__get_connection()
                cur.execute(query)
                cur.close()
                return True

            except pymysql.err.MySQLError:
                cur.close()
                # todo insert logger
                return False
        except Exception:
            # todo insert logger
            return False

    def insert_rule(self, rule):
        """
        insert the data from the object rule in the database. It return the idrules, if the rules was correctly
        inserted. Otherwise, it returns -1.
        :param rule: instance of Rule
        :return: int idrules
        """
        try:
            # variable to hold the object connection
            cur = None

            if not isinstance(rule, Rule) or rule is None:
                return -1

            # check if the rule has already been inserted in the database
            rule_result = self.get_rule_where(['orientation', 'surface'], [rule.orientation, rule.surface])

            if len(rule_result) > 0:
                # rule already in the DB, return its idpotential_ne
                return rule_result[0].idrules

            if len(rule.POS) == 0 or len(rule.lemmas) == 0:
                return -1
                # todo insert logger

            POS = "<sep>".join(rule.POS)
            lemmas = "<sep>".join(rule.lemmas)

            try:
                cur = self.__get_connection()

                query = "INSERT INTO `" + self.database + "`.`rules` (`surface`, `orientation`,`full_sentence`, " \
                                                          "`lemmas`, `POS`, `treated`) VALUES ('" \
                        + pymysql.escape_string(rule.surface) + "', '" + pymysql.escape_string(rule.orientation) \
                        + "', '" + pymysql.escape_string(rule.full_sentence) + "', '" + pymysql.escape_string(lemmas)\
                        + "', '" + pymysql.escape_string(POS) + "', '" + str(rule.treated) + "');"

                cur.execute(query)

            except pymysql.err.IntegrityError:
                # todo insert logger
                cur.close()
                return -1

            # inserted worked, get idpotential_ne and return it
            rule_id = cur.lastrowid
            cur.close()
            return rule_id

        except Exception:
            return -1
            # todo insert logger

    def insert_potential_ne(self, potential_ne):
        """
        inserts an object PotentialNE in the database and return its idpotential_ne, if the object was correctly
        inserted. Otherwise, it returns -1.
        :param potential_ne: object PotentialNE
        :return: int idpotential_ne
        """
        try:
            # variable to hold the object connection
            cur = None

            if not isinstance(potential_ne, PotentialNE) or potential_ne.surface is None:
                return -1

            pot_ne_result = self.get_potential_ne_where('surface', potential_ne.surface)

            if len(pot_ne_result) == 1:
                return pot_ne_result[0].idpotential_ne

            try:
                cur = self.__get_connection()
                query = "INSERT INTO `" + self.database + "`.`potential_ne` (`surface`, `frequency`, `treated`, `type`) VALUES ('" \
                        + pymysql.escape_string(potential_ne.surface) + "', '" + str(potential_ne.frequency) + "', '" \
                        + str(potential_ne.treated) + "', '" + potential_ne.ne_type + "');"
                cur.execute(query)

            except pymysql.err.IntegrityError:
                # todo insert logger
                cur.close()
                return -1

            # get idpotential_ne for the item just inserted
            potential_NE_id = cur.lastrowid
            cur.close()
            return potential_NE_id
        except Exception:
            # todo insert logger
            return -1

    def insert_relation_ne_rule(self, idrules, idpotential_ne):
        """
        insert the relation rule has potential_ne in the database. It return True if the relation was correctly
        inserted, and False otherwise.
        :param idrules: int
        :param idpotential_ne: int
        :return: boolean
        """

        try:
            cur = None

            if idrules is None or idpotential_ne is None or not isinstance(idrules, int) \
                    or not isinstance(idpotential_ne, int):
                return -1
            try:
                cur = self.__get_connection()

                query = 'INSERT INTO `' + self.database + '`.`potential_ne_has_rules` ' \
                                                            '(`potential_ne_idpotential_ne`, `rules_idrules`) VALUES ' \
                                                            '(' + str(idpotential_ne) + ', ' + str(idrules) + ');'
                cur.execute(query.replace("'", "''"))
                cur.close()
                return True

            except pymysql.err.IntegrityError:
                # todo insert logger
                cur.close()
                return False

        except Exception:
            # todo insert logger
            return False

    def get_rule_where(self, fields, values):
        """
        get an rules object respecting the condition passed using the field and the value passed as parameter. It
        return a list of rules.

        :param fields:
        :param values:
        :return:
        """
        if len(fields) != len(values):
            # todo insert logger
            return [] # error

        cur = None

        # build query
        query_fields = ""
        for index, field in enumerate(fields):

            # check if the value is string or int
            if isinstance(values[index], str):
                value = "'" + values[index] + "'"
            elif isinstance(values[index], int):
                value = str(values[index])

            query_fields += " rules." + field + "=" + value + " AND "

        # eliminate trailing AND
        if query_fields.endswith(" AND "):
            query_fields = query_fields[:-5]

        try:
            try:
                cur = self.__get_connection()
                cur.execute("SELECT * FROM " + self.database + ".rules WHERE " + query_fields + ";")

                # read result
                list_rules = self.__read_rules_result(cur._rows)

                return list_rules

            except pymysql.err.IntegrityError:
                cur.close()
                return []


        except Exception:
            # todo insert logger
            return []

    def get_potential_ne_where(self, field, value):
        """
        get an potential_ne object respecting the condition passed using the field and the value passed as parameter. It
        return a list of potential_ne.

        :param field:
        :param value:
        :return:
        """
        cur = None

        try:
            try:
                cur = self.__get_connection()

                if isinstance(value, str):
                    query = "SELECT * FROM " + self.database + ".potential_ne WHERE potential_ne." \
                            + pymysql.escape_string(field) + "='" + pymysql.escape_string(value) + "';"

                elif isinstance(value, int):
                    query = "SELECT * FROM " + self.database + ".potential_ne WHERE potential_ne." \
                            + pymysql.escape_string(field) + "=" + str(value) + ";"

                cur.execute(query)

                list_potential_ne = self.__read_potential_result(cur._rows)
                cur.close()

                return list_potential_ne

            except pymysql.err.IntegrityError:
                cur.close()
                return []

        except Exception:
            # todo insert logger
            return []

    def get_all_elements(self, table):
        try:
            cur= None
            result = []

            try:
                cur = self.__get_connection()
                cur.execute("SELECT * from " + self.database + "." + table + ";")

                if table == 'rules':
                    result = self.__read_rules_result(cur._rows)
                elif table == 'potential_ne':
                    result = self.__read_potential_result(cur._rows)

                cur.close()
                return result

            except pymysql.err.IntegrityError:
                cur.close()
                return False

        except Exception:
            return False

    def updated_potential_ne(self, potential_ne):

        try:

            if potential_ne is None and not isinstance(potential_ne, PotentialNE):
                return False

            if potential_ne.idpotential_ne == -1:

                pot_ne_result = self.get_potential_ne_where('surface', potential_ne.surface)

                if len(pot_ne_result) == 1:
                    potential_ne.idpotential_ne = pot_ne_result[0].idpotential_ne

            try:
                cur = self.__get_connection()
                query = "UPDATE `" + self.database + "`.`potential_ne` SET `surface`='"\
                        + pymysql.escape_string(potential_ne.surface) + "', `type`='" + potential_ne.ne_type +\
                        "', `treated`=" + str(potential_ne.treated) + ", `frequency`=" + str(potential_ne.frequency)\
                        + " WHERE `idpotential_ne`=" + str(potential_ne.idpotential_ne) + ";"

                cur.execute(query)

            except pymysql.err.IntegrityError:
                cur.close()
                return False

            cur.close()
            return True
        except Exception:
            return False

    def __read_rules_result(self, rows):

        list_rules = []
        for row in rows:
            rule = Rule(row[1], row[2], row[3], row[4], None)
            rule.idrules = row[0]
            rule.lemmas = row[5]
            rule.POS = row[6]
            list_rules.append(rule)

        return list_rules

    def __read_potential_result(self, rows):
        list_potential_ne = []
        for row in rows:
            potential_ne = PotentialNE(row[1], row[2])
            potential_ne.idpotential_ne = row[0]
            potential_ne.frequency = row[3]

            list_potential_ne.append(potential_ne)

        return list_potential_ne

    def __get_connection(self):
        """
        get an object conn to connect to the database.
        :return:
        """
        try:
            cur = self.__conn.cursor()
            cur.execute("use " + self.database + ";")

            return cur

        except pymysql.err.IntegrityError:
            return None
