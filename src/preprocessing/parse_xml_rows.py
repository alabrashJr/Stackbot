from parsing import xml_to_json, xml_to_csv
import argparse
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process given xml file into given format')
    parser.add_argument('-i', '--input-file', required=True,
                        help='Path of the file to be processed')
    parser.add_argument('-o', '--output-file', default='processed.json',
                        help='Path of the file to be written to')
    parser.add_argument('-f', '--output-format', default='csv', choices=['csv','json'],
                        help='Processing format')
    parser.add_argument('-c', '--csv-columns', nargs='+',
                        help='List of csv headers')
    args = vars(parser.parse_args())

    if args['output_format'] == 'csv' and args['csv_columns'] is None:
        print('Error: Missing arguments, you should give at least one column header for csv\nPlease see: python process_xml_rows.py -h', file=sys.stderr)
        sys.exit(1)

    print('starting processing:', args['input_file'], 'as', args['output_format'], 'file')

    if args['output_format'] == 'json':
        xml_to_json(args['input_file'], args['output_file'])
    elif args['output_format'] == 'csv':
        xml_to_csv(args['input_file'], args['output_file'], args['csv_columns'])
