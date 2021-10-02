import os
import requests
import ftplib as ftp
from urllib.request import urlopen
from xml.etree import ElementTree

# Weather functions:
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


# Data upload functions:
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
