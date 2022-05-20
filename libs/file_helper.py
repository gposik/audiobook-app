import os
import re
from typing import Tuple, Union
from werkzeug.datastructures import FileStorage
from flask_uploads import UploadSet, IMAGES, BOOKS


IMAGE_SET = UploadSet("images", IMAGES)
BOOK_SET = UploadSet("books", BOOKS)

upload_sets = {"image": IMAGE_SET, "book": BOOK_SET}


class FileHelper:
    def __init__(self, upload_set: Union[str, UploadSet]):
        if isinstance(upload_set, str):
            self.upload_set = upload_sets.get(upload_set)
        else:
            self.upload_set = UploadSet()

    @property
    def extensions(self) -> Tuple:
        return self.upload_set.extensions

    @property
    def destination(self) -> str:
        return self.upload_set.default_dest

    @property
    def destination(self, dest: str):
        self.upload_set.default_dest = dest

    def save_file(self, file: FileStorage, folder: str = None, name: str = None) -> str:
        return self.upload_set.save(file, folder, name)

    def get_path(self, filename: str = None, folder: str = None) -> str:
        return self.upload_set.path(filename, folder)

    def find_file_any_format(self, filename: str, folder: str) -> Union[str, None]:
        """
        Given a format-less filename, try to find the file by appending each of the allowed formats to the given
        filename and check if the file exists
        :param filename: formatless filename
        :param folder: the relative folder in which to search
        :return: the path of the image if exists, otherwise None
        """
        for _format in self.extensions:  # look for existing avatar and delete it
            avatar = f"{filename}.{_format}"
            avatar_path = self.upload_set.path(filename=avatar, folder=folder)
            if os.path.isfile(avatar_path):
                return avatar_path
        return None

    def _retrieve_filename(self, file: Union[str, FileStorage]) -> str:
        """
        Make our filename related functions generic, able to deal with FileStorage object as well as filename str.
        """
        if isinstance(file, FileStorage):
            return file.filename
        return file

    def is_filename_safe(self, file: Union[str, FileStorage]) -> bool:
        """
        Check if a filename is secure according to our definition
        - starts with a-z A-Z 0-9 at least one time
        - only contains a-z A-Z 0-9 and _().-
        - followed by a dot (.) and a allowed_format at the end
        """
        filename = self._retrieve_filename(file)

        allowed_format = "|".join(self.extensions)
        # format BOOKS into regex, eg: ('mobi','pdf') --> 'mobi|pdf'
        regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_format})$"
        return re.match(regex, filename) is not None

    def get_basename(self, file: Union[str, FileStorage]) -> str:
        """
        Return file's basename, for example
        get_basename('some/folder/image.jpg') returns 'image.jpg'
        """
        filename = self._retrieve_filename(file)
        return os.path.split(filename)[1]

    def get_extension(self, file: Union[str, FileStorage]) -> str:
        """
        Return file's extension, for example
        get_extension('image.jpg') returns '.jpg'
        """
        filename = self._retrieve_filename(file)
        return os.path.splitext(filename)[1]
