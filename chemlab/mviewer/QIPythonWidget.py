import atexit

from PyQt4.QtCore import QTimer

from IPython.kernel.zmq.kernelapp import IPKernelApp
from IPython.lib.kernel import find_connection_file

from IPython.qt.inprocess import QtInProcessKernelManager

from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.config.application import catch_config_error

from IPython.lib import guisupport

class QIPythonWidget(RichIPythonWidget):

    def __init__(self):
        super(QIPythonWidget, self).__init__()
        
    def initialize(self):
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        
        kernel = kernel_manager.kernel
        kernel.gui = 'qt4'
        
        kernel_client = kernel_manager.client()
        kernel_client.start_channels()
        
        app = guisupport.get_app_qt4()
        
        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            app.exit()
    
        self.kernel = kernel
        self.kernel_manager = kernel_manager
        self.kernel_client = kernel_client
        self.exit_requested.connect(stop)

    def get_user_namespace(self):
        return self.kernel.shell.user_ns

    def run_cell(self, *args, **kwargs):
        return self.kernel.shell.run_cell(*args, **kwargs)

    def ex(self, *args, **kwargs):
        return self.kernel.shell.ex(*args, **kwargs)
    
    def run_line_magic(self, *args, **kwargs):
        return self.kernel.shell.run_line_magic(*args, **kwargs)

    # class KernelApp(IPKernelApp):
    #     @catch_config_error
    #     def initialize(self, argv=[]):
    #         super(QIPythonWidget.KernelApp, self).initialize(argv)
    #         self.kernel.eventloop = self.loop_qt4_nonblocking
    #         self.kernel.start()
    #         self.start()

    #     def loop_qt4_nonblocking(self, kernel):
    #         kernel.timer = QTimer()
    #         kernel.timer.timeout.connect(kernel.do_one_iteration)
    #         kernel.timer.start(1000*kernel._poll_interval)

    #     def get_connection_file(self):
    #         return self.connection_file

    #     def get_user_namespace(self):
    #         return self.kernel.shell.user_ns

    # def __init__(self, parent=None, colors='linux', instance_args=[]):
    #     super(QIPythonWidget, self).__init__()
    #     self.app = self.KernelApp.instance(argv=instance_args)
        
    # def initialize(self, colors='linux'):
    #     self.app.initialize()
    #     self.set_default_style(colors=colors)
    #     self.connect_kernel(self.app.get_connection_file())

    # def connect_kernel(self, conn, heartbeat=False):
    #     km = QtKernelManager(connection_file=find_connection_file(conn))
    #     km.load_connection_file()
    #     km.kernel.start_channels(hb=heartbeat)
    #     self.kernel_manager = km
    #     atexit.register(self.kernel_manager.cleanup_connection_file)

    # def get_user_namespace(self):
    #     return self.app.get_user_namespace()

    # def run_cell(self, *args, **kwargs):
    #     return self.app.shell.run_cell(*args, **kwargs)