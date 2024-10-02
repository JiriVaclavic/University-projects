#!/usr/bin/env python3


import requests
import http.cookiejar
import os
from bs4 import BeautifulSoup
import time


class DataDownloader:
    # Setting instance variables
    ############################
    def __init__(
        self,
        year: str = "2022",
        url: str = "https://portal.cisjr.cz/pub/draha/celostatni/szdc/",
        folder: str = "downloaded_data",
    ) -> None:
        self.url = "{}{}/".format(url, year)
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.year = int(year)
        self.folder = os.path.join(os.getcwd(), folder)

    # Downloading all data files (*.zip) into folder
    ################################################
    def download_data(self, measure_time: bool = False, verbose: bool = False, force_download: bool = False) -> None:
        if measure_time:
            timer_start = time.time()

        UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
        with requests.session() as s:
            s.cookies = http.cookiejar.LWPCookieJar("cisjr_data.txt")
            s.headers.update({"User-Agent": UA})

            req = s.get(self.url, allow_redirects=True)

            prefixes = [str(self.year), str(self.year - 1)]
            soup = BeautifulSoup(req.text, "html.parser").find_all(
                lambda href: href.name == "a" and (href.text.startswith(tuple(prefixes)) or href.text.endswith(".zip"))
            )

            hrefs = [a["href"] for a in soup]
            # replacing all the month href redirects with hrefs of their individual respective data records hrefs (xml.zip hrefs)
            month_hrefs = [os.path.basename(a[:-1]) for a in hrefs if not (a.endswith(".zip"))]
            month_reqs = [requests.get(self.url + href + "/", allow_redirects=True) for href in month_hrefs]
            month_soups = [BeautifulSoup(req.text, "html.parser").find("pre") for req in month_reqs]
            month_soups = [s.find_all("a", href=lambda h: h and h.endswith(".zip")) for s in month_soups]
            month_data_hrefs = [[a["href"] for a in soup] for soup in month_soups]

            # merging all of the individual zip hrefs into one list to procceed with the downloading
            zip_hrefs = [href for month in month_data_hrefs for href in month]
            zip_hrefs.extend([h for h in hrefs if (h.endswith(".zip"))])

            # counter of downloaded zip_files used for verbose flag
            cnt = 0

            # getting urls for .zip files to download them
            for zip_href in zip_hrefs:
                cnt += 1
                trimmed_url = self.url.replace("https://portal.cisjr.cz", "")
                zip_href = zip_href.replace(trimmed_url, "")
                zip_path = os.path.join(self.folder, zip_href)

                # create appropriate folder for individual months if it does not already exist
                zip_folder = os.path.join(self.folder, os.path.dirname(zip_href))
                if not os.path.exists(zip_folder):
                    os.makedirs(zip_folder)

                # if file has not been downloaded yet (or is forced), it will be downloaded from specified url and saved to folder
                if force_download or not os.path.exists(zip_path):
                    zip_file = s.get(self.url + zip_href, stream=True)
                    with open(zip_path, "wb") as fd:
                        for chunk in zip_file.iter_content(chunk_size=128):
                            fd.write(chunk)
        if verbose:
            print(f"Downloaded {cnt} zip files.")

        if measure_time:
            total_time = time.time() - timer_start
            print("Total download time:", time.strftime("%H:%M:%S", time.gmtime(total_time)))


if __name__ == "__main__":
    downloader = DataDownloader()
    downloader.download_data(measure_time=True, verbose=True)
