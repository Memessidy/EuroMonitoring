import requests
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class MyParser:
    def __init__(self, links):

        self.links = links
        self.link = None
        self.code = None

        self.content = str()
        self.indexes = None
        self.data = {}
        self.names_and_codes = {}
        self.counter = 0

    def _get_text(self):
        response = requests.get(self.link)
        content = response.text
        # print(type(content), type(self.content))
        self.content += content

    def _get_indexes_for_parsing(self):
        start_ind = self.content.find(self.code)

        val = "PERCENT OF OPEN INTEREST"
        end_ind = self.content.find(val, start_ind)

        start_ind += len(self.code)
        self.indexes = (start_ind, end_ind)

    def _parse_content(self):
        curr_content = self.content[self.indexes[0]:self.indexes[1]]

        data_list = curr_content.split('\n')

        values = [i.strip() for i in data_list[9].split(' ') if i]
        self.data['NON-COMMERCIAL-LONG'] = values[0]
        self.data['NON-COMMERCIAL-Short'] = values[1]
        self.data['NON-COMMERCIAL-SPREADS'] = values[2]
        self.data['COMMERCIAL-LONG'] = values[3]
        self.data['COMMERCIAL-SHORT'] = values[4]
        self.data['TOTAL-LONG'] = values[5]
        self.data['TOTAL-SHORT'] = values[6]

        values = [i.strip() for i in data_list[11].split(' ') if i]
        self.data['CHANGES-FROM'] = values[2]
        self.data['CHANGE IN OPEN INTEREST'] = values[-1].strip(')')

        values = [i.strip() for i in data_list[12].split(' ') if i]
        self.data['CHANGES-NON-COMMERCIAL-Long'] = values[0]
        self.data['CHANGES-NON-COMMERCIAL-Short'] = values[1]
        self.data['CHANGES-NON-COMMERCIAL-SPREADS'] = values[2]
        self.data['CHANGES-COMMERCIAL-LONG'] = values[3]
        self.data['CHANGES-COMMERCIAL-SHORT'] = values[4]
        self.data['CHANGES-TOTAL-LONG'] = values[5]
        self.data['CHANGES-TOTAL-SHORT'] = values[6]

        self.data = {k: self._make_formatted_number(v) for k, v in self.data.items()}

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
        values = {}
        for i in self.content.split('\n'):
            if 'Code' in i:
                i = i.split()
                code = i[-1]
                name = i[:-1]
                first = i[:i.index('-')]
                active_name = ' '.join(first).strip()
                code = code.split('-')[-1]
                code = code.strip()
                self.counter += 1

                cur = {self.counter: {code: active_name}}
                values.update(cur)

        self.names_and_codes.update(values)

    def add_new_data(self):
        self.content += '\n'
        self._get_text()


    def run(self):
        for link in self.links:
            self.link = link
            self.add_new_data()
        self._get_names_and_codes()


        while True:
            print("Оберіть один із віріантів: ")
            print()
            for k, v in self.names_and_codes.items():
                print(k, v)

            print()
            variant = input(f"Ваш варіант (від 1 до {len(self.names_and_codes)}): ")
            if not variant.isdigit():
                print('Потрібне число!')
                continue
            variant = int(variant)
            if len(self.names_and_codes) >= variant > 0:
                cur = self.names_and_codes[variant]
                cur_code = list(cur)[0]
                self.code = cur_code

            self._get_indexes_for_parsing()
            self._parse_content()
            print()

            key = str(list(cur)[0])
            print(f"{cur[key]} - Code: {cur_code}")

            print()
            for k, v in self.data.items():
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


p1=MyParser(links=["https://www.cftc.gov/dea/futures/deacmesf.htm", "https://www.cftc.gov/dea/futures/deacmxsf.htm"])
p1.run()

