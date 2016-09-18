import threading
import subprocess
import os


class EnergyPlusThread(threading.Thread):
    def __init__(self, run_script, input_file, weather_file, msg_callback, success_callback, failure_callback, cancelled_callback):
        self.p = None
        self.std_out = None
        self.std_err = None
        self.run_script = run_script
        self.input_file = input_file
        self.weather_file = weather_file
        self.msg_callback = msg_callback
        self.success_callback = success_callback
        self.failure_callback = failure_callback
        self.cancelled_callback = cancelled_callback
        self.cancelled = False
        self.run_dir = ''
        threading.Thread.__init__(self)

    def run(self):
        self.cancelled = False
        self.run_dir = os.path.join(os.path.dirname(self.input_file), 'output-' + os.path.splitext(os.path.basename(self.input_file))[0])
        self.p = subprocess.Popen([
            self.run_script,
            '-d',
            self.run_dir,
            '-w',
            self.weather_file,
            self.input_file
        ],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        self.msg_callback("Simulation started")
        self.std_out, self.std_err = self.p.communicate()
        if self.cancelled:
            self.msg_callback("Simulation cancelled")
            self.cancelled_callback()
        else:
            if self.p.returncode == 0:
                self.msg_callback("Simulation completed")
                self.success_callback(self.std_out, self.run_dir)
            else:
                self.msg_callback("Simulation failed")
                self.failure_callback(self.std_out, self.run_dir)

    def stop(self):
        if self.p.poll() is None:
            self.msg_callback("Attempting to cancel simulation ...")
            # os.system('pkill -TERM -P {pid}'.format(pid=self.p.pid))
            self.cancelled = True
            self.p.kill()
