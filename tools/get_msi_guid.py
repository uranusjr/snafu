"""Retrieves GUID from the MSI to be vendored in version information.
"""
import msilib
import sys


def main():
    try:
        msi_s = sys.argv[1]
    except IndexError:
        msi_s = input('Paste MSI path: ')
    db = msilib.OpenDatabase(msi_s, msilib.MSIDBOPEN_READONLY)

    v = db.OpenView("select Value from Property where Property='ProductCode'")
    v.Execute(None)

    col_index = 0
    col_info = v.GetColumnInfo(msilib.MSICOLINFO_NAMES)
    while True:
        if col_info.GetString(col_index) == 'Value':
            break
        col_index += 1

    row = v.Fetch()
    guid = row.GetString(col_index)
    print('GUID:', guid)

    v.Close()


if __name__ == '__main__':
    main()
