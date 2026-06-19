from pathlib import Path
import configparser
import xmltodict

def load_language():
    config_path = Path(__file__).parent.parent / "data" / "config.ini"
    config = configparser.ConfigParser()
    config.read(str(config_path), "utf-8")
    print(config["a"]["b"])

    xml_path = Path(__file__).parent / "language_xml" / config["a"]["b"]
    print(str(xml_path))

    with open(xml_path, 'r', encoding='utf-8') as xml_file:
        xml_content = xml_file.read()

    strings = xmltodict.parse(xml_content)
    strings = strings["IAmigo"]
    return strings