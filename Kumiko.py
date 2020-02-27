#Author-Takumelo
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from math import pi,sin,cos, radians, sqrt
# import time

APP = None
KUMIKO_UI = None

INPUT_HANDLER = None

# Event handler that reacts to any changes the user makes to any of the command inputs.
class CommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            inputs = eventArgs.inputs
            cmdInput = eventArgs.input
        except:
            KUMIKO_UI.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts to when the command is destroyed. This terminates the script.            
class CommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            KUMIKO_UI.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            draw()
        except:
            if KUMIKO_UI:
                KUMIKO_UI.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        


# Event handler that reacts when the command definitio is executed which
# results in the command being created and this event being fired.
class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
        self._handlers = []
    def notify(self, args):
        try:

            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command execute event.
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            self._handlers.append(onExecute)

            # Connect to the command destroyed event.
            onDestroy = CommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            self._handlers.append(onDestroy)

            # Connect to the input changed event.           
            onInputChanged = CommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            self._handlers.append(onInputChanged)

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            # Create a tab input.
            tabCmdInput1 = inputs.addTabCommandInput('tab_1', 'Asanoha')
            tab1ChildInputs = tabCmdInput1.children

            global INPUT_HANDLER
            INPUT_HANDLER = AsanohaOption()
            INPUT_HANDLER.offset = tab1ChildInputs.addFloatSpinnerCommandInput('offset', 'Offset', 'cm', 0.01 , 10.0 , 0.1, 0.1)
            INPUT_HANDLER.side_length = tab1ChildInputs.addFloatSpinnerCommandInput('side_length', 'Side Length', 'cm', 0.01 , 10.0 , 0.1, 3.0)
            INPUT_HANDLER.row = tab1ChildInputs.addIntegerSpinnerCommandInput('row', 'Number of Rows', 1 , 3 , 1, 1)
            INPUT_HANDLER.col = tab1ChildInputs.addIntegerSpinnerCommandInput('col', 'Number of column', 1 , 3 , 1, 1)
        except:
            KUMIKO_UI.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class Options():
    pass

class AsanohaOption(Options):
    def __init__(self):
        self.offset = None
        self.side_length = None
        self.row = None
        self.col = None

class Point():
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Point(x, y, z)
    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        return Point(x, y, z)       
    def __mul__(self, other):
        x = self.x * other.x
        y = self.y * other.y
        z = self.z * other.z
        return Point(x, y, z)
    def __truediv__(self, other):
        x = self.x / other
        y = self.y / other
        z = self.z / other
        return Point(x, y, z)
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

class Triangle():
    def __init__(self, point1, point2, point3):
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.mid_pnt = (self.point1 + self.point2 + self.point3) / 3
    def calc_mid(self):
        pass
    def move(self, point):
        self.point1 += point
        self.point2 += point
        self.point3 += point
        self.mid_pnt = (self.point1 + self.point2 + self.point3) / 3
    def rotate(self, deg, root):
        tmp_pnt1 = self.point1 - root
        tmp_pnt2 = self.point2 - root
        tmp_pnt3 = self.point3 - root
        tmp_pnt1 = Point(
            tmp_pnt1.x * cos(radians(deg)) - tmp_pnt1.y * sin(radians(deg)),
            tmp_pnt1.x * sin(radians(deg)) + tmp_pnt1.y * cos(radians(deg)),
            tmp_pnt1.z
        )
        tmp_pnt2 = Point(
            tmp_pnt2.x * cos(radians(deg)) - tmp_pnt2.y * sin(radians(deg)),
            tmp_pnt2.x * sin(radians(deg)) + tmp_pnt2.y * cos(radians(deg)),
            tmp_pnt2.z
        )
        tmp_pnt3 = Point(
            tmp_pnt3.x * cos(radians(deg)) - tmp_pnt3.y * sin(radians(deg)),
            tmp_pnt3.x * sin(radians(deg)) + tmp_pnt3.y * cos(radians(deg)),
            tmp_pnt3.z
        )
        self.point1 = tmp_pnt1 + root
        self.point2 = tmp_pnt2 + root
        self.point3 = tmp_pnt3 + root
        self.mid_pnt = (self.point1 + self.point2 + self.point3) / 3
    def pnt_iter(self):
        return [self.point1, self.point2, self.point3]

class SketchDraw():
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.offset = 0.1
        global KUMIKO_UI
        KUMIKO_UI = self.app.userInterface
        self.design = self.app.activeProduct
        self.rootComp = self.design.rootComponent
        self.sketches = None
        self.sketch = None
        # for rectangle
        self.pnt1 = None
        self.pnt2 = None

    def create_new_sketch(self):
        self.sketches = self.rootComp.sketches
        self.xyPlane = self.rootComp.xYConstructionPlane
        self.sketch = self.sketches.add(self.xyPlane)
        self.lines = self.sketch.sketchCurves.sketchLines
    def draw_triangle_with_offset(self, triangle):
        before_cnt = self.lines.count
        fst_line = None
        recent_line = None
        fst_pnt = None
        fst_pnt_obj = None
        for ind, pnt in enumerate(triangle.pnt_iter()):
            if(ind == 0):
                fst_pnt = pnt
            elif(ind == 1):
                fst_pnt_obj = adsk.core.Point3D.create(fst_pnt.x, fst_pnt.y, fst_pnt.z)
                tmp_line = self.lines.addByTwoPoints(fst_pnt_obj, adsk.core.Point3D.create(pnt.x, pnt.y, pnt.z))
                recent_line = tmp_line
            else:
                tmp_line = self.lines.addByTwoPoints(recent_line.endSketchPoint, adsk.core.Point3D.create(pnt.x, pnt.y, pnt.z))
                recent_line = tmp_line
        tmp_line = self.lines.addByTwoPoints(adsk.core.Point3D.create(pnt.x, pnt.y, pnt.z), self.lines.item(before_cnt).startSketchPoint)
        after_cnt = self.lines.count
        curves = self.sketch.findConnectedCurves(tmp_line)
        dirPoint = adsk.core.Point3D.create(triangle.mid_pnt.x, triangle.mid_pnt.y, triangle.mid_pnt.z)
        offsetCurves = self.sketch.offset(curves, dirPoint, self.offset)
        for cnt in range(before_cnt, after_cnt):
            a = self.lines.item(before_cnt)
            a.deleteMe()
        self.erase_extra(offsetCurves)
    def erase_extra(self, offset_curves):
        for i in offset_curves:
            s_geo = i.startSketchPoint.geometry
            e_geo = i.endSketchPoint.geometry
            temp_x_s = s_geo.x
            temp_x_e = e_geo.x
            temp_y_s = s_geo.y
            temp_y_e = e_geo.y
            del_flg = True
            erase_flg = (
                (temp_x_s <= self.pnt1.x or temp_x_s >= self.pnt2.x) and (temp_x_e <= self.pnt1.x or temp_x_e >= self.pnt2.x)
            ) or (
                (temp_y_s <= self.pnt1.y or temp_y_s >= self.pnt2.y) and (temp_y_e <= self.pnt1.y or temp_y_e >= self.pnt2.y)
            )
            if(erase_flg):
                i.deleteMe()

    def draw_frame(self, pnt1, pnt2):
        self.pnt1 = pnt1
        self.pnt2 = pnt2
        self.lines.addTwoPointRectangle(adsk.core.Point3D.create(pnt1.x, pnt1.y, pnt1.z), adsk.core.Point3D.create(pnt2.x, pnt2.y, pnt2.z))
    def turn_on_comdef(self):
        self.sketch.isComputeDeferred = True
    def turn_off_comdef(self):
        self.sketch.isComputeDeferred = False

def draw():
    try:
        # start = time.time()
        sketchdraw = SketchDraw()
        sketchdraw.create_new_sketch()

        global INPUT_HANDLER
        offset = INPUT_HANDLER.offset.value
        side_length = INPUT_HANDLER.side_length.value
        col = INPUT_HANDLER.col.value
        row = INPUT_HANDLER.row.value

        sketchdraw.offset = offset
        temp_x_len = side_length / 2 / sqrt(side_length)
        frame_tmp_x = -(temp_x_len + side_length * cos(radians(60 / 2)))
        frame_tmp_y = -side_length / 2
        increment_x = side_length * cos(radians(60 / 2)) * 2
        increment_y = side_length * 2
        pnt1 = Point(frame_tmp_x, frame_tmp_y, 0)
        pnt2 = Point(frame_tmp_x + increment_x * col, frame_tmp_y + increment_y * row, 0)
        sketchdraw.draw_frame(pnt1, pnt2)

        p1 = Point(0, 0, 0)
        p2 = Point(-temp_x_len, side_length / 2, 0)
        p3 = Point(-temp_x_len, -side_length / 2, 0)
        t1 = Triangle(p1, p2, p3)

        sketchdraw.turn_off_comdef()

        temp_row = row + 2
        for h in range(temp_row):
            temp_col = col if h % 2 == 0 else col + 1
            for a in range(temp_col):
                # make a hexagon
                for j in range(6):
                    for i in range(3):
                        sketchdraw.draw_triangle_with_offset(t1)
                        t1.rotate(120, t1.point1)
                    t1.rotate(60, t1.point3)
                t1.move(Point(side_length * cos(radians(60 / 2)) * 2, 0, 0))
            slide = 1
            offset_x = (-side_length * cos(radians(60 / 2)) * 2 * (col + 1)) + slide * (side_length * cos(radians(60 / 2)))
            t1.move(Point(offset_x, side_length * cos(radians(60 / 2)) * 2 * sin(radians(60)), 0))
        sketchdraw.turn_on_comdef()
        # end = time.time()
        # KUMIKO_UI.messageBox(str(end - start) + "sec")
    except:
        if KUMIKO_UI:
            KUMIKO_UI.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        global APP, KUMIKO_UI
        APP = adsk.core.Application.get()
        KUMIKO_UI  = APP.userInterface
        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = KUMIKO_UI.commandDefinitions.itemById('cmdInputs')
        if not cmdDef:
            cmdDef = KUMIKO_UI.commandDefinitions.addButtonDefinition('cmdInputs', 'Kumiko Pattern Generator', 'to be')

        # Connect to the command created event.
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        onCommandCreated._handlers.append(onCommandCreated)

        # Execute the command definition.
        cmdDef.execute()

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)

    except:
        if KUMIKO_UI:
            KUMIKO_UI.messageBox('Failed:\n{}'.format(traceback.format_exc()))