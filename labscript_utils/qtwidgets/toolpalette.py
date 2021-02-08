#####################################################################
#                                                                   #
# toolpalette.py                                                    #
#                                                                   #
# Copyright 2013, Monash University                                 #
#                                                                   #
# This file is part of the labscript suite (see                     #
# http://labscriptsuite.org) and is licensed under the Simplified   #
# BSD License. See the license.txt file in the root of the project  #
# for the full license.                                             #
#                                                                   #
#####################################################################
import sys

from qtutils.qt.QtCore import *
from qtutils.qt.QtGui import *
from qtutils.qt.QtWidgets import *

EXPAND_ICON = ':/qtutils/fugue/toggle-small-expand'
CONTRACT_ICON = ':/qtutils/fugue/toggle-small'

_ENABLE_LAYOUT_EVENT_TYPE = QEvent.User

class ToolPaletteGroup(QVBoxLayout):
    
    def __init__(self,*args,**kwargs):
        QVBoxLayout.__init__(self,*args,**kwargs)
        self._widget_groups = {}
        self._width_groups = {}
        self._all_widths_linked = False
    
    # Creates and appends a new ToolPalette to this group
    # A reference to the new ToolPalette is returned
    def append_new_palette(self,name,*args,**kwargs):
        if name in self._widget_groups:
            raise RuntimeError('The tool palette group already has a palette named %s'%name)
            
        # Create the tool palette and store a reference to it and an index indicating the order of Tool Palettes
        tool_palette = ToolPalette(self,name,*args,**kwargs)
        push_button = QPushButton(name)        
        push_button.setIcon(QIcon(CONTRACT_ICON))
        push_button.setFocusPolicy(Qt.NoFocus)
        push_button.setToolTip('Click to hide')

        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0,0,0,0)
        frame_layout.setSpacing(0)

        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.addWidget(push_button)
        header_layout.addStretch(1)
        header_widget.setLayout(header_layout)
        header_layout.setContentsMargins(3,3,3,3)
        
        def create_callback(name):
            return lambda: self._on_button_clicked(name)
            
        push_button.clicked.connect(create_callback(name))
        self._widget_groups[name] = (len(self._widget_groups), tool_palette, push_button)
        
        frame_layout.addWidget(header_widget)
        frame_layout.addWidget(tool_palette)
        
        # append to the layout
        self.addWidget(frame)
        return tool_palette
     
    def _on_button_clicked(self,name):
        # work out if it is shown or hidden
        #call show or hide method
        if self._widget_groups[name][1].isHidden():
            self.show_palette(name)
        else:
            self.hide_palette(name)
        
        
    def show_palette(self,name):
        if name not in self._widget_groups:
            raise RuntimeError('The tool palette does not have a palette named %s'%name)
        _, palette, push_button = self._widget_groups[name]
        palette.show()
        push_button.setIcon(QIcon(CONTRACT_ICON))
        push_button.setToolTip('Click to hide')
            
    def show_palette_by_index(self,index):
        self.show_palette(self.get_name_from_index(index))
    
    def hide_palette(self,name):    
        if name not in self._widget_groups:
            raise RuntimeError('The tool palette does not have a palette named %s'%name)
        
        _, palette, push_button = self._widget_groups[name]
        palette.hide()
        push_button.setIcon(QIcon(EXPAND_ICON))
        push_button.setToolTip('Click to show')
    
    def hide_palette_by_index(self,index):
        self.hide_palette(self.get_name_from_index(index))
     
    # Creates and inserts a new ToolPalette at the specified index.
    # A reference to the new ToolPalette is returned
    def insert_new_palette(self,index,name,*args,**kwargs):
        # insert ...
        pass
    
    def has_palette(self,name):
        if name in self._widget_groups:
            return True
        return False
    
    def get_palette(self,name):        
        if name not in self._widget_groups:
            raise RuntimeError('The tool palette group does not contain a palette named %s'%name)
            
        return self._widget_groups[name][1]
    
    def get_palette_by_index(self,index):
        return self.get_palette(self.get_name_from_index(index))
    
    def reorder_palette(self,name,new_index):
        if name not in self._widget_groups:
            raise RuntimeError('The tool palette group does not contain a palette named %s'%name)
            
        return self.reorder_palette_by_index(self.get_index_from_name(name),new_index)
    
    def reorder_palette_by_index(self,old_index,new_index):
        if old_index < 0 or old_index >= count(self._widget_groups):
            raise RuntimeError('The specified old_index is out of bounds')
            
        if new_index < 0 or new_index >= count(self._widget_groups):
            raise RuntimeError('The specified new_index is out of bounds')    
            
        # TODO: now perform the reorder
        
        # TODO: recreate the layout
        
    def remove(self,name):
        if name not in self._widget_groups:
            raise RuntimeError('The tool palette group does not contain a palette named %s'%name)
            
        # TODO: Remove
        
    def remove_by_index(self,index):
       return self.remove(self.get_name_from_index(index))
    
    def get_name_from_index(self,index):
        for name, palette_data in self._widget_groups.items():
            if palette_data[0] == index:
                return name
                
        raise RuntimeError('The tool palette group does not contain a palette with index %d'%index)
        
    def get_index_from_name(self,name):
        if name not in self._widget_groups:
            raise RuntimeError('The tool palette group does not contain a palette named %s'%name)
            
        return self._widget_groups[name][0]
    
    ############################################################################################################################
    # The code below is related solely to linking the widths of items within several tool palettes that are part of this group #
    ############################################################################################################################
    
    # This property links the widths of all ToolPalettes in the ToolPalette group
    # It is a convenience property so that you don't have to create a linked_width_group conatining all Tool palettes in the tool palette group
    # and maintain the linked_width_group after ading new Tool Palettes to the Tool Palette Group
    @property
    def widths_linked(self):
        return self._all_widths_linked
    
    @widths_linked.setter
    def widths_linked(self,value):
        if self._width_groups and self._all_widths_linked:
            raise RuntimeError('You cannot link the widths of all tool palettes if you have already created a linked width group')
    
        self._all_widths_linked = value
    
    # This function links the widths of items in several ToolPalettes.
    def create_linked_width_group(self,width_group_name,names):
        if self._all_widths_linked:
            raise RuntimeError('You cannot create a linked_width_group if you have already linked all widths via the widths_linked_property')
    
        if width_group_name in self._width_groups:
            raise RuntimeError('The tool palette group already has a width group named %s'%width_group_name)
        
        # check if anything in names is already in another width group
        for width_group_name,width_group_data in self._width_groups.items():
            for name in names:
                if name in width_group_data[1]:
                    raise RuntimeError('The tool pallete named %s is already in the linked width group %s'%(name,width_group_name))
        
        # create width group
        self._width_groups[width_group_name] = (self._create_find_max_function(width_group_name),names)
    
    # This function adds the toolpallete called 'name' to the linked_width_group 'width_group_name'
    def add_to_linked_width_group(self,width_group_name,name):
        if self._all_widths_linked:
            raise RuntimeError('You cannot add to a linked_width_group if you have already linked all widths via the widths_linked_property')
            
        if width_group_name not in self._width_groups:
            raise RuntimeError('The tool palette group does not have a width group named %s'%width_group_name)
    
        for width_group_name,width_group_data in self._width_groups.items():
            if name in width_group_data[1]:
                raise RuntimeError('The tool pallete named %s is already in the linked width group %s'%(name,width_group_name))
        
        self._width_groups[width_group_name][1].append(name)
        # recreate the find_max_item_width function
        self._width_groups[width_group_name] = (self._create_find_max_function(width_group_name),self._width_groups[width_group_name][1])
    
    def remove_from_linked_width_group(self,width_group_name,name):
        pass
        #TODO:
    
    # This function creates and returns a reference to a function which finds the widest item in all Tool palettes in the specified
    # linked_width_group.
    def _create_find_max_function(self,width_group_name):
        def find_max_item_width():
            largest_item_width = 0
            for tp_name in self._width_groups[width_group_name][1]:
                item_width = self._widget_groups[tp_name][1]._find_max_item_width()
                if item_width > largest_item_width:
                    largest_item_width = item_width                    
            return largest_item_width            
        return find_max_item_width
        
    # This function gives the tool palletes a function to call to find out the widest item in their linked_width_group
    def _find_max_item_width(self,name):
        if self._all_widths_linked:
            return lambda: max([palette[1]._find_max_item_width() for palette in self._widget_groups.values()])
            
        # Look up to see if the tool palette is in a linked_width_group
        width_group = None
        for width_group_name,width_group_list in self._width_groups.items():
            if name in width_group_list[1]:
                width_group = width_group_name
                break
        
        if width_group:
            return self._width_groups[width_group][0]
        else:
            return self._widget_groups[name][1]._find_max_item_width
        
        
class ToolPalette(QScrollArea):
    def __init__(self,parent,name,*args,**kwargs):
        QScrollArea.__init__(self,*args,**kwargs)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
        self.setFrameStyle(QFrame.NoFrame)
        # create the grid layout
        #self.setWidget(QWidget(self))
        #self.widget().setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        self._layout = QGridLayout(self) 
        self._layout.setContentsMargins(3,0,3,3)
        self._layout.setHorizontalSpacing(3)
        self._layout.setVerticalSpacing(3)
        #self._layout.setMaximumSize(QSize(524287,524287))
        #self._layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self._widget_list = []
        self._parent_group = parent
        self._name = name
        
        # need to keep track of these internally because the GridLayout returns the number of 
        # allocated rows/columns with columnCount()/RowCount() rather than the number of visible ones
        self._column_count = 0
        self._row_count = 0
        
        # Variable for controlling whether or not self._layout_widgets() is
        # called in self.resizeEvent().
        self._layout_widgets_during_resizeEvent = True
        
    def addWidget(self,widget,force_relayout=True):
        # Append to end of tool pallete
        #widget.clicked.connect(embed)
        self._widget_list.append(widget)
        self._layout_widgets(force_relayout)
        
    def insertWidget(self,index,widget,force_relayout=True):
        # Insert into position 'index'
        self._widget_list.insert(index,widget)
        self._layout_widgets(force_relayout)
    
    def _find_max_item_width(self):
        # find the minimum size of the widest widget in the grid layout
        w_size_hints = [w.minimumSizeHint().width() for w in self._widget_list]
        if len(w_size_hints) < 1:
            return 0
        max_width = max(w_size_hints)
        return max_width
    
    def _layout_widgets(self,force_relayout = False):
        h_size_hints = [w.sizeHint().height() for w in self._widget_list]
        max_width = self._parent_group._find_max_item_width(self._name)()
        
        # find the width of the gridlayout
        layout_width = self.size().width()
        #layout_width = self._layout.sizeHint().width()
        layout_spacing = self._layout.horizontalSpacing()
        
        # How many widgets can fit in a row?
        # TODO: Work out hwy I need layout_spacing*3 here (we are getting the width of the scroll area, 
        # so need to take into account the borders around the grid layout? What are they?)
        num_widgets_per_row = (layout_width-layout_spacing*3)//(max_width+layout_spacing)

        # print self._name
        # print 'number_of_widgets: %d'%len(self._widget_list)
        # print 'layout_width: %d'%layout_width
        # print 'layout_spacing: %d'%layout_spacing
        # print 'max_width: %d'%max_width
        # print '(layout_width-layout_spacing*3)/(max_width+layout_spacing): %.3f'%((layout_width-layout_spacing*3)/(max_width+layout_spacing))
        # print 'num_widgets_per_row: %d'%num_widgets_per_row 
        
        if num_widgets_per_row < 1:
            num_widgets_per_row = 1
        elif num_widgets_per_row > len(self._widget_list):
            num_widgets_per_row = len(self._widget_list)
            
        if num_widgets_per_row != self._column_count or force_relayout:            
            #print 'changing number of columns'
            # remove all widgets
            for widget in self._widget_list:
                self._layout.removeWidget(widget)
            
            # re add all widgets into the grid layout
            row = 0
            column = 0
            for widget in self._widget_list:
                self._layout.addWidget(widget,row,column)
                column += 1
                if column >= num_widgets_per_row:
                    column = 0
                    row += 1
                    
            # This is here because the row count may have been increased at the end of the insertion
            # loop
            if column != 0:
                row += 1
            # update the row/column count
            self._column_count = num_widgets_per_row
            self._row_count = row
            
            # print (max(h_size_hints)+self._layout.verticalSpacing())*self._row_count+self._layout.verticalSpacing()*2
            # print max(h_size_hints)
            # print self._layout.verticalSpacing()
            # print self._row_count
            
            total_height = max(h_size_hints) * self._row_count
            total_height += self._layout.verticalSpacing() * (self._row_count - 1)
            total_height += self._layout.contentsMargins().top()
            total_height += self._layout.contentsMargins().bottom()
            self.setMinimumSize(QSize(self.minimumSize().width(), total_height))
            for i in range(self._layout.rowCount()):
                if i < self._row_count:
                    self._layout.setRowMinimumHeight(i,max(h_size_hints))
                else:
                    self._layout.setRowMinimumHeight(i,0)
        

    def minimumSize(self):
        # Get the widgets minimum size:
        widget_size = QWidget.minimumSize(self)
        
        # now get the smallest minimum size width of all child widgets:
        widths = [w.minimumSizeHint().width() for w in self._widget_list]
        #heights = [w.minimumSize().height() for w in self._widget_list]
        #print 'number of widgets %d'%len(self._widget_list)
        if len(widths) > 0:
            max_width = max(widths)
            #print 'max_width: %d'%max_width
            #print 'widget width: %d'%widget_size.width()
            if max_width > widget_size.width():
                widget_size = QSize(max_width,widget_size.height())
                #print 'modifying minimum size width'
        
        #print 'minimum size is %s'%str(widget_size)
            
        return widget_size
        
    def updateMinimumSize(self):
        self.setMinimumSize(self.minimumSize())
        
    def sizeHint(self):
        width = QScrollArea.sizeHint(self).width()
        height = self.minimumSize().height()
        return QSize(width, height)

    def minimumSizeHint(self):
        width = QScrollArea.minimumSizeHint(self).width()
        height = self.minimumSize().height()
        return QSize(width, height)

    def event(self, event):
        # Handle the custom event for reenabling the call to
        # self._layout_widgets() during self.resizeEvent().
        if (event.type() == _ENABLE_LAYOUT_EVENT_TYPE):
            self._layout_widgets_during_resizeEvent = True
            # Return True so that this event isn't sent along to other event
            # handlers as well.
            return True

        # Handle all other events in the usual way.
        return super().event(event)

    def resizeEvent(self, event):
        # overwrite the resize event!
        # This method can end up undergoing infinite recursion for some window
        # layouts, see
        # https://github.com/labscript-suite/labscript-utils/issues/27. It seems
        # that sometimes self._layout_widgets() increases the number of columns,
        # which then triggers a resizeEvent, which then calls
        # self._layout_widgets() which then decreases the number of columns to
        # its previous value, which triggers a resizeEvent, and so on. That loop
        # may occur e.g. if increasing/decreasing the number of columns
        # add/removes a scrollbar, which then changes the number of widgets that
        # can fit in a row. Keeping track of the recursion depth isn't trivial
        # because _layout_widgets() doesn't directly call itself; it just causes
        # more resizing events to be added to the event queue. To work around
        # that, this method will mark that future calls to this method shouldn't
        # call _layout_widgets() but will also add an event to the event queue
        # to reenable calling _layout_widgets() again once all of the resize
        # events caused by this call to it have been processed.
        
        try:
            #pass resize event on to qwidget
            QWidget.resizeEvent(self, event)
            size = event.size()
            if size.width() == self.size().width() and size.height() == self.size().height():
                if self._layout_widgets_during_resizeEvent:
                    # Avoid calling this again until all the resize events that
                    # will be put in the queue by self._layout_widgets() have
                    # run.
                    self._layout_widgets_during_resizeEvent = False
                    self._layout_widgets()
        finally:
            # Add event to end of the event queue to allow _layout_widgets() in
            # future calls. This event shouldn't be handled until the resize
            # events generated during _layout_widgets() have run.
            QCoreApplication.instance().postEvent(self, QEvent(_ENABLE_LAYOUT_EVENT_TYPE))


# A simple test!
if __name__ == '__main__':
    
    qapplication = QApplication(sys.argv)

    from .ddsoutput import DDSOutput

    window = QWidget()
    layout = QVBoxLayout(window)
    widget = QWidget()
    layout.addWidget(widget)
    tpg = ToolPaletteGroup(widget)
    toolpalette = tpg.append_new_palette('Digital Outputs')
    toolpalette2 = tpg.append_new_palette('Digital Outputs 2')
    #toolpalette = ToolPalette()
    #layout.addWidget(toolpalette)
    #layout.addItem(tpg)
    #toolpalette.show()
    
    layout.addItem(QSpacerItem(0,0,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding))
    for i in range(20):
        #button = QPushButton('Button %d'%i)
        button = DDSOutput('DDS %d'%i)
        #button.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        toolpalette.addWidget(button)
        
    for i in range(20):
        button = QPushButton('very very long Button %d'%i)
        
        button.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        toolpalette2.addWidget(button)
    
    #tpg.create_linked_width_group("Digital outs", ['Digital Outputs','Digital Outputs 2'])
    
    window.show()
    
    
    sys.exit(qapplication.exec_())
    
