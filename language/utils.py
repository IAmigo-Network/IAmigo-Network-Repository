from pathlib import Path
from os import getcwd
import configparser
import xmltodict

def load_language():

    config_path = Path(__file__) / "data" / "config.ini"
    config = configparser.ConfigParser()
    config.read(str(config_path))

    xml_path = Path(getcwd()) / "language" / "language_xml" / config['localization']['language']
    print(xml_path)

    with open(xml_path, 'r', encoding='utf-8') as xml_file:
        xml_content = xml_file.read()
        
    strings = xmltodict.parse(xml_content)
    strings = strings["IAmigo"]
    return strings

strings = load_language()
print(strings)