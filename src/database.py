import pathlib
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
import collections.abc
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

    A pair of string elements, to store sentence translation.
    Empty strings are invalid.
    """
    def __init__(self, elem0, elem1):
        if (type(elem0) and type(elem1)) != str:
            raise TypeError("string element expected.")
        elif (elem0 and elem1) == "":
            raise ValueError("cannot store empty strings.")
        self.elem0 = elem0
        self.elem1 = elem1

    def switch(self):
        """Switch the elements. Invert the TransPair order."""
        temp = self.elem0
        self.elem0 = self.elem1
        self.elem1 = temp

    @classmethod
    def fromlist(cls, item):
        # TODO: change to from_sequence to accept more sequences like dictionary
        if not isinstance(item, list) and not isinstance(item, list):
            raise TypeError("must be a list or a tuple.")
        elif len(item) < 2:
            raise ValueError(f"Receives a two elements list or tuple\
                             {len(item)} was given.")
        elif len(item) > 2:
            raise ValueError(f"Overload elements, receives a two elements list or tuple\
                             {len(item)} was given.")
        return cls(item[0], item[1])

    def __getitem__(self, index):
        if index == 0:
            return self.elem0
        elif index == 1:
            return self.elem1
        else:
            raise IndexError("TransPair index out of range")

    def __contains__(self, item):
        if (item == self.elem0) or (item == self.elem1):
            return True
        else:
            return False

    def __str__(self):
        return f"({self.elem0}, {self.elem1})"

    def __repr__(self):
        return f"TransPair({self.elem0}, {self.elem1})"

    def __eq__(self, other):
        if (self.elem0 == other.elem0) and (self.elem1 == other.elem1):
            return True
        else:
            return False


class TransList(collections.UserList):
    """A list/set of TransPair."""

    def __init__(self, *args):
        """
        :param args: TransPair or lists to construct TransPairs
        """
        super(TransList, self).__init__()
        for arg in args:
            self.append(arg)

    def __str__(self):
        indent = "    "
        trans_list_str = str()
        for i, item in enumerate(super(TransList, self).__iter__()):
            trans_list_str = trans_list_str + f"{indent} {str(item)}"
            if i < super(TransList, self).__len__() - 1:
                trans_list_str = trans_list_str + ", \n"
        return f"{{\n{trans_list_str}\n}}"

    def append(self, tp_key):
        """Adds a new TransPair element into the end of the TransList."""
        if not isinstance(tp_key, TransPair):
            raise TypeError("only TransPair object is accepted.")
        elif super(TransList, self).__contains__(tp_key):
            raise KeyError("TransPair {} already assigned.".format(tp_key))
        else:
            super(TransList, self).append(tp_key)

    def insert(self, i, tp_key):
        # TODO: test this method
        if type(tp_key) != TransPair:
            raise KeyError("the tp_key must be a TransPair object.")
        elif super(TransList, self).__contains__(tp_key):
            raise KeyError("TransPair {} already assigned.".format(tp_key))
        super(TransList, self).insert(i, tp_key)

    def extend(self, other):
        # TODO: test this method
        for trans_pair in other:
            self.append(trans_pair)

    def remove(self, tp_key):
        """Remove a TransPair element by element key."""
        super(TransList, self).remove(tp_key)

    def pop(self, index=-1):
        """Remove the item at the given position in the list, and return it.

        If no index is specified, a.pop() removes and returns the last item in
        the TransList.
        """
        super(TransList, self).pop(index)


class TransDatabase(dict):
    """Creates, load and manipulate TransLists.

    The TransDatabase are a dictionary that store and manipulate named TransList
    that manipulate TransPairs objects, and are constructed with some helpful
    attributes to organize your TransLists, load and manipulate TransPairs.
    In a TransDatabase, the TransList has a unique key to uniquely identify
    the TransList, but his content can be the same of other TransList.
    When you initialize a empty TransDatabase you need to identify a
    first_lang("e.g. EN-US") and second_lang("e.g. DE-CH") attribute. These are
    mere index for you to know the order in which you have to store the
    sentences, but not that does not stop the user store them wrong.
    """
    def __init__(self, first_lang, second_lang, *args):
        """
        :param first_lang:
        :param second_lang:
        :param args:
        """
        self.lang_attr = TransPair(first_lang, second_lang)
        self.trans_list_names = []
        self.database = {}

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def __getitem__(self, key):
        """
        :param key: can be index or a name of a TransList
        :return: TransList
        """
        pass

    def append(self, trans_list_name, trans_list):
        """Append TransList with its name.

        If TransList is empty the effect are the same of the method add_trans_list.
        """
        pass

    def add_trans_list(self, trans_list_name):
        """Add new empty TransList."""
        if trans_list_name in self.database:
            AttributeError("cannot assign two names")
        self.trans_list_names.append()

    def has_trans_list(self, trans_list_name):
        pass

    def save(self, file, overwrite=False):
        # TODO: implement json save
        pass

    def get_translation(self, to_translate, trans_list_name, lang):
        # TODO: instead of raise an exception change it only to log a the key error
        """Search translation and return translation partner.

        :param to_translate: Sentence to be searched
        :param trans_list_name: TransList name
        :param lang: Language of the sentence to be searched
        :return: str
        """

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

    def get_translation(self):
        pass


def test_db2():
    my_translist = TransList(("hi", "oi"))
    my_translist2 = TransList(["car", "carro"])
    new_translist = TransList()
    my_trans_pair = TransPair("olá", "hello")
    new_translist.extend(my_translist)
    new_translist.extend(my_translist2)

    print(my_translist, my_translist2, sep="\n")



def tl_contains_test():
    hi = TransPair("hi", "oi")
    my_trans_list = TransList(hi)
    my_trans_list.append(hi)


if __name__ == '__main__':
    pass