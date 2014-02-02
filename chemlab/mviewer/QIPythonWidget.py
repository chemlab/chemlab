import atexit

from PySide.QtCore import QTimer

from IPython.zmq.ipkernel import IPKernelApp
from IPython.lib.kernel import find_connection_file
from IPython.frontend.qt.kernelmanager import QtKernelManager
from IPython.frontend.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.config.application import catch_config_error


class QIPythonWidget(RichIPythonWidget):

    class KernelApp(IPKernelApp):
        @catch_config_error
        def initialize(self, argv=[]):
            super(QIPythonWidget.KernelApp, self).initialize(argv)
            self.kernel.eventloop = self.loop_qt4_nonblocking
            self.kernel.start()
            self.start()

        def loop_qt4_nonblocking(self, kernel):
            kernel.timer = QTimer()
            kernel.timer.timeout.connect(kernel.do_one_iteration)
            kernel.timer.start(1000*kernel._poll_interval)

        def get_connection_file(self):
            return self.connection_file

        def get_user_namespace(self):
            return self.kernel.shell.user_ns

    def __init__(self, parent=None, colors='linux', instance_args=[]):
        super(QIPythonWidget, self).__init__()
        self.app = self.KernelApp.instance(argv=instance_args)
        
    def initialize(self, colors='linux'):
        self.app.initialize()
        self.set_default_style(colors=colors)
        self.connect_kernel(self.app.get_connection_file())

    def connect_kernel(self, conn, heartbeat=False):
        km = QtKernelManager(connection_file=find_connection_file(conn))
        km.load_connection_file()
        km.start_channels(hb=heartbeat)
        self.kernel_manager = km
        atexit.register(self.kernel_manager.cleanup_connection_file)

    def get_user_namespace(self):
        return self.app.get_user_namespace()

    def run_cell(self, *args, **kwargs):
        return self.app.shell.run_cell(*args, **kwargs)