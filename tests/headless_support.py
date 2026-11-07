"""EGL rendering harness; no game input or window code is changed for testing."""
from panda3d.core import loadPrcFileData,Point2
loadPrcFileData('test renderer','load-display p3headlessgl\nwindow-type offscreen\nwin-size 1920 1080\naudio-library-name null\nsync-video false\nnotify-level warning')
from pcshop.app import WorkshopApp

class Pointer:
 def __init__(self):self.pos=Point2(0,0)
 def hasMouse(self):return True
 def getMouse(self):return self.pos

class TestApp(WorkshopApp):
 def bind_inputs(self):self.mouseWatcherNode=Pointer()
 def capture_mouse(self,capture):self.mouse_ready=False
 def center_pointer(self):pass
 def update(self,task):
  if self.mode is None:return task.cont
  return super().update(task)
