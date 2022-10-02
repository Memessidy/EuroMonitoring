import requests
import locale
from pprint import pprint

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class Parser:
    def __init__(self, links):
        self.__links = links
        self.__content = None
        self.__data_for_parsing = None
        self.__data = {}
        self.__cur_link = None

    def get_data_from_website(self):
        """
        Парсить весь текст з сайту
        """
        response = requests.get(self.__cur_link)
        self.__content = response.text

    def prepare_data_for_parse(self):
        # list з усіма котировками в форматі, як на сайті
        data = self.__content.split('\r\n \r\n')
        data[-1] = data[-1].split('\r\n\r\n<!--/ih:includeHTML-->')[0]
        self.__data_for_parsing = data[1:]

    def set_dictionary_values(self, dictionary, num, data_for_parsing, net_positions=False):
        line = data_for_parsing[num].split()
        dictionary['Non-commercial long'] = line[0]
        dictionary['Non-commercial short'] = line[1]
        dictionary['Non-commercial spreads'] = line[2]
        dictionary['Commercial long'] = line[3]
        dictionary['Commercial short'] = line[4]
        dictionary['Total long'] = line[5]
        dictionary['Total short'] = line[6]

        if net_positions:
            dictionary['Non-commercial net positions'] = str(
                int(line[3].replace(',', '')) - int(line[1].replace(',', '')))
            dictionary['Commercial net positions'] = str(int(line[4].replace(',', '')) - int(line[1].replace(',', '')))

        try:
            dictionary['Nonreportable positions long'] = line[7]
            dictionary['Nonreportable positions short'] = line[8]
        except IndexError:
            pass

        res = {k: self.make_formatted_number(v) for k, v in dictionary.items()}
        return res

    def make_formatted_number(self, num: str):
        negative = False

        if '-' in num:
            num = num.lstrip('-')
            negative = True

        if "," in num:
            return num
        else:
            if num.isdigit():
                num = float(num)
            else:
                return num

        if negative:
            res = '-' + locale.format_string('%d', num, grouping=True)
        else:
            res = locale.format_string('%d', num, grouping=True)

        return res

    def parse_data(self):

        index_data = {}

        for val in self.__data_for_parsing:
            current_index = val.split('\n')
            current_index = list(map(lambda x: x.strip(), current_index))
            current_index = list(filter(lambda x: bool(x), current_index))

            index = {}
            code = current_index[0].split()[-1].split('-')[1]
            name = ' '.join(current_index[0].split()[:-1])

            index['Code'] = code
            index['Name'] = name

            name_and_code = f'{name} Code: {code}'

            index['Futures only positions as of'] = current_index[1].split()[-2]
            index['Open interest'] = current_index[7].split()[-1]
            index['Contracts'] = ' '.join(current_index[7].split()[0:-3])

            commitments = {}
            changes = {}
            percent_of_open_interest_for_each_category_of_traders = {}
            number_of_traders_in_each_category = {}

            changes['Changes from'] = current_index[10].split()[2]
            changes['Change in open interest'] = current_index[10].split()[-1].strip(')')
            number_of_traders_in_each_category['Total traders'] = current_index[14].split()[-1].strip(')')

            index['Commitments'] = self.set_dictionary_values(commitments, 9, current_index, True)
            index['Changes'] = self.set_dictionary_values(changes, 11, current_index, False)
            index['Percent of open interest'] = self.set_dictionary_values\
                (percent_of_open_interest_for_each_category_of_traders, 13, current_index,
                                         False)
            index['Number of traders'] = self.set_dictionary_values\
                (number_of_traders_in_each_category, 15, current_index, False)

            index_data.update({name_and_code: index})

        self.__data.update(index_data)

    def run_parser(self):
        """
        Запуск парсеру:
        Отрумуємо всі діні з сайтів, зберігаємо в dict
        """

        # Для кожного лінку з массиву лінків
        for link in self.__links:
            self.__cur_link = link

            # Отримання даних з сайту
            self.get_data_from_website()
            # Підготовка даних (отримати всі індекси в текстовому вигляді)
            self.prepare_data_for_parse()
            # Отримуємо dict з усіма показниками
            self.parse_data()

    def refresh_all_data(self):
        if self.__content:
            self.__content = None
            self.__data_for_parsing = None
            self.__data = {}
            self.__cur_link = None
        self.run_parser()

    @property
    def data(self):
        return self.__data


if __name__ == '__main__':
    links = (['https://www.cftc.gov/dea/futures/deacmesf.htm', 'https://www.cftc.gov/dea/futures/deacmxsf.htm'])
    f = Parser(links)
    f.refresh_all_data()
    for i in f.data:
        print(i)