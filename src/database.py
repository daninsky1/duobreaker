import pathlib
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

# Setup the file path
# TODO: this folder needs to be config outside database
# self.db_folder = pathlib.Path.cwd() / 'database' / '{}'.format(self.file)
# self.db_folder.mkdir(exist_ok=True)
#
# # The workbook file name
# self.wb_file = self.db_folder / '{}_{}_to_{}_dictionary.xlsx'.format(
#     self.file, self.foreign_lang, self.native_lang
# )


class DatabaseError(Exception):
    pass


class Database:
    """Creates, load and manipulate a .xlsx database for sentences translations.

    The database are constructed with two languages, those languages have an
    order in how they are stored and manipulated, first_lang and second_lang,
    you need change those attributes in the database creation to a language name
    description, you can change those attributes after creation, but you cannot
    change the order of the database language after creation, keep those
    attributes values and order in mind. This order will determine how the
    database will add and get your translations.
    """

    def __init__(self):
        self.file = None
        self.first_lang = None
        self.second_lang = None
        self.spreadsheet = None     # spreadsheet name
        self.workbook = None
        self.worksheet = None       # current working spreadsheet

    def create(self, file, spreadsheet, first_lang="first lang",
               second_lang="second lang", overwrite=False):
        """Creates a database.

        :param file: Path-like object where the database will be created
        :param spreadsheet: Spreadsheet name inside the .xlsx file
        :param first_lang: first language description (default "first lang")
        :param second_lang: second language description (default "second lang")
        :return: None
        """
        if pathlib.Path.is_file(file) and not overwrite:
            raise DatabaseError("This file \"{}\" already exist.".format(file))

        self.file = file
        self.spreadsheet = spreadsheet
        self.first_lang = first_lang
        self.second_lang = second_lang

        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title(spreadsheet)

        header_font = Font(name='Arial', size=14, bold=True)
        default_font = Font(name='Arial', size=12)
        self.worksheet.column_dimensions['A'].font = default_font
        self.worksheet.column_dimensions['B'].font = default_font
        self.worksheet['A1'].font = header_font
        self.worksheet['B1'].font = header_font

        self.worksheet['A1'] = first_lang
        self.worksheet['B1'] = second_lang

        cell_width = 60
        cell_height = 20
        self.worksheet.column_dimensions['A'].width = cell_width
        self.worksheet.column_dimensions['B'].width = cell_width
        self.worksheet.row_dimensions[1].height = cell_height
        self.workbook.save(self.wb_file)

    def load(self, file, spreadsheet):
        """Load a from disk a database.

        :param file: Path-like object where the database will be opened
        :param spreadsheet: The spreadsheet name that'll be worked on
        :return: None
        """
        if not pathlib.Path.is_file(file):
            raise DatabaseError("This file \"{}\" doesn't exist.".format(file))

        self.workbook = load_workbook(self.file)
        self.worksheet = self.workbook[spreadsheet]

    def add_spreadsheet(self, spreadsheet):
        if self.file is None:
            raise DatabaseError("File are not loaded, use create or load method.\n")
        self.workbook.create_sheet(spreadsheet)

    def add_translation(self, fl_sentence, sl_sentence, add_anyway=False):
        """Append a translation to the database.

        :param fl_sentence: First language sentence.
        :param sl_sentence: Second language sentence.
        :param add_anyway: Ignore the unique  and add a recurrent translation
        :return: None
        """
        self.workbook = load_workbook(self.wb_file)
        self.worksheet = self.workbook[self.local_database]

        # Redundancy to check if the data it's
        exist = self.get_translation(fl_sentence, True)

        if (exist != None) and (add_anyway == False):
            raise Exception('TroubleWithTheFiles.\nThe translation already exists.')
        else:
            data = [fl_sentence, sl_sentence]
            self.worksheet.append(data)

    def change_lang_attrs(self, first_lang, second_lang):
        """Change the language attributes.

        :param first_lang:
        :param second_lang:
        :return: None
        """

    def save(self):
        self.workbook.save(self.file)

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

        self.workbook = load_workbook(self.wb_file)
        self.worksheet = self.workbook[self.local_database]

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
    terra = Database('Frutas', 'terra', 'en', 'pt')
    arvores = Database('Frutas', 'arvores', 'en', 'pt')
    frutos = Database('Frutas', 'mar', 'en', 'pt')

    terra.add_translation('papaya', 'mamão', True)
    terra.add_translation('papaya', 'mamão', True)
    terra.add_translation('papaya', 'mamão', True)
    terra.add_translation('papaya', 'mamão', True)
    frutos.add_translation('tomate', 'tomato', True)
    arvores.add_translation('maça', 'apple', True)






if __name__ == '__main__':
    workbook = Workbook()
    worksheet = workbook["Oi"]

