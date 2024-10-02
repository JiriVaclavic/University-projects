#!/usr/bin/env python3

from abc import ABC
from pymongo import MongoClient, errors
from message_parser import CZPTTCISMessage, CZCanceledPTTMessage
from configparser import ConfigParser


class MongoCommunicator(ABC):
    def __init__(self) -> None:
        self._PTT = "path_time_tables"  # collection name
        self._LOC = "locations"  # collection name

        config_object = ConfigParser()
        try:
            config_object.read("static/config.ini")
            connection_string = config_object["DATABASE"]["connection_string"]
            db_name = config_object["DATABASE"]["db_name"]

            self._db = MongoClient(connection_string)[db_name]
        except errors.ConnectionFailure:
            print("Nepodarilo se pripojit k databazi")
            exit(12)

    @property
    def db(self):
        """In case a direct use of database id needed."""
        return self._db

    @db.setter
    def db(self):
        pass


class MongoUploader(MongoCommunicator):
    def __init__(self) -> None:
        super().__init__()

    def create_record(self, cis_msg: CZPTTCISMessage) -> None:
        """Addition of new records into the database.

        @param cis_msg : CZPTTCISMessage
            Dict containing CIS ptt message info.
        """

        try:
            self._db[self._PTT].insert_one(cis_msg["ptt"])
        except errors.DuplicateKeyError:
            print("Duplicitni zaznam PTT, zaznam nebyl vlozen.")
            return

        # Add locations to locations collection if it not yet exists
        for loc in cis_msg["locations"]:
            self._db[self._LOC].update_one(
                filter={"_id": loc["_id"]},
                update={
                    "$setOnInsert": {
                        "country_code": loc["country_code"],
                        "location_primary_code": loc["location_primary_code"],
                    },
                    "$addToSet": {
                        "related_path_time_tables": {
                            "$each": loc["related_path_time_tables"],
                        },
                    },
                },
                upsert=True,
            )

    def update_record(self, ptt: CZCanceledPTTMessage) -> None:
        """Update of traversal calendar of corresponding CIS path time table record in the database.

        @param ptt : CZCanceledPTTMessage
            Dict containing canceled ptt message info.
        """
        document = self._db[self._PTT].find_one({"_id": ptt["_id"]})

        # print("--updatuje--")

        if document is not None:
            for day, bit in ptt["days_calendar"].items():
                document["days_calendar"][day] = bit and document["days_calendar"][day]

            # Update datetime of ptt
            self._db[self._PTT].update_one(
                {"$and": [{"_id": ptt["_id"]}, {"update_datetime": {"$lte": ptt["update_datetime"]}}]},
                {"$set": {"update_datetime": ptt["update_datetime"]}},
                upsert=False,
            )

            # Update ptt calendar days
            self._db[self._PTT].update_one(
                {"_id": ptt["_id"]},
                {"$set": {"days_calendar": document["days_calendar"]}},
                upsert=False,
            )


class MongoDownloader(MongoCommunicator):
    def __init__(self) -> None:
        super().__init__()

    def query_candidate_ptt(self, from_location: str, to_location: str) -> list[str]:
        """Returns a list of path time table ids, that contain both specified locations.

        @returns : list[str]
            List of path_time_table ids.
        """
        query_from = {"_id": from_location}
        query_to = {"_id": to_location}

        from_record = self.db[self._LOC].find_one(query_from)
        to_record = self.db[self._LOC].find_one(query_to)

        if from_record is None:
            print(f"Nenalezena lokalita: '{from_location}'")
            return []

        if to_record is None:
            print(f"Nenalezena lokalita: '{to_location}'")
            return []

        # intersect
        return list(set(from_record["related_path_time_tables"]) & set(to_record["related_path_time_tables"]))

    def query_ptt_ids(self, from_location, to_location, day, ptt_ids: list[str]):
        ptt_records = self.db[self._PTT].find({"_id": {"$in": ptt_ids}})

        list_of_results = []

        for rec in ptt_records:
            # First check whether the train leaves the starting point for the given day
            if day in rec["days_calendar"]:
                if not rec["days_calendar"][day]:
                    continue
            else:
                continue

            from_idx, from_info = self._get_location_info(from_location, rec["locations"])
            to_idx, to_info = self._get_location_info(to_location, rec["locations"])

            # Second check that the start location precedes the end location in the ptt's route
            if from_idx >= to_idx:
                continue

            # Third check that both of the locations contain train activity type 0001 (the train stops at the given location)
            if "0001" not in from_info["train_activities"] or "0001" not in to_info["train_activities"]:
                continue

            list_of_results.append(rec)

        return list_of_results

    def _get_location_info(self, location_id: str, location_list: list[dict]) -> tuple[int, dict]:
        """Return index and info of location.

        @param location_id : str
            Location name.

        @param location_list : list[dict]
            List of locations as retrieved from db.

        @returns : tuple[int, dict]
            int -> Index of location in list.
            dict -> Location info.
        """
        try:
            return next((idx, d) for (idx, d) in enumerate(location_list) if d["location_id"] == location_id)
        except StopIteration:
            print("Tohle by nemelo nikdy nastat! Prosim kontaktujte spravce kodu.")
            exit(1)
