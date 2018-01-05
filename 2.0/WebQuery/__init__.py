# -*- coding: utf-8 -*-
# Copyright: kuangkuang <upday7@163.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Project : WebQuery
Created: 12/24/2017
"""
import json
import random
import re
from functools import partial

from anki.hooks import addHook
# noinspection PyArgumentList
from anki.lang import _
from aqt import *
from aqt.models import Models
from aqt.utils import tooltip, restoreGeom

from .uuid import uuid4

# region bytes
items_bytes = bytearray(
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f'
    b'\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x0b\x13'
    b'\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00MIDAT8\x8d\xd5\x91\xc1\t\xc00\x0c\xc4TO'
    b'\x96\rL6\xf2F\x877\xc8d\xa6\xafB\x9f!P\xd2\xe8\x7fpB\xb0\x9b\x0b\xa0\xf7\x1e\x92\xc2\xdd'
    b'\x9b\x99\xb5\xd9\xb1\xa4\xb0\xaf\x9eM\xb3\xa4PU#3\x07\xc0\xa1\n\x0f\x87Vx\x17\x80?T\xd8'
    b'\xcf\r\xa5\x9e(\r0\x19&\xcc\x00\x00\x00\x00IEND\xaeB`\x82')

# endregion

# region Globals
this_addon_folder = os.path.split(__file__)[0]
webq_model_config_json_file = os.path.join(this_addon_folder, "web_query_model_config.json")


# endregion


# region Meta classes

# noinspection PyPep8Naming
class _MetaConfigObj(type):
    """
    Meta class for reading/saving config.json for anki addon
    """
    metas = {}

    class StoreLocation:
        Profile = 0
        AddonFolder = 1
        MediaFolder = 3

    # noinspection PyArgumentList
    def __new__(mcs, name, bases, attributes):

        config_dict = {k: attributes[k] for k in attributes.keys() if not k.startswith("_") and k != "Meta"}
        attributes['config_dict'] = config_dict

        for k in config_dict.keys():
            attributes.pop(k)
        c = super(_MetaConfigObj, mcs).__new__(mcs, name, bases, attributes)

        # region Meta properties
        # meta class
        meta = attributes.get('Meta', type("Meta", (), {}))
        # meta values
        setattr(meta, "config_dict", config_dict)
        setattr(meta, "__StoreLocation__", getattr(meta, "__StoreLocation__", 0))
        setattr(meta, "__config_file__", getattr(meta, "__config_file__", "config.json"))

        _MetaConfigObj.metas[c.__name__] = meta
        # endregion

        if not config_dict:
            return c

        mcs.attributes = attributes  # attributes that is the configuration items

        setattr(c, "media_json_file", mcs.MediaConfigJsonFile("_{}_{}".format(_MetaConfigObj.AddonModelName(),
                                                                              _MetaConfigObj.metas[
                                                                                  name].__config_file__).lower()))

        return c

    def __getattr__(cls, item):
        if item == "meta":
            return _MetaConfigObj.metas[cls.__name__]
        else:
            load_config = lambda: cls.get_config(cls.metas[cls.__name__].__StoreLocation__)
            config_obj = load_config()
            return config_obj.get(item)

    def __setattr__(cls, key, value):
        """
        when user set values to addon config obj class, will be passed to anki's addon manager and be saved.
        :param key:
        :param value:
        :return:
        """
        try:
            config_obj = cls.get_config(cls.metas[cls.__name__].__StoreLocation__)
            config_obj[key] = value
            store_location = cls.metas[cls.__name__].__StoreLocation__
            if store_location == cls.StoreLocation.AddonFolder:
                if cls.IsAnki21:
                    mw.addonManager.writeConfig(cls.AddonModelName, config_obj)
                else:
                    with open(cls.ConfigJsonFile(), "w") as f:
                        json.dump(config_obj, f)
            elif store_location == cls.StoreLocation.MediaFolder:
                with open(cls.media_json_file, "w") as f:
                    json.dump(config_obj, f)
            elif store_location == _MetaConfigObj.StoreLocation.Profile:
                if _MetaConfigObj.IsAnki21():
                    mw.pm.profile.update(config_obj)
                else:
                    mw.pm.meta.update(config_obj)
        except:
            super(_MetaConfigObj, cls).__setattr__(key, value)

    def get_config(cls, store_location):
        """

        :param store_location:
        :rtype: dict
        """

        def _get_json_dict(json_file):
            if not os.path.isfile(json_file):
                with open(json_file, "w") as f:
                    json.dump(cls.config_dict, f)
            with open(json_file, 'r') as ff:
                return json.load(ff)

        disk_config_obj = {}
        if store_location == _MetaConfigObj.StoreLocation.Profile:
            if _MetaConfigObj.IsAnki21():
                disk_config_obj = mw.pm.profile
            else:
                disk_config_obj = mw.pm.meta
        elif store_location == _MetaConfigObj.StoreLocation.AddonFolder:
            # ensure json file
            obj = _get_json_dict(_MetaConfigObj.ConfigJsonFile())

            if _MetaConfigObj.IsAnki21():
                disk_config_obj = mw.addonManager.getConfig(_MetaConfigObj.AddonModelName())
            else:
                disk_config_obj = obj
        elif store_location == _MetaConfigObj.StoreLocation.MediaFolder:
            disk_config_obj = _get_json_dict(cls.media_json_file)
        cls.config_dict.update(disk_config_obj)
        return cls.config_dict

    @staticmethod
    def IsAnki21():
        from anki import version
        return eval(version[:3]) >= 2.1

    @staticmethod
    def ConfigJsonFile():
        return os.path.join(_MetaConfigObj.AddonsFolder(), "config.json")

    @staticmethod
    def MediaConfigJsonFile(file_nm):
        return os.path.join(_MetaConfigObj.MediaFolder(), file_nm)

    @staticmethod
    def AddonsFolder():
        if _MetaConfigObj.IsAnki21():
            _ = os.path.join(mw.addonManager.addonsFolder(), _MetaConfigObj.AddonModelName())
        else:
            _ = os.path.join(mw.pm.addonFolder(), _MetaConfigObj.AddonModelName())
        if aqt.isWin:
            _ = _.encode(aqt.sys.getfilesystemencoding()).decode("utf-8")
        return _.lower()

    @staticmethod
    def AddonModelName():
        return __name__.split(".")[0]

    @staticmethod
    def MediaFolder():
        return os.path.join(mw.pm.profileFolder(), "collection.media")


# endregion

# region Auto-Update

try:
    import urllib2 as web
    from urllib import urlretrieve
except ImportError:
    from urllib import request as web
    from urllib.request import urlretrieve


class AddonUpdater(QThread):
    """
    Class for auto-check and upgrade source codes, uses part of the source codes from ankiconnect.py : D
    """

    def __init__(self, parent,
                 addon_name,
                 version_py,
                 source_zip,
                 local_dir, current_version, version_key_word="__version__"):
        """
        :param parent: QWidget
        :param addon_name: addon name
        :param version_key_word: version variable name, should be in format "X.X.X", this keyword should be stated in the first lines of the file
        :param version_py: remote *.py file possibly on github where hosted __version__ variable
        :param source_zip: zip file to be downloaded for upgrading
        :param local_dir: directory for extractions from source zip file
        :param current_version: current version string in format "X.X.X"

        :type parent: QWidget
        :type addon_name: str
        :type version_key_word: str
        :type version_py: str
        :type source_zip: str
        :type local_dir: str
        :type current_version: str
        """
        super(AddonUpdater, self).__init__(parent)
        self.source_zip = source_zip
        self.version_py = version_py
        self.local_dir = local_dir
        self.version_key_word = version_key_word
        self.addon_name = addon_name
        self.current_version = current_version

    @property
    def has_new_version(self):
        try:
            cur_ver = self._make_version_int(self.current_version)
            remote_ver = self._make_version_int(
                [l for l in self._download(self.version_py).split("\n") if self.version_key_word in l][0].split("=")[1])
            return cur_ver < remote_ver
        except:
            return False

    @staticmethod
    def _download(url):
        if url.lower().endswith(".py"):
            try:
                resp = web.urlopen(url, timeout=10)
            except web.URLError:
                return None

            if resp.code != 200:
                return None

            return resp.read()
        else:
            with open(urlretrieve(url)[0], "rb") as f:
                b = f.read()
            return b

    @staticmethod
    def _make_version_int(ver_string):
        ver_str = "".join([n for n in str(ver_string) if n in "1234567890"])
        return int(ver_str)

    @staticmethod
    def _make_data_string(data):
        return data.decode('utf-8')

    def upgrade(self):
        response = QMessageBox.question(
            self.parent(),
            self.addon_name,
            'Upgrade to the latest version?',
            QMessageBox.Yes | QMessageBox.No
        )

        if response == QMessageBox.Yes:
            try:
                data = self._download(self.source_zip)
                if data is None:
                    QMessageBox.critical(self.parent(),
                                         self.addon_name, 'Failed to download latest version.')
                else:
                    zip_path = os.path.join(self.local_dir,
                                            uuid4().hex + ".zip")
                    with open(zip_path, 'wb') as fp:
                        fp.write(data)

                    # unzip
                    from zipfile import ZipFile
                    zip_file = ZipFile(zip_path)
                    if not os.path.isdir(self.local_dir):
                        os.makedirs(self.local_dir, exist_ok=True)
                    for names in zip_file.namelist():
                        zip_file.extract(names, self.local_dir)
                    zip_file.close()

                    # remove zip file
                    os.remove(zip_path)

                    QMessageBox.information(self.parent(), self.addon_name,
                                            'Upgraded to the latest version, please restart Anki.')

                    return True
            except:
                QMessageBox.critical(self.parent(), self.addon_name,
                                     'Upgraded operation failed!')
            return False

    def run(self):
        if self.has_new_version:
            self.upgrade()


# endregion

class SyncConfig:
    __metaclass__ = _MetaConfigObj

    class Meta:
        __StoreLocation__ = _MetaConfigObj.StoreLocation.MediaFolder

    doc_size = (405, 808)
    image_field_map = {}
    qry_field_map = {}
    visible = True
    append_mode = False
    auto_save = False


class ProfileConfig:
    __metaclass__ = _MetaConfigObj

    class Meta:
        __StoreLocation__ = _MetaConfigObj.StoreLocation.Profile

    is_first_webq_run = True


class UserConfig:
    __metaclass__ = _MetaConfigObj

    class Meta:
        __StoreLocation__ = _MetaConfigObj.StoreLocation.MediaFolder
        __config_file__ = "user_cfg.json"

    load_on_question = True
    image_quality = 50
    provider_urls = [
        ("Bing", "https://www.bing.com/images/search?q=%s"),
        ("Wiki", "https://en.wikipedia.org/wiki/?search=%s"),
    ]
    preload = True


# endregion
class _Page(QWebPage):
    def __init__(self, parent, keyword=None, provider_url=''):
        super(_Page, self).__init__(parent)
        self.clicked_img_url = None
        self.keyword = keyword
        self._provider_url = provider_url

    def userAgentForUrl(self, url):
        return 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X) ' \
               'AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A93 '

    @property
    def provider(self):
        return self._provider_url

    @provider.setter
    def provider(self, val):
        self._provider_url = val

    # noinspection PyArgumentList
    def get_url(self):
        return QUrl(self.provider % self.keyword)

    def load(self, keyword):
        self.keyword = keyword
        if not keyword:
            url = QUrl('about:blank')
        else:
            url = self.get_url()
        self.mainFrame().load(url)


class _WebView(QWebView):

    def __init__(self, parent):
        super(_WebView, self).__init__(parent)
        self.qry_page = None

    def add_query_page(self, page):
        if not self.qry_page:
            self.qry_page = page
        self.setPage(self.qry_page)

    def load_page(self):
        if self.qry_page:
            self.qry_page.load()


class ImageLabel(QLabel):
    cropMode = True
    mouse_released = pyqtSignal()
    canceled = pyqtSignal(bool)

    def __init__(self):
        super(ImageLabel, self).__init__()
        self._image = None

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, img):
        self._image = img
        self.setPixmap(QPixmap.fromImage(img))

    def mouseReleaseEvent(self, event):
        self.crop()
        self.mouse_released.emit()

    def mousePressEvent(self, event):
        """

        :type event: QMouseEvent
        :return:
        """
        if event.button() == Qt.LeftButton:
            print("ImageHolder: " + str(event.pos()))
            self.mousePressPoint = event.pos()
            if self.cropMode:
                if hasattr(self, "currentQRubberBand"):
                    self.currentQRubberBand.hide()
                self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)
                self.currentQRubberBand.setGeometry(QRect(self.mousePressPoint, QSize()))
                self.currentQRubberBand.show()
        else:
            if self.currentQRubberBand:
                self.currentQRubberBand.hide()
            self.canceled.emit(True)

    def mouseMoveEvent(self, event):
        # print("mouseMove: " + str(event.pos()))
        if self.cropMode:
            self.currentQRubberBand.setGeometry(QRect(self.mousePressPoint, event.pos()).normalized())

    def paintEvent(self, event):
        if not self.image:
            return
        self.painter = QPainter(self)
        self.painter.setPen(QPen(QBrush(QColor(255, 241, 18, 100)), 15, Qt.SolidLine, Qt.RoundCap))
        self.painter.drawImage(0, 0, self.image)
        self.painter.end()

    def crop(self):
        rect = self.currentQRubberBand.geometry()
        self.image = self.image.copy(rect)
        self.setMinimumSize(self.image.size())
        self.resize(self.image.size())
        # QApplication.restoreOverrideCursor()
        self.currentQRubberBand.hide()
        self.repaint()


# noinspection PyMethodMayBeStatic
class CaptureOptionButton(QPushButton):
    field_changed = pyqtSignal(int)
    query_field_change = pyqtSignal(int)

    def __init__(self, parent, icon=None):
        if icon:
            super(CaptureOptionButton, self).__init__(icon, "", parent)
        else:
            super(CaptureOptionButton, self).__init__("Options", parent)
        self.fld_names = []
        self.selected_index = 1

        # set style
        # self.setFlat(True)
        self.setToolTip("Capture Options")

        # setup menu
        self.menu = QMenu(self)

        # init objects before setting up
        self.field_menu = None
        self.field_action_grp = None
        self.qry_field_menu = None
        self.qry_field_action_grp = None

        # setup option actions
        self.setup_option_actions()
        self.setup_image_field([])
        self.setup_query_field([])

        # add menu to button
        self.setMenu(self.menu)

        self.setText("Options")

    def setup_query_field(self, fld_names, selected_index=0):
        self.query_fld_names = fld_names
        if not self.qry_field_menu:
            pix = QPixmap()
            pix.loadFromData(items_bytes)
            icon = QIcon(pix)
            self.qry_field_menu = QMenu("Query Field", self.menu)
            self.qry_field_menu.setIcon(icon)
        if not self.qry_field_action_grp:
            self.qry_field_action_grp = QActionGroup(self.qry_field_menu)
            self.qry_field_action_grp.triggered.connect(self.qry_field_action_triggered)
        if self.query_fld_names:
            list(map(
                self.qry_field_action_grp.removeAction,
                self.qry_field_action_grp.actions()
            ))
            added_actions = list(map(
                self.qry_field_action_grp.addAction,
                self.query_fld_names
            ))
            if added_actions:
                list(map(lambda action: action.setCheckable(True), added_actions))
                selected_action = added_actions[selected_index]
                selected_action.setChecked(True)

        self.qry_field_menu.addActions(self.qry_field_action_grp.actions())
        self.menu.addSeparator().setText("Fields")
        self.menu.addMenu(self.qry_field_menu)

    def setup_image_field(self, fld_names, selected_index=1):
        self.fld_names = fld_names
        if not self.field_menu:
            pix = QPixmap()
            pix.loadFromData(items_bytes)
            icon = QIcon(pix)
            self.field_menu = QMenu("Image Field", self.menu)
            self.field_menu.setIcon(icon)
        if not self.field_action_grp:
            self.field_action_grp = QActionGroup(self.field_menu)
            self.field_action_grp.triggered.connect(self.field_action_triggered)
        if self.fld_names:
            list(map(
                self.field_action_grp.removeAction,
                self.field_action_grp.actions()
            ))
            added_actions = list(map(
                self.field_action_grp.addAction,
                self.fld_names
            ))
            if added_actions:
                list(map(lambda action: action.setCheckable(True), added_actions))
                selected_action = added_actions[selected_index]
                selected_action.setChecked(True)
                self.selected_index = selected_index
                # self.setText(selected_action.text())

        self.field_menu.addActions(self.field_action_grp.actions())
        self.menu.addSeparator().setText("Fields")
        self.menu.addMenu(self.field_menu)

    def setup_option_actions(self):
        # setup actions
        self.action_append_mode = QAction("Append Mode", self.menu)
        self.action_append_mode.setCheckable(True)
        self.action_append_mode.setToolTip("Append Mode: Check this if you need captured image to be APPENDED "
                                           "to field instead of overwriting it")
        self.action_append_mode.setChecked(SyncConfig.append_mode)

        self.action_auto_save = QAction("Auto-Save", self.menu)
        self.action_auto_save.setCheckable(True)
        self.action_auto_save.setToolTip("Auto-Save: If this is checked, image will be saved "
                                         "immediately once completed cropping.")
        self.action_auto_save.setChecked(SyncConfig.auto_save)

        # bind action slots
        self.action_append_mode.toggled.connect(self.on_append_mode)
        self.action_auto_save.toggled.connect(self.on_auto_save)

        # add actions to menu
        self.menu.addActions([
            ac for ac in map(lambda nm: getattr(self, nm),
                             [att for att in dir(self) if att.startswith("action_")])
        ])

    def qry_field_action_triggered(self, action):
        """

        :type action: QAction
        :return:
        """
        self.qry_selected_index = self.qry_field_action_grp.actions().index(action)
        action.setChecked(True)
        # self.setText(self.qry_field_action_grp.actions()[self.qry_selected_index].text())
        self.query_field_change.emit(self.qry_selected_index)

    def field_action_triggered(self, action):
        """

        :type action: QAction
        :return:
        """
        self.selected_index = self.field_action_grp.actions().index(action)
        action.setChecked(True)
        # self.setText(self.field_action_grp.actions()[self.selected_index].text())
        self.field_changed.emit(self.selected_index)

    def on_append_mode(self, checked):
        SyncConfig.append_mode = True if checked else False

    def on_auto_save(self, checked):
        SyncConfig.auto_save = True if checked else False


class ResizeButton(QPushButton):
    def __init__(self, parent, dock_widget):
        super(ResizeButton, self).__init__("<>", parent)
        self.start_resize = False
        self.dock_widget = dock_widget
        self.setFixedWidth(10)
        self.setToolTip("Press to change the width of this dock!")

    def mouseReleaseEvent(self, evt):
        self.start_resize = False

    def mousePressEvent(self, evt):
        self.start_resize = True

    def mouseMoveEvent(self, evt):
        if self.start_resize:
            new_width = QApplication.desktop().rect().right() - QCursor().pos().x()
            self.dock_widget.setFixedWidth(new_width)
            doc_size = (new_width, self.dock_widget.height())
            SyncConfigdoc_size = doc_size
            self.dock_widget.resize(QSize(new_width, self.dock_widget.height()))
        evt.accept()


class WebQueryWidget(QWidget):
    img_saving = pyqtSignal(QImage)
    capturing = pyqtSignal()
    viewing = pyqtSignal()

    def add_query_page(self, page):
        self._view.add_query_page(page)

        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, True)
        self.show_grp(self.capture_grp, False)

    def reload(self):
        self._view.reload()

    def __init__(self, parent):
        super(WebQueryWidget, self).__init__(parent)

        # all widgets
        self._view = _WebView(self)
        self.lable_img_capture = ImageLabel()
        self.lable_img_capture.mouse_released.connect(self.cropped)
        self.lable_img_capture.canceled.connect(self.crop_canceled)

        self.loading_lb = QLabel()
        self.capture_button = QPushButton('Capture (C)', self)
        self.capture_button.setShortcut(QKeySequence(Qt.Key_C))
        self.capture_button.clicked.connect(self.on_capture)

        self.return_button = QPushButton('Return', self)
        self.return_button.setMaximumWidth(100)
        self.return_button.setShortcut(QKeySequence("ALT+Q"))
        self.return_button.clicked.connect(self.on_view)

        # region Save Image Button and Combo Group
        self.save_img_button = QPushButton('Save (C)', self)
        self.save_img_button.setShortcut(QKeySequence(Qt.Key_C))
        self.save_img_button.setShortcutEnabled(Qt.Key_C, False)
        self.save_img_button.clicked.connect(self.save_img)

        # just in case dock cannot be resized properly
        dock_widget = self.parent()
        assert isinstance(dock_widget, QDockWidget)
        dock_widget.setFixedWidth(SyncConfig.doc_size[0])
        self.resize_btn = ResizeButton(self, dock_widget)

        self.capture_option_btn = CaptureOptionButton(self)
        self.capture_option_btn.setMaximumWidth(100)
        self.img_btn_grp_ly = QHBoxLayout()
        self.img_btn_grp_ly.addWidget(self.resize_btn)
        self.img_btn_grp_ly.addSpacing(5)
        self.img_btn_grp_ly.addWidget(self.capture_option_btn)
        self.img_btn_grp_ly.addWidget(self.return_button)
        self.img_btn_grp_ly.addWidget(self.save_img_button)
        self.img_btn_grp_ly.addWidget(self.capture_button)

        # endregion

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.loading_lb, alignment=Qt.AlignCenter)
        self.layout.addWidget(self._view)
        self.layout.addWidget(self.lable_img_capture, alignment=Qt.AlignCenter)
        self.layout.addItem(self.img_btn_grp_ly)

        # widget groups
        self.loading_grp = [self.loading_lb]
        self.view_grp = [self._view, self.capture_button, self.capture_option_btn]
        self.capture_grp = [self.lable_img_capture, self.return_button, self.save_img_button, ]

        # Visible
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, False)
        self.show_grp(self.capture_grp, False)

        # other slots
        self._view.loadStarted.connect(self.loading_started)
        self._view.loadFinished.connect(self.load_completed)

        self.setLayout(self.layout)

        # variable
        self._loading_url = ''

    def loading_started(self):
        loading_gif_dir = os.path.join(this_addon_folder, "loading_gif")
        if os.path.isdir(loading_gif_dir):
            gifs = [f for f in os.listdir(loading_gif_dir) if os.path.isfile(os.path.join(loading_gif_dir, f))
                    and f.upper().strip().endswith(".GIF")]
        else:
            gifs = []
        if gifs:
            gif = random.choice(gifs)
            gif = os.path.join(loading_gif_dir, gif)
        else:
            gif = os.path.join(this_addon_folder, "loading.gif")
        if os.path.isfile(gif):
            mv = QMovie(gif)
            self.loading_lb.setMovie(mv)
            mv.start()

        self.show_grp(self.loading_grp, True)
        self.show_grp(self.view_grp, False)
        self.show_grp(self.capture_grp, False)

    def load_completed(self, *args):
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, True)
        self.show_grp(self.capture_grp, False)

    def show_grp(self, grp, show):
        for c in grp:
            c.setVisible(show)

    def on_capture(self, *args):
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

        self._view.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lable_img_capture.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        rect = self._view.rect()
        self.lable_img_capture.image = QImage(QPixmap.grabWindow(self._view.winId(), rect.x(),
                                                                 rect.y()))
        self.lable_img_capture.adjustSize()

        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, False)
        self.show_grp(self.capture_grp, True)

        # self.lable_img_capture.setVisible(True)

    def on_view(self, *args):
        QApplication.restoreOverrideCursor()

        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, True)
        self.show_grp(self.capture_grp, False)

        self.viewing.emit()
        self._view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.lable_img_capture.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def save_img(self, *args):
        self.img_saving.emit(self.lable_img_capture.image)
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, True)
        self.show_grp(self.capture_grp, False)
        self._view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.lable_img_capture.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def cropped(self):
        QApplication.restoreOverrideCursor()
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, False)
        self.show_grp(self.capture_grp, True)
        if SyncConfig.auto_save:
            self.save_img()
            self.save_img_button.setShortcutEnabled(Qt.Key_C, False)
        else:
            self.save_img_button.setShortcutEnabled(Qt.Key_C, True)

    def crop_canceled(self):
        self.return_button.click()


class ModelDialog(Models):
    # noinspection PyUnresolvedReferences
    def __init__(self, mw, parent=None, fromMain=False):
        # region copied from original codes in aqt.models.Models
        self.mw = mw
        self.parent = parent or mw
        self.fromMain = fromMain
        QDialog.__init__(self, self.parent, Qt.Window)
        self.col = mw.col
        self.mm = self.col.models
        self.mw.checkpoint(_("Note Types"))
        self.form = aqt.forms.models.Ui_Dialog()
        self.form.setupUi(self)
        self.form.buttonBox.helpRequested.connect(lambda: openHelp("notetypes"))
        self.setupModels()
        restoreGeom(self, "models")
        # endregion

        # add additional button
        self.button_tab_visibility = QPushButton("Web Query Tab Visibility", self)
        self.button_tab_visibility.clicked.connect(self.onWebQueryTabConfig)
        self.button_tab_visibility.setEnabled(False)
        self.form.modelsList.itemClicked.connect(
            partial(lambda item: self.button_tab_visibility.setEnabled(True if item else False)))
        self.form.gridLayout_2.addWidget(self.button_tab_visibility, 2, 0, 1, 1)

    @property
    def mid(self):
        return self.model['id']

    @property
    def default_config(self):
        return {str(self.mid):
                # name, provider_url, visibility
                    [[n, u, True] for n, u in UserConfig.provider_urls]
                }

    def onWebQueryTabConfig(self, clicked):
        self.config = self.default_config
        if os.path.isfile(webq_model_config_json_file):
            with open(webq_model_config_json_file, "r") as f:
                try:
                    self.config = json.load(f)
                    default_config_items = self.default_config[str(self.mid)]
                    config_items = self.config[str(self.mid)]
                    if config_items.__len__() < default_config_items.__len__():
                        self.config[str(self.mid)].extend(default_config_items[config_items.__len__():])
                    else:
                        self.config[str(self.mid)] = self.config[str(self.mid)][:default_config_items.__len__()]
                except:
                    pass

        class _dlg(QDialog):
            def __init__(inner_self):
                super(_dlg, inner_self).__init__(self)
                inner_self.setWindowTitle("Toggle Visibility")

                inner_self.mode_config_items = self.config.get(str(self.mid), self.default_config[str(self.mid)])

                # shown check boxes
                inner_self.checkboxes = list(map(
                    lambda args: QCheckBox("{}: {}".format(args[0], args[1]), inner_self),
                    inner_self.mode_config_items)
                )
                list(map(lambda args: args[1].setChecked(inner_self.mode_config_items[args[0]][2]),
                         enumerate(inner_self.checkboxes)))
                list(map(lambda args: args[1].toggled.connect(partial(inner_self.on_visibility_checked, args[0])),
                         enumerate(inner_self.checkboxes)))

                ly = QVBoxLayout(inner_self)
                list(map(ly.addWidget, inner_self.checkboxes))
                inner_self.setLayout(ly)

            def on_visibility_checked(inner_self, index, checked):
                inner_self.mode_config_items[index][2] = checked
                with open(webq_model_config_json_file, "w+") as f:
                    self.config[self.mid] = inner_self.mode_config_items
                    json.dump(self.config, f)

        _dlg().exec_()


class WebQryAddon:

    def __init__(self, version):
        self.shown = False

        # region variables
        self.current_index = 0
        self._first_show = True
        self.version = version

        # endregion

        self.dock = None
        self.pages = []
        self.webs = []
        self._display_widget = None

        addHook("showQuestion", self.start_query)
        addHook("showAnswer", self.show_widget)
        addHook("deckClosing", self.hide)
        addHook("reviewCleanup", self.hide)
        addHook("profileLoaded", self.profileLoaded)

        self.init_menu()

    def cur_tab_index_changed(self, tab_index):
        self.current_index = tab_index
        if not UserConfig.preload:
            self.show_widget()

    @property
    def page(self):
        return self.pages[self.current_index]

    @property
    def web(self):
        return self.webs[self.current_index]

    def init_menu(self):
        action = QAction(mw.form.menuTools)
        action.setText("Web Query")
        action.setShortcut(QKeySequence("ALT+W"))
        mw.form.menuTools.addAction(action)
        action.triggered.connect(self.toggle)

    def profileLoaded(self):
        # region owverwrite note type management
        def onNoteTypes():
            ModelDialog(mw, mw, fromMain=True).exec_()

        mw.form.actionNoteTypes.triggered.disconnect()
        mw.form.actionNoteTypes.triggered.connect(onNoteTypes)
        # eng region

        AddonUpdater(
            mw,
            "Web Query",
            "https://raw.githubusercontent.com/upday7/WebQuery/dev-check_new_version/2.0/webquery.py",
            "https://github.com/upday7/WebQuery/blob/dev-check_new_version/2.0/2.0.zip?raw=true",
            mw.pm.addonFolder(),
            self.version
        ).start()

    # endregion
    @property
    def reviewer(self):
        """

        :rtype: Reviewer
        """
        return mw.reviewer

    @property
    def card(self):
        """

        :rtype: Card
        """
        return self.reviewer.card

    @property
    def note(self):
        """

        :rtype: Note
        """
        return self.reviewer.card.note()

    @property
    def word(self):
        if not mw.reviewer:
            return None
        qry_field = SyncConfig.qry_field_map.get(str(self.note.mid), 0)
        word = re.sub('<[^<]+?>', '', self.note.fields[qry_field]).strip()
        return word

    @property
    def model_config(self):
        default_empty = {str(self.note.mid): {}}
        if os.path.isfile(webq_model_config_json_file):
            with open(webq_model_config_json_file, "r") as f:
                try:
                    config = json.load(f)
                except:
                    config = default_empty
        else:
            config = default_empty
        try:
            return config[str(self.note.mid)]
        except KeyError:
            config = default_empty

        return config[str(self.note.mid)]

    @property
    def model_hidden_tab_index(self):
        if self.model_config:
            model_hidden_tab_index = [i for i, args in enumerate(self.model_config) if not args[2]]
        else:
            model_hidden_tab_index = []
        return model_hidden_tab_index

    def add_dock(self, title):
        config = SyncConfig

        class DockableWithClose(QDockWidget):
            closed = pyqtSignal()

            def __init__(self, title, parent):
                super(DockableWithClose, self).__init__(title, parent)

            def closeEvent(self, evt):
                self.closed.emit()
                QDockWidget.closeEvent(self, evt)

            def resizeEvent(self, evt):
                assert isinstance(evt, QResizeEvent)
                doc_size = (evt.size().width(),
                            evt.size().height())
                config.doc_size = doc_size
                super(DockableWithClose, self).resizeEvent(evt)
                evt.accept()

            # def sizeHint(self):
            #    return QSize(config.doc_size[0], config.doc_size[1])

        dock = DockableWithClose(title, mw)
        # dock.setObjectName(title)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        # region dock widgets
        available_urls = [url for i, (n, url) in enumerate(UserConfig.provider_urls)
                          if i not in self.model_hidden_tab_index]
        self.webs = list(
            map(lambda x: WebQueryWidget(dock, ), range(available_urls.__len__()))
        )
        self.pages = list(
            map(lambda params: _Page(parent=self.webs[params[0]], provider_url=params[1]),
                enumerate(available_urls))
        )

        for web in self.webs:
            web.img_saving.connect(self.save_img)

        # region main / tab widgets
        self._display_widget = QWidget(dock)
        if UserConfig.provider_urls.__len__() - self.model_hidden_tab_index.__len__() > 1:
            self._display_widget = QTabWidget(dock)
            self._display_widget.setTabPosition(self._display_widget.East)
            added_web = 0
            for i, (nm, url) in enumerate(UserConfig.provider_urls):
                if i in self.model_hidden_tab_index:
                    continue
                try:
                    self._display_widget.addTab(self.webs[added_web], nm)
                    added_web += 1
                except IndexError:
                    continue
            self._display_widget.currentChanged.connect(self.cur_tab_index_changed)
        else:
            l = QVBoxLayout(self._display_widget)
            try:
                l.addWidget(self.web)
            except IndexError:
                QMessageBox.warning(
                    mw, "No Provider URL", "You have no <em>[Provider URL]</em>"
                                           " selected<br><br>Go to Tools > Manage Note Types > Web Query Tab Visibility")
                return
            self._display_widget.setLayout(l)
        self._display_widget.setVisible(False)

        # endregion
        dock.setWidget(self._display_widget)
        mw.addDockWidget(Qt.RightDockWidgetArea, dock)

        return dock

    def start_query(self):
        if not self.ensure_dock():
            return
        if not self.word:
            return
        if UserConfig.preload:
            self.start_pages()
        if not UserConfig.load_on_question:
            self.hide_widget()
        else:
            self.show_widget()

    def start_pages(self):
        QApplication.restoreOverrideCursor()
        for wi, web in enumerate(self.webs, ):
            page = self.pages[wi]
            page.loadFinished.connect(lambda s: web.reload)
            page.load(self.word)
            web.add_query_page(page)
            if self.reviewer:
                image_field = SyncConfig.image_field_map.get(str(self.note.mid), 1)
                qry_field = SyncConfig.qry_field_map.get(str(self.note.mid), 0)
                items = [(f['name'], ord)
                         for ord, f in sorted(self.note._fmap.values())]
                web.capture_option_btn.setup_image_field([i for i, o in items], image_field)
                web.capture_option_btn.setup_query_field([i for i, o in items], qry_field)
                web.capture_option_btn.field_changed.connect(self.img_field_changed)
                web.capture_option_btn.query_field_change.connect(self.qry_field_changed)

    def hide_widget(self):
        self._display_widget.setVisible(False)

    def show_widget(self):
        if not self.dock:
            return
        self._display_widget.setVisible(True)
        if self._first_show:
            self.web.reload()
            self._first_show = False
        if not UserConfig.preload:
            self.start_pages()

    def hide(self):
        if self.dock:
            mw.removeDockWidget(self.dock)
            self.dock.destroy()
        self.dock = None

    def show_dock(self):
        self.dock.setVisible(True)

    def ensure_dock(self):
        if ProfileConfig.is_first_webq_run:
            QMessageBox.warning(
                mw, "Web Query", """
                <p>
                    <b>Welcome !</b>
                </p>
                <p>This is your first run of <EM><b>Web Query</b></EM>, please read below items carefully:</p>
                <ul>
                    <li>
                        Choose proper <em>[Image]</em> field in "Options" button in right dock widget 
                        BEFORE YOU SAVING ANY IMAGES, by default its set to the 2nd
                        field of your current note.
                    </li>
                    <li>
                        You are able to change the <em>[Query]</em> field in "Options" also, 
                        which is set to the 1st field by default.
                    </li>
                </ul>
                """)
            ProfileConfig.is_first_webq_run = False

        if not self.dock:
            self.dock = self.add_dock(_('Web Query'), )
            if not self.dock:
                return False
            self.dock.closed.connect(self.on_closed)
        self.dock.setVisible(SyncConfig.visible)
        return True

    def toggle(self):
        if not self.ensure_dock():
            return
        if self.dock.isVisible():
            SyncConfig.visible = False
            self.hide()
        else:
            SyncConfig.visible = True
            self.show_dock()

    def on_closed(self):
        mw.progress.timer(100, self.hide, False)

    def img_field_changed(self, index):
        if index == -1:
            return
        _mp = SyncConfig.image_field_map
        _mp[str(self.note.mid)] = index
        SyncConfig.image_field_map = _mp

        for web in self.webs:
            if not web is self.web:
                items = [(f['name'], ord)
                         for ord, f in sorted(self.note._fmap.values())]
                web.capture_option_btn.setup_image_field([i for i, o in items], index)

    def qry_field_changed(self, index):
        if index == -1:
            return
        _mp = SyncConfig.qry_field_map
        _mp[str(self.note.mid)] = index
        SyncConfig.qry_field_map = _mp

        for web in self.webs:
            if not web is self.web:
                items = [(f['name'], ord)
                         for ord, f in sorted(self.note._fmap.values())]
                web.capture_option_btn.setup_query_field([i for i, o in items], index)

    def save_img(self, img):
        """

        :type img: QImage
        :return:
        """
        img = img.convertToFormat(QImage.Format_RGB32, Qt.ThresholdDither | Qt.AutoColor)
        if not self.reviewer:
            return
        fld_index = self.web.capture_option_btn.selected_index
        anki_label = '<img src="{}">'
        fn = "web_qry_{}.jpg".format(uuid4().hex.upper())
        if SyncConfig.append_mode:
            self.note.fields[fld_index] += anki_label.format(fn)
        else:
            self.note.fields[fld_index] = anki_label.format(fn)
        if img.save(fn, 'jpg', UserConfig.image_quality):
            self.note.flush()
            self.card.flush()
            tooltip("Saved image to current card: {}".format(fn), 5000)
