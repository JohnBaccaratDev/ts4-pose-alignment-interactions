import inspect
import os
import sims4


class PaiConfig():
    with sims4.reload.protected(globals()):
        _to_export = list()
        _reading_config = False

    class classproperty:
        def __init__(self, fget=None, fset=None):
            self.fget = fget
            self.fset = fset

        def __get__(self, instance, owner):
            if self.fget is None:
                raise AttributeError("unreadable attribute")
            return self.fget(owner)

        def __set__(self, instance, value):
            if self.fset is None:
                raise AttributeError("can't set attribute")
            return self.fset(type(instance) if instance else instance, value)

        def getter(self, func):
            return type(self)(func, self.fset)

        def setter(self, func):
            return type(self)(self.fget, func)

    _affect_all_posed = False

    @classproperty
    def affect_all_posed(cls) -> bool:
        return cls._affect_all_posed
    @affect_all_posed.setter
    def affect_all_posed(cls, value):
        cls._affect_all_posed = value

    _auto_snapping_move_rotate = False

    @classproperty
    def auto_snapping_move_rotate(cls) -> bool:
        return cls._auto_snapping_move_rotate
    @auto_snapping_move_rotate.setter
    def auto_snapping_move_rotate(cls, value):
        cls._auto_snapping_move_rotate = value


    # Don't ask me why this only returns the proper attributes the first time.
    @classmethod
    def get_to_export(cls):
        if len(cls._to_export) > 0:
            return

        for attr in dir(cls):
            raw_attr = inspect.getattr_static(cls, attr)
            if type(raw_attr).__name__ == "classproperty":
                cls._to_export.append(attr)


    @classmethod
    def get_config_path(cls):
        path = os.path.abspath(__file__)
        while not os.path.isdir(path):
            path = os.path.dirname(path)

        return os.path.join(path, "JohnBaccarat_PoseAlignmentInteractions.ini")


    @classmethod
    def read_config(cls):

        path = cls.get_config_path()

        if not os.path.isfile(path):
            cls.write_config()
            return

        cls._reading_config = True
        with open(cls.get_config_path(), "r") as config:
            for line in config:
                parts = line.split("=")
                if len(parts) > 1 and parts[0] in cls._to_export:
                    s = "=".join(parts[1:])
                    if isinstance(getattr(cls, parts[0]), bool):
                        v = s.lower().strip() in ("true", "1", "y", "yes")
                    else:
                        v = s
                    setattr(cls, parts[0], v)

        cls._reading_config = False


    @classmethod
    def write_config(cls):
        if cls._reading_config:
            return

        with open(cls.get_config_path(), "w") as config:
            for attr in cls._to_export:
                prop = getattr(cls, attr)
                config.writelines(["\n", str(attr) + "=" + str(prop)])
