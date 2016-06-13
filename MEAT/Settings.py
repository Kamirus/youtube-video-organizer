from collections import OrderedDict
import json,os,inspect

SETTINGS_FILE_NAME = 'settings.json'

# With that we can have full path
def getFullPathOfScript():
    return "%s/" % os.path.dirname(
            os.path.abspath(
                inspect.getfile(inspect.currentframe())
                )
            )

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

    def merge(self, older):
    # this method will add elements from older which werent in this dict
        for k,v in older.items():
            try:
                self[k]
            except:
                self[k] = older[k]

    def default(self):
        self.clear()
        self.update(self.getDefault())

    def getDefault(self) -> OrderedDict:
        # here define what you want to have in settings file
        res = OrderedDict()

        res['maxCharsForTitle'] = None
        # res['tags'] = ['funny','music','vlog','gameplay','education']
        res['dontChangeValuesInThatListWhileUpdatingAll'] = ['show','seen','tags']

        return res

    def _init(self):
        try:
            self._overwriteWith(self.getDefault())
        except ValueError as e:
            print("While initializing error occurred",e,sep='\n')


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