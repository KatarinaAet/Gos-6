import re
import difflib
import argparse
import yaml
import io

def templates_to_dict(templates_file):
    d = {}
    i = 0
    with open('{0}'.format(templates_file), 'r') as f:
        for line in f:
            (key, val) = (i, line)
            d[int(key)] = val
            i = i + 1

    return d

def prepare_templates_to_pattern_matching(templates_file_dict):
    d = {}
    for key in templates_file_dict.keys():
        result = re.sub(r'[А-Я]*_[А-Я]*', '.*?', templates_file_dict[key])
        d[key] = result
    return d

def serialize(filename, templates_file):
    d_templates = templates_to_dict(templates_file)
    d_regex = prepare_templates_to_pattern_matching(d_templates)
    d = {}
    list_input = []
    list_to_serialize = []
    textfile = open(filename, 'r')
    filetext = textfile.read()
    textfile.close()
    for key in d_regex.keys():
        matches = re.findall(d_regex[key], filetext)
        list_to_serialize = []
        for i in range(len(matches)):
            ans = split_str(matches[i], d_regex[key])
            list_to_serialize.append(ans)
        d[key] = list_to_serialize
    with io.open('data.yaml', 'w', encoding='utf8') as outfile:
        yaml.dump(d, outfile, default_flow_style=False, allow_unicode=True)
    # with open('serialize.txt', 'w') as file:
    #     file.write(str(d))

def split_str(matches, dict_regex):
    list_input = matches.split()
    list_reg = dict_regex.split()
    ans = []
    tup = []
    if (len(list_input) == len(list_reg)):
        tup = []
        for i in list_input:
            if i in list_input and i not in list_reg:
                tup.append(i)
    return tup

def deserialize(dict_errors, templates_file):
    result = ""
    with open("data.yaml", 'r') as stream:
        dict_errors = yaml.safe_load(stream)
    #json_data = json.loads(open("serialize.txt"))
    d_templates = templates_to_dict(templates_file)
    d_regex = prepare_templates_to_pattern_matching(d_templates)
    for key in dict_errors.keys():
        for i in range(len(dict_errors[key])):
            sub_reg = d_regex[key]
            for j in range(len(dict_errors[key][i])):
                sub_reg = sub_reg.replace(".*?", dict_errors[key][i][j], 1)
            result = result + sub_reg
    with open('deserialize.txt', 'w') as file:
        file.write(str(result))


def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Commands',
                                       description='Команды',
                                       help='Команды для работы с serializer/deserializer')
    serializer = subparsers.add_parser('serialize', help='сериализовать логи')
    serializer.add_argument('-logfile', metavar='logfile',
                             type=str, help='Директория для файла с логами')
    serializer.add_argument('-templatefile', metavar='templatefile',
                             type=str, help='Директория для файла с шаблонами')
    serializer.set_defaults(func=parse_ser)

    deserializer = subparsers.add_parser('deserialize', help='сериализовать логи')
    deserializer.add_argument('-logfile', metavar='logfile',
                             type=str, help='Директория для файла с логами')
    deserializer.add_argument('-templatefile', metavar='templatefile',
                             type=str, help='Директория для файла с шаблонами')
    deserializer.set_defaults(func=parse_deser)
    return parser

def parse_ser(args):
    serialize(args.logfile, args.templatefile)

def parse_deser(args):
    deserialize(args.logfile, args.templatefile)

parser = create_parser()

namespace = parser.parse_args()

if not vars(namespace):
    parser.print_usage()
else:
    namespace.func(namespace)