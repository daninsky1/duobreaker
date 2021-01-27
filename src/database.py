import pathlib
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from openpyxl.utils import units

header_font = Font(name='Arial',
                   size=14,
                   bold=True)
default_font = Font(name='Arial',
                    size=12)

class Database():
    """
    Creates or load a database file(workbook).

    global_database - the name of the excel file. (The parent file)
    local_database = the name of the sheet to be work with. (The child object)
    foreign_lang - the abbreviation of the studded language that will be stored
    will be the first in order.
    native_lang - the abbreviation of the native language that will be stored
    will be the second in order.
    """
    def __init__(self, global_database, local_database,
                 foreign_lang='foreign_lang', native_lang='native_lang'):
        # Create or load a workbook
        self.local_database = local_database
        self.global_database = global_database
        self.foreign_lang = foreign_lang
        self.native_lang = native_lang

        # Setup the file path
        self.db_folder = pathlib.Path.cwd() / 'database' / '{}'.format(self.global_database)
        self.db_folder.mkdir(exist_ok=True)

        # The workbook file name
        self.wb_file = self.db_folder / '{}_{}_to_{}_dictionary.xlsx'.format(
            self.global_database, self.foreign_lang, self.native_lang
        )

        width_s = 60
        height_s = 20

        try:
            # Try: load an existing workbook
            self.workbook = load_workbook(self.wb_file)
        except FileNotFoundError:
            # except: Create the workbook
            self.workbook = Workbook()
            self.worksheet = self.workbook.active
            self.worksheet.title = local_database
            # Column font style
            self.worksheet.column_dimensions['A'].font = default_font
            self.worksheet.column_dimensions['B'].font = default_font
            # Header and reassign font style
            self.worksheet['A1'] = foreign_lang
            self.worksheet['A1'].font = header_font
            self.worksheet['B1'] = native_lang
            self.worksheet['B1'].font = header_font

            self.worksheet.column_dimensions['A'].width = width_s
            self.worksheet.column_dimensions['B'].width = width_s
            self.worksheet.row_dimensions[1].height = height_s
            self.workbook.save(self.wb_file)
        else:
            try:
                self.worksheet = self.workbook[self.local_database]
            except KeyError:
                # Auto creates sheet
                self.worksheet = self.workbook.create_sheet(self.local_database)
                # Column font style
                self.worksheet.column_dimensions['A'].font = default_font
                self.worksheet.column_dimensions['B'].font = default_font
                # Header and reassign font style
                self.worksheet['A1'] = foreign_lang
                self.worksheet['A1'].font = header_font
                self.worksheet['B1'] = native_lang
                self.worksheet['B1'].font = header_font

                self.worksheet.column_dimensions['A'].width = width_s
                self.worksheet.column_dimensions['B'].width = width_s
                self.worksheet.row_dimensions[1].height = height_s
                # Save
                self.workbook.save(self.wb_file)

    def add_translation(self, foreign_sentence, native_sentence, add_anyway=False):
        """
        Adds phrase or word to databases
        add_anyway = Forces the method to write the even if is repeated
        """

        self.workbook = load_workbook(self.wb_file)
        self.worksheet = self.workbook[self.local_database]

        # Redundancy to check if the data it's
        exist = self.search_translation(foreign_sentence, True)

        if (exist != None) and (add_anyway == False):
            raise Exception('TroubleWithTheFiles.\nThe translation already exists.')
        else:
            data = [foreign_sentence, native_sentence]
            self.worksheet.append(data)
            self.workbook.save(self.wb_file)

    def search_translation(self, to_translate, foreign_to_native):
        """Return the translation of a absolute sentence(string) based on two files
        interchangeable
        foreign_to_native = bolean value
        """

        if not isinstance(foreign_to_native, bool):
            raise EOFError('TypeError. It\'s not a boolean value.')

        if foreign_to_native:
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


if __name__ == '__main__':
    terra = Database('Frutas', 'terra', 'en', 'pt')
    arvores = Database('Frutas', 'arvores', 'en', 'pt')
    frutos = Database('Frutas', 'mar', 'en', 'pt')

    terra.add_translation('papaya', 'mamão', True)
    terra.add_translation('papaya', 'mamão', True)
    terra.add_translation('papaya', 'mamão', True)
    terra.add_translation('papaya', 'mamão', True)
    frutos.add_translation('tomate', 'tomato', True)
    arvores.add_translation('maça', 'apple', True)

