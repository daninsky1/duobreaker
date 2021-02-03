import pathlib
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
import copy

# TODO: maybe is better import openpyxl inside the methods save and load scope

# Setup the file path
# TODO: this folder needs to be config outside database
# self.db_folder = pathlib.Path.cwd() / 'database' / '{}'.format(self.file)
# self.db_folder.mkdir(exist_ok=True)
#
# # The workbook file name
# self.wb_file = self.db_folder / '{}_{}_to_{}_dictionary.xlsx'.format(
#     self.file, self.foreign_lang, self.native_lang
# )


class TransPair:
    """A translation pair.

    A pair of string elements, empty strings are invalid.
    """
    def __init__(self, elem0, elem1):
        if (type(elem0) and type(elem1)) != str:
            raise TypeError("string element expected.")
        elif (elem0 and elem1) == "":
            raise AttributeError("cannot store empty strings.")
        self.elem0 = elem0
        self.elem1 = elem1

    def __getitem__(self, index):
        if index == 0:
            return self.elem0
        elif index == 1:
            return self.elem1
        else:
            raise IndexError("TransPair index out of range")

    def __str__(self):
        return f"({self.elem0}, {self.elem1})"

    def __repr__(self):
        return f"TransPair({self.elem0}, {self.elem1})"

    def __eq__(self, other):
        if (self.elem0 == other.elem0) and (self.elem1 == other.elem1):
            return True
        else:
            return False

    def switch(self):
        """Switch the elements. Invert the TransPair order."""
        temp = self.elem0
        self.elem0 = self.elem1
        self.elem1 = temp


class TransList:
    """A list of TransPair."""

    def __init__(self, *args):
        self.map = []
        for arg in args:
            if type(arg) == TransPair:
                self.append(arg)
            elif type(arg) == (list and tuple):
                if len(arg) != 2:
                    raise IndexError("arg list size must consist of 2  string elements.")
                self.append(TransPair(arg[0], arg[1]))
            else:
                raise TypeError("arg must be a TransPair list or a tuple.")

    def append(self, tp_key):
        """Adds a new TransPair element into the end of the TransList."""
        if type(tp_key) != TransPair:
            raise KeyError("the tp_key must be a TransPair object.")
        elif tp_key in self.map:
            raise KeyError("TransPair {} already assigned.".format(tp_key))
        self.map.append(tp_key)

    def insert(self, i, tp_key):
        if type(tp_key) != TransPair:
            raise KeyError("the tp_key must be a TransPair object.")
        elif tp_key in self.map:
            raise KeyError("TransPair {} already assigned.".format(tp_key))
        self.map.insert(i, tp_key)

    def extend(self, other):
        # TODO: not implemented
        if type(other) != TransPair:
            raise KeyError("the tp_key must be a TransPair object.")
        pass

    def remove(self, tp_key):
        """Remove a TransPair element by element key."""
        self.map.remove(tp_key)

    def pop(self, tp_index):
        """Removes one element of the list by index."""
        if type(tp_index) != int:
            raise KeyError("tp_index must be a integer.")
        self.map.pop(tp_index)

    def __iter__(self):
        return self.map.__iter__()

    def __len__(self):
        return self.map.__len__()

    def __getitem__(self, key):
        return self.map.__getitem__(key)

    def __str__(self):
        str_list = ""
        for item in self.map:
            str_list = str_list + str(item) + ",\n"
        return f"{{\n{str_list}\n}}"

    def __eq__(self, other):
        """Check if the list are the same in the same order.

        If the TransLists have the same TransPairs with other order will return False
        not equal.
        """
        if len(self.map) != len(other.map):
            return False
        for curr_transpair, other_transpair in zip(self.map, other.map):
            print(curr_transpair, other_transpair)
            if curr_transpair == other_transpair:
                continue
            else:
                return False
        return True


class DatabaseError(Exception):
    pass

"""01661600"""

class TransDatabase:
    """Creates, load and manipulate sentences translations.

    The TransDatabase are objects that maps translation sentences inside of a
    spreadsheet or multiple spreadsheets. The propose are to store sentences of
    a language (your native language) in pair with another language (foreign
    language).
    In a TransDatabase, the spreadsheet has a unique value to uniquely identify
    the spreadsheet, but his content can be the same of other spreadsheet,
    you can have how many you need.
    When you initialize a empty TransDatabase you need to uniquely identify a
    first_lang("e.g. EN-US") and second_lang("e.g. DE-CH") value. These are mere
    attributes for you to know the order in which you have to store the sentences,
    this does not guarantee that you will store them wrong, if it happens, use
    the correction methods available in this class.
    For easier implementation the sentence values need to be unique.
    """

    def __init__(self, first_lang, second_lang, database_map={}):
        """Creates a database.

        :param spreadsheet: Spreadsheet name inside the .xlsx file
        :param first_lang: first language description (default "first lang")
        :param second_lang: second language description (default "second lang")
        :return: None
        """
        self.database_map = database_map
        self.first_lang = first_lang
        self.second_lang = second_lang


    def add_spreadsheet(self, spreadsheet):
        if spreadsheet in self.database_map:
            DatabaseError("Spreadsheet {} already exist.".format(spreadsheet))

        self.database_map[spreadsheet] = []

    def add_translation(self, spreadsheet, fl_sentence, sl_sentence):
        """Append a translation to the database.

        :param spreadsheet: spreadsheet to be add
        :param fl_sentence: First language sentence.
        :param sl_sentence: Second language sentence.
        :return: None
        """
        trans_pair = [fl_sentence, sl_sentence]
        if spreadsheet not in self.database_map:
            raise DatabaseError("This spreadsheet {} doesn't exist.".format(spreadsheet))
        elif trans_pair in self.database_map[spreadsheet]:
            raise DatabaseError("This translation pair already exist.")

        self.database_map[spreadsheet].append(trans_pair)

    @classmethod
    def from_disk(cls, file):
        """Load a from disk a .xlsx translation database.

        :param file: Path-like object where the database will be opened
        :return: class
        """
        if not pathlib.Path(file).is_file():
            raise DatabaseError("This file \"{}\" doesn't exist.".format(file))

        workbook = load_workbook(file)
        sheet = workbook.active
        first_lang = sheet["A1"].value
        second_lang = sheet["B1"].value
        database_map = TransDatabase(first_lang, second_lang)
        for spreadsheet in workbook.sheetnames:
            spreadsheet = workbook[spreadsheet]
            database_map[spreadsheet] = []
            for row in spreadsheet.iter_rows(min_row=1, max_col=2, values_only=True):
                database_map[spreadsheet] = None

        return cls(first_lang, second_lang, database_map=database_map)

    def has_spreadsheet(self, spreadsheet):
        """Search a spreadsheet in the database_map.

        :param spreadsheet: spreadsheet to search for
        :return: boolean
        """
        if spreadsheet in self.database_map:
            return True
        else:
            return False

    def has_trans_pair(self, spreadsheet, fl_sentence, sl_sentence):
        trans_pair = [fl_sentence, sl_sentence]
        if trans_pair in self.database_map[spreadsheet]:
            return True
        else:
            return False

    def change_lang_attrs(self, first_lang, second_lang):
        """Change the language attributes."""

        self.first_lang = first_lang
        self.second_lang = second_lang

    def save(self, file, overwrite=False):
        workbook = Workbook()
        worksheet = workbook.active   # current working spreadsheet

        default_font = Font(name='Arial', size=12)
        header_font = Font(name='Arial', size=14, bold=True)
        worksheet.column_dimensions['A'].font = default_font
        worksheet.column_dimensions['B'].font = default_font
        worksheet['A1'].font = header_font
        worksheet['B1'].font = header_font

        worksheet['C1'] = self.first_lang
        worksheet['D1'] = self.second_lang

        cell_width = 60
        cell_height = 20
        worksheet.column_dimensions['A'].width = cell_width
        worksheet.column_dimensions['B'].width = cell_width
        worksheet.row_dimensions[1].height = cell_height

        if not overwrite and pathlib.Path.is_file(file):
            raise DatabaseError("This file \"{}\" already exist.".format(file))

        workbook.save(file)



    def get_translation(self, to_translate, switch_lang):
        """Search translation.
        
        :param to_translate: Sentence to be searched
        :param switch_lang: If is true invert the language search
        :return: str
        """
        if not isinstance(switch_lang, bool):
            raise EOFError('TypeError. It\'s not a boolean value.')

        if switch_lang:
            search_i = 0
            transl_i = 1
        else:
            search_i = 1
            transl_i = 0

        self.database = load_workbook(self.wb_file)
        self.worksheet = self.database[self.local_database]

        for dictionary in self.worksheet.rows:
            # Returns a tuple with the cells with the translations
            if to_translate == dictionary[search_i].value:
                return dictionary[transl_i].value
        return None

    def check_health(self):
        """Compares the number of lines in each database,
        if does'nt match something is wrong.
        If sheet = None he auto check all sheet length"""

        rows_values = self.worksheet.values
        rows = self.worksheet.iter_rows()
        for row, row_values in zip(rows, rows_values):
            if None in row_values:
                raise Exception('''TroubleWithTheFile.
Something is missing in:
{}'''.format(row))


def test_db1():
    terra = TransDatabase('Frutas', 'terra', 'en', 'pt')
    arvores = TransDatabase('Frutas', 'arvores', 'en', 'pt')
    frutos = TransDatabase('Frutas', 'mar', 'en', 'pt')

    terra.add_translation('papaya', 'mamão', True)
    terra.add_translation('papaya', 'mamão', True)
    terra.add_translation('papaya', 'mamão', True)
    terra.add_translation('papaya', 'mamão', True)
    frutos.add_translation('tomate', 'tomato', True)
    arvores.add_translation('maça', 'apple', True)



def test_xlsx(file):
    database = TransDatabase.from_disk(file)

def test_db():
    # test_xlsx(r"E:\Daniel\Dev\Python\duo_breaker\duo_breaker_v1\database\Acidentes\Acidentes_en_to_pt_dictionary.xlsx")
    my_unique_values = {"banana", "oleo", "oil"}
    print(my_unique_values)

if __name__ == '__main__':
    my_translist = TransList(("hi", "oi"))
    my_translist2 = TransList(("hi", "oi"))
    trans_pair = TransPair("car", "carro")
    # my_translist2.append(trans_pair)
    print(my_translist)
    print(my_translist2)
    print(my_translist == my_translist2)
