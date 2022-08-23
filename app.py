import requests
import locale

from parser_settings import links

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class MyParser:
    def __init__(self, links):

        self.__links = links
        self.__link = None

        self.__code_of_index = None
        self.__content = str()
        self.__indexes = None
        self.__data = {}
        self.__names_and_codes = {}

        self.__current_data_index = None

        self.refresh_data()

    def _get_text(self):
        response = requests.get(self.__link)
        content = response.text
        self.__content += content

    def _get_indexes_for_parsing(self):
        start_ind = self.__content.find(self.__code_of_index)

        val = "PERCENT OF OPEN INTEREST"
        end_ind = self.__content.find(val, start_ind)

        start_ind += len(self.__code_of_index)
        self.__indexes = (start_ind, end_ind)

    def _parse_content(self):
        curr_content = self.__content[self.__indexes[0]:self.__indexes[1]]

        data_list = curr_content.split('\n')

        values = [i.strip() for i in data_list[9].split(' ') if i]
        self.__data['NON-COMMERCIAL-LONG'] = values[0]
        self.__data['NON-COMMERCIAL-Short'] = values[1]
        self.__data['NON-COMMERCIAL-SPREADS'] = values[2]
        self.__data['COMMERCIAL-LONG'] = values[3]
        self.__data['COMMERCIAL-SHORT'] = values[4]
        self.__data['TOTAL-LONG'] = values[5]
        self.__data['TOTAL-SHORT'] = values[6]

        values = [i.strip() for i in data_list[11].split(' ') if i]
        self.__data['CHANGES-FROM'] = values[2]
        self.__data['CHANGE IN OPEN INTEREST'] = values[-1].strip(')')

        values = [i.strip() for i in data_list[12].split(' ') if i]
        self.__data['CHANGES-NON-COMMERCIAL-Long'] = values[0]
        self.__data['CHANGES-NON-COMMERCIAL-Short'] = values[1]
        self.__data['CHANGES-NON-COMMERCIAL-SPREADS'] = values[2]
        self.__data['CHANGES-COMMERCIAL-LONG'] = values[3]
        self.__data['CHANGES-COMMERCIAL-SHORT'] = values[4]
        self.__data['CHANGES-TOTAL-LONG'] = values[5]
        self.__data['CHANGES-TOTAL-SHORT'] = values[6]

        self.__data = {k: self._make_formatted_number(v) for k, v in self.__data.items()}

    def _make_formatted_number(self, num: str):

        if "," in num:
            return num
        else:
            if num.isdigit():
                num = float(num)
            else:
                return num

        return locale.format_string('%d', num, grouping=True)

    def _get_names_and_codes(self):
        for i in self.__content.split('\n'):
            if 'Code' in i:
                i = i.split()
                code = i[-1]
                first = i[:i.index('-')]
                active_name = ' '.join(first).strip()
                code = code.split('-')[-1]
                code = code.strip()

                self.__names_and_codes[code] = active_name

    def _add_new_data(self):
        self.__content += '\n'
        self._get_text()

    def refresh_data(self):
        if any((self.__data, self.__names_and_codes, self.__content)):
            self.__data = {}
            self.__names_and_codes = {}
            # self.__code_of_index = ""
            self.__content = ""
            self.__indexes = None
            self.__link = None
            self.__current_data_index = None

        for link in self.__links:
            self.__link = link
            self._add_new_data()
        self._get_names_and_codes()

    def _get_index_information(self):
        self._get_indexes_for_parsing()
        self._parse_content()

    @property
    def code_of_index(self):
        return self.__code_of_index

    @code_of_index.setter
    def code_of_index(self, value):
        if value not in self.__names_and_codes:
            raise ValueError('Invalid Code!')
        self.__code_of_index = value

    @property
    def names_and_codes(self):
        return self.__names_and_codes

    @property
    def data(self):
        if not self.code_of_index:
            raise ValueError('code is empty!')

        if self.__code_of_index == self.__current_data_index:
            return self.__data
        else:
            self._get_index_information()
            self.__current_data_index = self.code_of_index
            return self.__data


def text_ui():
    p1 = MyParser(links=links)

    codes = {}
    for i, item in enumerate(p1.names_and_codes.items(), start=1):
        codes[i] = item

    length_of_codes = len(codes)

    while True:

        print('Оберіть один із варіантів: ')

        print()
        for k, v in codes.items():
            print(f"{k} {v[1]} Code: {v[0]}")

        print()
        variant = input(f"Ваш варіант (від 1 до {length_of_codes}): ")
        print()

        if not variant.isdigit():
            print('Потрібне число!')
            continue
        variant = int(variant)

        if variant > length_of_codes:
            print('Це забагато!')
            continue

        if length_of_codes >= variant > 0:
            code = codes[variant][0]
            name = codes[variant][1]
            p1.code_of_index = code

        print(f"{name} - Code: {code} ")
        print()

        for k, v in p1.data.items():
            print(k, v)

        print()
        while True:
            print(f"Бажаєте продовжити? Y-так, N-ні ")
            variant = input('Ваш вибір: ')

            variant = variant.upper()
            if variant not in ["Y", "N"]:
                print('Треба Y чи N')

            elif variant == 'Y':
                break
            else:
                return