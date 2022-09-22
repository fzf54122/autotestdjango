import os
from typing import List
import inspect
import sys
import imp
import temp_cases.auditor


class CommonUtils:

    def get_all_files(self, path: str):
        if not os.path.exists(path):
            raise Exception(f"Path {path} does not exist")

        file_list: List = []
        for root, dirs, files in os.walk(path):
            for file in files:
                file_list.append(os.path.abspath(os.path.join(root, file)))
            for _dir in dirs:
                files = self.get_all_files(os.path.join(root, _dir))
                file_list.extend(files)
        return file_list

    def get_class_in_file(self, file: str):
        class_inst = None

        if not os.path.exists(file):
            raise Exception(f"File {file} does not exist")
        if not os.path.isfile(file):
            raise Exception(f"{file} is not a file")

        fp, path, desc = imp.find_module(file)

        return class_inst


if __name__ == '__main__':
    result = CommonUtils().get_all_files('../temp_cases/auditor/v3.4')
    filtered_result = list(filter(lambda x: x.split('/')[-1].startswith('test') and x.endswith('.py'), result))
    for file in filtered_result:
        classes = CommonUtils().get_class_in_file(file)
        print(classes)