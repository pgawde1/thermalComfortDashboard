"""
# Author: Pratik Gawde, Pranita Shewale
# Date: 11 Nov, 2024
# PROJECT 02
# Description: main file for thermalComfortDashboard
"""
import os
import time
from time import sleep
import threading

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askdirectory

import serial.tools.list_ports

from pythermalcomfort.models import pmv_ppd
from pythermalcomfort.utilities import clo_dynamic, v_relative

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Sensor import Sensor, SensorError


class UI:

    def __init__(self):
        """
        class constructor
        """
        # create window first

        self.__frame_chart = None
        self.__style_CO2_Frame = None
        self.__style_TH_Label = None
        self.__progressbar = None
        self.__frame_wrapperCOM_Progress = None
        self.__progressbarValue = 0
        self.__canvas_widget = None
        self.__canvas = None
        self.__point = None
        self.__button_apply_settings = None
        self.__label_clothing = None
        self.__frame_clothing = None
        self.__label_activity = None
        self.__frame_activity = None
        self.__frame_settings = None
        self.__combo_clothing = None
        self.__combo_activity = None
        self.__label_sensation_reading = None
        self.__var_sensation = None
        self.__label_sensation = None
        self.__frame_sensation = None
        self.__var_append_create = None
        self.__stopLoggingEvent = threading.Event()
        self.__radio_create = None
        self.__radio_append = None
        self.__logging_thread_handle = None
        self.__checkbox_difference = None
        self.__var_only_difference = None
        self.__create_button = None
        self.__append_button = None
        self.__file_option = None
        self.__frame_options = None
        self.__entry_fileName = None
        self.__label_fileName = None
        self.__frame_fileName = None
        self.__button_filebrowse = None
        self.__entry_folderName = None
        self.__label_folder = None
        self.__frame_folder_log = None
        self.__button_stop_log = None
        self.__button_start_log = None
        self.__frame_button_log = None
        self.__frame_reading_wrapper = None
        self.__title_label = None
        self.__frame_log = None
        self.__active_data_thread_handle = None
        self.__CO2 = 0
        self.__Humidity = 0
        self.__Temperature = 0
        self.__button_closePort = None
        self.__button_openPort = None
        self.__combo_COMPort = None
        self.__label_COMPort = None
        self.__frame_ComPort = None
        self.__label_CO2Unit = None
        self.__label_CO2Reading = None
        self.__label_CO2Text = None
        self.__frame_CO2 = None
        self.__label_humidityUnits = None
        self.__label_humidityReading = None
        self.__label_humidityText = None
        self.__frame_humidity = None
        self.__radio_celsius = None
        self.__radio_Fahrenheit = None
        self.__selected_temperature_unit = None
        self.__label_temperatureUnit = None
        self.__label_temperatureReading = None
        self.__frame_radio_units = None
        self.__label_temperatureText = None
        self.__frame_temperature = None
        self.__co2_var = None
        self.__h_var = None
        self.__t_var = None
        self.__exitEvent = threading.Event()
        self.__portCloseEvent = threading.Event()
        self.__dataUpdated_LOG_Event = threading.Event()
        self.__dataUpdated_GUI_Event = threading.Event()
        self.__root = Tk()
        self.__dict_activity = {
            "Seated, quiet": 1.0,
            "Reading, seated": 1.0,
            "Writing": 1.0,
            "Typing": 1.1,
            "Standing, relaxed": 1.2,
            "Filing, seated": 1.2,
            "Flying aircraft, routine": 1.2,
            "Filing, standing": 1.4,
            "Driving a car": 1.5,
            "Walking about": 1.7,
            "Cooking": 1.8,
            "Table sawing": 1.8,
            "Walking 2mph (3.2kmh)": 2.0,
            "Lifting/packing": 2.1,
            "Seated, heavy limb movement": 2.2,
            "Light machine work": 2.2,
            "Flying aircraft, combat": 2.4,
            "Walking 3mph (4.8kmh)": 2.6,
            "House cleaning": 2.7,
            "Driving, heavy vehicle": 3.2,
            "Dancing": 3.4,
            "Calisthenics": 3.5,
            "Walking 4mph (6.4kmh)": 3.8,
            "Tennis": 3.8,
            "Heavy machine work": 4.0,
            "Handling 100lb (45 kg) bags": 4.0
        }
        self.__dict_clothing = {"Walking shorts, short-sleeve shirt": 0.36,
                                "Typical summer indoor clothing": 0.5,
                                "Knee-length skirt, short-sleeve shirt, sandals, underwear": 0.54,
                                "Trousers, short-sleeve shirt, socks, shoes, underwear": 0.57,
                                "Trousers, long-sleeve shirt": 0.61,
                                "Knee-length skirt, long-sleeve shirt, full slip": 0.67,
                                "Sweat pants, long-sleeve sweatshirt": 0.74,
                                "Jacket, Trousers, long-sleeve shirt": 0.96,
                                "Typical winter indoor clothing": 1.0}

    def on_closing(self):
        """
        this function is called when window is closed
        """
        plt.close(self.__fig)
        self.__progressbar.stop()

        self.__exitEvent.set()

        if self.__active_data_thread_handle:
            # only wait for producer thread if it exists.
            # It may be that sensor thread was never started.
            self.__active_data_thread_handle.join()
            self.__active_data_thread_handle = None
            print("sensor thread exit")
        if self.__logging_thread_handle:
            self.__logging_thread_handle.join()
            self.__logging_thread_handle = None
            print("logging thread exit")

        # plt.close(self.__fig)
        self.__exitEvent.clear()
        self.__root.quit()

    def start(self):
        """
        this function is called when program starts to draw ui
        """
        self.draw_gui()
        self.__root.mainloop()
        print("gui exit")

    def sensor_data_thread(self):
        """
        this is the THREAD to collect data from sensor
        """
        try:
            scd40 = Sensor(self.__combo_COMPort.get().split(":")[0])
            self.__combo_COMPort["state"] = "disabled"
            self.__button_openPort["state"] = "disabled"
            self.__button_closePort["state"] = "enabled"
            while True:
                if self.__exitEvent.is_set():
                    # this is set when gui loop exits in start function. Event is set. When producer thread wakes up, it exits.
                    # self.__exitEvent.clear()
                    print("exiting producer")
                    return

                if self.__portCloseEvent.is_set():
                    self.__portCloseEvent.clear()
                    self.__combo_COMPort["state"] = "readonly"
                    self.__button_openPort["state"] = "enabled"
                    self.__button_closePort["state"] = "disabled"
                    self.__active_data_thread_handle = None
                    self.__progressbarValue = 0
                    return

                scd40.getData()
                # g_mutex_readings.acquire()
                # print("data-mutex[acq]")
                # print(f"T:{scd40.getTemperature()},H:{scd40.getHumidity()},CO2:{scd40.getCO2()}")
                self.__Temperature = scd40.getTemperature()
                self.__Humidity = scd40.getHumidity()
                self.__CO2 = scd40.getCO2()
                # g_mutex_readings.release()
                # print("data-mutex[rel]")
                print(f"T:{self.__Temperature},H:{self.__Humidity},CO2:{self.__CO2}")
                # self.update_readings()
                # self.__progressbarValue =  20
                self.__dataUpdated_LOG_Event.set()
                self.__dataUpdated_GUI_Event.set()
                sleep(1)
        except SensorError as err:
            print(err)
            messagebox.showerror("Error", f"Failed to open port {self.__combo_COMPort.get().split(":")[0]} !")

    def update_sensation(self):
        """
        this function is called periodically to update the ui elements from UI thread
        """
        metabolic_rate = self.__dict_activity[self.__combo_activity.get()]
        clothing = clo_dynamic(self.__dict_clothing[self.__combo_clothing.get()], metabolic_rate)
        air_relative = v_relative(0.1, metabolic_rate)
        result = pmv_ppd(tdb=self.__Temperature, tr=25, vr=air_relative, rh=self.__Humidity, met=metabolic_rate,
                         clo=clothing, standard="ashrae")
        if result['pmv'] <= -2.5:
            self.__var_sensation.set("Cold")
            self.__style_TH_Label.configure("THFrame.TLabel", background="blue")
        elif -2.5 < result['pmv'] <= -1.5:
            self.__var_sensation.set("Cool")
            self.__style_TH_Label.configure("THFrame.TLabel", background="SkyBlue1")
        elif -1.5 < result['pmv'] <= -0.5:
            self.__var_sensation.set("Slightly Cool")
            self.__style_TH_Label.configure("THFrame.TLabel", background="LightBlue1")
        elif -0.5 < result['pmv'] <= 0.5:
            self.__var_sensation.set("Neutral")
            self.__style_TH_Label.configure("THFrame.TLabel", background="snow")
        elif 0.5 < result['pmv'] <= 1.5:
            self.__var_sensation.set("Slightly Warm")
            self.__style_TH_Label.configure("THFrame.TLabel", background="peach puff")
        elif 1.5 < result['pmv'] <= 2.5:
            self.__var_sensation.set("Warm")
            self.__style_TH_Label.configure("THFrame.TLabel", background="sandy brown")
        else:
            self.__var_sensation.set("Hot")
            self.__style_TH_Label.configure("THFrame.TLabel", background="tomato")

    def update_readings(self):
        """
        this function is called periodically to update the ui elements from UI thread
        """
        if self.__dataUpdated_GUI_Event.is_set():
            self.__dataUpdated_GUI_Event.clear()
            print("updateUI...")

            # 1. update temperature reading in ui
            if self.__selected_temperature_unit.get() == "°C":
                self.__t_var.set(str(self.__Temperature))
            else:
                self.__t_var.set(str(round(((self.__Temperature * 9 / 5) + 32), 1)))

            # 2. update humidity reading in ui
            self.__h_var.set(str(self.__Humidity))

            # 3. update co2 reading in ui
            self.__co2_var.set(str(self.__CO2))
            if self.__CO2 <= 600:
                self.__style_CO2_Frame.configure("CO2Frame.TFrame", background="lime green")
                self.__style_CO2_Label.configure("CO2Frame.TLabel", background="lime green")
            elif self.__CO2 <= 1000:
                self.__style_CO2_Frame.configure("CO2Frame.TFrame", background="OliveDrab1")
                self.__style_CO2_Label.configure("CO2Frame.TLabel", background="OliveDrab1")
            elif self.__CO2 <= 2000:
                self.__style_CO2_Frame.configure("CO2Frame.TFrame", background="sandy brown")
                self.__style_CO2_Label.configure("CO2Frame.TLabel", background="sandy brown")
            else:
                self.__style_CO2_Frame.configure("CO2Frame.TFrame", background="orange red")
                self.__style_CO2_Label.configure("CO2Frame.TLabel", background="orange red")

            # 4. update sensation feeling in ui
            self.update_sensation()

            # 5. plot new reading in chart
            self.__point.set_data([self.__Temperature], [self.__Humidity])
            self.__canvas.draw()

        self.__root.after(100, self.update_readings)

    def get_com_ports(self):
        """
        this function is used to get available com ports in system
        """
        ports = serial.tools.list_ports.comports()
        l_ports = []
        for port, desc, hwid in ports:
            l_ports.append(f"{port}: {desc}")
        return l_ports

    def open_button_action(self):
        """
        this function is called when open com port button is pressed in ui
        """
        print(self.__combo_COMPort.get())

        if self.__combo_COMPort.get() == "":  # Check if nothing is selected
            messagebox.showwarning("No Selection", "Please select a COM port.")
            return

        try:
            self.__active_data_thread_handle = threading.Thread(target=self.sensor_data_thread)
            self.__active_data_thread_handle.start()
            self.__progressbar.start()

        except Exception as err:
            print(err)

    def close_button_action(self):
        """
        this function is called when close com port button is pressed in ui
        """
        print(f"request to close {self.__combo_COMPort.get()}")
        if self.__active_data_thread_handle:
            # assumes that thread was created and is running
            self.__portCloseEvent.set()
            self.__progressbar.stop()

    def temperature_unitChange(self):
        """
        this function is called to change units of readings from c to f and vice versa
        """
        if self.__selected_temperature_unit.get() == "°C":
            self.__t_var.set(str(self.__Temperature))
        else:
            self.__t_var.set(str(round(((self.__Temperature * 9 / 5) + 32), 1)))
        print(f"{self.__selected_temperature_unit.get()} is set")

    def sensor_log_thread(self):
        """
        this is THREAD that will do the logging to file when logging is started
        """
        self.__button_stop_log["state"] = "enabled"
        self.__button_start_log["state"] = "disabled"
        self.__button_filebrowse["state"] = "disabled"

        self.__entry_folderName["state"] = "disabled"
        self.__entry_fileName["state"] = "disabled"

        self.__radio_append["state"] = "disabled"
        self.__radio_create["state"] = "disabled"
        self.__checkbox_difference["state"] = "disabled"

        lastTemperature = None
        lastHumidity = None
        lastCO2 = None

        print(self.__entry_folderName.get())
        print(self.__entry_fileName.get())

        if self.__var_only_difference.get():
            print("checked")
        logfileObj = None
        if self.__var_append_create.get() == "create":
            logfileObj = open(f"{self.__entry_folderName.get()}/{self.__entry_fileName.get()}.csv", "w")
            logfileObj.write("time,t,h,co2\n")
        else:
            # append is selected. this assumes that column headers are already present
            logfileObj = open(f"{self.__entry_folderName.get()}/{self.__entry_fileName.get()}.csv", "a")
        while True:
            if self.__exitEvent.is_set():
                if logfileObj:
                    logfileObj.close()
                    logfileObj = None
                return
            if self.__stopLoggingEvent.is_set():
                self.__stopLoggingEvent.clear()
                self.__button_stop_log["state"] = "disabled"
                self.__button_start_log["state"] = "enabled"
                self.__button_filebrowse["state"] = "enabled"

                self.__entry_folderName["state"] = "enabled"
                self.__entry_fileName["state"] = "enabled"

                self.__radio_append["state"] = "enabled"
                self.__radio_create["state"] = "enabled"
                self.__checkbox_difference["state"] = "enabled"
                if logfileObj:
                    logfileObj.close()
                    logfileObj = None
                return
            if self.__dataUpdated_LOG_Event.is_set():
                self.__dataUpdated_LOG_Event.clear()
                # code comes here only when data is generated
                print(f"LOG :{self.__Temperature},{self.__Humidity},{self.__CO2}")

                if self.__var_only_difference.get():
                    if (self.__Temperature != lastTemperature) or (self.__Humidity != lastHumidity) or (
                            self.__CO2 != lastCO2):
                        logfileObj.write(f"{int(time.time())},{self.__Temperature},{self.__Humidity},{self.__CO2}\n")
                    else:
                        print("reading same as before!!")
                else:
                    logfileObj.write(f"{int(time.time())},{self.__Temperature},{self.__Humidity},{self.__CO2}\n")

                lastTemperature = self.__Temperature
                lastHumidity = self.__Humidity
                lastCO2 = self.__CO2
            time.sleep(0.1)

    def start_logging(self):
        """
        this function is called when start log button is pressed in ui.
        this then launches the logging thread
        """
        folder_path = self.__entry_folderName.get()
        file_name = self.__entry_fileName.get()

        if not folder_path:
            messagebox.showerror(title="folder error", message="Invalid folder path")
            return

        if not os.path.isdir(folder_path):
            messagebox.showerror(title="folder error", message=f"{folder_path} is invalid")
            return

        if not file_name:
            messagebox.showerror(title="file error", message=f"Invalid file name")
            return

        print(f"Folder - {folder_path}, File - {file_name}")

        self.__logging_thread_handle = threading.Thread(target=self.sensor_log_thread)
        self.__logging_thread_handle.start()

    def stop_logging(self):
        """
        this function is called when stop logging button is pressed in the ui
        this signals the logging thread to terminate
        """
        print(f"request to stop logging")
        if self.__logging_thread_handle:
            # assumes that thread was created and is running
            self.__stopLoggingEvent.set()

    def browse_folder(self):
        """
        this function is used to ask for logging folder
        """
        selected_folder = askdirectory(title="Select a folder")
        if selected_folder:
            self.__entry_folderName.delete(0, END)
            self.__entry_folderName.insert(0, selected_folder)
            print(f"Selected folder: {selected_folder}")

    def apply_changed_settings(self):
        """
        this function is called when apply button is pressed in ui.
        it generates a new graph based on settings
        """
        # print(self.__combo_activity.get())
        # print(self.__combo_clothing.get())
        list_rh, list_low, list_high = self.get_graph_margins()
        self.__ax.clear()
        self.__ax.fill_betweenx(list_rh, list_low, list_high, color='teal', alpha=0.2)
        plt.legend(['Neutral Band'])
        self.__point, = self.__ax.plot([], [], marker='*', color='red', markersize=10, label='Point')
        self.__ax.set_xlabel('Air Temperature (C)')
        self.__ax.set_ylabel('Relative Humidity (%)')
        self.__ax.set_xlim(10, 36)
        self.__ax.set_ylim(0, 100)
        self.__ax.set_xticks(range(10, 36, 2))
        self.__ax.set_yticks(range(0, 100, 10))
        self.__ax.set_title('T vs Rh in Neutral Band')
        plt.grid()

        self.__canvas.draw()

    def get_graph_margins(self):
        """
        this function gets neutral band margins
        """
        low_list = []
        high_list = []
        rh_list = []
        metabolic_rate = self.__dict_activity[self.__combo_activity.get()]
        clothing = clo_dynamic(self.__dict_clothing[self.__combo_clothing.get()], metabolic_rate)
        air_relative = v_relative(0.1, metabolic_rate)

        for rh in range(101):
            i = 10.0
            low = 0.0
            high = 0.0
            while i < 36.0:

                result = pmv_ppd(tdb=i, tr=25, vr=air_relative, rh=rh, met=metabolic_rate, clo=clothing,
                                 standard="ashrae")
                if result['pmv'] > -0.5 and low == 0.0:
                    low = i
                elif result['pmv'] >= 0.5 and high == 0.0:
                    high = i
                    break
                else:
                    i += 0.1
            # print(f"rh:{rh}")
            # print(f"low:{low}")
            # print(f"high:{high}")
            # dic[rh]={"l":low,"h":high}
            rh_list.append(round(rh, 1))
            low_list.append(round(low, 1))
            high_list.append(round(high, 1))
            # print(f"{round(rh, 1)},{round(low, 1)},{round(high, 1)}")
            # print("done")
        # other way of getting readings
        # i=10.0
        # temp_list = []
        # while i <= 36:
        #     temp_list.append(i)
        #     i = i + 0.1
        # for rh in range(101):
        #     result = pmv_ppd(tdb=temp_list, tr=25, vr=air_relative, rh=rh, met=metabolic_rate, clo=clothing, standard="ashrae",limit_inputs=False)
        #     low = 0.0
        #     low_index = 0
        #     low_temp = 0.0
        #     high = 0.0
        #     high_index = 0
        #     high_temp = 0.0
        #     for index, value in enumerate(result["pmv"]):
        #         if value > -0.5 and low == 0.0:
        #             low = value
        #             low_index = index
        #             low_temp = 10.0 + (index / 10)
        #         elif value >= 0.5 and high == 0.0:
        #             high = value
        #             high_index = index
        #             high_temp = 10.0 + (index / 10)
        #             break
        #     # print(f"rh= {rh}, low: {low_temp}->{low} , high:{high_temp}->{high}")
        #     rh_list.append(round(rh, 1))
        #     low_list.append(round(low_temp, 1))
        #     high_list.append(round(high_temp, 1))

        return rh_list, low_list, high_list

    def draw_gui(self):
        """
        this is master function for all UI elements to be created and packed
        """
        self.__root.title("thermalComfortDashboard 1.0")
        self.__root.minsize(width=1000, height=1000)

        # vars
        self.__t_var = StringVar()
        self.__h_var = StringVar()
        self.__co2_var = StringVar()

        self.__frame_wrapperCOM_Progress = ttk.Frame()
        self.__frame_wrapperCOM_Progress.pack(anchor="nw", fill="x", expand=TRUE)
        # create a Frame for COM Port -------------------------------------------------------
        self.__frame_ComPort = ttk.Frame(
            self.__frame_wrapperCOM_Progress,
            borderwidth=5,
            relief="raised",
            # padding=20,
        )
        self.__frame_ComPort.pack(anchor="nw", padx=10, pady=10, side=LEFT)

        self.__label_COMPort = ttk.Label(self.__frame_ComPort, text="COM Port: ")
        # self.__label_COMPort["relief"] = SOLID
        self.__label_COMPort.pack(side=LEFT)

        self.__combo_COMPort = ttk.Combobox(self.__frame_ComPort, state="readonly", values=self.get_com_ports())
        self.__combo_COMPort.pack(side=LEFT, padx=10)

        self.__button_openPort = ttk.Button(self.__frame_ComPort, text="open", command=self.open_button_action)
        self.__button_openPort.pack(side=LEFT, padx=10)

        self.__button_closePort = ttk.Button(self.__frame_ComPort, text="close", state="disabled",
                                             command=self.close_button_action)
        self.__button_closePort.pack(side=LEFT, padx=10)
        # -------------------------------------

        self.__progressbar = ttk.Progressbar(self.__frame_wrapperCOM_Progress, mode="indeterminate")
        self.__progressbar.pack(side=LEFT, fill="x", expand=True, padx=10)
        # -------------------------------------
        # create a wrapper frame
        self.__frame_reading_wrapper = ttk.Frame(
            self.__root,
            # width=50,
            # height=50,
            # borderwidth=5,
            # relief="raised",
            # padding=20,
        )
        self.__frame_reading_wrapper.pack(fill="x")
        # create a Frame for temperature -------------------------------------------------------
        self.__style_TH_Label = ttk.Style()
        self.__style_TH_Label.configure("THFrame.TLabel", background="LightBlue1")

        self.__frame_temperature = ttk.Frame(
            self.__frame_reading_wrapper,
            # width=50,
            # height=50,
            borderwidth=5,
            relief="raised",
            padding=20,
            style="THFrame.TLabel"
        )
        self.__frame_temperature.pack(side=LEFT, anchor="nw", padx=10, pady=10, fill="x", expand=TRUE)

        # 1.create a temperature text Label
        self.__label_temperatureText = ttk.Label(
            self.__frame_temperature,
            text="Temperature",
            font=("Arial", 30),
            borderwidth=1,
            width=15,
            anchor=CENTER,
            style="THFrame.TLabel"
        )
        # self.__label_temperatureText["relief"] = SOLID
        self.__label_temperatureText.pack()

        # 2. create a temperature reading Label
        self.__label_temperatureReading = ttk.Label(
            self.__frame_temperature,
            text="20.3",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            textvariable=self.__t_var,
            anchor="e",
            style="THFrame.TLabel"

        )
        # self.__label_temperatureReading["relief"] = SOLID
        self.__label_temperatureReading.pack(pady=5, side=LEFT, fill="x", expand=TRUE)

        # 3. create a label for temperature units text

        # variable to hold state of selected radio button and label for units
        self.__selected_temperature_unit = StringVar()
        self.__selected_temperature_unit.set("°C")

        self.__label_temperatureUnit = ttk.Label(
            self.__frame_temperature,
            text="",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            textvariable=self.__selected_temperature_unit,
            anchor="w",
            style="THFrame.TLabel"
        )
        # self.__label_temperatureUnit["relief"] = SOLID
        self.__label_temperatureUnit.pack(pady=5, side=LEFT, fill="x", expand=TRUE)

        # 4. create a frame to hold radio buttons for units
        self.__frame_radio_units = ttk.Frame(
            self.__frame_temperature,
            style="THFrame.TLabel"
        )
        self.__frame_radio_units.pack(anchor="w", side="left")
        # self.__frame_radio_units["relief"] = SOLID

        # 5. create radio buttons and pack
        self.__radio_celsius = ttk.Radiobutton(
            self.__frame_radio_units, text="°C", value="°C", variable=self.__selected_temperature_unit,
            command=self.temperature_unitChange
        )
        self.__radio_Fahrenheit = ttk.Radiobutton(
            self.__frame_radio_units, text="°F", value="°F", variable=self.__selected_temperature_unit,
            command=self.temperature_unitChange
        )

        self.__radio_celsius.pack(fill=X, expand=TRUE)
        self.__radio_Fahrenheit.pack(fill=X, expand=TRUE)

        # ------create a Frame for humidity -------------------------------------------------------

        self.__frame_humidity = ttk.Frame(
            self.__frame_reading_wrapper, borderwidth=5, relief="raised", padding=20,
            style="THFrame.TLabel"
        )
        self.__frame_humidity.pack(side=LEFT, anchor="nw", padx=10, pady=10, expand=TRUE, fill="x")

        # 1. create label for humidity text
        self.__label_humidityText = ttk.Label(
            self.__frame_humidity,
            text="Humidity",
            font=("Arial", 30),
            borderwidth=1,
            width=15,
            anchor=CENTER,
            style="THFrame.TLabel"
        )
        # self.__label_humidityText["relief"] = SOLID
        self.__label_humidityText.pack()

        # 2. create label for humidity reading
        self.__label_humidityReading = ttk.Label(
            self.__frame_humidity,
            text="100 %",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            textvariable=self.__h_var,
            anchor="e",
            style="THFrame.TLabel"
        )
        # self.__label_humidityReading["relief"] = SOLID
        self.__label_humidityReading.pack(pady=5, side=LEFT, expand=True, fill="x")

        # 3. create label for humidity units
        self.__label_humidityUnits = ttk.Label(
            self.__frame_humidity,
            text="%",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            anchor="w",
            style="THFrame.TLabel"
        )
        # self.__label_humidityUnits["relief"] = SOLID
        self.__label_humidityUnits.pack(pady=5, side=LEFT, expand=TRUE, fill="x")

        # ------create a Frame for CO2 -------------------------------------------------------
        self.__style_CO2_Frame = ttk.Style()
        self.__style_CO2_Frame.configure("CO2Frame.TFrame", background="LightBlue1")
        self.__style_CO2_Label = ttk.Style()
        self.__style_CO2_Label.configure("CO2Frame.TLabel", background="LightBlue1")

        self.__frame_CO2 = ttk.Frame(
            self.__frame_reading_wrapper, borderwidth=5, relief="raised", padding=20, style="CO2Frame.TFrame"
        )
        self.__frame_CO2.pack(side=LEFT, anchor="nw", padx=10, pady=10, fill="x", expand=TRUE)

        # 1. create label for co2 text
        self.__label_CO2Text = ttk.Label(
            self.__frame_CO2,
            text="CO2",
            font=("Arial", 30),
            borderwidth=1,
            width=15,
            anchor=CENTER,
            style="CO2Frame.TLabel"
        )
        # self.__label_CO2Text["relief"] = SOLID
        self.__label_CO2Text.pack()

        # 2. create a label for co2 reading
        self.__label_CO2Reading = ttk.Label(
            self.__frame_CO2,
            text="2000 ppm",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            textvariable=self.__co2_var,
            anchor="e",
            style="CO2Frame.TLabel"
        )
        # self.__label_CO2Reading["relief"] = SOLID
        self.__label_CO2Reading.pack(pady=5, side=LEFT, fill="x", expand=TRUE)

        # 3. create a label for co2 units
        self.__label_CO2Unit = ttk.Label(
            self.__frame_CO2,
            text="ppm",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            anchor="w",
            style="CO2Frame.TLabel"
        )
        # self.__label_CO2Unit["relief"] = SOLID

        self.__label_CO2Unit.pack(pady=5, side=LEFT, fill="x", expand=TRUE)

        # FRAME for LOGGING--------------------------------------------------
        self.__frame_log = ttk.Frame(self.__root, width=50, height=50, borderwidth=5, relief="raised", padding=20)
        self.__frame_log.pack(anchor="nw", padx=10, pady=10, fill="x")

        # Title Label
        self.__title_label = ttk.Label(self.__frame_log, text="Log", font=("Arial", 14))
        self.__title_label.pack(anchor="w", pady=5)

        # Buttons Frame
        self.__frame_button_log = ttk.Frame(self.__frame_log)
        self.__frame_button_log.pack(fill="x", pady=5)

        self.__button_start_log = ttk.Button(self.__frame_button_log, text="Start", command=self.start_logging,
                                             width=10)
        self.__button_start_log.pack(side="left", padx=5)

        self.__button_stop_log = ttk.Button(self.__frame_button_log, state="disabled", text="Stop",
                                            command=self.stop_logging, width=10)
        self.__button_stop_log.pack(side="left", padx=5)

        # Folder Path Frame
        self.__frame_folder_log = ttk.Frame(self.__frame_log)
        self.__frame_folder_log.pack(fill="x", pady=5)

        self.__label_folder = ttk.Label(self.__frame_folder_log, text="Folder Path:")
        self.__label_folder.pack(side="left", padx=5)

        self.__entry_folderName = ttk.Entry(self.__frame_folder_log)
        self.__entry_folderName.pack(side="left", fill="x", expand=True, padx=5)

        self.__button_filebrowse = ttk.Button(self.__frame_folder_log, text="Browse", command=self.browse_folder)
        self.__button_filebrowse.pack(side="left", padx=5)

        # File Name Frame
        self.__frame_fileName = ttk.Frame(self.__frame_log)
        self.__frame_fileName.pack(fill="x", pady=5)

        self.__label_fileName = ttk.Label(self.__frame_fileName, text="File Name:")
        self.__label_fileName.pack(side="left", padx=5)

        self.__entry_fileName = ttk.Entry(self.__frame_fileName)
        self.__entry_fileName.pack(side="left", fill="x", expand=True, padx=5)

        # Options Frame
        self.__frame_options = ttk.Frame(self.__frame_log)
        self.__frame_options.pack(fill="x", pady=5)

        self.__var_append_create = StringVar(value="append")

        self.__radio_append = ttk.Radiobutton(self.__frame_log, text="Append if exists",
                                              variable=self.__var_append_create, value="append")
        self.__radio_append.pack(side="left", padx=5)

        self.__radio_create = ttk.Radiobutton(self.__frame_log, text="Create new", variable=self.__var_append_create,
                                              value="create")
        self.__radio_create.pack(side="left", padx=5)

        # Checkbox and Dropdown Frame
        # misc_frame = ttk.Frame(self.__frame_log)
        # misc_frame.pack(fill="x", pady=5)

        self.__var_only_difference = BooleanVar()
        self.__checkbox_difference = ttk.Checkbutton(self.__frame_log, text="Log Differences",
                                                     variable=self.__var_only_difference)
        self.__checkbox_difference.pack(side="left", padx=5)

        # ---------------------------------------------------------
        self.__frame_sensation = ttk.Frame(self.__root, borderwidth=5, relief="raised", padding=20)
        self.__frame_sensation.pack(anchor="nw", padx=10, pady=10, fill="x")

        self.__label_sensation = ttk.Label(self.__frame_sensation, text="Sensation", font=("Arial", 30))
        self.__label_sensation.pack(anchor="w", pady=5)

        self.__var_sensation = StringVar()
        self.__var_sensation.set("___")
        self.__label_sensation_reading = ttk.Label(self.__frame_sensation, text="-", textvariable=self.__var_sensation,
                                                   font=("Arial", 30), )
        self.__label_sensation_reading.pack(anchor="w", pady=5)

        self.__frame_settings = ttk.Frame(self.__frame_sensation, borderwidth=5, relief="raised", padding=20)
        self.__frame_settings.pack(anchor="w", side=LEFT)
        self.__frame_activity = ttk.Frame(self.__frame_settings, borderwidth=5, padding=20)
        self.__frame_activity.pack(side=LEFT)
        self.__label_activity = ttk.Label(self.__frame_activity, text="Activity", font=("Arial", 14))
        self.__label_activity.pack()
        self.__combo_activity = ttk.Combobox(self.__frame_activity, width=30,
                                             values=[key for key in self.__dict_activity])
        self.__combo_activity.set("Seated, quiet")
        self.__combo_activity.pack()

        self.__frame_clothing = ttk.Frame(self.__frame_settings, borderwidth=5, padding=20)
        self.__frame_clothing.pack(side=LEFT)
        self.__label_clothing = ttk.Label(self.__frame_clothing, text="Clothing", font=("Arial", 14))
        self.__label_clothing.pack()
        self.__combo_clothing = ttk.Combobox(self.__frame_clothing, width=30,
                                             values=[key for key in self.__dict_clothing])
        self.__combo_clothing.set("Typical summer indoor clothing")
        self.__combo_clothing.pack()

        self.__button_apply_settings = ttk.Button(self.__frame_settings, text="apply",
                                                  command=self.apply_changed_settings)
        self.__button_apply_settings.pack(side=LEFT, padx=10)

        # MATPLOtLIB---------------------------------------------------------------------------------------------------------
        self.__fig, self.__ax = plt.subplots()

        list_rh, list_low, list_high = self.get_graph_margins()

        self.__ax.fill_betweenx(list_rh, list_low, list_high, color='teal', alpha=0.2)
        #
        self.__ax.set_xlabel('Air Temperature (C)')
        self.__ax.set_ylabel('Relative Humidity (%)')
        self.__ax.set_xlim(10, 36)
        self.__ax.set_ylim(0, 100)
        self.__ax.set_title('T vs Rh in Neutral Band')
        plt.legend(['Neutral Band'])
        plt.grid()

        # create an empty point object to be plotted later on
        self.__point, = self.__ax.plot([], [], marker='*', color='red', markersize=10, label='Point')

        # Embed the Matplotlib figure in Tkinter
        self.__frame_chart = ttk.Frame(self.__frame_sensation, borderwidth=5, relief="raised", padding=20)
        self.__frame_chart.pack(anchor="w", expand=True, fill=BOTH)
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=self.__frame_chart)
        self.__canvas_widget = self.__canvas.get_tk_widget()
        self.__canvas_widget.pack()

        # other tasks to be done before gui loop is called---------------------------------------------------------
        self.__root.after(100, self.update_readings)

        # Extra trial space---------------------------------------------------------
        self.__root.protocol("WM_DELETE_WINDOW", self.on_closing)


def main():
    thermalDashboard = UI()
    thermalDashboard.start()


main()
