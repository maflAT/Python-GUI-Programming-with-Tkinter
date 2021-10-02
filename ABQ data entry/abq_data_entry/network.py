from urllib.request import urlopen
from xml.etree import ElementTree


def get_local_weather(station: str):
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
