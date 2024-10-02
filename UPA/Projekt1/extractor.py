#!/usr/bin/env python3

import os
import time
import gzip
import zipfile
import xml.etree.ElementTree as ET
from xml.dom.minidom import Element
from subprocess import call, run, PIPE
from mongo_communicator import MongoUploader
from message_parser import CZPTTCISMessageParser, CZCanceledPTTMessageParser


class Extractor:
    # Setting instance variables
    ############################
    def __init__(
        self,
        dir_path: str = f"{os.getcwd()}/downloaded_data",
    ) -> None:
        self._zip_files = []
        self._CIS = CZPTTCISMessageParser()
        self._Canceled = CZCanceledPTTMessageParser()
        self._MongoUploader = MongoUploader()

        for root, _, files in os.walk(dir_path):
            for name in files:
                self._zip_files.append(os.path.join(root, name))

    # Extracting individual compressed files, processing them in-memory and uploading them to database
    ##################################################################################################
    def extract_and_upload_xmls(self, measure_time: bool = False) -> None:
        if measure_time:
            timer_start = time.time()

        for zfile in self._zip_files:
            zfile_compression_type = run(["file", zfile], stdout=PIPE, stderr=PIPE, universal_newlines=True)

            # Use zipfile to extract
            if "Zip archive" in zfile_compression_type.stdout:
                with zipfile.ZipFile(zfile, "r") as z:
                    for f in z.filelist:
                        xml_content = z.read(f)

                        root = ET.fromstring(xml_content)
                        self._upload_xml(message_type=root.tag, xml_element_tree=root)

            # Use gzip to extract
            elif "gzip compressed" in zfile_compression_type.stdout:
                with gzip.open(zfile, "r") as f:
                    xml_content = f.read()

                    root = ET.fromstring(xml_content)
                    self._upload_xml(message_type=root.tag, xml_element_tree=root)

        if measure_time:
            total_time = time.time() - timer_start
            print(f"Total time: {time.strftime('%H:%M:%S', time.gmtime(total_time))}")

    # Pre-parse and upload of xml data file into database
    #####################################################
    def _upload_xml(self, message_type: str, xml_element_tree: Element):
        if message_type == "CZPTTCISMessage":
            msg = self._CIS.parse_from_element(xml_element_tree)
            self._MongoUploader.create_record(msg)

        elif message_type == "CZCanceledPTTMessage":
            msg = self._Canceled.parse_from_element(xml_element_tree)
            self._MongoUploader.update_record(msg)


if __name__ == "__main__":
    Extractor().extract_and_upload_xmls(measure_time=True)
