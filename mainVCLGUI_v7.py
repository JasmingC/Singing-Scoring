#! /usr/bin/python
# -*- coding: utf-8 -*-

# tkinter example for VLC Python bindings
# Copyright (C) 2015 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
"""A simple example for VLC python bindings using tkinter.
Requires Python 3.4 or later.
Author: Patrick Fay
Date: 23-09-2015
"""

# Tested with Python 3.7.4, tkinter/Tk 8.6.9 on macOS 10.13.6 only.
__version__ = '20.05.04'  # mrJean1 at Gmail

# import external libraries
import vlc
# import standard libraries
import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
    from Tkinter import ttk
    from Tkinter.filedialog import askopenfilename
    from Tkinter.tkMessageBox import showerror
else:
    import tkinter as Tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename
    from tkinter.messagebox import showerror
from os.path import basename, expanduser, isfile, join as joined
import subprocess
from pathlib import Path
import time
import shutil
from judge import Judge


_isMacOS   = sys.platform.startswith('darwin')
_isWindows = sys.platform.startswith('win')
_isLinux   = sys.platform.startswith('linux')

# from RecordX import RecordX
import multiprocessing as mp
import asyncio
import os
import glob
import os.path
from os import path
from Rec_gui import *
from tkinter import StringVar
from tkinter import Scrollbar
from YouTubeDownload import YouTubeDownload
from Merge_Audio_Video import Merge_Audio_Video
from pytube import YouTube
import traceback
import logging

# 唱歌音高、節奏評分
import os
import numpy as np
import librosa
import librosa.display
from fastdtw import fastdtw as fdtw
from tslearn.metrics import dtw as tsdtw
from dtaidistance import dtw as dtaidtw
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt
import utils_score as utils
import hparam_score as hp
import time
import json
from beat_track_v5 import Beat
from Pitch_Shift import Pitch_Shift

if _isMacOS:
    from ctypes import c_void_p, cdll
    # libtk = cdll.LoadLibrary(ctypes.util.find_library('tk'))
    # returns the tk library /usr/lib/libtk.dylib from macOS,
    # but we need the tkX.Y library bundled with Python 3+,
    # to match the version number of tkinter, _tkinter, etc.
    try:
        libtk = 'libtk%s.dylib' % (Tk.TkVersion,)
        prefix = getattr(sys, 'base_prefix', sys.prefix)
        libtk = joined(prefix, 'lib', libtk)
        dylib = cdll.LoadLibrary(libtk)
        # getNSView = dylib.TkMacOSXDrawableView is the
        # proper function to call, but that is non-public
        # (in Tk source file macosx/TkMacOSXSubwindows.c)
        # and dylib.TkMacOSXGetRootControl happens to call
        # dylib.TkMacOSXDrawableView and return the NSView
        _GetNSView = dylib.TkMacOSXGetRootControl
        # C signature: void *_GetNSView(void *drawable) to get
        # the Cocoa/Obj-C NSWindow.contentView attribute, the
        # drawable NSView object of the (drawable) NSWindow
        _GetNSView.restype = c_void_p
        _GetNSView.argtypes = c_void_p,
        del dylib

    except (NameError, OSError):  # image or symbol not found
        def _GetNSView(unused):
            return None
        libtk = "N/A"

    C_Key = "Command-"  # shortcut key modifier

else:  # *nix, Xwindows and Windows, UNTESTED

    libtk = "N/A"
    C_Key = "Control-"  # shortcut key modifier

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        # self.widget.insert("end", str, (self.tag,))
        self.widget.insert("end", str)
        self.widget.configure(state="disabled")

class _Tk_Menu(Tk.Menu):
    '''Tk.Menu extended with .add_shortcut method.
       Note, this is a kludge just to get Command-key shortcuts to
       work on macOS.  Other modifiers like Ctrl-, Shift- and Option-
       are not handled in this code.
    '''
    _shortcuts_entries = {}
    _shortcuts_widget  = None

    def add_shortcut(self, label='', key='', command=None, **kwds):
        '''Like Tk.menu.add_command extended with shortcut key.
           If needed use modifiers like Shift- and Alt_ or Option-
           as before the shortcut key character.  Do not include
           the Command- or Control- modifier nor the <...> brackets
           since those are handled here, depending on platform and
           as needed for the binding.
        '''
        # <https://TkDocs.com/tutorial/menus.html>
        if not key:
            self.add_command(label=label, command=command, **kwds)

        elif _isMacOS:
            # keys show as upper-case, always
            self.add_command(label=label, accelerator='Command-' + key,
                                          command=command, **kwds)
            self.bind_shortcut(key, command, label)

        else:  # XXX not tested, not tested, not tested
            self.add_command(label=label, underline=label.lower().index(key),
                                          command=command, **kwds)
            self.bind_shortcut(key, command, label)

    def bind_shortcut(self, key, command, label=None):
        """Bind shortcut key, default modifier Command/Control.
        """
        # The accelerator modifiers on macOS are Command-,
        # Ctrl-, Option- and Shift-, but for .bind[_all] use
        # <Command-..>, <Ctrl-..>, <Option_..> and <Shift-..>,
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M6>
        if self._shortcuts_widget:
            if C_Key.lower() not in key.lower():
                key = "<%s%s>" % (C_Key, key.lstrip('<').rstrip('>'))
            self._shortcuts_widget.bind(key, command)
            # remember the shortcut key for this menu item
            if label is not None:
                item = self.index(label)
                self._shortcuts_entries[item] = key
        # The Tk modifier for macOS' Command key is called
        # Meta, but there is only Meta_L[eft], no Meta_R[ight]
        # and both keyboard command keys generate Meta_L events.
        # Similarly for macOS' Option key, the modifier name is
        # Alt and there's only Alt_L[eft], no Alt_R[ight] and
        # both keyboard option keys generate Alt_L events.  See:
        # <https://StackOverflow.com/questions/6378556/multiple-
        # key-event-bindings-in-tkinter-control-e-command-apple-e-etc>

    def bind_shortcuts_to(self, widget):
        '''Set the widget for the shortcut keys, usually root.
        '''
        self._shortcuts_widget = widget

    def entryconfig(self, item, **kwds):
        """Update shortcut key binding if menu entry changed.
        """
        Tk.Menu.entryconfig(self, item, **kwds)
        # adjust the shortcut key binding also
        if self._shortcuts_widget:
            key = self._shortcuts_entries.get(item, None)
            if key is not None and "command" in kwds:
                self._shortcuts_widget.bind(key, kwds["command"])


class Player(Tk.Frame):
    """The main window has to deal with events.
    """
    _geometry = ''
    _stopped  = None

    def __init__(self, parent, title=None, video=''):
        Tk.Frame.__init__(self, parent)

        self.parent = parent  # == root
        self.parent.title(title or "KTVplayer")
        # 固定視窗大小
        # self.parent.geometry('1024x768')
        # 最大化視窗
        self.parent.state('zoomed')
        self.video = expanduser(video)
     
        # Menu Bar
        #   File Menu
        menubar = Tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = _Tk_Menu(menubar)
        fileMenu.bind_shortcuts_to(parent)  # XXX must be root?

        fileMenu.add_shortcut("Open...", 'o', self.OnOpen)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Play", 'p', self.OnPlay)  # Play/Pause
        fileMenu.add_command(label="Stop", command=self.OnStop)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Mute", 'm', self.OnMute)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Record", 'r', self.on_rec)
        fileMenu.add_shortcut("StopRecord", 's', self.on_stop)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Vocal Separation", 'v', self.Vocal_Separation_asyncio)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Judge Score", 'j', self.Judge_Score_asyncio)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Close", 'w' if _isMacOS else 's', self.OnClose)
        if _isMacOS:  # intended for and tested on macOS
            fileMenu.add_separator()
            fileMenu.add_shortcut("Full Screen", 'f', self.OnFullScreen)
        menubar.add_cascade(label="File", menu=fileMenu)
        self.fileMenu = fileMenu
        self.playIndex = fileMenu.index("Play")
        self.muteIndex = fileMenu.index("Mute")

        # first, top panel shows video

        self.videopanel = ttk.Frame(self.parent)
        self.canvas = Tk.Canvas(self.videopanel)
        self.canvas.pack(fill=Tk.BOTH, expand=1)
        self.videopanel.pack(fill=Tk.BOTH, expand=1)
        
        # 建立存放錄音資料夾
        from pathlib import Path
        self.RecordPath = "./Record_audio"
        Path(self.RecordPath).mkdir(parents=True, exist_ok=True)

        #YouTuber網址 Label
        youTuberlabel = tk.Label(self.parent, text='請輸入YouTuber網址:')
        youTuberlabel.pack(side=Tk.LEFT)
        #YouTuber Text
        URL2 =    'https://youtu.be/66e50-LWLmE' # 測試網址  李榮浩慢冷
        
        self.youTuberText = tk.Entry(self.parent ,width=50)
        self.youTuberText.insert(0, URL2)
        self.youTuberText.pack(side=Tk.LEFT)
        
        #下載按鈕
        self.download = ttk.Button(self.parent, text="下載", command=self.change_form_state)
        self.download.pack(side=Tk.LEFT)

        # 升降KEY Label
        KEYlabel = tk.Label(self.parent, text='升降KEY:')
        KEYlabel.pack(side=Tk.LEFT)

        # 選擇升降KEY Combobox
        self.KEY_Combobox = ttk.Combobox(root, values=['+6','+5','+4','+3','+2','+1','0','-1','-2','-3','-4','-5','-6'],width=15)
        self.KEY_Combobox.current(6)
        self.KEY_Combobox.pack(side=Tk.LEFT)
        
        # Add a Scrollbar(horizontal)
        v=Scrollbar(self.parent, orient='vertical')
        v.pack(side=Tk.LEFT, fill='y')

        # Log Text
        self.logText = tk.Text(self.parent, height=5,width=100)
        # Attach the scrollbar with the text widget
        v.config(command=self.logText.yview)
        self.logText.pack(side=Tk.LEFT)
        # sys.stdout = TextRedirector(self.logText, "stdout")
        # sys.stderr = TextRedirector(self.logText, "stderr")

        # panel to hold buttons
        self.buttons_panel = Tk.Toplevel(self.parent)
        self.buttons_panel.title("buttons_panel")
        self.is_buttons_panel_anchor_active = True
        
        self.initRecord()
        buttons = ttk.Frame(self.buttons_panel)
        # buttons = ttk.Frame(self.parent)
        self.playButton = ttk.Button(buttons, text="Play", command=self.OnPlay)
        stop            = ttk.Button(buttons, text="Stop", command=self.OnStop)
        self.muteButton = ttk.Button(buttons, text="Mute", command=self.OnMute)
        self.rec_button = ttk.Button(buttons, text="Record", command=self.on_rec)
        # self.stopRecordButton = ttk.Button(buttons, text="StopRecord", command=self.on_stop)
        self.playButton.pack(side=Tk.LEFT)
        stop.pack(side=Tk.LEFT)
        self.muteButton.pack(side=Tk.LEFT)
        self.rec_button.pack(side=Tk.LEFT)
        # self.stopRecordButton.pack(side=Tk.LEFT)

        self.volMuted = False
        self.volVar = Tk.IntVar()
        self.volSlider = Tk.Scale(buttons, variable=self.volVar, command=self.OnVolume,
                                  from_=0, to=100, orient=Tk.HORIZONTAL, length=200,
                                  showvalue=0, label='Volume')
        self.volSlider.pack(side=Tk.RIGHT)
        self.volSlider.set(100)
        buttons.pack(side=Tk.BOTTOM, fill=Tk.X)

        # panel to hold player time slider
        timers = ttk.Frame(self.buttons_panel)
        self.timeVar = Tk.DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = Tk.Scale(timers, variable=self.timeVar, command=self.OnTime,
                                   from_=0, to=1000, orient=Tk.HORIZONTAL, length=500,
                                   showvalue=0)  # label='Time',
        self.timeSlider.pack(side=Tk.BOTTOM, fill=Tk.X, expand=1)
        self.timeSliderUpdate = time.time()
        timers.pack(side=Tk.BOTTOM, fill=Tk.X)

        # 紀錄是否已經播放結束
        self.playEnd = False
        # 是否已停止錄音
        self.stopRecord = False

        # VLC player
        args = []
        if _isLinux:
            args.append('--no-xlib')
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()
       
        self.parent.bind("<Configure>", self.OnConfigure)  # catch window resize, etc.
        self.parent.update()

        # After parent.update() otherwise panel is ignored.
        self.buttons_panel.overrideredirect(True)

        # Estetic, to keep our video panel at least as wide as our buttons panel.
        self.parent.minsize(width=502, height=0)

        if _isMacOS:
            # Only tested on MacOS so far. Enable for other OS after verified tests.
            self.is_buttons_panel_anchor_active = True

            # Detect dragging of the buttons panel.
            self.buttons_panel.bind("<Button-1>", lambda event: setattr(self, "has_clicked_on_buttons_panel", event.y < 0))
            self.buttons_panel.bind("<B1-Motion>", self._DetectButtonsPanelDragging)
            self.buttons_panel.bind("<ButtonRelease-1>", lambda _: setattr(self, "has_clicked_on_buttons_panel", False))
            self.has_clicked_on_buttons_panel = False
        else:
            self.is_buttons_panel_anchor_active = False

        self._AnchorButtonsPanel()

        self.OnTick()  # set the timer up
    def get_loop(self,loop):
        self.loop=loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    def change_form_state(self):
        coroutine1 = self.OnDownloadYouTube()
        new_loop = asyncio.new_event_loop()     #在當前執行緒下創建時間迴圈，（未啟用），在start_loop裡面啟動它
        t = threading.Thread(target=self.get_loop,args=(new_loop,))   #通過當前執行緒開啟新的執行緒去啟動事件迴圈
        t.start()
        asyncio.run_coroutine_threadsafe(coroutine1,new_loop)  #這幾個是關鍵，代表在新執行緒中事件迴圈不斷“遊走”執行


    def getKEY_Combobox(self):
        '''
        從Combobox取得目前所選擇KEY
        '''
        # 取得升降KEY索引值
        indexKEY = self.KEY_Combobox.current()
        KEYValue = self.KEY_Combobox.get()
        selectedKEY = 0
        if indexKEY == 0:
            selectedKEY = 6
        elif indexKEY == 1:
            selectedKEY = 5
        elif indexKEY == 2:
            selectedKEY = 4
        elif indexKEY == 3:
            selectedKEY = 3
        elif indexKEY == 4:
            selectedKEY = 2
        elif indexKEY == 5:
            selectedKEY = 1
        elif indexKEY == 6:
            selectedKEY = 0
        elif indexKEY == 7:
            selectedKEY = -1
        elif indexKEY == 8:
            selectedKEY = -2
        elif indexKEY == 9:
            selectedKEY = -3
        elif indexKEY == 10:
            selectedKEY = -4
        elif indexKEY == 11:
            selectedKEY = -5
        elif indexKEY == 12:
            selectedKEY = -6
     
        return selectedKEY

    async def OnDownloadYouTube(self):
        """
        下載Youtube影片
        """
        try:
            # 從Combobox取得目前所選擇KEY
            selectedKEY = self.getKEY_Combobox() 
            # 存放mp3、mp4路徑
            saveFolder = './videos/'
            # [Text]取得Youtube網址
            url = self.youTuberText.get()
            # 使用youtube_dl下載影片
            #youTube = YouTubeDownload(saveFolder)
            urls = [url]

            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
            yt = YouTube(url)
            #print(yt.title)

            
            # urls = ['https://www.youtube.com/watch?v=K5rjNK_De-I']
            # Empty Text
            self.logText.delete('1.0', tk.END)
            self.logText.insert(tk.END,"選擇升降KEY:" + str(selectedKEY) + "\n")
            self.logText.insert(tk.END,"1.YouTube網址:"+str(url)+"\n")
    
            # 清空儲存檔案資料夾
            #saveFolder = './YouTubeDownload/'
            #youTube.empty_folder(saveFolder)
            
            # 3.下載YouTube mp3檔案
            start = time.time()
            start_preprocess = time.time()
            proc = subprocess.Popen([ "python","progress.py","Download mp3","30"])
            self.logText.insert(tk.END,"2.下載YouTube mp3中...\n")
            yt.streams.filter().get_audio_only().download(filename= yt.title + '.mp3')
            end = time.time()
            totalTime = str(round(end - start,2))
            self.logText.insert(tk.END,'3.' + str(yt.title) + "下載完成!"+"\n")
            proc.terminate()
            self.logText.insert(tk.END,'花費時間:' + totalTime + "秒" + "\n")
            newFileName = "temp.mp3"
            # 移除temp.mp3
            if (path.exists(newFileName)):
                os.remove(newFileName)

            # 4.檔案重新命名完成!
            # 下載後檔案重新命名為temp.mp3
            start = time.time()
            await self.RenameFile(yt.title + '.mp3',newFileName)
            end = time.time()
            totalTime = str(round(end - start,5))
            self.logText.insert(tk.END,"4.檔案重新命名完成!" + newFileName +"\n")
            # self.logText.insert(tk.END,'花費時間:' + totalTime + "秒\n")

            # 清空output
            shutil.rmtree('./output/temp')

            # 5. Spleeter人聲分離
            start = time.time()
            self.logText.insert(tk.END,"5.人聲分離中..."+"\n")
            command = "spleeter separate -p spleeter:2stems -o output " + newFileName
            proc = subprocess.Popen([ "python","progress.py","Vocal Separation","120"])
            os.system(command)
            self.logText.insert(tk.END,"6.人聲分離完成! 儲存位置./output/temp/"+"\n")
            proc.terminate()
            end = time.time()
            totalTime = str(round(end - start,2))
            self.logText.insert(tk.END,'花費時間:' + totalTime + "秒" + "\n")

            # 7.下載YouTube mp4檔案
            start = time.time()
            self.logText.insert(tk.END,"7.下載YouTube mp4檔案中..." + "\n")
            proc = subprocess.Popen([ "python","progress.py","Download mp4","5"])
            yt.streams.filter().get_by_resolution('360p').download()
            # FileName2 = await youTube.download_youtube_dl_mp4(urls)
            self.logText.insert(tk.END,"8.下載YouTube mp4檔案完成!" + yt.title + "\n")
            proc.terminate()
            end = time.time()
            totalTime = str(round(end - start,2))
            self.logText.insert(tk.END,'花費時間:' + totalTime + "秒" + "\n")

            # 新檔名
            video = 'tempVideo.mp4'
            # 9.2 移除tempVideo.webm
            if (path.exists(video)):
                os.remove(video)
            
            await self.RenameFile(yt.title + '.mp4',video)

                

               
            # 10.將音訊升降Key
            # 讀取伴奏音檔
            audio = './output/temp/accompaniment.wav'
            # 讀取原唱音檔
            audio2 = './output/temp/vocals.wav'
            # 輸出位置
            outputFolder = './output/temp/'
            # 輸出檔案名稱
            fileName1 = 'pitch_shift'
            fileName2 = 'vocals'
            PS = Pitch_Shift()
            # 指定升降Key
            # pitch_shift_0.wav
            # keys = [-2,-1,0,1,2]
            keys = [selectedKEY]
            self.selectedKEY = selectedKEY
            
            start = time.time()
            proc = subprocess.Popen([ "python","progress.py","Pitch shift","60"])
            self.logText.insert(tk.END,"10.升降Key處理中..." + "\n")
            # 升降Key調整
            y,y_shift_results = await PS.aug_pitch_shift(audio,outputFolder,fileName1,Keys=keys,samplerate=44100)
            y,y_shift_results = await PS.aug_pitch_shift(audio2,outputFolder,fileName2,Keys=keys,samplerate=44100)
            end = time.time()
            proc.terminate()
            totalTime = str(round(end - start,2))
            self.logText.insert(tk.END,'花費時間:' + totalTime + "秒" + "\n")
            

            # 11.將音訊檔加入影片中
            start = time.time()
            self.logText.insert(tk.END,"11.將伴奏音訊檔加入影片中..." + "\n")
            proc = subprocess.Popen([ "python","progress.py","Merge","80"])
            for key in keys:
                audio = './output/temp/pitch_shift_' + str(key) + '.wav'
                output = './output/temp/mergeResult_' + str(key) + '.mp4'
                # audio = './output/temp/accompaniment.wav'
                # output = './output/temp/mergeResult.mp4'
                merge = Merge_Audio_Video()
                await merge.combine_audio_in_video_async(video,audio,output)
            
            proc.terminate()
            self.logText.insert(tk.END,"12.全部完成!音訊檔加入影片完成！儲存位置:"+ output + "\n")
            end = time.time()
            end_preprocess = time.time()
            totalTime = str(round(end - start,2))
            preprocess_time = str(round(end_preprocess - start_preprocess,2))
            self.logText.insert(tk.END,'前處理花費時間:' + preprocess_time + "秒" + "\n")
            
        except Exception as e:
            logging.error(traceback.format_exc())
    async def RenameFile(self,old_name,new_name):
        '''
        檔案重新命名
        ''' 
        import os
        # Renaming the file
        os.rename(old_name, new_name)
        print('檔案重新命名完成!')
    def OnClose(self, *unused):
        """Closes the window and quit.
        """
        # print("_quit: bye")
        self.parent.quit()  # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to avoid
        # ... Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def _DetectButtonsPanelDragging(self, _):
        """If our last click was on the boarder
           we disable the anchor.
        """
        if self.has_clicked_on_buttons_panel:
            self.is_buttons_panel_anchor_active = False
            self.buttons_panel.unbind("<Button-1>")
            self.buttons_panel.unbind("<B1-Motion>")
            self.buttons_panel.unbind("<ButtonRelease-1>")

    def _AnchorButtonsPanel(self):
        video_height = self.parent.winfo_height()
        panel_x = self.parent.winfo_x()
        panel_y = self.parent.winfo_y() + video_height + 23 # 23 seems to put the panel just below our video.
        panel_height = self.buttons_panel.winfo_height()
        panel_width = self.parent.winfo_width()
        self.buttons_panel.geometry("%sx%s+%s+%s" % (panel_width, panel_height, panel_x, panel_y))

    def OnConfigure(self, *unused):
        """Some widget configuration changed.
        """
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M12>
        self._geometry = ''  # force .OnResize in .OnTick, recursive?

        if self.is_buttons_panel_anchor_active:
            self._AnchorButtonsPanel()

    def OnFullScreen(self, *unused):
        """Toggle full screen, macOS only.
        """
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/wm.htm#M10>
        f = not self.parent.attributes("-fullscreen")  # or .wm_attributes
        if f:
            self._previouscreen = self.parent.geometry()
            self.parent.attributes("-fullscreen", f)  # or .wm_attributes
            self.parent.bind("<Escape>", self.OnFullScreen)
        else:
            self.parent.attributes("-fullscreen", f)  # or .wm_attributes
            self.parent.geometry(self._previouscreen)
            self.parent.unbind("<Escape>")

    def Judge_Score_asyncio(self):
        '''
        唱歌評分非同步執行
        '''
        try:
            coroutine1 = self.Judge_Score()
            new_loop = asyncio.new_event_loop()     #在當前執行緒下創建時間迴圈，（未啟用），在start_loop裡面啟動它
            t = threading.Thread(target=self.get_loop,args=(new_loop,))   #通過當前執行緒開啟新的執行緒去啟動事件迴圈
            t.start()
            asyncio.run_coroutine_threadsafe(coroutine1,new_loop)  #這幾個是關鍵，代表在新執行緒中事件迴圈不斷“遊走”執行
        except Exception as e:
            print ('Error Judge_Score_asyncio():',e)

    async def Judge_Score(self):
        '''
        唱歌評分
        '''
        # 從Combobox取得目前所選擇KEY
        selectedKEY = self.getKEY_Combobox()
    
        # 手動選擇使用者唱歌音訊檔
        user_audio_path = askopenfilename(initialdir = Path(expanduser("./output/rec_temp/")),
                                title = "Choose a video",
                                filetypes = (("all files", "*.*"),
                                             ("mp4 files", "*.mp4"),
                                             ("mov files", "*.wav")))

        # 標準唱歌音訊檔，結合升降KEY
        standard_audio_path = "./output/temp/vocals_" + str(selectedKEY) + ".wav"
        standard_accompaniment_path = "./output/temp/pitch_shift_" + str(selectedKEY) + ".wav"
        
        import os.path
        file_exists = os.path.exists(standard_audio_path)
        if (file_exists == False):
            self.logText.insert(tk.END,"Error 檔案不存在:"+ standard_audio_path +"\n")
            return
        
        # print ('user_audio_path:',user_audio_path)
        # print ('standard_audio_path:',standard_audio_path)
        
        self.logText.insert(tk.END,"0.讀取使用者音訊檔:"+ user_audio_path +"\n")
        self.logText.insert(tk.END,"0.讀取標準音訊檔:"+ standard_audio_path +"\n")
        self.logText.insert(tk.END,"1.開始評分..." +"\n")
    
        # 音準評分
        
        self.judge(standard_audio_path,user_audio_path)

        # 節奏評分
        self.bpm_score(standard_audio_path,user_audio_path)
        
        # 完成評分
        self.logText.insert(tk.END,"2.完成評分..." +"\n")



    def bpm_score(self,standard_audio_path,user_audio_path):
        '''
        計算節奏分數
        '''
        proc = subprocess.Popen([ "python","progress.py","Get your vocal evaluated about Tempo","150"])
        Audio_Path = {'Standard':standard_audio_path,'User':user_audio_path} 
        i = 1
        # BMP
        Standard_BPM = 0
        User_BPM = 0
        # 設定畫布大小
        fig = plt.figure(figsize=(12, 6))

        for key,value in Audio_Path.items():
            # 讀取音訊
            y, sr = librosa.load(value,sr=16000)
            # y, sr = librosa.load(librosa.ex('choice'), duration=10)
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        #     print(key,' tempo:',tempo)
        #     print(key,' beats:',beats)
            librosa.frames_to_time(beats, sr=sr)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr,
                                                    aggregate=np.median)
            tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env,
                                                sr=sr)
            tempo = round(tempo,2)
            if (key == 'Standard'):
                Standard_BPM = tempo
            else:
                User_BPM = tempo

            # print(key,' tempo:',tempo)
            # print(key,' beats:',beats)

            hop_length = 512
            times = librosa.times_like(onset_env, sr=sr, hop_length=hop_length)
            M = librosa.feature.melspectrogram(y=y, sr=sr, hop_length=hop_length)
            # librosa.display.specshow(librosa.power_to_db(M, ref=np.max),
            #                         y_axis='mel', x_axis='time', hop_length=hop_length,
            #                         ax=ax[0])
            # ax[0].label_outer()
            # ax[0].set(title='Mel spectrogram')

        #     ax[i].plot(times, librosa.util.normalize(onset_env),
        #             label='Onset strength')

            # 子圖1
            subplot1 = fig.add_subplot(2,1,i)
            y = librosa.util.normalize(onset_env)
            # 畫出onset_envelope
            subplot1.plot(times, y,label='Onset strength')
            # 畫出Beats
            subplot1.vlines(times[beats], 0, 1, alpha=0.5, color='r',
                        linestyle='--', label='Beats')
            subplot1.legend() # 顯示線圖標籤名稱           
            plt.title(f'{key} BPM:{tempo}') # 標題
            plt.xlabel("Time") # x lable
            plt.ylabel("Amplitude") # y label
            i += 1

        print(Standard_BPM)
        print(User_BPM) 

        diff = abs(Standard_BPM - User_BPM)
        score_tempo = 100 - diff / 2

        if abs(2*Standard_BPM - User_BPM) < diff:
            diff = abs(2*Standard_BPM - User_BPM)
            score_tempo = 100 - diff
        if abs(Standard_BPM - 2*User_BPM) < diff:
            diff = abs(Standard_BPM - 2*User_BPM)
            score_tempo = 100 - diff

        
        # 上下限調整    
        if score_tempo > 95: 
            score_tempo = 95   
        if score_tempo < 60: 
            score_tempo = 60
        

        self.logText.insert(tk.END,'使用者節奏分數:' + str(score_tempo) + '分' +"\n")
        print('使用者節奏分數:',round(score_tempo,2),'分')
        proc.terminate()
        plt.tight_layout() # 自動調整圖形之間間距
        plt.show()

    async def Vocal_Separation(self):
        '''
        ##Spleeter人聲分離
        '''
        # if a file is already running, then stop it.
        self.OnStop()
        # Create a file dialog opened in the current home directory, where
        # you can display all kind of files, having as title "Choose a video".
        video = askopenfilename(initialdir = Path(expanduser("./Record_audio/")),
                                title = "Choose a video",
                                filetypes = (("all files", "*.*"),
                                             ("mp4 files", "*.mp4"),
                                             ("mov files", "*.mov")))
                                             
        proc = subprocess.Popen([ "python","progress.py","Vocal Separation","150"])
        self.logText.insert(tk.END,"1.檔案路徑:" + video +"\n")
        # 取得檔案名稱
        filename = os.path.basename(video)
        self.logText.insert(tk.END,"2.取得檔案名稱:" + filename +"\n")
        # 移動檔案到程式目錄，並重新命名
        shutil.copyfile(video, filename)
        # os.rename(video, filename)
        newFileName = filename
        
        start = time.time()
        
        self.logText.insert(tk.END,"3.人聲分離中..."+"\n")
        command = "spleeter separate -p spleeter:2stems -o output " + newFileName
        os.system(command)
        self.logText.insert(tk.END,"4.人聲分離完成! 儲存位置./output/"+ filename + "/" + "\n")
        proc.terminate()
        end = time.time()
        totalTime = str(round(end - start,2))
        self.logText.insert(tk.END,'花費時間:' + totalTime + "秒" + "\n")
    def Vocal_Separation_asyncio(self):
        coroutine1 = self.Vocal_Separation()
        new_loop = asyncio.new_event_loop()     #在當前執行緒下創建時間迴圈，（未啟用），在start_loop裡面啟動它
        t = threading.Thread(target=self.get_loop,args=(new_loop,))   #通過當前執行緒開啟新的執行緒去啟動事件迴圈
        t.start()
        asyncio.run_coroutine_threadsafe(coroutine1,new_loop)  #這幾個是關鍵，代表在新執行緒中事件迴圈不斷“遊走”執行
    def OnMute(self, *unused):
        """Mute/Unmute audio.
        """
        # audio un/mute may be unreliable, see vlc.py docs.
        self.volMuted = m = not self.volMuted  # self.player.audio_get_mute()
        self.player.audio_set_mute(m)
        u = "Unmute" if m else "Mute"
        self.fileMenu.entryconfig(self.muteIndex, label=u)
        self.muteButton.config(text=u)
        # update the volume slider text
        self.OnVolume()

    def OnOpen(self, *unused):
        """Pop up a new dialow window to choose a file, then play the selected file.
        """
        # if a file is already running, then stop it.
        self.OnStop()
        # Create a file dialog opened in the current home directory, where
        # you can display all kind of files, having as title "Choose a video".
        video = askopenfilename(initialdir = Path(expanduser("./output/temp/")),
                                title = "Choose a video",
                                filetypes = (("all files", "*.*"),
                                             ("mp4 files", "*.mp4"),
                                             ("mov files", "*.mov")))

        # video = askopenfilename(initialdir = Path(expanduser("~")),
        #                         title = "Choose a video",
        #                         filetypes = (("all files", "*.*"),
        #                                      ("mp4 files", "*.mp4"),
        #                                      ("mov files", "*.mov")))
        self._Play(video)

    def _Pause_Play(self, playing):
        # re-label menu item and button, adjust callbacks
        p = 'Pause' if playing else 'Play'
        c = self.OnPlay if playing is None else self.OnPause
        self.fileMenu.entryconfig(self.playIndex, label=p, command=c)
        # self.fileMenu.bind_shortcut('p', c)  # XXX handled
        self.playButton.config(text=p, command=c)
        self._stopped = False

    def _Play(self, video):
        # helper for OnOpen and OnPlay
        if isfile(video):  # Creation
            m = self.Instance.media_new(str(video))  # Path, unicode
            self.player.set_media(m)
            self.parent.title("tkVLCplayer - %s" % (basename(video),))

            # set the window id where to render VLC's video output
            h = self.videopanel.winfo_id()  # .winfo_visualid()?
            if _isWindows:
                self.player.set_hwnd(h)
            elif _isMacOS:
                # XXX 1) using the videopanel.winfo_id() handle
                # causes the video to play in the entire panel on
                # macOS, covering the buttons, sliders, etc.
                # XXX 2) .winfo_id() to return NSView on macOS?
                v = _GetNSView(h)
                if v:
                    self.player.set_nsobject(v)
                else:
                    self.player.set_xwindow(h)  # plays audio, no video
            else:
                self.player.set_xwindow(h)  # fails on Windows
            # FIXME: this should be made cross-platform
            self.OnPlay()

    def OnPause(self, *unused):
        """Toggle between Pause and Play.
        """
        if self.player.get_media():
            self._Pause_Play(not self.player.is_playing())
            self.player.pause()  # toggles
    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status.input_overflow:
            try:
                # NB: This increment operation is not atomic, but this doesn't
                #     matter since no other thread is writing to the attribute.
                self.input_overflows += 1
            except Exception as e:
                pass
        # NB: self.recording is accessed from different threads.
        #     This is safe because here we are only accessing it once (with a
        #     single bytecode instruction).
        if self.recording:
            self.audio_q.put(indata.copy())
            self.previously_recording = True
        else:
            if self.previously_recording:
                self.audio_q.put(None)
                self.previously_recording = False

        self.peak = max(self.peak, np.max(np.abs(indata)))
        try:
            self.metering_q.put_nowait(self.peak)
        except queue.Full:
            pass
        else:
            self.peak = 0
    def create_stream(self, device=None):
        self.stream = None
        if self.stream is not None:
            self.stream.close()
        self.stream = sd.InputStream(
            device=device, channels=1, callback=self.audio_callback)
        self.stream.start()
    def wait_for_thread(self):
        # NB: Waiting time could be calculated based on stream.latency
        self.after(10, self._wait_for_thread)
    def _wait_for_thread(self):
        if self.thread.is_alive():
            self.wait_for_thread()
            return
        self.thread.join()
        self.init_buttons()
    def init_buttons(self):
        self.rec_button['text'] = 'record'
        self.rec_button['command'] = self.on_rec
        if self.stream:
            self.rec_button['state'] = 'normal'
        # self.settings_button['state'] = 'normal'
    def initRecord(self):
        # We try to open a stream with default settings first, if that doesn't
        # work, the user can manually change the device(s)
        self.create_stream()

        self.recording = self.previously_recording = False
        self.audio_q = queue.Queue()
        self.peak = 0
        self.metering_q = queue.Queue(maxsize=1)
    def on_rec(self):
        '''
        開始錄音
        '''
        self.recording = True
        self.logText.insert(tk.END,"開始錄音..." + "\n")

        # 隨機檔名
        # filename = tempfile.mktemp(
        #     prefix='rec_', suffix='.wav', dir=self.RecordPath)
        
        # 固定檔名
        self.recFileName = self.RecordPath + '/rec_temp.wav'

        # 確認rec_temp.wav檔案是否已存在，若存在刪除
        ## If file exists, delete it ##
        if os.path.isfile(self.recFileName):
            os.remove(self.recFileName)

        if self.audio_q.qsize() != 0:
            print('WARNING: Queue not empty!')
        self.thread = threading.Thread(
            target=file_writing_thread,
            kwargs=dict(
                file=self.recFileName,
                mode='x',
                samplerate=int(self.stream.samplerate),
                channels=self.stream.channels,
                q=self.audio_q,
            ),
        )
        self.thread.start()
        self.rec_button['text'] = 'stop'
        self.rec_button['command'] = self.on_stop
        self.rec_button['state'] = 'normal'
        # self.file_label['text'] = filename
        # NB: File creation might fail!  For brevity, we don't check for this.
    def on_stop(self):
        '''
        停止錄音
        '''
        self.logText.insert(tk.END,"停止錄音，存放位置:" + self.recFileName + "\n")
        
        self.rec_button['state'] = 'disabled'
        self.recording = False

        # proc = subprocess.Popen([ "python","progress.py","Merge two audio","30"])
        # self.logText.insert(tk.END,"合成音訊中" + "\n")
        # merge = Merge_Audio_Video()
        # start = time.time()
        # merge.merge_two_audio('./Record_audio/rec_temp.wav',"./output/temp/pitch_shift_" + str(self.selectedKEY) + ".wav","./output/merge/merge_output.mp3")
        # end = time.time()
        
        # totalTime = str(round(end - start,2))
        # print("花費:",totalTime,"秒")
        # proc.terminate()
        self.wait_for_thread()
        
    def OnPlay(self, *unused):
        """Play video, if none is loaded, open the dialog window.
        """
        # 開始錄音
        # asyncio.run(self.Record())

        # 紀錄是否已經播放結束
        self.playEnd = False
        # 停止錄音
        self.stopRecord = False
            
        # if there's no video to play or playing,
        # open a Tk.FileDialog to select a file
        if not self.player.get_media():
            if self.video:
                self._Play(expanduser(self.video))
                self.video = ''
            else:
                self.OnOpen()
        # Try to play, if this fails display an error message
        elif self.player.play():  # == -1
            self.showError("Unable to play the video.")
        else:
            # 開始錄音
            self.on_rec()
            self._Pause_Play(True)
            # set volume slider to audio level
            vol = self.player.audio_get_volume()
            if vol > 0:
                self.volVar.set(vol)
                self.volSlider.set(vol)

    def OnResize(self, *unused):
        """Adjust the window/frame to the video aspect ratio.
        """
        g = self.parent.geometry()
        if g != self._geometry and self.player:
            u, v = self.player.video_get_size()  # often (0, 0)
            if v > 0 and u > 0:
                # get window size and position
                g, x, y = g.split('+')
                w, h = g.split('x')
                # alternatively, use .winfo_...
                # w = self.parent.winfo_width()
                # h = self.parent.winfo_height()
                # x = self.parent.winfo_x()
                # y = self.parent.winfo_y()
                # use the video aspect ratio ...
                if u > v:  # ... for landscape
                    # adjust the window height
                    h = round(float(w) * v / u)
                else:  # ... for portrait
                    # adjust the window width
                    w = round(float(h) * u / v)
                self.parent.geometry("%sx%s+%s+%s" % (w, h, x, y))
                self._geometry = self.parent.geometry()  # actual

    def OnStop(self, *unused):
        """Stop the player, resets media.
        """
        if self.player:
            self.player.stop()
            self._Pause_Play(None)
            # reset the time slider
            self.timeSlider.set(0)
            self._stopped = True
        # XXX on macOS libVLC prints these error messages:
        # [h264 @ 0x7f84fb061200] get_buffer() failed
        # [h264 @ 0x7f84fb061200] thread_get_buffer() failed
        # [h264 @ 0x7f84fb061200] decode_slice_header error
        # [h264 @ 0x7f84fb061200] no frame!

    def OnTick(self):
        """Timer tick, update the time slider to the video time.
        """
        if self.player:
            # since the self.player.get_length may change while
            # playing, re-set the timeSlider to the correct range
            t = self.player.get_length() * 1e-3  # to seconds
            t2 = self.player.get_length() * 1e-3  # to seconds
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.player.get_time() * 1e-3  # to seconds
                # don't change slider while user is messing with it
                if t > 0 and time.time() > (self.timeSliderUpdate + 2):
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())
                if ((t >= t2-2) and (self.stopRecord == False)):
                    self.playEnd = True
                    
        # 播放結束，停止錄音
        if (self.playEnd):  
            self.playEnd = False
            # 停止錄音
            self.stopRecord = True
            self.on_stop()
        # start the 1 second timer again
        self.parent.after(1000, self.OnTick)
        # adjust window to video aspect ratio, done periodically
        # on purpose since the player.video_get_size() only
        # returns non-zero sizes after playing for a while
        if not self._geometry:
            self.OnResize()

    def OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                # this is a hack. The timer updates the time slider.
                # This change causes this rtn (the 'slider has changed' rtn)
                # to be invoked.  I can't tell the difference between when
                # the user has manually moved the slider and when the timer
                # changed the slider.  But when the user moves the slider
                # tkinter only notifies this rtn about once per second and
                # when the slider has quit moving.
                # Also, the tkinter notification value has no fractional
                # seconds.  The timer update rtn saves off the last update
                # value (rounded to integer seconds) in timeSliderLast if
                # the notification time (sval) is the same as the last saved
                # time timeSliderLast then we know that this notification is
                # due to the timer changing the slider.  Otherwise the
                # notification is due to the user changing the slider.  If
                # the user is changing the slider then I have the timer
                # routine wait for at least 2 seconds before it starts
                # updating the slider again (so the timer doesn't start
                # fighting with the user).
                self.player.set_time(int(t * 1e3))  # milliseconds
                self.timeSliderUpdate = time.time()

    def OnVolume(self, *unused):
        """Volume slider changed, adjust the audio volume.
        """
        vol = min(self.volVar.get(), 100)
        v_M = "%d%s" % (vol, " (Muted)" if self.volMuted else '')
        self.volSlider.config(label="Volume " + v_M)
        if self.player and not self._stopped:
            # .audio_set_volume returns 0 if success, -1 otherwise,
            # e.g. if the player is stopped or doesn't have media
            if self.player.audio_set_volume(vol):  # and self.player.get_media():
                self.showError("Failed to set the volume: %s." % (v_M,))

    def showError(self, message):
        """Display a simple error dialog.
        """
        self.OnStop()
        showerror(self.parent.title(), message)

    def judge(self,standard_audio_path,user_audio_path ):
        '''
        音準評分計算
        '''
        start = time.time()
        
        self.logText.insert(tk.END,'讀取音訊...' +"\n")
        proc = subprocess.Popen([ "python","progress.py","Get your vocal evaluated about Pitch","250"])
        print('讀取音訊...')

        # 使用者音訊讀取
        user_wav, sr = librosa.load(user_audio_path, sr=hp.sample_rate)
        # 標準音訊
        standard_wav, sr = librosa.load(standard_audio_path, sr=hp.sample_rate)

        # 波形圖
        fig = plt.figure(figsize=(12, 6))

        # 子圖1:標準原始波形圖
        subplot1 = fig.add_subplot(2,1,1)
        librosa.display.waveplot(standard_wav, sr=sr)
        plt.title('Standard waveform')
        plt.ylabel("Amplitude") # y label
        # plt.xlabel("Population growth by year") # x label

        # 子圖2:使用者原始波形圖
        subplot2 = fig.add_subplot(2,1,2)
        librosa.display.waveplot(user_wav, sr=hp.sample_rate)
        plt.title('User waveform')
        plt.ylabel("Amplitude") # y label
        plt.tight_layout() # 自動調整圖形之間間距

        # 1.計算梅爾倒頻譜係數MFCC 
        self.logText.insert(tk.END,'1/5 計算MFCC...' +"\n")
        print('1/5 計算MFCC...')

        user_mfccs = librosa.feature.mfcc(y=user_wav, sr=hp.sample_rate, n_mfcc=13)
        standard_mfccs = librosa.feature.mfcc(y=standard_wav, sr=hp.sample_rate, n_mfcc=13)
        
        '''
        # 2.產生MFCC圖
        self.logText.insert(tk.END,'2/5 產生MFCC 圖...' +"\n")
        print('2/5 產生MFCC 圖...')
        assert np.shape(user_mfccs)[0] == np.shape(standard_mfccs)[0]
        
        fig2 = plt.figure(figsize=(12, 6))
        # 子圖3:標準 MFCC 圖
        subplot3 = fig2.add_subplot(2,1,1)
        img3 = librosa.display.specshow(standard_mfccs, sr=sr, x_axis='time')
        plt.title('Standard MFCC ')
        plt.ylabel("Frequency(Hz)") # y label
        fig2.colorbar(img3, ax=subplot3) 

        # 子圖4:User MFCC 圖
        subplot4 = fig2.add_subplot(2,1,2)
        img4 = librosa.display.specshow(user_mfccs, sr=sr, x_axis='time')
        plt.title('User MFCC ')
        plt.ylabel("Frequency(Hz)") # y label
        fig2.colorbar(img4, ax=subplot4) 
        plt.tight_layout() # 自動調整圖形之間間距
    
        '''

        # 2.產生Mel頻譜圖
        self.logText.insert(tk.END,'2/5 產生Mel頻譜圖...' +"\n")
        print('2/5 產生Mel頻譜圖...')
        fig, ax = plt.subplots(2,1,figsize=(12,6))
        mel_spec_stan = librosa.feature.melspectrogram(standard_wav, sr=sr)
        stan_db = librosa.power_to_db(mel_spec_stan, ref=np.max)
        img1 = librosa.display.specshow(stan_db, y_axis='mel', x_axis='time', ax=ax[0])
        ax[0].set(title='Standard Mel spectrogram')
        plt.colorbar(img1, ax=ax[0], format='%+2.0f dB')

        mel_spec_user1 = librosa.feature.melspectrogram(user_wav, sr=sr)
        user1_db = librosa.power_to_db(mel_spec_user1, ref=np.max)
        img2 = librosa.display.specshow(user1_db, y_axis='mel', x_axis='time', ax=ax[1])
        ax[1].set(title='User Mel spectrogram')
        plt.colorbar(img2, ax=ax[1], format='%+2.0f dB')
        plt.tight_layout()


        
        # 3.比較使用者音訊與zeros
        self.logText.insert(tk.END,'3/5 比較使用者音訊與zeros...' +"\n")
        print('3/5 比較使用者音訊與zeros...')
        zeros = np.zeros([13, np.shape(user_mfccs)[1]])
        userAudio = np.array(list())
        sum_user = 0.
        
        time1 = time.time()
        for i in range(np.shape(user_mfccs)[0]):
            s1 = np.array(zeros[i], dtype = np.double)
            s2 = np.array(user_mfccs[i], dtype = np.double)
            dist_dtai_compare_out = dtaidtw.distance_fast(s1, s2)
            userAudio = np.append(userAudio, dist_dtai_compare_out)
            if i > 3:
                sum_user += dist_dtai_compare_out
        time2 = time.time()
        print("userAudio:",userAudio)
        print("time:",time2-time1)
        

        # 3.比較標準音訊與zeros
        self.logText.insert(tk.END,'4/5 比較標準音訊與zeros...' +"\n")
        print('4/5 比較標準音訊與zeros...')
        zeros = np.zeros([13, np.shape(user_mfccs)[1]])
        stanAudio = np.array(list())
        sum_stan = 0.
    

        time1 = time.time()
        for i in range(np.shape(user_mfccs)[0]):
            s1 = np.array(zeros[i], dtype = np.double)
            s2 = np.array(standard_mfccs[i], dtype = np.double) 
            dist_dtai_stan_out = dtaidtw.distance_fast(s1, s2)
            stanAudio = np.append(stanAudio, dist_dtai_stan_out) 
            if i > 3:
                sum_stan += dist_dtai_stan_out
        time2 = time.time()
        print("scores_stan_:",stanAudio)
        print("time:",time2-time1)
        
        print("sum_user:",sum_user)
        print("sum_stan:",sum_stan)
        score1 = 1 - min(sum_stan,sum_user) / max(sum_stan,sum_user)
        score2 = 0
        for i in range(3):
            score2 += min(stanAudio[i],userAudio[i]) / max(stanAudio[i],userAudio[i])
        print("score1:",score1)
        print("score2:",score2)
        score = score2 / 3 * 100 - score1 * 100
        '''
        scores = np.zeros(13, dtype = np.double)
        print("scores:",scores)
        for i in range(13):
            print("i:",i)
            print("userAudio[",i,"]",userAudio[i])
            print("stanAudio[",i,"]",stanAudio[i])
            print("min(userAudio[",i,"],stanAudio[",i,"]:",min(userAudio[i],stanAudio[i]))
            print("max(userAudio[",i,"],stanAudio[",i,"]:",max(userAudio[i],stanAudio[i]))
            scores[i] = min(userAudio[i],stanAudio[i]) / max(userAudio[i],stanAudio[i])
            #scores[i] = min(userAudio[i],stanAudio[i]) / max(userAudio[i],stanAudio[i])
            print("scores[",i,"]:",scores[i])
        
        print("scores:",scores)
        print("scores_mean:",scores.mean())
        
        score = scores.mean() *100
        print("score:",score)
        '''
        # 計算得分
        # print('scores_stan:',scores_stan,'scores_stan.mean():',scores_stan.mean())
        # print('scores:',scores,'scores.mean():',scores.mean())
        self.logText.insert(tk.END,'5/5 計算得分完成!' +"\n")
        print('5/5 計算得分完成!')


        # 分數上下限設定
        if score > 95:
            score = 95
        if score < 20:
            score = 20  
        
        end = time.time()
        proc.terminate()
        self.logText.insert(tk.END,'花費時間:' + str(round((end-start),2)) + '秒' +"\n")
        self.logText.insert(tk.END,'使用者音準分數:' + str(round(score,0)) + '分' +"\n")
        
        print('花費時間:',round((end-start),2),'秒')
        print("使用者音準分數:",score,"分")
        #print('使用者音準分數:',round(score,0),'分')
        
        return score

if __name__ == "__main__":

    _video = ''

    while len(sys.argv) > 1:
        arg = sys.argv.pop(1)
        if arg.lower() in ('-v', '--version'):
            # show all versions, sample output on macOS:
            # % python3 ./tkvlc.py -v
            # tkvlc.py: 2019.07.28 (tkinter 8.6 /Library/Frameworks/Python.framework/Versions/3.7/lib/libtk8.6.dylib)
            # vlc.py: 3.0.6109 (Sun Mar 31 20:14:16 2019 3.0.6)
            # LibVLC version: 3.0.6 Vetinari (0x3000600)
            # LibVLC compiler: clang: warning: argument unused during compilation: '-mmacosx-version-min=10.7' [-Wunused-command-line-argument]
            # Plugin path: /Applications/VLC3.0.6.app/Contents/MacOS/plugins
            # Python: 3.7.4 (64bit) macOS 10.13.6

            # Print version of this vlc.py and of the libvlc
            print('%s: %s (%s %s %s)' % (basename(__file__), __version__,
                                         Tk.__name__, Tk.TkVersion, libtk))
            try:
                vlc.print_version()
                vlc.print_python()
            except AttributeError:
                pass
            sys.exit(0)

        elif arg.startswith('-'):
            print('usage: %s  [-v | --version]  [<video_file_name>]' % (sys.argv[0],))
            sys.exit(1)

        elif arg:  # video file
            _video = expanduser(arg)
            if not isfile(_video):
                print('%s error: no such file: %r' % (sys.argv[0], arg))
                sys.exit(1)

    # Create a Tk.App() to handle the windowing event loop
    root = Tk.Tk()
    player = Player(root, video=_video)
    root.protocol("WM_DELETE_WINDOW", player.OnClose)  # XXX unnecessary (on macOS)
    root.mainloop()