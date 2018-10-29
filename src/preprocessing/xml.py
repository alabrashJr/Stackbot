from xml import etree
from xml.etree import ElementTree
import json
import csv

class StreamArray(list):
    """
    Converts a generator into a list object that can be json serializable
    while still retaining the iterative nature of a generator.

    It converts it to a list without having to exhaust the generator
    and keep it's contents in memory.
    """
    def __init__(self, generator):
        self.generator = generator
        self._len = 1

    def __iter__(self):
        self._len = 0
        for item in self.generator:
            yield item
            self._len += 1

    def __len__(self):
        """
        Json parser looks for a this method to confirm whether or not it can
        be parsed
        """
        return self._len

def attributes_to_dict(line):
    """Parses xml row into python dict"""
    try:
        parsed = etree.fromstring(line)
        ret = {}
        for key in parsed.keys():
            ret[key] = parsed.get(key)
    except(etree.XMLSyntaxError):
        print('Error encountered while trying to parse: ',line)
    return ret

def iterate_over_xml(xmlfile):
    """Iterates over xml files rows and yields dict of rows attributes"""
    doc = ElementTree.iterparse(xmlfile, events=('start', 'end'))
    _, root = next(doc)
    start_tag = None
    for event, element in doc:
        if event == 'start' and start_tag is None:
            start_tag = element.tag
        if event == 'end' and element.tag == start_tag:
            yield element.attrib
            start_tag = None
            root.clear()

def xml_to_json(xmlfile, jsonfile):
    """Converts xml files into json formatted files"""
    with open(jsonfile, 'w') as outfile:
        stream_array = StreamArray(iterate_over_xml(xmlfile))
        for chunk in json.JSONEncoder(indent='\t').iterencode(stream_array):
            outfile.write(chunk)

def xml_to_csv(xmlfile, outfile, list_of_headers):
    """Converts xml files into csv files with given headers"""
    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, dialect='excel', fieldnames=list_of_headers, restval='null', extrasaction='ignore')
        writer.writeheader()
        for row in iterate_over_xml(xmlfile):
            writer.writerow(row)
