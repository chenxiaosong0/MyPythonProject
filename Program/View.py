# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
# from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as  NavigationToolbar
from PyQt5 import QtCore, QtGui, QtWidgets
from Program.DataModel import Model
from Algorithm.PathPlanning import Path_Planning

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib
import time
matplotlib.use("Qt5Agg")  # 声明使用QT5
#继承自FigureCanvas的类  嵌入PYQT5窗口中的地图的画布
class graph_FigureCanvas(FigureCanvas):
    def __init__(self,floor = None,title = None, parent=None, width=15, height=5, dpi=100):
        self.floor = floor
        self.title = title
        #第一步：创建一个创建Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)# 创建图形对象并配置其参数
        #第二步：在父类中激活Figure窗口
        super(graph_FigureCanvas, self).__init__(self.fig)# 初始化父类
        if 'members' in self.floor.graph:
            floors = self.floor.graph['members']
            # self.fig, self.axs = plt.subplots(1, len(floors), figsize=(15, 5))
            self.axs = self.fig.subplots(1, len(floors))
        else:
            #     #第三步：创建一个子图，用于绘制图形用，111表示子图编号，如matlab的subplot(1,1,1)
            self.ax = self.fig.add_subplot(111)# 添加子图到图形中
        #第四步：就是画图，【可以在此类中画，也可以在其它类中画】,最好是在别的地方作图

        self.setParent(parent) # 设置父窗口
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)# 设置大小策略为可扩展
        self.updateGeometry()# 更新几何形状
        self.fig.tight_layout()# 调整子图的布局

        self.lef_mouse_pressed = False  # 鼠标左键是否按下
        self.connect_event()  # 连接事件
        self.highlighted_node = None  # 高亮的节点

    def connect_event(self):
        self.mpl_connect('button_press_event', self.on_mouse_press)  # 鼠标左键按下
        self.mpl_connect('button_release_event', self.on_mouse_release)  # 鼠标左键释放
        self.mpl_connect('motion_notify_event', self.on_mouse_move)  # 鼠标移动
        self.mpl_connect("scroll_event", self.on_mouse_wheel)	#鼠标滚动事件

    # 鼠标左键按下
    def on_mouse_press(self, event):
        if event.button == 1:  # 鼠标左键
            click_x, click_y = event.xdata, event.ydata  # 获取鼠标点击的坐标
            if click_x is None or click_y is None:
                return
            # 设置一个阈值，用于确定点击坐标与节点坐标之间的“接近度”
            threshold = 0.2
            clicked_node = None
            # 获取节点位置
            location = nx.get_node_attributes(self.floor, 'location')
            colors = nx.get_node_attributes(self.floor, 'node_colors')
            # 遍历节点位置字典
            for node, (x, y) in location.items():
                delta_x = abs(x - click_x)
                delta_y = abs(y - click_y)
                if delta_x < threshold and delta_y < threshold:
                    clicked_node = node
                    break
            if clicked_node == self.highlighted_node:  # 如果点击的节点和之前高亮的节点相同，则取消高亮
                print("选中节点与上一次相同！")
                return
            # 如果之前有高亮的节点，复原
            if self.highlighted_node is not None:
                print(f"1.复位前一次高亮的节点: {self.highlighted_node}")
                x_old, y_old = location[self.highlighted_node]
                self.ax.scatter(x_old, y_old, color=colors[self.highlighted_node], marker='o',edgecolors='black',linewidths=0.7,zorder=2)  # 恢复之前节点的颜色和大小
                self.draw()  ## 更新绘图
            # 高亮当前点击的节点
            if clicked_node is not None:
                self.highlighted_node = clicked_node
                x, y = location[clicked_node]
                print(f"2.本次点击的节点: {clicked_node}, 坐标: ({x}, {y})")
                self.ax.scatter(x, y, c='red', marker='o', edgecolors='black', linewidths=0.7, zorder=2)
                self.draw()  ## 更新绘图
            else:# 如果没有点击到节点，重置高亮节点
                self.highlighted_node = None


    # 鼠标左键释放
    def on_mouse_release(self, event):
        pass
        # if event.button == 1:  # 鼠标左键
        #     self.lef_mouse_pressed = False
        #     print(f"on_mouse_release鼠标位置: ({event.x}, {event.y})")
    # 鼠标移动
    def on_mouse_move(self, event):
        pass


    # 鼠标滚动事件
    def on_mouse_wheel(self, event):
        pass
        # # 鼠标滚动事件
        # if event.button == 'up':
        #     print(f"on_mouse_wheel鼠标滚动: 放大")
        #     # self.ax.set_xlim(self.ax.get_xlim() * 1.1)
        #     # self.ax.set_ylim(self.ax.get_ylim() * 1.1)
        # elif event.button == 'down':
        #     print(f"on_mouse_wheel鼠标滚动: 缩小")
        #     # self.ax.set_xlim(self.ax.get_xlim() * 0.9)
        #     # self.ax.set_ylim(self.ax.get_ylim() * 0.9)
        # self.draw()  # 重绘图形

    #单层地图绘制
    def draw_floor(self):
        start_time = time.time()
        if 'members' in self.floor.graph:
            members = self.floor.graph['members']
            self.draw_floors(members, [f"Floor {i}" for i in range(1, len(members)+1)])
        else:
            # 获取节点位置和颜色
            pos = nx.get_node_attributes(self.floor, 'pos')
            colors = nx.get_node_attributes(self.floor, 'node_colors')
            location = nx.get_node_attributes(self.floor, 'location')
            # 提取 X, Y 画布坐标
            x = [loc[0] for loc in location.values()]
            y = [loc[1] for loc in location.values()]
            self.ax.set_title(self.title)
            # 绘制边
            for edge in self.floor.edges():
                x_edges = [location[edge[0]][0], location[edge[1]][0]]
                y_edges = [location[edge[0]][1], location[edge[1]][1]]
                self.ax.plot(x_edges, y_edges, c='gray',zorder=1)
                # 获取边的权重值（假设可以通过 edge_weight 方法获取）
                edge_weight = self.floor.edges[edge]['weight']  # 直接获取权重值
                self.ax.text((x_edges[0] + x_edges[1]) / 2, (y_edges[0] + y_edges[1]) / 2, edge_weight, ha='center',
                             va='center',
                             color='black',
                             zorder=2)
            # 绘制节点
            self.ax.scatter(x, y, c=[colors[node] for node in self.floor.nodes()], marker='o',edgecolors='black',linewidths=0.7,zorder=2)
            self.ax.set_xlabel('排 坐标')
            self.ax.set_ylabel('列 坐标')
            plt.tight_layout()#调整子图间距
            self.draw()#更新绘图内容
            end_time = time.time()
            print(f"绘制{self.title}地图耗时：{end_time-start_time}秒")

    def draw_floors(self, floors, titles):#绘制多个地图
        start_time = time.time()
        # 创建多个子图
        # self.fig, self.axs = self.fig.subplots(1, len(floors), figsize=(15, 5))
        # self.axs = self.fig.subplots(1, len(floors))
        # 绘制每个子图
        for ax, graph, title in zip(self.axs, floors, titles):
            # 获取节点位置和颜色
            pos = nx.get_node_attributes(graph, 'pos')
            colors = nx.get_node_attributes(graph, 'node_colors')
            location = nx.get_node_attributes(graph, 'location')
            # 提取 X, Y 画布坐标
            x = [loc[0] for loc in location.values()]
            y = [loc[1] for loc in location.values()]
            ax.set_title(title)
            # 绘制边
            for edge in graph.edges():
                x_edges = [location[edge[0]][0], location[edge[1]][0]]
                y_edges = [location[edge[0]][1], location[edge[1]][1]]
                ax.plot(x_edges, y_edges, c='gray',zorder=1)
            ax.scatter(x, y, c=[colors[node] for node in graph.nodes()], marker='o',edgecolors='black',linewidths=0.7,zorder=2)
            ax.set_xlabel('排 坐标')
            ax.set_ylabel('列 坐标')

        self.fig.tight_layout()#调整子图间距
        self.draw()#更新绘图内容
        end_time = time.time()
        print(f"绘制{len(floors)}层地图耗时：{end_time-start_time}秒")

class Ui_MainWindow(object):
    def __init__(self):
        #读取数据
        self.model = Model();
        #寻路算法
        self.path_planing = Path_Planning()
        #创建画布
        self.first_floor_canvas = graph_FigureCanvas(floor=self.model.floor1, title="First Floor")
        self.second_floor_canvas = graph_FigureCanvas(floor=self.model.floor2, title="Second Floor")
        self.third_floor_canvas = graph_FigureCanvas(floor=self.model.floor3, title="Third Floor")
        self.combined_floor_canvas = graph_FigureCanvas(floor=self.model.combined_graph, title="Combined_graph")

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        # MainWindow.resize(1200, 900)
        MainWindow.setMinimumHeight(900)
        MainWindow.setMinimumWidth(1500)
        MainWindow.showMaximized()
        font = QtGui.QFont()
        font.setPointSize(12)
        self.centralwidget = QtWidgets.QWidget(MainWindow)#设置中心窗口
        self.centralwidget.setObjectName("centralwidget")#设置中心窗口名称
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.centralwidget)#设置垂直布局
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)#设置选项卡控件
        self.tabWidget.setAutoFillBackground(True)#设置选项卡控件背景颜色
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)#设置选项卡控件形状
        self.tabWidget.setTabsClosable(False)#设置选项卡是否可关闭
        self.tabWidget.setMovable(True)#设置选项卡是否可拖动
        self.tabWidget.setTabBarAutoHide(False)#设置选项卡标签是否自动隐藏
        self.tabWidget.setObjectName("tabWidget")
        self.first_floor = QtWidgets.QWidget()#设置选项卡1
        font = QtGui.QFont()
        font.setPointSize(11)
        self.first_floor.setFont(font)
        self.first_floor.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.first_floor.setObjectName("first_floor")
        self.tabWidget.addTab(self.first_floor, "")
        self.second_floor = QtWidgets.QWidget()#设置选项卡2
        self.second_floor.setObjectName("second_floor")
        self.tabWidget.addTab(self.second_floor, "")
        self.third_floor = QtWidgets.QWidget()#设置选项卡3
        self.third_floor.setAccessibleName("")#设置选项卡3名称
        self.third_floor.setObjectName("third_floor")#设置选项卡3名称
        self.tabWidget.addTab(self.third_floor, "")
        self.allMaps = QtWidgets.QWidget()#设置选项卡4
        self.allMaps.setObjectName("allMaps")
        self.tabWidget.addTab(self.allMaps, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        self.Right_widget = QtWidgets.QWidget(self.centralwidget)#设置右侧控件
        self.Right_widget.setObjectName("Right_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.Right_widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.AGV_groupBox = QtWidgets.QGroupBox(self.Right_widget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.AGV_groupBox.setFont(font)
        self.AGV_groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.AGV_groupBox.setAutoFillBackground(False)
        self.AGV_groupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.AGV_groupBox.setObjectName("AGV_groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.AGV_groupBox)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.AddAGV_gridLayout = QtWidgets.QGridLayout()
        self.AddAGV_gridLayout.setObjectName("AddAGV_gridLayout")
        self.AGV_ID = QtWidgets.QLabel(self.AGV_groupBox)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.AGV_ID.setFont(font)
        self.AGV_ID.setAlignment(QtCore.Qt.AlignCenter)
        self.AGV_ID.setObjectName("AGV_ID")
        self.AddAGV_gridLayout.addWidget(self.AGV_ID, 1, 0, 1, 1)
        self.random_addAGV = QtWidgets.QPushButton(self.AGV_groupBox)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.random_addAGV.setFont(font)
        self.random_addAGV.setObjectName("random_addAGV")
        self.AddAGV_gridLayout.addWidget(self.random_addAGV, 0, 0, 1, 2)
        self.AGV_location = QtWidgets.QLabel(self.AGV_groupBox)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.AGV_location.setFont(font)
        self.AGV_location.setAlignment(QtCore.Qt.AlignCenter)
        self.AGV_location.setObjectName("AGV_location")
        self.AddAGV_gridLayout.addWidget(self.AGV_location, 2, 0, 1, 1)
        self.AGV_ID_comboBox = QtWidgets.QSpinBox(self.AGV_groupBox)
        self.AGV_ID_comboBox.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.AGV_ID_comboBox.setFont(font)
        self.AGV_ID_comboBox.setAlignment(QtCore.Qt.AlignCenter)
        self.AGV_ID_comboBox.setMaximum(10000)
        self.AGV_ID_comboBox.setObjectName("AGV_ID_comboBox")
        self.AddAGV_gridLayout.addWidget(self.AGV_ID_comboBox, 1, 1, 1, 1)
        self.AGV_location_comboBox = QtWidgets.QSpinBox(self.AGV_groupBox)
        self.AGV_location_comboBox.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.AGV_location_comboBox.setFont(font)
        self.AGV_location_comboBox.setAlignment(QtCore.Qt.AlignCenter)
        self.AGV_location_comboBox.setMaximum(10000)
        self.AGV_location_comboBox.setObjectName("AGV_location_comboBox")
        self.AddAGV_gridLayout.addWidget(self.AGV_location_comboBox, 2, 1, 1, 1)
        self.addAGV = QtWidgets.QPushButton(self.AGV_groupBox)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.addAGV.setFont(font)
        self.addAGV.setObjectName("addAGV")
        self.AddAGV_gridLayout.addWidget(self.addAGV, 3, 0, 1, 2)
        self.verticalLayout_2.addLayout(self.AddAGV_gridLayout)
        self.verticalLayout.addWidget(self.AGV_groupBox)
        self.Task_groupBox = QtWidgets.QGroupBox(self.Right_widget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Task_groupBox.setFont(font)
        self.Task_groupBox.setObjectName("Task_groupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Task_groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.Task_gridLayout = QtWidgets.QGridLayout()
        self.Task_gridLayout.setObjectName("Task_gridLayout")
        self.random_AddTask = QtWidgets.QPushButton(self.Task_groupBox)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.random_AddTask.setFont(font)
        self.random_AddTask.setObjectName("random_AddTask")
        self.Task_gridLayout.addWidget(self.random_AddTask, 0, 0, 1, 2)
        self.start_label = QtWidgets.QLabel(self.Task_groupBox)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.start_label.setFont(font)
        self.start_label.setAlignment(QtCore.Qt.AlignCenter)
        self.start_label.setObjectName("start_label")
        self.Task_gridLayout.addWidget(self.start_label, 1, 0, 1, 1)
        self.start_spinBox = QtWidgets.QSpinBox(self.Task_groupBox)
        self.start_spinBox.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.start_spinBox.setFont(font)
        self.start_spinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.start_spinBox.setMaximum(10000)
        self.start_spinBox.setObjectName("start_spinBox")
        self.Task_gridLayout.addWidget(self.start_spinBox, 1, 1, 1, 1)
        self.end_label = QtWidgets.QLabel(self.Task_groupBox)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.end_label.setFont(font)
        self.end_label.setAlignment(QtCore.Qt.AlignCenter)
        self.end_label.setObjectName("end_label")
        self.Task_gridLayout.addWidget(self.end_label, 2, 0, 1, 1)
        self.end_spinBox = QtWidgets.QSpinBox(self.Task_groupBox)
        self.end_spinBox.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.end_spinBox.setFont(font)
        self.end_spinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.end_spinBox.setMaximum(10000)
        self.end_spinBox.setObjectName("end_spinBox")
        self.Task_gridLayout.addWidget(self.end_spinBox, 2, 1, 1, 1)
        self.point_AGV = QtWidgets.QLabel(self.Task_groupBox)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.point_AGV.setFont(font)
        self.point_AGV.setAlignment(QtCore.Qt.AlignCenter)
        self.point_AGV.setObjectName("point_AGV")
        self.Task_gridLayout.addWidget(self.point_AGV, 3, 0, 1, 1)
        self.point_AGV_comboBox = QtWidgets.QComboBox(self.Task_groupBox)
        self.point_AGV_comboBox.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.point_AGV_comboBox.setFont(font)
        self.point_AGV_comboBox.setAutoFillBackground(True)
        self.point_AGV_comboBox.setEditable(True)
        self.point_AGV_comboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContentsOnFirstShow)
        self.point_AGV_comboBox.setObjectName("point_AGV_comboBox")
        self.point_AGV_comboBox.addItem("")
        self.point_AGV_comboBox.addItem("")
        self.Task_gridLayout.addWidget(self.point_AGV_comboBox, 3, 1, 1, 1)
        self.addTask = QtWidgets.QPushButton(self.Task_groupBox)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.addTask.setFont(font)
        self.addTask.setObjectName("addTask")
        self.Task_gridLayout.addWidget(self.addTask, 4, 0, 1, 2)
        self.verticalLayout_3.addLayout(self.Task_gridLayout)
        self.verticalLayout.addWidget(self.Task_groupBox)
        self.horizontalLayout.addWidget(self.Right_widget)
        self.horizontalLayout.setStretch(0, 9)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1099, 89))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.textBrowser = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_4.addWidget(self.textBrowser)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_5.addWidget(self.scrollArea)
        self.verticalLayout_5.setStretch(0, 9)
        self.verticalLayout_5.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1118, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setBaseSize(QtCore.QSize(0, 5))
        self.statusbar.setAutoFillBackground(True)
        self.statusbar.setInputMethodHints(QtCore.Qt.ImhTime)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.open = QtWidgets.QAction(MainWindow)
        self.open.setCheckable(False)
        self.open.setPriority(QtWidgets.QAction.HighPriority)
        self.open.setObjectName("open")
        self.Save = QtWidgets.QAction(MainWindow)
        self.Save.setObjectName("Save")
        self.menu.addAction(self.open)
        self.menu.addAction(self.Save)
        self.menubar.addAction(self.menu.menuAction())

        self.first_floor_layout = QtWidgets.QVBoxLayout(self.first_floor)
        first_floor_toolbar = NavigationToolbar(self.first_floor_canvas, self.first_floor)
        self.first_floor_layout.addWidget(first_floor_toolbar)
        self.first_floor_layout.addWidget(self.first_floor_canvas)
        self.first_floor_layout.setContentsMargins(0, 0, 0, 0)
        self.first_floor_layout.setObjectName("first_floor_layout")
        self.first_floor_canvas.draw_floor()#画出第一层地图

        self.second_floor_layout = QtWidgets.QVBoxLayout(self.second_floor)
        second_floor_toolbar = NavigationToolbar(self.second_floor_canvas, self.second_floor)
        self.second_floor_layout.addWidget(second_floor_toolbar)
        self.second_floor_layout.addWidget(self.second_floor_canvas)
        self.second_floor_layout.setContentsMargins(0, 0, 0, 0)
        self.second_floor_layout.setObjectName("second_floor_layout")
        self.second_floor_canvas.draw_floor()#画出第二层地图

        self.third_floor_layout = QtWidgets.QVBoxLayout(self.third_floor)
        third_floor_toolbar = NavigationToolbar(self.third_floor_canvas, self.third_floor)
        self.third_floor_layout.addWidget(third_floor_toolbar)
        self.third_floor_layout.addWidget(self.third_floor_canvas)
        self.third_floor_layout.setContentsMargins(0, 0, 0, 0)
        self.third_floor_layout.setObjectName("third_floor_layout")
        self.third_floor_canvas.draw_floor()#画出第三层地图

        self.combined_graph_layout = QtWidgets.QVBoxLayout(self.allMaps)
        combined_floor_toolbar = NavigationToolbar(self.combined_floor_canvas, self.combined_floor_canvas)
        self.combined_graph_layout.addWidget(combined_floor_toolbar)
        self.combined_graph_layout.addWidget(self.combined_floor_canvas)
        self.combined_graph_layout.setContentsMargins(0, 0, 0, 0)
        self.combined_graph_layout.setObjectName("combined_graph_layout")
        self.combined_floor_canvas.draw_floor()#画出全景地图

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "四向穿梭车货位优化与集成调度管理系统"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.first_floor), _translate("MainWindow", "第一层货位地图"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.second_floor), _translate("MainWindow", "第二层货位地图"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.third_floor), _translate("MainWindow", "第三层货位地图"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.allMaps), _translate("MainWindow", "全景地图"))
        self.AGV_groupBox.setTitle(_translate("MainWindow", "车辆管理"))
        self.AGV_ID.setText(_translate("MainWindow", "AGV_ID"))
        self.random_addAGV.setText(_translate("MainWindow", "随机添加AGV"))
        self.AGV_location.setText(_translate("MainWindow", "起始位置"))
        self.addAGV.setText(_translate("MainWindow", "添加AGV"))
        self.Task_groupBox.setTitle(_translate("MainWindow", "任务管理"))
        self.random_AddTask.setText(_translate("MainWindow", "随机添加任务"))
        self.start_label.setText(_translate("MainWindow", "起点"))
        self.end_label.setText(_translate("MainWindow", "终点"))
        self.point_AGV.setText(_translate("MainWindow", "指定AGV"))
        self.point_AGV_comboBox.setItemText(0, _translate("MainWindow", "AGV1"))
        self.point_AGV_comboBox.setItemText(1, _translate("MainWindow", "AGV2"))
        self.addTask.setText(_translate("MainWindow", "添加任务"))
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.open.setText(_translate("MainWindow", "open"))
        self.Save.setText(_translate("MainWindow", "Save"))

if __name__ == '__main__':
    import sys
    from qt_material import apply_stylesheet
    import qdarkstyle
    from PyQt5.QtWidgets import QApplication, QMainWindow

    try:
        app = QApplication(sys.argv)
        # setup stylesheet
        # apply_stylesheet(app, theme='dark_cyan.xml')
        dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
        app.setStyleSheet(dark_stylesheet)
        MainWindow = QMainWindow()

        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"应用启动失败: {e}")  # 错误处理，输出启动失败原因


