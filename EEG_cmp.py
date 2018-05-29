# -*- coding: utf-8 -*-
# MY PROJECT
# !/usr/bin/python
# import sys
# from Tkinter import Frame, PhotoImage, RIDGE, Label, Canvas, LabelFrame, Button
#  import scipy
# import scipy.io

from ttk import Combobox

import canvasDraw
import canvasDraw2
import compareAllMatrixes
import nmsimilarity as Nm
from exceptions import ValueError

import xlrd
import numpy
from Tkinter import *
import tkMessageBox
import tkFont
import tkColorChooser
import tkFileDialog
try:
    import MySQLdb
except ImportError:
    import pymysql as MySQLdb

#######################################################################################################################


class MatrixUtils(object):
    """Function that Works with matrix"""

    MATRIX_SIZE = 64  # const size for all matrixes

    @staticmethod
    # convert string to matrix
    def import_matrix_from_excel(path_name):
        book = xlrd.open_workbook(path_name)
        sh = book.sheet_by_index(0)
        mat = []
        for rx in range(MatrixUtils.MATRIX_SIZE):
            mat.append([])
            for cx in range(MatrixUtils.MATRIX_SIZE):
                mat[rx].append(sh.cell_value(rowx=rx, colx=cx))
        return mat

    @staticmethod
    # convert string to matrix
    def str_to_matrix(matrix_str):
        m_1d_array = matrix_str[1:-1].split(",")
        m_1d_array = [float(x) for x in m_1d_array]
        matrix = numpy.ndarray(shape=(MatrixUtils.MATRIX_SIZE, MatrixUtils.MATRIX_SIZE), dtype='float32')
        for i in xrange(len(m_1d_array)):
            x, y = i / MatrixUtils.MATRIX_SIZE, i % MatrixUtils.MATRIX_SIZE
            matrix[x][y] = m_1d_array[i]
        return matrix

    @staticmethod
    # convert matrix to str
    def matrix_to_str(matrix):
        return "[" + ",".join([",".join([str(e) for e in r]) for r in matrix]) + "]"

    """
    @staticmethod
    # Reads a 64x64 matrix from .mat file
    def read_matrix_from_mat_file(file_path):
        mat = scipy.io.loadmat(file_path, squeeze_me=True)
        matrix = mat['correlationMAT']
        return matrix
    """

    @staticmethod
    # matching between matrix to participant
    def get_matrix_by_experiment_id(experiment_id):
        query = "SELECT experimentid, resultid, matrix \
                 FROM finalproject.result \
                 WHERE experimentid = {0};"
        result = get_sql_query_result(query.format(experiment_id))
        matrixes = []
        for row in result:
            experiment_id, result_id, matrix = row[0], row[1], MatrixUtils.str_to_matrix(row[2])
            matrixes.append({"experiment_id": experiment_id,
                             "result_id": result_id,
                             "matrix": matrix})

        return matrixes

    @staticmethod
    # save matrix in DB
    def save_matrix_by_experiment_id(matrix, participant_id, step, experiment_id):
        # experiment_id validation
        try:
            experiment_id = int(experiment_id)
        except ValueError:
            tkMessageBox.showerror("Experiment id only int")

        try:
            participant_id = int(participant_id)
        except ValueError:
            tkMessageBox.showerror("participant id only int")

        conn = MySQLdb.connect(user='root', passwd="DY696963", db="finalproject")
        cur = conn.cursor()

        # insert the new matrix into the results table
        query = "INSERT INTO result(matrix,participantid, step, experimentid) values('{0}' , {1}, {2}, {3});" \
            .format(MatrixUtils.matrix_to_str(matrix), participant_id, step, experiment_id)
        try:
            cur.execute(query)
            conn.commit()
        except:
            conn.rollback()


#######################################################################################################################


class MainFrame(Tk):
    """Building the windows"""

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.title_font = tkFont.Font(family='Helvetica', size=10, weight="bold", slant="italic")
        self.height = 740
        self.width = 900
        self.geometry('{}x{}+{}+{}'.format(self.width, self.height, "500", "50"))
        self.resizable(1, 1)
        self.db_host = "localhost"
        self.db_name = "root"
        self.db_pass = "Braude"
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenu, FirstPage, CompareTwoGraphs, ExistingParticipant, AddNewParticipant, AddNewExperiment,
                  ViewMatrix, CompareTwoGraphsResult, AutoCompareResult):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("FirstPage")

    def show_frame(self, page_name):
        # Show a frame for the given page name
        frame = self.frames[page_name]
        frame.execute_draw()
        frame.tkraise()

#######################################################################################################################


class FirstPage(Frame):
    """ Building 'FirstPage' window"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.hostLabel = Label(self, text="DB host     :", font=controller.title_font)
        self.hostLabel.place(x=10, y=25)
        self.nameLabel = Label(self, text="DB name     :", font=controller.title_font)
        self.nameLabel.place(x=10, y=75)
        self.passwordLabel = Label(self, text="DB password :", font=controller.title_font)
        self.passwordLabel.place(x=10, y=125)

        self.hostEntry = Entry(self)
        self.hostEntry.insert(0, self.controller.db_host)
        self.hostEntry.place(x=110, y=25, width=150)
        self.nameEntry = Entry(self)
        self.nameEntry.insert(0, self.controller.db_name)
        self.nameEntry.place(x=110, y=75, width=150)
        self.passwordEntry = Entry(self)
        self.passwordEntry.insert(0, self.controller.db_pass)
        self.passwordEntry.place(x=110, y=125, width=150)

        enterButton = Button(self, text="Enter", font=controller.title_font, command=lambda: self.on_enter())
        enterButton.place(x=60, y=200, width=150)

    def on_enter(self):
        self.controller.db_host = self.hostEntry.get()
        self.controller.db_name = self.nameEntry.get()
        self.controller.db_pass = self.passwordEntry.get()
        self.create_db()

    def create_db(self):
        """Create DB with name finalproject"""
        cursor = None
        try:
            db = MySQLdb.connect(self.controller.db_host,  self.controller.db_name,  self.controller.db_pass)
            cursor = db.cursor()
        except MySQLdb.Error:
            tkMessageBox.showerror('Error', 'One or more fields are not consistent with your database details. Please try again.')

        if cursor is not None:
            try:
                cursor.execute("CREATE DATABASE finalproject;")
                cursor.execute("USE finalproject;")

                cursor.execute("CREATE TABLE IF NOT EXISTS `finalproject`.`experiment` (\
                                `experimentid` INT NOT NULL AUTO_INCREMENT,\
                                `experimentname` VARCHAR(45) NOT NULL,\
                                `description` VARCHAR(1000) NOT NULL,\
                                PRIMARY KEY (`experimentid`));")

                cursor.execute("CREATE TABLE IF NOT EXISTS `finalproject`.`experpartic` (\
                                `participantid` INT NOT NULL,\
                                `experimentid` INT NOT NULL,\
                                PRIMARY KEY (`participantid`, `experimentid`));")

                cursor.execute("CREATE TABLE IF NOT EXISTS `finalproject`.`groups` (\
                                `groupid` INT NOT NULL AUTO_INCREMENT,\
                                `groupname` VARCHAR(45) NOT NULL,\
                                PRIMARY KEY (`groupid`));")
                cursor.execute("INSERT INTO  `finalproject`.`groups`(groupid,groupname) VALUES(1,'adhd')")
                cursor.execute("INSERT INTO `finalproject`.`groups`(groupid,groupname) VALUES(2,'hgc')")

                cursor.execute("CREATE TABLE IF NOT EXISTS `finalproject`.`participant` (\
                                `participantid` INT NOT NULL AUTO_INCREMENT,\
                                `firstname` VARCHAR(45) NOT NULL,\
                                `lastname` VARCHAR(45) NOT NULL,\
                                `date` VARCHAR(45) NOT NULL,\
                                `age` INT NOT NULL,\
                                `groupid` INT NOT NULL,\
                                PRIMARY KEY (`participantid`));")

                cursor.execute("CREATE TABLE IF NOT EXISTS `finalproject`.`result` (\
                                `resultid` INT NOT NULL AUTO_INCREMENT,\
                                `matrix` MEDIUMTEXT NOT NULL,\
                                `participantid` INT NOT NULL,\
                                `step` INT NOT NULL,\
                                `experimentid` INT NOT NULL,\
                                PRIMARY KEY (`resultid`));")

                db.commit()
                db.close()
            except MySQLdb.Error:
                pass  # print "DataBase already exists"

            self.controller.show_frame("MainMenu")

    def execute_draw(self):
        self.controller.title('EEG Comparison')
#######################################################################################################################


class MainMenu(Frame):
    """Building the first window - 'Main Menu'"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        button1 = Button(self, text="Compare Two Graphs", font=controller.title_font,
                         command=lambda: controller.show_frame("CompareTwoGraphs"))
        button1.place(anchor="n", relx=0.5, y=-65, rely=0.2, height=130, width=600)
        button2 = Button(self, text="Existing Participant", font=controller.title_font,
                         command=lambda: controller.show_frame("ExistingParticipant"))
        button2.place(anchor="n", relx=0.5, y=-65, rely=0.4, height=130, width=600)
        button3 = Button(self, text="Add New Participant", font=controller.title_font,
                         command=lambda: controller.show_frame("AddNewParticipant"))
        button3.place(anchor="n", relx=0.5, y=-65, rely=0.6, height=130, width=600)
        button4 = Button(self, text="Adding an experiment to the system / user", font=controller.title_font,
                         command=lambda: controller.show_frame("AddNewExperiment"))
        button4.place(anchor="n", relx=0.5, y=-65, rely=0.8, height=130, width=600)

    def execute_draw(self):
        self.controller.title('MainMenu')


#######################################################################################################################


class CompareTwoGraphs(Frame):
    """Building Compare Two Graphs window"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        left_frame = Frame(self, relief=RIDGE, bd=1)
        left_frame.place(anchor="nw", relx=0.02, rely=0.02, relwidth=0.45, height=320)

        right_frame = Frame(self, relief=RIDGE, bd=1)
        right_frame.place(anchor="ne", relx=0.98, rely=0.02, relwidth=0.45, height=320)

        label1 = Label(left_frame, text="Experiment", font=controller.title_font)
        label1.place(x=5, y=5)

        label2 = Label(left_frame, text="Group", font=controller.title_font)
        label2.place(x=5, y=100)

        label3 = Label(left_frame, text="ID", font=controller.title_font)
        label3.place(x=5, y=195)

        label4 = Label(left_frame, text="Step in Experiment", font=controller.title_font)
        label4.place(x=5, y=290)

        label5 = Label(right_frame, text="Experiment", font=controller.title_font)
        label5.place(x=5, y=5)

        label6 = Label(right_frame, text="Group", font=controller.title_font)
        label6.place(x=5, y=100)

        label7 = Label(right_frame, text="ID", font=controller.title_font)
        label7.place(x=5, y=180)

        label8 = Label(right_frame, text="Step in Experiment", font=controller.title_font)
        label8.place(x=5, y=290)

        self.combobox1 = Combobox(left_frame)
        self.combobox1.place(x=170, y=5)

        self.combobox2 = Combobox(left_frame)
        self.combobox2.place(x=170, y=100)

        self.combobox3 = Combobox(left_frame)
        self.combobox3.place(x=170, y=195)

        self.combobox4 = Combobox(left_frame)
        self.combobox4.place(x=170, y=290)

        self.combobox5 = Combobox(right_frame)
        self.combobox5.place(x=170, y=5)

        self.combobox6 = Combobox(right_frame)
        self.combobox6.place(x=170, y=100)

        self.combobox7 = Combobox(right_frame)
        self.combobox7.place(x=170, y=195)

        self.combobox8 = Combobox(right_frame)
        self.combobox8.place(x=170, y=290)

        # validate
        def validate_show_result_button():
            """validation"""
            if self.combobox4.get() == "" or self.combobox8.get() == "":
                tkMessageBox.showerror('Error', 'Complete all the sections above!')
            else:
                self.controller.frames["CompareTwoGraphsResult"].back_window = "CompareTwoGraphs"
                controller.show_frame("CompareTwoGraphsResult")

        button1 = Button(self, text="Show Result", font=controller.title_font,
                         command=validate_show_result_button, width=25, height=5)
        button1.place(anchor="s", relx=0.5, rely=0.8)

        def back_button():
            """ If Back button is pushed"""
            self.combobox1.set("")  # clear the combobox
            self.combobox2.set("")
            self.combobox3.set("")
            self.combobox4.set("")

            self.combobox5.set("")
            self.combobox6.set("")
            self.combobox7.set("")
            self.combobox8.set("")
            controller.show_frame("MainMenu")

        button2 = Button(self, text="Back", font=controller.title_font,
                         command=back_button, width=15)
        button2.place(x=5, rely=0.95)

        def get_participants_id(event):
            """For the selected participant,
            by selecting the experiment and selecting the group,
            dataBase will show us all users belonging to the same group in the same experiment"""

            self.combobox1['values'] = [row[0] for row in get_sql_query_result("SELECT experimentname FROM experiment")]
            self.combobox2['values'] = ["-".join([str(row[0]), row[1]]) for row in
                                        get_sql_query_result("SELECT groupid, groupname FROM groups")]

            if event.type == '35':  # event= (ComboboxSelected)
                self.combobox3.set("")
                self.combobox4.set("")
                self.combobox4['values'] = []

        self.combobox1.bind("<Button-1>", get_participants_id)
        self.combobox2.bind("<Button-1>", get_participants_id)

        self.combobox1.bind("<<ComboboxSelected>>", get_participants_id)
        self.combobox2.bind("<<ComboboxSelected>>", get_participants_id)

        def update_combo3(event):
            """work with combobox3"""
            if event.type == '4':  # event = combobox pushed
                experiment = self.combobox1.get()
                groupid = self.combobox2.get().lower().split("-")[0]
                if experiment == "" or groupid == "":
                    return

                query = "SELECT participantid, firstname, lastname \
                        FROM finalproject.experiment \
                        NATURAL JOIN finalproject.participant \
                        NATURAL join finalproject.experpartic \
                        WHERE experimentname='{experiment}' \
                                AND groupid={groupid};"

                result = get_sql_query_result(query.format(experiment=experiment, groupid=groupid))

                participants = []

                for row in result:
                    participants.append("{id}: ({first} {last})".format(id=row[0], first=row[1], last=row[2]))

                self.combobox3['values'] = participants

            if event.type == '35':  # event = comboboxselected
                self.combobox4.set("")
                self.combobox4['values'] = []

        self.combobox3.bind("<Button-1>", update_combo3)
        self.combobox3.bind("<<ComboboxSelected>>", update_combo3)

        def find_resultid_by_participantid_and_experimentid(event):
            """Find the step of the left participant"""
            experiment = self.combobox1.get()
            query = "SELECT experimentid \
                    FROM finalproject.experiment \
                    WHERE experimentname='{experiment}';"

            expid = get_sql_query_result(query.format(experiment=experiment))

            participant = str(self.combobox3.get()).split(":")

            query1 = " SELECT step FROM finalproject.result \
                      WHERE participantid = {participantid} \
                      AND experimentid = {experimentid}; " \
                .format(participantid=participant[0], experimentid=expid[0][0])
            stepid = get_sql_query_result(query1)
            step = []
            for x in stepid:
                step.append("step : {step}".format(step=x[0]))
            self.combobox4['values'] = step

            if len(step) > 0:
                self.combobox4.current(0)
            else:
                self.combobox4.set("")

        self.combobox4.bind("<Button-1>", find_resultid_by_participantid_and_experimentid)

        def get_participants_id(event):
            """For the selected participant,
            by selecting the experiment and selecting the group,
            dataBase will show us all users belonging to the same group in the same experiment"""

            self.combobox5['values'] = [row[0] for row in get_sql_query_result("SELECT experimentname FROM experiment")]
            self.combobox6['values'] = ["-".join([str(row[0]), row[1]]) for row in
                                        get_sql_query_result("SELECT groupid, groupname FROM groups")]

            if event.type == '35':  # event= (ComboboxSelected)
                self.combobox7.set("")
                self.combobox8.set("")
                self.combobox8['values'] = []

        self.combobox5.bind("<Button-1>", get_participants_id)
        self.combobox6.bind("<Button-1>", get_participants_id)

        self.combobox5.bind("<<ComboboxSelected>>", get_participants_id)
        self.combobox6.bind("<<ComboboxSelected>>", get_participants_id)

        def update_combo7(event):
            """work with combobox7"""

            experiment = self.combobox5.get()
            groupid = self.combobox6.get().lower().split("-")[0]
            if experiment == "" or groupid == "":
                return
            if event.type == '4':  # event = combobox7 is pushed
                query = "SELECT participantid, firstname, lastname \
                    FROM finalproject.experiment \
                    NATURAL JOIN finalproject.participant \
                    NATURAL join finalproject.experpartic \
                    WHERE experimentname='{experiment}' \
                    AND groupid={groupid};"

                result = get_sql_query_result(query.format(experiment=experiment, groupid=groupid))

                participants = []

                for row in result:
                    participants.append("{id}: ({first} {last})".format(id=row[0], first=row[1], last=row[2]))

                self.combobox7['values'] = participants

            if event.type == '35':  # event = comboboxselected
                self.combobox8.set("")
                self.combobox8['values'] = []

        self.combobox7.bind("<Button-1>", update_combo7)
        self.combobox7.bind("<<ComboboxSelected>>", update_combo7)

        def find_resultid_by_participantid_and_experimentid(event):
            """find the step of the rigth participant"""
            experiment = self.combobox5.get()
            query = "SELECT experimentid \
                    FROM finalproject.experiment \
                    WHERE experimentname='{experiment}';"

            expid = get_sql_query_result(query.format(experiment=experiment))

            participant = str(self.combobox7.get()).split(":")

            query1 = "SELECT step FROM finalproject.result \
                      WHERE participantid = {participantid} \
                      AND experimentid = {experimentid};" \
                .format(participantid=participant[0], experimentid=expid[0][0])
            stepid = get_sql_query_result(query1)
            step = []
            for x in stepid:
                step.append("step : {step}".format(step=x[0]))
            self.combobox8['values'] = step

        self.combobox8.bind("<Button-1>", find_resultid_by_participantid_and_experimentid)

    def things_for_CompareTwoGraphsResult(self):
        """ Find to 'Compare Two Graphs' the values he need """

        query = "SELECT experimentid \
                    FROM finalproject.experiment \
                    WHERE experimentname='{experiment}';"

        query1 = "SELECT matrix FROM finalproject.result \
                        WHERE participantid = {participantid} \
                        AND experimentid = {experimentid} \
                        AND step = {step}"

        experiment = self.combobox1.get()
        expid = get_sql_query_result(query.format(experiment=experiment))[0][0]
        partic_id_name = self.combobox3.get().split(":")[0]
        step_in_exper = self.combobox4.get().split(":")[1]
        result = get_sql_query_result(query1.format(participantid=partic_id_name,
                                                    experimentid=expid, step=step_in_exper))[0][0]
        self.controller.frames["CompareTwoGraphsResult"].matrix_left = MatrixUtils.str_to_matrix(str(result))
        self.controller.frames["CompareTwoGraphsResult"].matrix_left_info = (self.combobox1.get(),
                                                                             self.combobox2.get(),
                                                                             self.combobox3.get(),
                                                                             self.combobox4.get().split(":")[1])

        experiment = self.combobox5.get()
        expid = get_sql_query_result(query.format(experiment=experiment))[0][0]
        partic_id_name = self.combobox7.get().split(":")[0]
        step_in_exper = self.combobox8.get().split(":")[1]
        result = get_sql_query_result(query1.format(participantid=partic_id_name,
                                                    experimentid=expid, step=step_in_exper))[0][0]
        self.controller.frames["CompareTwoGraphsResult"].matrix_right = MatrixUtils.str_to_matrix(str(result))
        self.controller.frames["CompareTwoGraphsResult"].matrix_right_info = (self.combobox5.get(),
                                                                              self.combobox6.get(),
                                                                              self.combobox7.get(),
                                                                              self.combobox8.get().split(":")[1])
        self.controller.frames["CompareTwoGraphsResult"].back_window = "CompareTwoGraphs"

    def execute_draw(self):
        self.controller.title('CompareTwoGraphs')


#######################################################################################################################


class ExistingParticipant(Frame):
    """ Building 'Existing Participant' window"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.my_matrix = []
        self.my_vector = []

        label1 = Label(self, text="Experiment", font=controller.title_font)
        label1.place(x=10, y=25)

        label2 = Label(self, text="Group", font=controller.title_font)
        label2.place(x=10, y=70)

        label3 = Label(self, text="ID (Full Name)", font=controller.title_font)
        label3.place(x=10, y=115)

        label4 = Label(self, text="Step in Experiment", font=controller.title_font)
        label4.place(x=10, y=400)

        label5 = Label(self, text="* Note:\n"
                                  + "If you want to add a matrix for a particular participant,\n"
                                  + "please complete all the sections above (Experiment, Group, ID).\n"
                                  + "If you want to view a particular matrix,\n"
                                  + "please fill the section below in addition to the sections above.",
                       font=controller.title_font, anchor="w", justify=LEFT)
        label5.place(x=10, y=270)

        self.combobox1 = Combobox(self)
        self.combobox1.place(x=250, y=25)

        self.combobox2 = Combobox(self)
        self.combobox2.place(x=250, y=70)

        self.combobox3 = Combobox(self)
        self.combobox3.place(x=250, y=115)

        self.combobox4 = Combobox(self)
        self.combobox4.place(x=250, y=400)

        def back_button():
            """ If back button is pushed"""

            self.combobox1.set("")  # clear combobox
            self.combobox2.set("")
            self.combobox3.set("")
            self.combobox4.set("")
            controller.show_frame("MainMenu")

        button1 = Button(self, text="Back", font=controller.title_font,
                         command=back_button,
                         width=15)
        button1.place(relx=0.1, rely=0.95)

        ment = StringVar()
        mEntery = Entry(self, textvariable=ment, width=65)
        mEntery.place(relx=0.25, y=205, height=25)

        def get_participants_id(event):
            """For the selected participant,
               by selecting the experiment and selecting the group,
               dataBase will show us all users belonging to the same group in the same experiment"""

            self.combobox1['values'] = [row[0] for row in get_sql_query_result("SELECT experimentname FROM experiment")]
            self.combobox2['values'] = ["-".join([str(row[0]), row[1]]) for row in
                                        get_sql_query_result("SELECT groupid, groupname FROM groups")]

            if event.type == '35':  # event= (ComboboxSelected)
                self.combobox3.set("")
                self.combobox4.set("")
                self.combobox4['values'] = []

        self.combobox1.bind("<Button-1>", get_participants_id)
        self.combobox2.bind("<Button-1>", get_participants_id)

        self.combobox1.bind("<<ComboboxSelected>>", get_participants_id)
        self.combobox2.bind("<<ComboboxSelected>>", get_participants_id)

        def update_combo3(event):
            """ work with combobox3"""

            if event.type == '4':
                experiment = self.combobox1.get()
                groupid = self.combobox2.get().lower().split("-")[0]
                if experiment == "" or groupid == "":
                    return

                query = "SELECT participantid, firstname, lastname \
                        FROM finalproject.experiment \
                        NATURAL JOIN finalproject.participant \
                        NATURAL join finalproject.experpartic \
                        WHERE experimentname='{experiment}' \
                                AND groupid={groupid};"

                result = get_sql_query_result(query.format(experiment=experiment, groupid=groupid))

                participants = []

                for row in result:
                    participants.append("{id}: ({first} {last})".format(id=row[0], first=row[1], last=row[2]))

                self.combobox3['values'] = participants

            if event.type == '35':  # event = ComboboxSelected
                self.combobox4.set("")
                self.combobox4['values'] = []

        self.combobox3.bind("<Button-1>", update_combo3)
        self.combobox3.bind("<<ComboboxSelected>>", update_combo3)

        def find_resultid_by_participantid_and_experimentid(event):
            """find the step for the left participant"""
            if self.combobox3.get() != "":
                experiment = self.combobox1.get()
                query = "SELECT experimentid \
                        FROM finalproject.experiment \
                        WHERE experimentname='{experiment}';"

                expid = get_sql_query_result(query.format(experiment=experiment))

                participant = str(self.combobox3.get()).split(":")
                query1 = " SELECT step FROM finalproject.result \
                          WHERE participantid = {participantid} \
                          AND experimentid = {experimentid}; " \
                    .format(participantid=participant[0], experimentid=expid[0][0])
                stepid = get_sql_query_result(query1)
                step = []
                for x in stepid:
                    step.append("step : {step}".format(step=x[0]))
                self.combobox4['values'] = step

                if len(step) > 0:
                    self.combobox4.current(0)
                else:
                    self.combobox4.set("")

        self.combobox4.bind("<Button-1>", find_resultid_by_participantid_and_experimentid)

        def add_test_result():
            """ Adding the result to DB, to the specific participant"""
            if mEntery.get() == "":
                tkMessageBox.showerror('Error', 'Faild added, select a file before adding')
            elif self.combobox3.get() == "":
                tkMessageBox.showerror('Error', 'Faild added, select a participant before adding')
            else:
                tkMessageBox.showinfo('Succsseful', 'Succssefully added')

            experiment = self.combobox1.get().lower()

            query = "SELECT experimentid \
                        FROM finalproject.experiment \
                        WHERE experimentname='{experiment}';"
            expid = get_sql_query_result(query.format(experiment=experiment))

            participant = str(self.combobox3.get()).split(":")
            query1 = "SELECT COUNT(resultid) \
                        FROM finalproject.result \
                        WHERE experimentid={experimentid} \
                        AND participantid={participantid};".format(experimentid=expid[0][0],
                                                                   participantid=participant[0])

            step = get_sql_query_result(query1)
            step = (step[0][0] + 1)

            MatrixUtils.save_matrix_by_experiment_id(MatrixUtils.import_matrix_from_excel(mEntery.get()),
                                                     participant[0],
                                                     step, expid[0][0])

            mEntery.delete(0, 'end')  # Clear the text from entrybox

        button2 = Button(self, text="Add Step Result", font=controller.title_font, command=add_test_result, width=15)
        button2.place(x=10, y=205)

        def browse_from_filesystem():
            """ Browse the file from system"""
            mEntery.insert(0, mOpen())

        def mOpen():
            """ load a file"""
            rv = tkFileDialog.askopenfile()
            try:
                mEntery.delete(0, 'end')
                return rv.name
            except AttributeError:
                return mEntery.get()

        button3 = Button(self, text="Browse", font=controller.title_font, command=browse_from_filesystem, width=8)
        button3.place(relx=0.80, y=205)

        def validate_auto_compare_button():
            if self.combobox3.get() == "":
                self.combobox4["values"] = []
                tkMessageBox.showerror('Error', 'Complete all the sections above!(AutoComp)')
            else:
                experiment = self.combobox1.get()
                query = "SELECT experimentid \
                                        FROM finalproject.experiment \
                                        WHERE experimentname='{experiment}';"

                expid = get_sql_query_result(query.format(experiment=experiment))

                participant = str(self.combobox3.get()).split(":")
                query1 = " SELECT step FROM finalproject.result \
                                          WHERE participantid = {participantid} \
                                          AND experimentid = {experimentid}; " \
                    .format(participantid=participant[0],
                            experimentid=expid[0][0])
                stepid = get_sql_query_result(query1)
                step = []
                for x in stepid:
                    step.append("step : {step}".format(step=x[0]))

                if len(step) < 2:  # we can not do sequence's compare if there are less then 2 matrixes
                    tkMessageBox.showerror('Error', 'There are not enough steps in the experiment (at least 2)')
                else:
                    controller.show_frame("AutoCompareResult")

        button5 = Button(self, text="Auto Compare", font=controller.title_font,
                         command=validate_auto_compare_button, width=15)
        button5.place(x=10, y=160)

        def remove_exsisting_participant(participantid):
            """ Deletes all information that exists on this participant"""
            query = "DELETE  FROM  result WHERE participantid = {participantid}; "
            sql_execute_query(query.format(participantid=participantid))

            query = "DELETE  FROM  experpartic WHERE participantid = {participantid}; "
            sql_execute_query(query.format(participantid=participantid))

            query = "DELETE  FROM participant WHERE participantid = {participantid};"
            sql_execute_query(query.format(participantid=participantid))

            if self.combobox3.get() == "":
                tkMessageBox.showerror('Delete', 'Delete failed, select a participant before deleting')
            else:
                tkMessageBox.showinfo('Succsseful delete', 'Succssefully deleted')
                self.combobox3.set("")
                self.combobox3['values'] = []
                self.combobox4.set("")
                self.combobox4['values'] = []

        button6 = Button(self, text="Delete participant", font=controller.title_font, width=15,
                         command=lambda: remove_exsisting_participant(str(self.combobox3.get()).split(":")[0]))
        button6.place(relx=0.7, rely=0.95)

        def validate_view_matrix_button():
            """Validation of 'View Matrix' button"""
            if self.combobox4.get() == "":
                tkMessageBox.showerror('Error', "Choose a step")
            else:
                controller.show_frame("ViewMatrix")

        button4 = Button(self, text="View Matrix", font=controller.title_font, width=15,
                         command=validate_view_matrix_button)
        button4.place(x=10, y=445)

    def things_for_ViewMatrix(self):
        """calculate the values that 'View Matrix' window need"""
        experiment = self.combobox1.get()
        query = "SELECT experimentid \
                    FROM finalproject.experiment \
                    WHERE experimentname='{experiment}';"

        expid = get_sql_query_result(query.format(experiment=experiment))
        partic_id_name = self.combobox3.get().split(":")[0]
        step_in_exper = self.combobox4.get().split(":")[1]

        query1 = "SELECT matrix FROM finalproject.result \
                        WHERE participantid = {participantid} \
                        AND experimentid = {experimentid} \
                        AND step = {step}"
        result = get_sql_query_result(query1.format(participantid=partic_id_name,
                                                    experimentid=expid[0][0],
                                                    step=step_in_exper))[0][0]
        self.my_matrix = MatrixUtils.str_to_matrix(str(result))
        self.my_vector = (self.combobox1.get(),
                          self.combobox2.get(),
                          self.combobox3.get(),
                          self.combobox4.get().split(":")[1])

    def things_for_AutoCompareResult(self):
        """calculate the values that 'View Matrix' window need"""
        experiment = self.combobox1.get()
        query = "SELECT experimentid \
                FROM finalproject.experiment \
                WHERE experimentname='{experiment}';"

        expid = get_sql_query_result(query.format(experiment=experiment))[0][0]
        partic_id_name = self.combobox3.get().split(":")[0]

        query1 = "SELECT matrix FROM finalproject.result \
                    WHERE participantid = {participantid} \
                    AND experimentid = {experimentid} ;".format(participantid=partic_id_name, experimentid=expid)

        result1 = get_sql_query_result(query1)

        self.controller.frames["AutoCompareResult"].matrices = []
        for i in xrange(len(result1)):
            self.controller.frames["AutoCompareResult"].matrices.append(MatrixUtils.str_to_matrix(str(result1[i][0])))

        self.controller.frames["AutoCompareResult"].vector = (self.combobox1.get(),
                                                              self.combobox2.get(),
                                                              self.combobox3.get())

    def execute_draw(self):
        self.controller.title('ExistingParticipant')


####################################################################################################################


class AddNewExperiment(Frame):
    """Building 'Add New Experiment' window"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        first_frame = Frame(self, relief=RIDGE, bd=1)
        first_frame.place(anchor="nw", relx=0.02, rely=0.02, relwidth=0.96, relheight=0.42)

        second_frame = Frame(self, relief=RIDGE, bd=1)
        second_frame.place(anchor="nw", relx=0.02, rely=0.52, relwidth=0.96, relheight=0.42)

        label1 = Label(first_frame, text="Add New Experiment", font=controller.title_font)
        label1.place(relx=0.35, rely=0.1)

        labe2 = Label(first_frame, text="Experiment Name * ", font=controller.title_font)
        labe2.place(x=10, y=135)

        labe3 = Label(first_frame, text="Description * ", font=controller.title_font)
        labe3.place(x=10, y=235)

        label4 = Label(second_frame, text="Add Experiment For Participant", font=controller.title_font)
        label4.place(relx=0.35, rely=0.1)

        label5 = Label(second_frame, text="Participants", font=controller.title_font)
        label5.place(x=10, rely=0.35)

        label6 = Label(second_frame, text="Experiments", font=controller.title_font)
        label6.place(x=10, rely=0.8)

        self.combobox1 = Combobox(second_frame)
        self.combobox1.place(relx=0.23, rely=0.35)

        self.combobox2 = Combobox(second_frame)
        self.combobox2.place(relx=0.23, rely=0.8)
        ment2 = StringVar()
        mEntery2 = Entry(first_frame, textvariable=ment2, width=30)
        mEntery2.place(x=180, y=135)

        ment3 = StringVar()
        mEntery3 = Entry(first_frame, textvariable=ment3, width=30)
        mEntery3.place(x=180, y=235)

        def clear_with_back():
            """ if back button is pushed"""

            controller.show_frame("MainMenu")
            # Clear the text from the entry boxes
            mEntery2.delete(0, 'end')
            mEntery3.delete(0, 'end')
            self.combobox1.set("")
            self.combobox2.set("")

        button1 = Button(self, text="Back", font=controller.title_font, command=clear_with_back, width=15)
        button1.place(x=5, rely=0.95)

        def _validate_experiment(experimentname, description):
            """validation"""
            # Exprimentname validation
            if experimentname == "":
                tkMessageBox.showerror('Error', 'Invalid experimnetname!')
                raise ValueError("Illegal Experiment name")

            query = "SELECT experimentname FROM finalproject.experiment"
            expname = get_sql_query_result(query)

            flag = 0
            for exp in expname:
                help = exp[0]
                if experimentname == help:
                    flag = 1

            if flag == 0:
                pass
            else:
                tkMessageBox.showerror('Error', 'Experiment added failed, this name is already exist')
                raise ValueError("Invalid Experiment name")

                # Description validation
            if description == "":
                tkMessageBox.showerror('Error', 'Invalid description!')
                raise ValueError("Invalid description")

        # Adding new experiment to DB
        def add_new_experiment(experimentname, description):
            try:
                _validate_experiment(experimentname, description)
            except ValueError:
                return
            query = "INSERT INTO finalproject.experiment(experimentname, description) values('{0}','{1}');" \
                .format(experimentname, description)
            sql_execute_query_with_exp(query)
            tkMessageBox.showinfo('Experiment Created', 'Experiment created sucessfully')

            mEntery2.delete(0, 'end')
            mEntery3.delete(0, 'end')

        button2 = Button(first_frame, text="Save", font=controller.title_font, width=30, height=3,
                         command=lambda: add_new_experiment(ment2.get(), ment3.get()))
        button2.place(relx=0.5, rely=0.6)

        def update(event):
            result = [row[0] for row in get_sql_query_result("SELECT experimentname FROM experiment")]
            self.combobox2['values'] = result

        self.combobox2.bind("<Button-1>", update)

        def get_participants_id(event):

            query = "SELECT participantid, firstname, lastname \
                    FROM finalproject.participant;"

            result = get_sql_query_result(query)

            participants = []

            for row in result:
                participants.append("{id}: ({first} {last})".format(id=row[0], first=row[1], last=row[2]))

            self.combobox1['values'] = participants

        self.combobox1.bind("<Button-1>", get_participants_id)

        def add_button():
            if self.combobox1.get() == "":
                tkMessageBox.showerror('Error', "Choose participant")
            elif self.combobox2.get() == "":
                tkMessageBox.showerror('Error', "Choose experiment")
            else:
                query1 = "SELECT experimentid FROM experiment WHERE experimentname = '{experiment}';" \
                    .format(experiment=self.combobox2.get())
                result1 = get_sql_query_result(query1)[0][0]

                query = "SELECT participantid,experimentid FROM experpartic WHERE participantid = {participantid}  " \
                    .format(participantid=self.combobox1.get().split(":")[0])
                result = get_sql_query_result(query)

                for row in result:
                    if row[1] == result1:
                        tkMessageBox.showerror('Error', "Participant already exist in experiment")
                        raise ValueError
                experiment = self.combobox2.get()
                query1 = "SELECT experimentid FROM experiment WHERE experimentname = '{experiment}';"

                expid = get_sql_query_result(query1.format(experiment=experiment))
                participantid = self.combobox1.get().split(":")

                query = "INSERT INTO experpartic (participantid,experimentid) VALUES({0},{1})"
                sql_execute_query_with_exp(query.format(participantid[0], expid[0][0]))
                tkMessageBox.showinfo('Success', "Participant added succssfuly")
                self.combobox1.set("")
                self.combobox2.set("")

        button3 = Button(second_frame, text="Add", font=controller.title_font, width=30, height=3, command=add_button)
        button3.place(relx=0.5, rely=0.5)

    def execute_draw(self):
        self.controller.title('Adding an experiment to the system / user')


#######################################################################################################################


class AddNewParticipant(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        label1 = Label(self, text="First Name", font=controller.title_font)
        label1.place(x=10, y=50)

        label2 = Label(self, text="Last Name", font=controller.title_font)
        label2.place(x=10, y=120)

        label3 = Label(self, text="Date of experiment", font=controller.title_font)
        label3.place(x=10, y=190)

        label4 = Label(self, text="Age", font=controller.title_font)
        label4.place(x=10, y=260)

        label5 = Label(self, text="Group ID", font=controller.title_font)
        label5.place(x=10, y=330)

        ment1 = StringVar()
        mEntery1 = Entry(self, textvariable=ment1)
        mEntery1.place(x=150, y=50)

        ment2 = StringVar()
        mEntery2 = Entry(self, textvariable=ment2)
        mEntery2.place(x=150, y=120)

        ment3 = StringVar()
        mEntery3 = Entry(self, textvariable=ment3)
        mEntery3.place(x=150, y=190)

        ment4 = StringVar()
        mEntery4 = Entry(self, textvariable=ment4)
        mEntery4.place(x=150, y=260)

        self.combobox1 = Combobox(self, values=["-".join([str(row[0]), row[1]]) for row in
                                                get_sql_query_result("SELECT groupid, groupname FROM groups")])
        self.combobox1.place(x=150, y=330)

        def _validate_participant(firstname, lastname, date, age, groupid):
            """Validation"""
            # First name validation
            if firstname == "":
                tkMessageBox.showerror('Error', 'Invalid first name!')
                raise ValueError("Illegal first name!")

            # Lastname validation
            if lastname == "":
                tkMessageBox.showerror('Error', 'Invalid last name!')
                raise ValueError("Illegal last name!")

            # Date validation
            try:
                date != ""
                dd, mm, yyyy = date.split(".")
                int(dd)
                int(mm)
                int(yyyy)
            except ValueError:
                tkMessageBox.showerror('Error', 'Invalid date!')
                raise

            # Age validation
            try:
                if age == "" or age != str(int(age)):
                    raise ValueError("Illegal age")
            except ValueError:
                tkMessageBox.showerror('Error', 'Invalid age!')
                raise

            # Groupid validation
            try:
                if groupid == "":
                    raise ValueError("Choose groupid")
            except ValueError:
                tkMessageBox.showerror('Error', 'Invalid groupid!')

        def add_new_participant(firstname, lastname, date, age, groupid):
            """ Adding the participant to DB"""
            try:
                _validate_participant(firstname, lastname, date, age, groupid)
            except ValueError:
                return
            try:
                query = "INSERT INTO finalproject.participant(firstname,lastname,date,age,groupid) values('{0}','{1}','{2}',{3},{4});" \
                    .format(firstname, lastname, date, age, self.combobox1.get().split("-")[0])
                sql_execute_query_with_exp(query)
                tkMessageBox.showinfo('Participant Created', 'Participant created sucessfully')
                mEntery1.delete(0, 'end')
                mEntery2.delete(0, 'end')
                mEntery3.delete(0, 'end')
                mEntery4.delete(0, 'end')
                self.combobox1.set("")

            except BaseException as e:
                tkMessageBox.showinfo('Error', 'Participantid already exsist')

        button1 = Button(self, text="Save", font=controller.title_font, width=15,
                         command=lambda: add_new_participant(ment1.get(), ment2.get(), ment3.get(), ment4.get(),
                                                             self.combobox1.get()))
        button1.place(x=450, rely=0.95)

        def clear_with_back():
            controller.show_frame("MainMenu")
            mEntery1.delete(0, 'end')
            mEntery2.delete(0, 'end')
            mEntery3.delete(0, 'end')
            mEntery4.delete(0, 'end')
            self.combobox1.set("")

        button2 = Button(self, text="Back", font=controller.title_font, width=15,
                         command=clear_with_back)
        button2.place(x=0, rely=0.95)

    def execute_draw(self):
        self.controller.title('AddNewParticipant')


#######################################################################################################################


class ViewMatrix(Frame):
    """Building 'View Matrix' window"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.configure(borderwidth="5", relief=RIDGE)
        parent.configure(borderwidth="5", relief=RIDGE)
        parent.pack()

        self.matrix = []
        self.c_width = 400
        self.c_height = 500
        row_size = 25

        experiment = "to fill"
        group = "to fill"
        participant = "to fill"
        matrix_name = "to fill"

        node_name = "---"
        degree = "---"
        betweennes_centrality = "---"
        local_efficiency = "---"

        self.canvas = Canvas(self)

        self.back = Button(self, text="Back", command=lambda: self.back_func_deletion(), width=15)
        self.back.place(x=5, rely=0.95)

        self.graph_frame = Frame(self, relief=RIDGE)
        self.graph_frame.place(anchor="ne", relx=0.98, rely=0.02, height=row_size * 4.1, relwidth=0.37)
        self.graph_frame.configure(bd=1)

        self.label1 = Label(self.graph_frame, text="Experiment:  {}".format(experiment))
        self.label1.place(x=0, y=0, height=row_size, relwidth=1)
        self.label1.configure(anchor="nw")

        self.label3 = Label(self.graph_frame, text="        Group:  {}".format(group))
        self.label3.place(x=0, y=row_size * 1, height=row_size, relwidth=1)
        self.label3.configure(anchor="nw")

        self.label5 = Label(self.graph_frame, text="Participant:  {}".format(participant))
        self.label5.place(x=0, y=row_size * 2, height=row_size, relwidth=1)
        self.label5.configure(anchor="nw")

        self.label7 = Label(self.graph_frame, text="        Matrix:  {}".format(matrix_name))
        self.label7.place(x=0, y=row_size * 3, height=row_size, relwidth=1)
        self.label7.configure(anchor="nw")

        self.electrode_info = LabelFrame(self, text="Electrode Info")
        self.electrode_info.place(anchor="ne", relx=0.98, y=row_size * 5, height=row_size * 7, relwidth=0.37)
        self.electrode_info.configure(relief=RIDGE, bd=1)

        self.node_name_lbl = Label(self.electrode_info, text="                  Node name:  {}".format(node_name))
        self.node_name_lbl.place(relx=0.0, rely=0.11, height=row_size, relwidth=1)
        self.node_name_lbl.configure(anchor="w")

        self.degree_lbl = Label(self.electrode_info, text="                          Degree:  {}".format(degree))
        self.degree_lbl.place(relx=0.0, rely=0.33, height=row_size, relwidth=1)
        self.degree_lbl.configure(anchor="w")

        self.betweennes_centrality_lbl = Label(self.electrode_info,
                                               text="Betweennes centrality:  {}".format(betweennes_centrality))
        self.betweennes_centrality_lbl.place(relx=0.0, rely=0.55, height=row_size, relwidth=1)
        self.betweennes_centrality_lbl.configure(anchor="w")

        self.local_efficiency_lbl = Label(self.electrode_info,
                                          text="           Local efficiency:  {}".format(local_efficiency))
        self.local_efficiency_lbl.place(relx=0.0, rely=0.77, height=row_size, relwidth=1)
        self.local_efficiency_lbl.configure(anchor="w")

        self.labels_to_change = [self.node_name_lbl, self.degree_lbl, self.betweennes_centrality_lbl,
                                 self.local_efficiency_lbl]
        self.canvas.place(anchor="nw", relx=0.02, rely=0.02, height=self.c_height, width=self.c_width)

    def back_func_deletion(self):
        """If 'Show Comparison' is pushed"""
        self.canvas.delete("all")
        self.controller.show_frame("ExistingParticipant")

    def execute_draw(self):
        self.controller.title('View Matrix')
        self.controller.frames["ExistingParticipant"].things_for_ViewMatrix()
        self.matrix = self.controller.frames["ExistingParticipant"].my_matrix
        vector = self.controller.frames["ExistingParticipant"].my_vector
        self.label1.configure(text="Experiment:  {}".format(vector[0]))
        self.label3.configure(text="        Group:  {}".format(vector[1]))
        self.label5.configure(text="Participant:  {}".format(vector[2]))
        self.label7.configure(text="        Matrix:  {}".format(vector[3]))

        canvasDraw.canvas_draw(self.canvas, self.matrix, self.c_width, self.c_height, self.labels_to_change)


#######################################################################################################################

class CompareTwoGraphsResult(Frame):
    """Building 'Compare Two Graphs Result' window"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.c_width = 400
        self.c_height = 500
        row_size = 20
        # =====================will hold the things for canvasDraw==============
        self.back_window = ""
        self.matrix_right = []
        self.matrix_left = []
        self.matrix_right_info = []
        self.matrix_left_info = []
        # ======================================================================

        self.similarity_label = Label(self)
        self.similarity_label.place(relx=0.5, rely=0, anchor="n")
        self.similarity_label.configure(anchor="w")

        # --------------------------------------right_brain---------------------------------------------
        self.right_brain = Frame(self)
        self.right_brain.place(relx=0, y=row_size, relheight=1, height=-2 * row_size, relwidth=0.5, anchor="nw")
        self.right_brain.configure(relief=RIDGE, bd=0)

        self.graph_frame_r = Frame(self.right_brain)  # ======================================================== graph_frame_r ===
        self.graph_frame_r.place(anchor="nw", relx=0.2, y=0, height=row_size * 4, relwidth=1)
        self.graph_frame_r.configure(relief=RIDGE, bd=0)

        self.experiment1_lbl = Label(self.graph_frame_r, text="Select node")
        self.experiment1_lbl.place(relx=0, y=0, height=row_size, relwidth=1)
        self.experiment1_lbl.configure(anchor="nw")

        self.group1_lbl = Label(self.graph_frame_r, text="---")
        self.group1_lbl.place(relx=0, y=row_size, height=row_size, relwidth=1)
        self.group1_lbl.configure(anchor="nw")

        self.participant1_lbl = Label(self.graph_frame_r, text="---")
        self.participant1_lbl.place(relx=0, y=row_size * 2, height=row_size, relwidth=1)
        self.participant1_lbl.configure(anchor="nw")

        self.matrix_name1_lbl = Label(self.graph_frame_r, text="---")
        self.matrix_name1_lbl.place(relx=0, y=row_size * 3, height=row_size, relwidth=1)
        self.matrix_name1_lbl.configure(anchor="nw")

        self.canvas_right = Canvas(self.right_brain)
        self.canvas_right.place(relx=0.5, y=80, height=self.c_height, width=self.c_width, anchor="n")

        self.electrode_info_r = LabelFrame(self.right_brain)  # ============================================= electrode_info_r ===
        self.electrode_info_r.place(relx=0, y=82 + self.c_height, height=row_size * 3, relwidth=1, anchor="nw")
        self.electrode_info_r.configure(text="Electrode Info")

        self.node_name1_lbl = Label(self.electrode_info_r, text="                  Node name:  {}".format("Choose node"))
        self.node_name1_lbl.place(relx=0, y=0, height=row_size, relwidth=0.5)
        self.node_name1_lbl.configure(anchor="nw")

        self.degree1_lbl = Label(self.electrode_info_r, text="                          Degree:  {}".format("---"))
        self.degree1_lbl.place(relx=0, y=row_size, height=row_size, relwidth=0.5)
        self.degree1_lbl.configure(anchor="nw")

        self.betweennes_centrality1_lbl = Label(self.electrode_info_r, text="Betweennes centrality:  {}".format("---"))
        self.betweennes_centrality1_lbl.place(relx=0.5, y=0, height=row_size, relwidth=0.5)
        self.betweennes_centrality1_lbl.configure(anchor="nw")

        self.local_efficiency1_lbl = Label(self.electrode_info_r, text="           Local efficiency:  {}".format("---"))
        self.local_efficiency1_lbl.place(relx=0.5, y=row_size, height=row_size, relwidth=0.5)
        self.local_efficiency1_lbl.configure(anchor="nw")

        self.strings_to_change_right = (self.node_name1_lbl, self.degree1_lbl, self.betweennes_centrality1_lbl, self.local_efficiency1_lbl)

        # --------------------------------------right_brain---------------------------------------------
        # --------------------------------------left_brain----------------------------------------------
        self.left_brain = Frame(self)
        self.left_brain.place(relx=0.5, y=row_size, relheight=1, height=-2 * row_size, relwidth=0.5, anchor="nw")
        self.left_brain.configure(relief=RIDGE, bd=0)

        self.graph_frame_l = Frame(self.left_brain)  # ======================================================== graph_frame_l ===
        self.graph_frame_l.place(anchor="nw", relx=0.2, y=0, height=row_size * 4, relwidth=1)
        self.graph_frame_l.configure(relief=RIDGE, bd=0)

        self.experiment2_lbl = Label(self.graph_frame_l, text="Select node")
        self.experiment2_lbl.place(relx=0, y=0, height=row_size, relwidth=1)
        self.experiment2_lbl.configure(anchor="nw")

        self.group2_lbl = Label(self.graph_frame_l, text="---")
        self.group2_lbl.place(relx=0, y=row_size, height=row_size, relwidth=1)
        self.group2_lbl.configure(anchor="nw")

        self.participant2_lbl = Label(self.graph_frame_l, text="---")
        self.participant2_lbl.place(relx=0, y=row_size * 2, height=row_size, relwidth=1)
        self.participant2_lbl.configure(anchor="nw")

        self.matrix_name2_lbl = Label(self.graph_frame_l, text="---")
        self.matrix_name2_lbl.place(relx=0, y=row_size * 3, height=row_size, relwidth=1)
        self.matrix_name2_lbl.configure(anchor="nw")

        self.canvas_left = Canvas(self.left_brain)
        self.canvas_left.pack()
        self.canvas_left.place(relx=0.5, y=80, height=self.c_height, width=self.c_width, anchor="n")

        self.electrode_info_l = LabelFrame(self.left_brain)  # ============================================= electrode_info_l ===
        self.electrode_info_l.place(relx=0, y=82 + self.c_height, height=row_size * 3, relwidth=1, anchor="nw")
        self.electrode_info_l.configure(text="Electrode Info")

        self.node_name2_lbl = Label(self.electrode_info_l, text="                  Node name:  {}".format("Choose node"))
        self.node_name2_lbl.place(relx=0, y=0, height=row_size, relwidth=0.5)
        self.node_name2_lbl.configure(anchor="nw")

        self.degree2_lbl = Label(self.electrode_info_l, text="                          Degree:  {}".format("---"))
        self.degree2_lbl.place(relx=0, y=row_size, height=row_size, relwidth=0.5)
        self.degree2_lbl.configure(anchor="nw")

        self.betweennes_centrality2_lbl = Label(self.electrode_info_l, text="Betweennes centrality:  {}".format("---"))
        self.betweennes_centrality2_lbl.place(relx=0.5, y=0, height=row_size, relwidth=0.5)
        self.betweennes_centrality2_lbl.configure(anchor="nw")

        self.local_efficiency2_lbl = Label(self.electrode_info_l, text="           Local efficiency:  {}".format("---"))
        self.local_efficiency2_lbl.place(relx=0.5, y=row_size, height=row_size, relwidth=0.5)
        self.local_efficiency2_lbl.configure(anchor="nw")

        self.strings_to_change_left = (self.node_name2_lbl, self.degree2_lbl, self.betweennes_centrality2_lbl, self.local_efficiency2_lbl)

        # --------------------------------------left_brain---------------------------------------------
        back = Button(self, text="Back", command=lambda: self.back_func_deletion())
        back.place(relx=0.5, rely=0.99, height=25, width=90, anchor="s")

    def back_func_deletion(self):
        self.canvas_right.delete("all")
        self.canvas_left.delete("all")
        self.node_name1_lbl.configure(text="                  Node name:  {}".format("---"))  # unset node name
        self.degree1_lbl.configure(text="                          Degree:  {}".format("---"))
        self.betweennes_centrality1_lbl.configure(text="Betweennes centrality:  {}".format("---"))
        self.local_efficiency1_lbl.configure(text="           Local efficiency:  {}".format("---"))
        self.node_name1_lbl.configure(text="                  Node name:  {}".format("---"))  # unset node name
        self.degree2_lbl.configure(text="                          Degree:  {}".format("---"))
        self.betweennes_centrality2_lbl.configure(text="Betweennes centrality:  {}".format("---"))
        self.local_efficiency2_lbl.configure(text="           Local efficiency:  {}".format("---"))
        self.controller.show_frame(self.back_window)

    def execute_draw(self):
        self.controller.title('CompareTwoGraphsResult')
        if self.back_window == "CompareTwoGraphs":
            self.controller.frames["CompareTwoGraphs"].things_for_CompareTwoGraphsResult()
        elif self.back_window == "AutoCompareResult":
            self.controller.frames["ExistingParticipant"].things_for_AutoCompareResult()
        else:
            pass

        graph_matrix_l = Nm.nmGraph(self.matrix_left)
        graph_matrix_r = Nm.nmGraph(self.matrix_right)
        similarity = Nm.NmSimilarity(graph_matrix_l, graph_matrix_r, 0.5)
        similarity_value = similarity.final_graph_similarity
        similarity_vector = similarity.connection_vector
        self.similarity_label.configure(text="Similarity: {}%".format(similarity_value))
        canvasDraw2.canvas_draw(self.canvas_left, self.canvas_right,
                                self.matrix_right, self.matrix_left,
                                self.c_width, self.c_height,
                                self.strings_to_change_left, self.strings_to_change_right,
                                similarity_vector)

        self.experiment1_lbl.configure(text="Experiment:  {}".format(self.matrix_left_info[0]))
        self.group1_lbl.configure(text="        Group:  {}".format(self.matrix_left_info[1]))
        self.participant1_lbl.configure(text="Participant:  {}".format(self.matrix_left_info[2]))
        self.matrix_name1_lbl.configure(text="        Matrix:  {}".format(self.matrix_left_info[3]))

        self.experiment2_lbl.configure(text="Experiment:  {}".format(self.matrix_right_info[0]))
        self.group2_lbl.configure(text="        Group:  {}".format(self.matrix_right_info[1]))
        self.participant2_lbl.configure(text="Participant:  {}".format(self.matrix_right_info[2]))
        self.matrix_name2_lbl.configure(text="        Matrix:  {}".format(self.matrix_right_info[3]))


#######################################################################################################################


class AutoCompareResult(Frame):
    """Building 'Auto Compare Result'"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.c_width = self.controller.height - 20
        self.c_height = 500
        row_size = 25
        self.new_auto_comp = True
        self.matrices = []
        self.vector = []

        self.matrix_right_info = []
        self.matrix_left_info = []
        self.ovals_list = []
        self.num_of_matrix = None

        self.canvas = Canvas(self)
        self.canvas.place(anchor="nw", relx=0.02, rely=0.02, height=self.c_height, width=self.c_width)

        self.frame = Frame(self)
        self.frame.place(anchor="nw", relx=0.02, rely=0.02, y=self.c_height, height=row_size * 3.5, width=self.c_width)
        self.frame.configure(bd=0, relief=RIDGE)

        self.show_comparison = Button(self.frame, state="disabled", text="Show comparison",
                                      command=lambda: self.show_comparison_func())
        self.show_comparison.place(anchor="ne", relx=0.98, rely=0.02, height=30, width=110)

        self.back = Button(self.frame, text="Back", command=lambda: self.back_func_deletion())
        self.back.place(anchor="se", relx=0.98, rely=0.98, height=30, width=110)

        self.label1 = Label(self.frame, text="-", font=controller.title_font)
        self.label1.place(x=10, y=5)

        self.label2 = Label(self.frame, text="-", font=controller.title_font)
        self.label2.place(x=10, y=row_size + 5)

        self.label3 = Label(self.frame, text="-", font=controller.title_font)
        self.label3.place(x=10, y=row_size * 2 + 5)

    def show_comparison_func(self):
        """If 'Show Comparison' is pushed"""
        text_id = compareAllMatrixes.OvalTags.active.text1
        left, right = self.canvas.itemcget(text_id, "text").split("-")

        self.controller.frames["CompareTwoGraphsResult"].matrix_right = self.matrices[int(right) - 1]
        self.controller.frames["CompareTwoGraphsResult"].matrix_left = self.matrices[int(left) - 1]
        self.controller.frames["CompareTwoGraphsResult"].matrix_right_info = self.vector + (right,)
        self.controller.frames["CompareTwoGraphsResult"].matrix_left_info = self.vector + (left,)
        self.controller.frames["CompareTwoGraphsResult"].back_window = "AutoCompareResult"
        self.new_auto_comp = False
        self.controller.show_frame("CompareTwoGraphsResult")

    def back_func_deletion(self):
        """If 'Show Comparison' is pushed"""
        self.canvas.delete("all")
        self.new_auto_comp = True
        self.controller.show_frame("ExistingParticipant")

    def execute_draw(self):
        self.controller.title('AutoCompareResult')
        if self.new_auto_comp is True:
            self.controller.frames["ExistingParticipant"].things_for_AutoCompareResult()  # calls for function
            self.label1.config(text="Experiment:        {}".format(self.vector[0]))
            self.label2.config(text="Group:                {}".format(self.vector[1]))
            self.label3.config(text="ID (Full Name):    {}".format(self.vector[2]))
            compareAllMatrixes.canvas_draw_auto_compare(self)


#######################################################################################################################


def sql_execute_query_with_exp(query):
    """For sql query with exceptions"""
    conn = MySQLdb.connect(user='root', passwd="DY696963", db="finalproject")
    cur = conn.cursor()

    try:
        cur.execute(query)
        conn.commit()
    except Exception as e:
        conn.rollback()
        return str(e)
    finally:
        conn.close()


def sql_execute_query(query):
    """For all sql query except 'INSERT'"""
    conn = MySQLdb.connect(user='root', passwd="DY696963", db="finalproject")
    cur = conn.cursor()

    try:
        cur.execute(query)
        conn.commit()
    except BaseException:
        conn.rollback()
    finally:
        conn.close()


def get_sql_query_result(query):
    """For " INSERT " sql query"""
    global conn
    try:
        conn = MySQLdb.connect(user='root', passwd="DY696963", db="finalproject")
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        return result
    finally:
        conn.close()


#######################################################################################################################################################
# Main
if __name__ == "__main__":
    app = MainFrame()
    app.mainloop()
