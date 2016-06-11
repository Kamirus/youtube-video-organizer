from collections import OrderedDict
from editYoutubers import getFullPathOfScript
import json,os

SETTINGS_FILE_NAME = 'settings.json'

# OrderedDict which is the representation of json settings file
# while creating the object: settings file is initialized (default settings) if not found; dict is filled with file
# after cration we can manage this object like normal dictionary, after making changes .save() and done
class Settings(OrderedDict):
    def __init__(self, folderPath='raw/', *args, **kwds):
        super().__init__(*args, **kwds)
        self._folderPath = getFullPathOfScript()+folderPath
        self._path = '{}{}'.format(self._folderPath,SETTINGS_FILE_NAME)
        if SETTINGS_FILE_NAME not in os.listdir(self._folderPath):
            self._init()
        self.load()
        # test
        print(self)

    def load(self):
        try:
            file = open(self._path, 'r')
            self.clear()
            self.update(json.load(file))
            file.close()
        except:
            raise ValueError("[ERROR]\ncannot load settings file")

    def save(self):
        try:
            self._overwriteWith(self)
        except ValueError as e:
            print("While saving error occurred",e,sep='\n')

    def default(self):
        self.clear()
        self.update(self._getDefault())

    def _init(self):
        try:
            self._overwriteWith(self._getDefault())
        except ValueError as e:
            print("While initializing error occurred",e,sep='\n')

    def _getDefault(self) -> OrderedDict:
        # here define what you want to have in settings file
        res = OrderedDict()

        res['tags'] = ['funny','music','vlog','gameplay','education']

        return res

    def _overwriteWith(self, Dict:OrderedDict):
        try:
            file = open(self._path, 'w' )
            json.dump(Dict,
                      file,
                      indent=4,
                      ensure_ascii=False)
            file.close()
        except Exception as e:
            print(e)
            raise ValueError("Something went wrong while overwritting settings file ({})".format(self._path))