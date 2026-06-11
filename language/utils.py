import xmltodict

def load_language():
    
    xml_path = r'C:\Users\davi56961306\Desktop\IAmigo\language\PT-BR.xml'

    with open(xml_path, 'r', encoding='utf-8') as xml_file:
        xml_content = xml_file.read()
        
    strings = xmltodict.parse(xml_content)
    strings = strings["IAmigo"]
    return strings

print(load_language())