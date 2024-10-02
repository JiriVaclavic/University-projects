#!/usr/bin/env python3

from datetime import datetime, date
from mongo_communicator import MongoUploader, MongoDownloader
import argparse


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="./connection_finder [ARGS]",
        description="Find all possible train connections.",
    )
    parser.add_argument("-f", "--from", help="From destination.", required=True)
    parser.add_argument("-t", "--to", help="To destination.", required=True)
    parser.add_argument("-d", "--day", help="Day in format 'yyyy-mm-dd'", required=True)
    return parser


if __name__ == "__main__":
    parser = init_argparse()
    args = vars(parser.parse_args())

    try:
        if args["day"] != datetime.strptime(args["day"], "%Y-%m-%d").strftime("%Y-%m-%d"):
            raise ValueError
    except ValueError:
        print("Day is not in valid format.")
        exit(1)

    mongo_uploader = MongoUploader()
    mongo_downloader = MongoDownloader()

    candidates = mongo_downloader.query_candidate_ptt(args["from"], args["to"])

    results = mongo_downloader.query_ptt_ids(args["from"], args["to"], args["day"], candidates)

    for res in results:

        print(res["_id"])
        x, y, z = "Stanice", "Příjezd", "Odjezd"
        print(f"{x:<30}{y:<30}{z:<30}")
        for loc in res["locations"]:
            station = loc["location_id"]
            arrival_time = loc["arrival_time"][:8] or "–"
            departure_time = loc["departure_time"][:8] or "–"
            print(f"{station:<30}{arrival_time:<30}{departure_time:<30}")

        print()
        print("-------------------------------------")
        print()
