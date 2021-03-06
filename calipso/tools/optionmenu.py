from Tkconstants import RAISED
from Tkinter import Menubutton, TclError, Widget, Menu


class _SetIt:
    """
    Internal class for wrapping command into widget OptionMenu
    """
    def __init__(self, var, value, callback=None):
        self.__value = value
        self.__var = var
        self.__callback = callback

    def __call__(self, *args):
        self.__var.set(self.__value)
        if self.__callback:
            self.__callback(self.__value, *args)


class ShapeOptionMenu(Menubutton):
    """
    Custom OptionMenu which allows the user to select a value from
    a menu and update upon button click.

    :param master: The widget to draw to
    :param variable: A ``StringVar()`` object for displaying options
    :param str value: The default value of the menu
    :param **kwargs: Tkinter dict args *note:* **only** supports `-command`
    """

    def __init__(self, master, variable, value, **kwargs):
        kw = {'borderwidth': 2, 'textvariable': variable,
              'indicatoron': 1, 'relief': RAISED, 'anchor': 'c',
              'highlightthickness': 2}
        Widget.__init__(self, master, 'menubutton', kw)
        self.var = variable
        self.widget_name = 'tk_optionmenu'
        self.__menu = Menu(self, name='menu', tearoff=0)
        self.menu_name = self.__menu._w
        self.callback = kwargs.get('command')
        if 'command' in kwargs:
            del kwargs['command']
        if kwargs:
            raise TclError('unknown option -' + kwargs.keys()[0])
        self.__menu.add_command(label=value,
                                command=_SetIt(variable, value, self.callback))
        self['menu'] = self.__menu

    def set_menu(self, options):
        """
        Set the internal menu, this allows the program to dynamically
        create menus on the fly when a user clicks.

        :param list options: A list of :py:class:`str` objects which is the new menu
        """
        del self.__menu
        self.__menu = Menu(self, name='menu', tearoff=0)
        for op in options:
            self.__menu.add_command(label=op,
                                    command=_SetIt(self.var, op,
                                                   self.callback))
