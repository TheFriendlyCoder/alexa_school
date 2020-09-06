import logging
import requests
import pandas as pd

WEB_URL = "https://francophonesud.nbed.nb.ca/retards-et-fermetures"
SCHEDULE_URL = "https://bp.nbed.nb.ca/notices/BPRFtbl.aspx?dst=dsfs&amp;vtbl=1"


class School:
    """Abstraction around school-specific data parsed from the school
    district's website"""
    SCHOOL_FIELD = "Nom de l'école"
    OPEN_FIELD = "École"
    BUS_FIELD = "Autobus"
    MESSAGE_FIELD = "Messages"

    def __init__(self, df):
        """
        Args:
            df: Panda's dataframe containing school data parsed from the website
        """
        self._df = df

    def __str__(self):
        return self._df.to_markdown()

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        """str: name of the school"""
        return self._df[self.SCHOOL_FIELD]

    @property
    def messages(self):
        """str: status messages associated with the school"""
        return self._df[self.MESSAGE_FIELD]

    @property
    def is_open(self):
        """bool: True if school is open, False if not"""
        return self._df[School.OPEN_FIELD] == "Ouvert"

    @property
    def has_late_busses(self):
        """bool: True if 1 or more buses are late, False if all are running
        on time"""
        return self._df[School.BUS_FIELD] != "À l’heure"


class District:
    """Abstraction around school district data parsed from the district website
    """
    DISTRICT_FIELD = "Région"

    def __init__(self, df):
        """
        Args:
            df: Pandas data frame describing the district
        """
        self._df = df

    def __str__(self):
        return self._df.to_markdown()

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        """str: Name of the district"""
        # NOTE: Some districts have the same name but in different character
        #       casing so we just return a lower-cased representation
        temp = self._df[self.DISTRICT_FIELD].str.lower().unique()
        assert len(temp) == 1
        return temp[0]

    @property
    def schools(self):
        """list (School): 1 or more schools associated with this district"""
        return [School(df[1]) for df in self._df.iterrows()]

    @property
    def school_names(self):
        """list (str): list of school names associated with this district"""
        retval = list()
        for cur_school in self.schools:
            retval.append(cur_school.name)
        return retval

    def get_school(self, name):
        """Gets a specific school from the district

        Args:
            name (str):
                name of the school to get data for

        Returns:
            School:
                reference to the school with the given name, or None if no
                such school exists
        """
        for cur_school in self.schools:
            if cur_school.name.lower() == name.lower():
                return cur_school
        return None


class ScheduleParser:
    """Interface for parsing HTML data loaded from the school district website
    """
    def __init__(self, html):
        """
        Args:
            html (str):
                HTML data loaded from the website. Is expected to contain a
                single HTML table containing rows describing each school in
                each school district
        """
        assert ScheduleParser.validate(html)

        temp = pd.read_html(
            html, header=0, converters={School.MESSAGE_FIELD: str})

        self._data = temp[0]
        self._data.fillna("", inplace=True)

    def __str__(self):
        return self._data.to_markdown()

    @staticmethod
    def validate(html):
        """Checks to see if HTML loaded from the website is parseable

        Args:
            html (str):
                HTML data loaded from the district website

        Returns:
            bool:
                True if the HTML content was parseable, False if not. Details
                of any parsing errors are reported to the logger.
        """
        log = logging.getLogger(__name__)
        temp = pd.read_html(
            html, header=0, converters={School.MESSAGE_FIELD: str})
        if len(temp) == 0:
            log.error("No HTML tables found in input data")
            return False
        if len(temp) > 1:
            log.error(f"Expected 1 HTML table in the source data but "
                      f"found {len(temp)} instead")
            return False
        data = temp[0]
        data.fillna("", inplace=True)

        log.debug("Parsed HTML data table:")
        log.debug(data.to_markdown())

        school_names = list()
        for cur_school in data[School.SCHOOL_FIELD]:
            if cur_school == "":
                log.error("Detected row with no valid school name")
                return False

            if cur_school in school_names:
                log.error(f"Multiple schools with the same name "
                          f"detected: {cur_school}")
                return False
            school_names.append(cur_school)

        return True

    @property
    def districts(self):
        """list (District): 0 or more districts parsed from the HTML content"""
        unique_names = self._data[District.DISTRICT_FIELD].str.lower().unique()
        retval = list()
        for cur_name in unique_names:
            rows = self._data[self._data[District.DISTRICT_FIELD].str.lower() == cur_name]
            retval.append(District(rows))
        return retval

    def get_district(self, name):
        """Gets a specific district from the HTML content

        Args:
            name (str):
                the name of the district to locate

        Returns:
            District:
                Reference to the district details for the named district, or
                None if no district with the given name exists
        """
        for cur_district in self.districts:
            if cur_district.name.lower() == name.lower():
                return cur_district
        return None

    @property
    def district_names(self):
        """list (str): list of names of all districts parsed from the HTML"""
        retval = list()
        for cur_district in self.districts:
            retval.append(cur_district.name)
        return retval

    @property
    def school_names(self):
        """list (str): list of unique names of all schools in all districts"""
        retval = list()
        for cur_district in self.districts:
            for cur_school in cur_district.schools:
                retval.append(cur_school.name)
        return retval


if __name__ == "__main__":  # pragma: no cover
    text = requests.get(SCHEDULE_URL).text
    print(ScheduleParser.validate(text))
    obj = ScheduleParser(text)
