#!/usr/bin/env python3

from typing import TypedDict
from xml.dom.minidom import Element
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta


class Location(TypedDict):
    _id: str  # name
    country_code: str  # 2 chars
    location_primary_code: str  # 5 chars
    related_path_time_tables: list[str]


class CZPTTLocation(TypedDict):
    location_id: str  # name
    arrival_time: str  # hh:mm:ss
    arrival_offset: int
    departure_time: str  # hh:mm:ss
    departure_offset: int
    dwell_time: float
    responsible_ru: str
    responsible_im: str
    train_type: int
    traffic_type: int
    commercial_traffic_type: int
    train_activities: list[str]  # type of train (i.e. 0001 – (un)boarding of passengers)
    operational_train_number: int


class PathTimeTable(TypedDict):
    _id: str  # PA_ID + TR_ID (48 znaku)
    update_datetime: datetime
    locations: list[CZPTTLocation]
    start_date: str
    end_date: str
    days_calendar: dict
    network_specific_parameter: str


class CZPTTCISMessage(TypedDict):
    ptt: PathTimeTable
    locations: list[Location]


class CZCanceledPTTMessage(TypedDict):
    _id: str  # PA_ID + TR_ID (48 znaku)
    update_datetime: datetime
    days_calendar: dict


def create_date_seq(start: datetime | date, count: int) -> list[date]:
    """Return a list of dates.

    @param start
        First day of list.
    @param count
        Lenght of returned list.
    """
    date_series = [start + timedelta(days=x) for x in range(count)]

    if type(start) == datetime:
        return [d.date() for d in date_series]
    else:
        return date_series


def parse_transport_id(transport_id_tree: Element) -> str:
    """Create 24 char PATH or TRAIN id."""

    result = ""
    result += transport_id_tree.find("ObjectType").text
    result += transport_id_tree.find("Company").text
    result += transport_id_tree.find("Core").text
    result += transport_id_tree.find("Variant").text
    result += transport_id_tree.find("TimetableYear").text
    return result


def parse_identifier(identifiers_tree: Element) -> str:
    """Create 48 char id composed of PA and TR.

    @param identifiers_tree : Element
        The tree must have 2 children of type 'PlannedTransportIdentifiers'
    """

    planned_identifiers = identifiers_tree.findall("PlannedTransportIdentifiers")

    assert len(planned_identifiers) == 2, "Only 2 Planned Identifiers allowed"

    pa_id_tree, tr_id_tree = planned_identifiers

    return parse_transport_id(pa_id_tree) + parse_transport_id(tr_id_tree)


def parse_update_datetime(root: Element) -> datetime:
    """Parse message creation or cancellation datetime to update corresponding path time table."""

    if root.find("CZPTTCreation") is not None:
        update_time = root.find("CZPTTCreation").text
    elif root.find("CZPTTCancelation") is not None:
        update_time = root.find("CZPTTCancelation").text

    return datetime.fromisoformat(update_time)


def parse_days_calendar(calendar_tree: Element, CIS_message: bool = True) -> dict[date, bool]:
    """Parse of path time table's scheduled days of transport."""
    period = calendar_tree.find("ValidityPeriod")
    days_calendar = calendar_tree.find("BitmapDays").text

    start_datetime = datetime.fromisoformat(period.find("StartDateTime").text)

    date_seq = create_date_seq(start_datetime, len(days_calendar))

    if CIS_message:
        # True meaning that the time table is valid for the given day, False meaning otherwise
        days_calendar = {str(day): (True if bit == "1" else False) for day, bit in zip(date_seq, days_calendar)}
    else:
        # NOT of the original values for better update into the database
        # Now False means that the original time table day is invalid, True, that it stays as it was
        days_calendar = {str(day): (False if bit == "1" else True) for day, bit in zip(date_seq, days_calendar)}
    return days_calendar


class CZPTTCISMessageParser:
    def __init__(self) -> None:
        pass

    def parse_from_element(self, xml_root: Element) -> CZPTTCISMessage:
        self._root = xml_root

        # Unique path time table identifier
        self._path_time_table_id = parse_identifier(xml_root.find("Identifiers"))

        # Route's transport nodes
        self._locations = self._parse_locations()

        self._path_time_table = PathTimeTable(
            _id=self._path_time_table_id,
            update_datetime=parse_update_datetime(xml_root),
            locations=self._parse_CZPTTLocations(),
            start_date=self._parse_period_date(),
            end_date=self._parse_period_date(return_start_date=False),
            days_calendar=parse_days_calendar(xml_root.find("CZPTTInformation").find("PlannedCalendar")),
            network_specific_parameter=self._parse_network_specific_parameters(),
        )

        result = CZPTTCISMessage(ptt=self._path_time_table, locations=self._locations)
        return result

    def _parse_CZPTTLocations(self) -> list[CZPTTLocation]:
        CZPTTLocation_list = self._root.find("CZPTTInformation").findall("CZPTTLocation")
        result = []

        arrival_time = ""
        arrival_offset = ""
        departure_time = ""
        departure_offset = ""

        for czptt_location in CZPTTLocation_list:

            timing_at_location = czptt_location.find("TimingAtLocation")

            if timing_at_location is not None:
                timings = timing_at_location.findall("Timing")
                for timing in timings:
                    if timing.attrib["TimingQualifierCode"] == "ALA":
                        arrival_time = timing.find("Time").text
                        arrival_offset = int(timing.find("Offset").text)
                    elif timing.attrib["TimingQualifierCode"] == "ALD":
                        departure_time = timing.find("Time").text
                        departure_offset = int(timing.find("Offset").text)

            ta_list = []
            train_activities = czptt_location.find("TrainActivity")
            if train_activities is not None:
                for train_activity_type in train_activities:
                    ta_list.append(train_activity_type.text)

            dte = czptt_location.find("TimingAtLocation").find("DwellTime")
            rru = czptt_location.find("ResponsibleRU")
            rim = czptt_location.find("ResponsibleIM")
            tt = czptt_location.find("TrainType")
            ntt = czptt_location.find("TrafficType")
            ctt = czptt_location.find("CommercialTrafficType")
            otn = czptt_location.find("OperationalTrainNumber")

            result.append(
                CZPTTLocation(
                    location_id=czptt_location.find("Location").find("PrimaryLocationName").text,
                    arrival_time=arrival_time,
                    arrival_offset=arrival_offset,
                    departure_time=departure_time,
                    departure_offset=departure_offset,
                    dwell_time=dte.text if dte is not None else "",
                    responsible_ru=rru.text if rru is not None else "",
                    responsible_im=rim.text if rim is not None else "",
                    train_type=tt.text if tt is not None else "",
                    traffic_type=ntt.text if ntt is not None else "",
                    commercial_traffic_type=ctt.text if ctt is not None else "",
                    train_activities=ta_list,
                    operational_train_number=otn.text if otn is not None else "",
                )
            )
        return result

    def _parse_locations(self) -> list[Location]:
        """Parse of path time table's transport nodes."""
        CZPTTLocation_list = self._root.find("CZPTTInformation").findall("CZPTTLocation")
        result = []

        for CZPTTLocation in CZPTTLocation_list:
            location = CZPTTLocation.find("Location")

            location_name = location.find("PrimaryLocationName").text
            country_code = location.find("CountryCodeISO").text
            location_primary_code = location.find("LocationPrimaryCode").text

            result.append(
                Location(
                    _id=location_name,
                    country_code=country_code,
                    location_primary_code=location_primary_code,
                    related_path_time_tables=[self._path_time_table_id],
                )
            )
        return result

    def _parse_period_date(self, return_start_date: bool = True) -> str:
        """Parse of path time table's schedule start/end date."""
        information = self._root.find("CZPTTInformation")
        calendar = information.find("PlannedCalendar")
        period = calendar.find("ValidityPeriod")

        if return_start_date:
            return str(datetime.fromisoformat(period.find("StartDateTime").text).date())
        else:
            return str(datetime.fromisoformat(period.find("EndDateTime").text).date())

    def _parse_network_specific_parameters(self) -> dict:
        """Parse of path time table's additional network specific parameters."""
        network_info_list = self._root.findall("NetworkSpecificParameter")
        result = []

        for info in network_info_list:
            net_info = {i.tag: i.text for i in info}
            result.append(net_info)

        return result


class CZCanceledPTTMessageParser:
    def __init__(self) -> None:
        pass

    def parse_from_element(self, xml_root: Element) -> CZCanceledPTTMessage:
        self._root = xml_root

        # Unique path time table identifier
        self._path_time_table_id = parse_identifier(xml_root)

        self._update_datetime = parse_update_datetime(xml_root)

        self._days_calendar = parse_days_calendar(xml_root.find("PlannedCalendar"), CIS_message=False)

        result = CZCanceledPTTMessage(
            _id=self._path_time_table_id,
            update_datetime=self._update_datetime,
            days_calendar=self._days_calendar,
        )

        return result
