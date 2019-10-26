import os.path


"""This module is File object
It writes, reads and re-writes content to file.

import:
    from file import File
"""

class File:
    """This is a main class for writing and reading files.
    Please, don't use this class directly.
    """
    def __init__(self, file_name, format="txt"):
        self.format = format
        self.file_name = file_name

        if not os.path.exists(f"{self.file_name}.{self.format}"):
            open(f"{self.file_name}.{self.format}", 'w').close()

    def __add__(self, other):
        """Add the contents of files and return new File object."""
        return type(self)(self.file_name + other.file_name).write_data(self.read_data()
                                                    + other.read_data())

    def __eq__(self, other):
        """Compare the contents of files."""
        return self.read_data() == other.read_data()

    def __str__(self):
        """Return name with format of file."""
        return f"{self.file_name}.{self.format}"

    def read_data(self):
        """This method reads file and return data"""
        with open(f"{self.file_name}.{self.format}", 'r') as file:
            return file.read()

    def write_data(self, content):
        """This method writes data to file"""
        with open(f"{self.file_name}.{self.format}", 'a') as file:
            file.write(content)

    def re_write(self, content):
        """This method deletes content completely and writes new content"""
        with open(f"{self.file_name}.{self.format}", 'w') as file:
            file.write(content)
