import os
import re
from typing import Callable, Iterable, Optional, Union, List
from flask import Flask
from werkzeug.datastructures import FileStorage
from flask_uploads import UploadSet, IMAGES, BOOKS, AUDIO, DEFAULTS


# UploadSet predefine args: <name>, <extensions>, <default_dest>
IMAGE_CONF = ("images", IMAGES)
BOOK_CONF = ("books", BOOKS)
AUDIO_CONF = ("audios", AUDIO)


class FileHelper(UploadSet):
    def __init__(
        self,
        name: str,
        extensions: Iterable[str] = DEFAULTS,
        default_dest: Optional[Callable[[Flask], str]] = None,
    ) -> None:
        super().__init__(name, extensions, default_dest)

    def find_file_any_format(
        self, filename: str, folder: str = None
    ) -> Union[str, None]:
        """
        Given a format-less filename, try to find the file by appending each of the allowed formats to the given
        filename and check if the file exists
        :param filename: formatless filename
        :param folder: the relative folder in which to search
        :return: the path of the image if exists, otherwise None
        """
        for _format in self.extensions:
            file = f"{filename}.{_format}"
            file_path = self.path(filename=file, folder=folder)
            if os.path.isfile(file_path):
                return file_path
        return None

    @property
    def destination(self):
        return self.config.destination

    def get_files(self, folder: str = None) -> List[str]:
        """Given a relative folder find all files inside it"""

        if folder is not None:
            target_folder = os.path.join(self.config.destination, folder)
        else:
            target_folder = self.config.destination

        file_list = []
        if os.path.isdir(target_folder):
            with os.scandir(target_folder) as it:
                for entry in it:
                    if entry.is_file():
                        file_list.append(entry.name)
        return file_list

    def remove_file(self, file: str, folder: str = None) -> None:
        file_path = self.path(filename=file, folder=folder)
        os.remove(file_path)

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
        # format extensions into regex, eg: ('mobi','pdf') --> 'mobi|pdf'
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
