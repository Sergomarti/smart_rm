import os
import threading
from functools import wraps
import logging
import datetime
import json
from pathlib import *

thread_lock = threading.Lock()
my_log = logging.getLogger('smartRM')


def all_size_dir(removed_path: str):
    all_size = os.path.getsize(removed_path)
    dir_f = os.listdir(removed_path)
    for file in dir_f:
        file_path = os.path.join(removed_path, file)
        all_size += all_size_dir(file_path)
    return all_size


def file_exchange(file_size):
    for i in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if file_size < 1024.0:
            return f'{file_size:.1f} {i}'
        else:
            file_size /= 1024.0


def add_path(q):
    @wraps(q)
    def internal(obj, *args):
        common_path, *args = args
        if os.path.exists(common_path):
            if os.access(common_path, os.W_OK):
                if os.path.abspath(common_path):
                    return q(obj, common_path, *args)
                else:
                    common_path = os.path.abspath(common_path)
                    return q(obj, common_path, *args)
            else:
                raise FileExistsError('No access to change file')
        else:
            raise FileExistsError('File not founded')

    return internal


class DeleteFile:
    def __init__(self, removed_path, new_path):
        self.removed_path = os.path.split(removed_path)[0]
        self.name = os.path.basename(removed_path)
        self.new_pat = new_path
        if os.path.isdir(removed_path):
            self.size_file = all_size_dir(removed_path)
        else:
            self.size_file = os.path.getsize(removed_path)
        self.time_delete = datetime.datetime.now().strftime("%d/%m/%Y,%H:%M:%S")
        my_log.debug('Add removed file')

    def info(self):
        removal_information = {'file_name': self.name,
                               'removed_path': self.removed_path,
                               'size_file': file_exchange(self.size_file),
                               'time_delete': self.time_delete
                               }
        return removal_information


class SmartRm:
    def __init__(self):
        home_dir = str(Path.home())
        self.path_to_the_trash = os.path.join(home_dir, 'Trash')
        if not os.path.exists(self.path_to_the_trash):
            os.mkdir(self.path_to_the_trash)
            os.chmod(self.path_to_the_trash, 0o777)
            self.path_to_the_trash = os.path.abspath(self.path_to_the_trash)
            my_log.info(f'The basket was not found, but we have already created it at{self.path_to_the_trash}')

    @add_path
    def _directory_steps(self, path_to_file, path_to_death):
        if os.path.isdir(path_to_file):
            name_of_d = os.path.basename(path_to_file)
            make_new_dir = os.path.join(path_to_death, name_of_d)
            if not os.path.exists(make_new_dir):
                os.mkdir(make_new_dir)
            my_log.debug(f'Created a new directory in the trash bin {make_new_dir}')
            for file in os.listdir(path_to_file):
                new_path_file = os.path.join(path_to_file, file)
                self._directory_steps(new_path_file, make_new_dir)
                my_log.debug('Self worked')
            os.rmdir(path_to_file)
        else:
            file_name = os.path.basename(path_to_file)
            make_path_file = os.path.join(path_to_death, file_name)
            os.replace(path_to_file, make_path_file)
            my_log.debug('Directory deleted')

    @add_path
    def way_trash_bin(self, path_file):
        trash_file = os.path.basename(path_file)
        if trash_file == False:
            list_trash = os.listdir(path_file)
            for file in list_trash:
                way_trash = os.path.join(path_file, file)
                self.way_trash_bin(way_trash)
            return
        new_trash_way = os.path.join(self.path_to_the_trash, trash_file)
        rubbish = DeleteFile(path_file, new_trash_way)
        self._directory_steps(path_file, self.path_to_the_trash)
        self._new_info(rubbish)
        my_log.info('You moved the file to the trash bin')

    def _new_info(self, rubbish: DeleteFile):
        save_way = os.path.join(self.path_to_the_trash, '.information.json')
        outdated_data = {}
        my_log.debug('Open save file if that exist')
        if os.path.exists(save_way):
            with open(save_way) as file:
                if not os.path.getsize(save_way) == 0:
                    outdated_data.update(json.load(file))
        thread_lock.acquire()
        with open(save_way, 'w') as file:
            outdated_data[f'{rubbish.name}'] = rubbish.info()
            json.dump(outdated_data, file)
            my_log.debug('Save information about file')
        thread_lock.release()

    def trash_info(self):
        save_way = os.path.join(self.path_to_the_trash, '.information.json')
        if not os.path.exists(save_way):
            return 'Trash is empty'
        history_data = (f"{'name':^30} | {'size':^30} | {'removed time':^30}\n")
        with open(save_way) as file:
            data = json.load(file)
            if not data:
                return 'Waste bin empty'
            for files in data:
                info = data[files]
                history_data += (f"{info['file_name']:^30} | "
                                 f"{info['size_file']:^30} | "
                                 f"{info['time_delete']:^30}\n")
        my_log.debug('Information transferred')
        return history_data

    def upload_data(self):
        save_way = os.path.join(self.path_to_the_trash, '.information.json')
        info = {}
        if os.path.exists(save_way):
            with open(save_way) as file:
                if not os.path.getsize(save_way) == 0:
                    info.update(json.load(file))
                return info
        else:
            raise FileExistsError('File was not found')

    def data_update(self, tr_file):
        save_way = os.path.join(self.path_to_the_trash, '.information.json')
        thread_lock.acquire()
        outdated_data = self.upload_data()
        outdated_data.pop(tr_file)
        with open(save_way, 'w') as file:
            json.dump(outdated_data, file)
        thread_lock.release()
        my_log.debug('Information about trash was updated')

    def restore_file(self, trash_file: str):
        info = self.upload_data()
        if not (info and trash_file in info):
            my_log.debug(f'Trash {trash_file} was not found in trash')
            raise FileExistsError(f'Sorry, but trash {trash_file} was not found in trash')
        else:
            new_data = info.pop(trash_file)
            path_of_file = os.path.join(self.path_to_the_trash, trash_file)
            path_to_restore = new_data['removed_path']
            self._directory_steps(path_of_file, path_to_restore)
            self.data_update(trash_file)
            my_log.info('File was restored')

    @add_path
    def _deletion(self, path_to_file):
        if os.path.isdir(path_to_file):
            for file in os.listdir(path_to_file):
                file_path = os.path.join(path_to_file, file)
                self._deletion(file_path)
            os.rmdir(path_to_file)
        else:
            my_log.debug('Remove file forever')
            os.remove(path_to_file)

    def delete_forever(self, trash_file: str):
        way_trash = os.path.join(self.path_to_the_trash, trash_file)
        data = self.upload_data()
        if not (data and trash_file in data):
            raise FileExistsError(f'Trash was not found')
        else:
            self._deletion(way_trash)
            my_log.info(f'File was deleted {trash_file} forever')
            my_log.debug('Update information')
            data.pop(f'{trash_file}')
            self.data_update(trash_file)

    def clear_all_trash(self):
        file_list = os.listdir(self.path_to_the_trash)
        for file in file_list:
            if file == '.information.json':
                continue
            removal = threading.Thread(target=self.delete_forever, args=(file[:],))
            removal.start()
        my_log.info('Trash all cleared')

s