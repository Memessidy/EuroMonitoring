import requests
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def get_text(link):
    # filename = r"D:\WorkSpace\Untitled Folder 1\text.txt"
    #
    # with open(file=filename, mode="r", encoding='iso-8859-1') as somefile:
    #     content = somefile.read()

    response = requests.get("https://www.cftc.gov/dea/futures/deacmesf.htm")
    content = response.text
    return content


def make_formatted_number(num: str):
    if "," in num:
        return num
    else:
        num = float(num)

    return locale.format_string('%d', num, grouping=True)


def parse_data(content):
    start_ind = content.find('132741')
    end_ind = content.find('133741')
    list_of_content = content[start_ind:end_ind].split()
    data = {}

    data['NON-COMMERCIAL-Long'] = make_formatted_number(list_of_content[42])
    data['NON-COMMERCIAL-Short'] = make_formatted_number(list_of_content[43])
    data['NON-COMMERCIAL-SPREADS'] = make_formatted_number(list_of_content[44])
    data['COMMERCIAL-LONG'] = make_formatted_number(list_of_content[45])
    data['COMMERCIAL-SHORT'] = make_formatted_number(list_of_content[46])
    data['TOTAL-LONG'] = make_formatted_number(list_of_content[47])
    data['TOTAL-SHORT'] = make_formatted_number(list_of_content[48])

    data['CHANGES-FROM'] = list_of_content[53]
    data['CHANGE IN OPEN INTEREST'] = make_formatted_number(list_of_content[58].strip(')'))

    data['CHANGES-NON-COMMERCIAL-Long'] = make_formatted_number(list_of_content[59])
    data['CHANGES-NON-COMMERCIAL-Short'] = make_formatted_number(list_of_content[60])
    data['CHANGES-NON-COMMERCIAL-SPREADS'] = make_formatted_number(list_of_content[61])
    data['CHANGES-COMMERCIAL-LONG'] = make_formatted_number(list_of_content[62])
    data['CHANGES-COMMERCIAL-SHORT'] = make_formatted_number(list_of_content[63])
    data['CHANGES-TOTAL-LONG'] = make_formatted_number(list_of_content[64])
    data['CHANGES-TOTAL-SHORT'] = make_formatted_number(list_of_content[65])

    return data


def main():
    link = "https://www.cftc.gov/dea/futures/deacmesf.htm"
    content = get_text(link)
    data = parse_data(content=content)

    for item, value in data.items():
        print(f"{item}: {value}")

    print()
    input('Press enter to exit: ')


if __name__ == "__main__":
    main()
