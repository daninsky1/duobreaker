import database
import pathlib


def get_dirs(path):
    pass


def get_files(basepath, extension):
    """Makes a recursive search in the base path for a given extension file
     and return a list with the pathlib.Path matches.
    """
    return list(pathlib.Path(basepath).glob(f"**/*.{extension}"))


def refactor_xlsx():
    """This is a case of refactoring a xlsx and savind a copy in the same folder
    pattern. Do not use for anything else."""
    files = get_files("../olddatabase/", "xlsx")
    for file in files:
        tdb = database.TransDatabase.fromfile(file)
        print(file)
        basename = pathlib.Path(file).name
        basedir = pathlib.Path(file).parent.name
        new_path = pathlib.Path(f"../database/{basedir}")
        new_path.mkdir(parents=True, exist_ok=True)
        new_file = new_path.joinpath(basename)
        tdb.save(new_file)
        print(new_file)


def chk_ponctuation():
    # TODO: check ponctuation on the database and correct
    pass

if __name__ == "__main__":
    refactor_xlsx()
    # my_tdb = database.TransDatabase.fromfile("..\olddatabase\Acidentes\Acidentes_en_to_pt_dictionary.xlsx")
    # my_tdb.save("../test.xlsx")