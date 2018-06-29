import os
import chardet
import wx

"""
    统计代码行数
"""


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(550, 400))
        self.__file_types = {'.java': False, '.c': False, '.cpp': False, '.py': False, '.php': False,
                             '.html': False, '.css': False, '.js': False, '.xml': False, '.jsp': False}
        self.__content_box = wx.BoxSizer(wx.VERTICAL)
        self.__file_type_input = None
        self.__work_content = None
        self.__dir_path = ""  # 代码目录的路径
        self.__init_ui()

    def __init_ui(self):
        self.SetBackgroundColour(wx.Colour(248, 248, 248))

        # 初始化文件类型部分
        self.__init_file_type()

        # 初始化下面工作区部分
        self.__init_work_area()

        self.Bind(wx.EVT_BUTTON, self.__on_clicked)

        self.SetSizer(self.__content_box)

    def __init_file_type(self):
        file_box = wx.BoxSizer(wx.VERTICAL)

        # 文件类型标题
        file_type_title = wx.StaticText(self, label='统计文件类型')
        title_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        file_type_title.SetFont(title_font)
        file_box.Add(file_type_title, flag=wx.ALL | wx.EXPAND)

        # 文件类型 CheckBox
        file_type_font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        file_types_sizer = wx.FlexGridSizer(2, 5, 10, 10)

        for key in self.__file_types.keys():  # 逐个添加默认支持的 CheckBox
            cb = wx.CheckBox(self, -1, key, (0, 0), (80, 30))
            cb.SetFont(file_type_font)
            file_types_sizer.Add(cb)

        file_box.Add(file_types_sizer, flag=wx.ALL | wx.EXPAND, border=15)

        # 添加自定义文件类型区域(水平布局)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.__file_type_input = wx.TextCtrl(self, style=wx.TE_LEFT, size=(300, 25))
        self.__file_type_input.SetHint('请输入文件格式(格式为: .后缀)')
        hbox.Add(self.__file_type_input)

        btn_add = wx.Button(self, label="添加")
        hbox.Add(btn_add, flag=wx.LEFT | wx.EXPAND, border=30)
        file_box.Add(hbox)

        self.__content_box.Add(file_box, flag=wx.ALL | wx.EXPAND, border=15)
        self.Bind(wx.EVT_CHECKBOX, self.__on_checked)

    def __init_work_area(self):
        work_sizer = wx.FlexGridSizer(1, 2, 10, 10)

        # 显示进度的文本区域
        self.__work_content = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY, size=(300, 180))
        work_sizer.Add(self.__work_content)

        # 两个按钮的垂直区域
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        open_button = wx.Button(self, label="选择目录")
        button_sizer.Add(open_button, flag=wx.LEFT | wx.BOTTOM | wx.EXPAND, border=20)
        start_button = wx.Button(self, label="开始")
        button_sizer.Add(start_button, flag=wx.LEFT | wx.EXPAND, border=20)
        work_sizer.Add(button_sizer)

        self.__content_box.Add(work_sizer, flag=wx.LEFT | wx.EXPAND, border=15)

    def __on_checked(self, e):
        """
        监听文件类型的选择状态, 从而记录是否被选中
        """
        cb = e.GetEventObject()
        self.__file_types[cb.GetLabel()] = cb.GetValue()

    def __on_clicked(self, e):
        label = e.GetEventObject().GetLabel()
        if '添加' == label:
            ext = str(self.__file_type_input.GetValue())
            if len(ext) == 0 or "." != ext[0]:  # 判断是否有点, 如果没有点则不符合规则, 提示用户
                wx.MessageBox("输入的文件类型后缀不符合规则", "提示", wx.OK | wx.ICON_INFORMATION)
                return

            self.__file_types[ext] = True  # 符合规则, 则添加到字典中
        elif '选择目录' == label:
            dir_dialog = wx.DirDialog(None, "Choose input directory", "",
                                      wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
            if dir_dialog.ShowModal() == wx.ID_OK:
                self.__dir_path = dir_dialog.GetPath()

        elif '开始' == label:
            # 判断是否选择了代码所在目录
            if 0 == len(self.__dir_path):
                wx.MessageBox("忘记选择目录了", "提示", wx.OK | wx.ICON_INFORMATION)
                return

            # 检查是否选择文件类型
            if not self.__is_select_file_type():
                wx.MessageBox("忘记选择文件类型了", "提示", wx.OK | wx.ICON_INFORMATION)
                return
            self.__work_content.SetValue("")  # 开始之前将原来的数据清空
            self.start_work()

    def __count_line(self, file_path):
        """
        统计 file_path 对方的文件的代码行数
        :param file_path:  代码文件路径
        :return: 代码文件的代码行数
        """
        # 获得文件类型的编码格式
        reader = open(file_path, "rb")  # 以 rb 的形式打开，否则会再现编码格式错误
        # file_encoding = chardet.detect(reader.read())

        # 以 file_encoding 编码格式打开
        # reader = open(file_path, encoding=file_encoding['encoding'])
        return len(reader.readlines())

    def start_work(self):
        work_progress = ""
        # 指定待统计代码行数显示的路径及要统计的文件类型
        file_num = 0
        total_line = 0
        count_file_num = 0  # 统计的文件数量
        # 遍历代码所在目录
        for root, dirs, files in os.walk(self.__dir_path):  # root 为目录, dirs 为该目录下的文件夹, files 为该目录下的所有文件
            # print("root: %s " % root)
            # print("dirs: %s " % dirs)
            # print("files: %s " % files)

            file_num = file_num + len(files)  # 统计文件个数
            # 逐个获得文件对象, 如果是要统计的文件类型, 则读取文件, 获取行数
            for f in files:
                ext = os.path.splitext(f)[1]
                if self.__file_types.get(ext):
                    self.__work_content.AppendText(f + "\n")
                    line = self.__count_line(root + "\\" + f)
                    total_line = total_line + line
                    count_file_num = count_file_num + 1
        self.__work_content.AppendText("文件总数: %d, 符合的文件数量: %d\n统计代码总行数: %d" % (file_num, count_file_num, total_line))

    def __is_select_file_type(self):
        """
        检查是否选择了文件类型，如果至少选择了或者添加了一种，则返回 True; 否则, 返回false
        :return:如果至少选择了或者添加了一种，则返回 True; 否则, 返回false
        """
        # 遍历文件字典的值列表，如果存在 True 的元素，立即返回 True
        for v in self.__file_types.values():
            if v:
                return True

        return False  # 如果没有从上面结束, 则全部为 False, 没有选择文件类型


if __name__ == '__main__':
    # start_work()
    app = wx.App()
    window = MyFrame(None, title='代码统计器 By ZekeTian')
    window.Show()

    app.MainLoop()  # 不断循环, 使得窗口不消失

"""
os.path 常用函数
os.path.dirname(path) 去掉文件名, 获得文件所在的目录路径 
os.path.basename(path) 去掉目录路径, 获得文件名
os.path.join(path_a, file_b) 将 a、b 两部分合并为一个路径, 一般前面为路径后面为文件名
os.path.split(path) 将路径分割为目录路径与文件名组成的元组
os.path.splitdrive(path) 将路径分割为盘符与路径组成的元组
os.path.splitext(path) 将路径分割为文件名与后缀名组成的元组  
"""
