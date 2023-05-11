# -*-coding:utf-8-*-
import configparser
import os


class Conf:
    def __init__(self, filename='config.ini'):
        self.conf = configparser.ConfigParser()
        self._root_path = os.path.dirname(os.path.abspath(__file__))
        self._file_path = os.path.join('{}/{}'.format(self._root_path, filename))
        if os.path.isfile(self._file_path):
            self.conf.read(self._file_path, encoding='utf-8')
        else:
            self._file_path = os.path.join('./{}'.format(filename))
            self.conf.read(self._file_path, encoding='utf-8')

    def get_all_sections(self) -> list:
        return self.conf.sections()

    def get_all_options(self) -> list:
        temp = []
        for i in self.get_all_sections():
            temp.append({i: self.get_options(i)})
        return temp

    def get_options(self, section) -> list:
        return self.conf.options(section)

    def get_section_items(self, section) -> list:
        return self.conf.items(section)

    def get_item(self, section, option):
        temp = self.conf.get(section, option)
        if temp == '-1':
            return None
        try:
            return int(temp)
        except ValueError:
            return temp

    def set_section(self, section, option, new_value: str) -> bool:
        self.conf.set(section, option, new_value)
        try:
            self.conf.write(open(self._file_path, 'w', encoding='utf-8'))
        except Exception as e:
            return False
        return True

# if __name__ == '__main__':
#     conf = Conf()
#     print(conf.get_all_sections())
#     print(conf.get_all_options())
#     print(conf.get_options('server'))
#     print(conf.get_section_items('server'))
#     print(conf.get_item('server', 'port'))
#     conf.set_section('server', 'port', str(9999))
