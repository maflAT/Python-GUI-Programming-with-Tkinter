import os
import requests
import ftplib as ftp
from typing import NamedTuple
from urllib.request import urlopen
from xml.etree import ElementTree
from threading import Thread
from queue import Queue


class Message(NamedTuple):
    """Communication protocol from REST Uploader to Application."""

    status: str
    subject: str
    body: str


#####################
# Weather functions #
#####################


def get_local_weather(station: str) -> dict[str, str]:
    """Retrieve weather data for `station` from weather.gov."""

    url = f"http://w1.weather.gov/xml/current_obs/{station}.xml"
    response = urlopen(url)
    xmlroot = ElementTree.fromstring(response.read())
    weatherdata: dict[str, str] = {
        "observation_time_rfc822": None,
        "temp_c": None,
        "relative_humidity": None,
        "pressure_mb": None,
        "weather": None,
    }
    for tag in weatherdata:
        element = xmlroot.find(tag)
        if element is not None:
            weatherdata[tag] = element.text
    return weatherdata


#########################
# Data upload functions #
#########################


def upload_to_corporate_rest(
    filepath: str, upload_url: str, auth_url: str, username: str, password: str
):
    """Upload data using http requests."""
    session = requests.session()
    response = session.post(auth_url, data={"username": username, "password": password})
    response.raise_for_status()

    files = {"file": open(filepath, "rb")}
    response = session.put(upload_url, files=files)
    files["file"].close()
    response.raise_for_status()


def upload_to_corporate_ftp(
    filepath: str, ftp_host: str, ftp_port: int, ftp_user: str, ftp_pass: str
):
    with ftp.FTP() as ftp_cx:
        ftp_cx.connect(host=ftp_host, port=ftp_port)
        ftp_cx.login(user=ftp_user, passwd=ftp_pass)
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as fh:
            ftp_cx.storbinary(f"STOR {filename}", fh)


class CorporateRestUploaderWithQueue(Thread):
    def __init__(
        self,
        filepath: str,
        upload_url: str,
        auth_url: str,
        username: str,
        password: str,
        queue: Queue,
    ):
        super().__init__()
        self.filepath = filepath
        self.upload_url = upload_url
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.queue = queue

    def run(self, *args, **kwargs) -> None:
        session = requests.session()

        # Authentication
        self._putmessage(
            status="info",
            subject="Authenticating",
            body=f"Authentication to {self.auth_url} as {self.username}",
        )
        try:
            response = session.post(
                url=self.auth_url,
                data={"username": self.username, "password": self.password},
            )
            response.raise_for_status()
        except Exception as e:
            self._putmessage(
                status="error", subject="Authentication Failure", body=str(e)
            )
            return

        # Upload
        files = {"file": open(self.filepath, "rb")}
        self._putmessage(
            status="info",
            subject="Starting Upload",
            body=f"Staring Upload of {self.filepath} to {self.upload_url}",
        )
        try:
            response = session.put(url=self.upload_url, files=files)
            files["file"].close()
            response.raise_for_status()
        except Exception as e:
            self._putmessage(status="error", subject="Upload Failure", body=str(e))
            return
        self._putmessage(
            status="done",
            subject="Complete",
            body=f"File {self.filepath} successfully uploaded to ABQ REST interface",
        )

    def _putmessage(self, status: str, subject: str, body: str):
        self.queue.put(Message(status, subject, body))
