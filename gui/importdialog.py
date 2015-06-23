'''
Created on Jun 15, 2015

@author: Grant Mercer

'''

import collections, string
from Tkinter import Toplevel, Entry, Button, BOTH, Frame, \
    Label, BOTTOM, TOP, X, RIDGE

from gui import Constants
from gui.db import db, dbPolygon
from gui.tools import TreeListBox, center
from sqlalchemy import or_
#import TkTreectrl as treectrl
#import db

class dbDialog(Toplevel):
    '''
    Dialog window which prompts user for a selection of objects to import as well as
    showing a customizable list for displaying the data
    '''
    def __init__(self, root, master):
        '''
        root -> root tk widget, often Tk()
        master -> the main window, for access of polygonList
        '''
        Toplevel.__init__(self, root)
        self.protocol('WM_DELETE_WINDOW')
                
        self.session = db.getSession()
        self.__itList = list()
        self.__stack = collections.deque(maxlen=15)
        self.__searchString = ""
        self.__master = master        
        self.title("Import from existing database")
        center(self, (Constants.IMPORTWIDTH,Constants.IMPORTHEIGH)) # simple function to center window and set size
        
        self.container = Frame(self)                                # create center frame, for use of splitting window horizontally later
        self.container.pack(side=TOP, fill=BOTH, expand=True)       # place
        
        self.createTopFrame()                                       # create the top frame and pack buttons / etc. on it
        self.createBottomFrame()                                    # create the bottom frame and pack
        
    def createTopFrame(self):
        '''
        Initialize the upper frame of the window in charge of buttons
        '''
        self.topFrame = Frame(self.container)                       # create top frame
        self.topFrame.pack(side=TOP, fill=X, expand=False)
        
        self.label = Label(self.topFrame, text="Search ")           # search label 
        self.e = Entry(self.topFrame)                               # input box for searching specific attributes
        self.e.bind("<KeyRelease>", self.refineSearch)
        self.label.grid(row=0, column=0, padx=5, pady=10)
        self.e.grid(row=0, column=1, padx=5, pady=10)
            
        # custom command for filtering objects by properties
        self.filterButton = Button(self.topFrame, text="Filter", command=self.filterDialog,
                                   width=10)
        self.filterButton.grid(row=0, column=3, padx=5, pady=10)
        
    def refineSearch(self, event):
        lst = list()
        if event.char.isalnum(): self.__searchString += event.char
        print "char: ", repr(event.char), "searchString ", self.__searchString
        if self.e.get() != '':
            print "not empty...."
            if event.char == '':
                print "popping stack..."
                self.__searchString = self.__searchString[:-1]
                if self.__stack : 
                    del self.tree.info[:]
                    self.tree.info = self.__stack.pop()
                    self.tree.update()
            elif event.char.isalnum():
                print "searching...", [s[4] for s in self.tree.info if self.__searchString in s[4]]
                for obj in self.session.query(dbPolygon).filter(or_(
                        dbPolygon.tag.contains(self.__searchString), 
                        dbPolygon.attributes.contains(self.__searchString),
                        dbPolygon.notes.contains(self.__searchString))):
                    lst.append(                                                          # user see's this list
                        (obj.tag, obj.plot, obj.time_, obj.hdf, obj.attributes[1:-1], obj.notes)
                    )
                self.__stack.append(self.tree.info)
                self.tree.info = lst
                self.tree.update()
        else:
            self.__searchString = ""
            self.__displayAll()
            
        """
        for obj in self.session.query(dbPolygon).filter(or_( \
                        dbPolygon.tag.in_([s[0] for s in self.tree.info if self.__searchString in s[0]]), \
                        dbPolygon.attributes.in_([s[4] for s in self.tree.info if self.__searchString in s[4]]))):
        """
            
 
        #print "tree: ",self.tree.list
        
    def createBottomFrame(self):
        '''
        Create and display database in listbox, also add lower button frame for import
        button
        '''
        self.bottomFrame = Frame(self.container)                                            # create bottom frame
        self.bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=True)          
        self.separator = Frame(self.bottomFrame, relief=RIDGE, height=2, bg="gray")         # tiny separator splitting the top and bottom frame
        self.separator.pack(side=TOP, fill=X, expand=False)
        self.bottomButtonFrame = Frame(self.bottomFrame)                                    # bottom frame for import button
        self.bottomButtonFrame.pack(side=BOTTOM, fill=X, expand=False)
        
        self.tree = TreeListBox(self.bottomFrame,
            ['name', 'plot', 'date', 'file', 'attributes', 'notes'])
        
        for obj in self.session.query(dbPolygon).all():
            self.__itList.append(obj)                                                       # insert JSON obj representation into internal list
        
        self.__displayAll()
           
        self.button = Button(self.bottomButtonFrame, text="Import", width=30,
                             command=self.importSelection)
        self.button.pack(side=BOTTOM, pady=10)
    
    def importSelection(self):
        '''
        Import selected objects from libox into program
        '''
        items = self.tree.tree.selection()
        for tag in items:
            tag = self.tree.tree.item(tag, option="values")
            # the tag represents the selected item, but must be converted to an index
            #print self.__itList[idx]
            names = [x.tag for x in self.__itList]
            self.__master.getPolygonList().readPlot(
                readFromString=str(self.__itList[names.index(tag[0])]))
        self.free()
            
    def filterDialog(self):
        pass
    
    def __displayAll(self):
        lst = list()
        self.__offset = 0
        if self.tree.info : self.__stack.append(self.tree.info)
        for obj in self.session.query(dbPolygon).all():
            lst.append(                                                          # user see's this list
                (obj.tag, obj.plot, obj.time_, obj.hdf, obj.attributes[1:-1], obj.notes)
            )
            
        self.tree.info = lst
        self.tree.update()
        
    def free(self):
        '''
        Free window
        '''
        self.session.commit()
        self.session.close()
        self.destroy()
        
