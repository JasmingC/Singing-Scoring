from __future__ import unicode_literals
from pytube import YouTube
from moviepy.editor import *
import platform
import subprocess
from moviepy import *
from moviepy.editor import *
import glob
import youtube_dl
import asyncio

class FilenameCollectorPP(youtube_dl.postprocessor.common.PostProcessor):
    def __init__(self):
        super(FilenameCollectorPP, self).__init__(None)
        self.filenames = []

    def run(self, information):
        self.filenames.append(information["filepath"])
        return [], information

class YouTubeDownload:
    def __init__(self,saveFolder):
        self.fileName = ''
        self.saveFolder = saveFolder
        # 建立存放YouTubeDownload資料夾
        from pathlib import Path
        self.path2 = "./YouTubeDownload/"
        Path(self.path2).mkdir(parents=True, exist_ok=True)
    def progress(self,chunk, file_handle, bytes_remaining):
        contentSize = video.filesize
        size = contentSize - bytes_remaining

        print('\r' + '[Download progress]:[%s%s]%.2f%%;' % (
        '█' * int(size*20/contentSize), ' '*(20-int(size*20/contentSize)), float(size/contentSize*100)), end='')
    
    def mp4ToMp3(self):
        '''
        mp4轉成mp3
        '''
        # mp4 轉成 mp3
        print('mp4 轉成 mp3')
        video2 = VideoFileClip(self.saveFolder + self.fileName + '.mp4')
        video2.audio.write_audiofile(self.saveFolder + self.fileName + '.mp3')

    def playMp3(self,filePath):
        '''
        播放mp3
        '''
        import playsound
        playsound.playsound(filePath)
    def getFileName(self):
        return self.fileName
    def downloadVideo(self,url):
        '''
        下載YouTube影片
        '''
        try:
            # Init
            yt = YouTube(url, on_progress_callback=self.progress)
            
            video = yt.streams.first()
            
            # 下載最高畫質影片
            yt.streams.get_highest_resolution().download(self.saveFolder)
        except:
            print(f'影片高畫質: {yt.title} 無法下載，跳過繼續下載最低畫質影片。', end='\n\n')
            # 下載最低畫質影片
            yt.streams.get_lowest_resolution.download(self.saveFolder)
        else:
            print(f"影片{yt.title}下載完成!", end='\n\n')
        
        # self.filePath = self.saveFolder + yt.title
        self.fileName = yt.title

        # # file_size
        # file_size = video.filesize

        # # Download
        # video.download()
    def merge_audio_video(self):
        '''
        合併影片和聲音OK!
        '''
        video_dirs = glob.glob('./videos/123.mp4')
        audio = AudioFileClip("./videos/accompaniment.wav")# 提取音轨
        for video_dir in video_dirs:
            video = VideoFileClip(video_dir)# 读入视频
            video = video.set_audio(audio)# 将音轨合成到视频中
            file = video_dir.split("\\")[-1]
            video.write_videofile(file)# 输出
    def merge_media(self):
        '''
        合併影片和聲音
        '''
        # from pathlib import Path
        # # 相對路徑轉成絕對路徑
        # fpath1 = Path('./videos/123.mp3').absolute()
        # fpath2 = Path('./videos/123.mp4').absolute()
        # fpath3 = Path('./videos/output.mp4').absolute()
        # print(fpath1)

        temp_audio = os.path.join('C:\videos\123.mp3')
        temp_video = os.path.join('C:\videos\123.mp4')
        temp_output = os.path.join('C:\videos\output.mp4')
        # temp_video = os.path.join(self.saveFolder, self.fileName + '.mp4')
        # temp_audio = os.path.join(self.saveFolder, self.fileName + '.mp3')
        # temp_output = os.path.join(self.saveFolder, 'output.mp4')

        cmd = f'ffmpeg -i {temp_video} -i {temp_audio} \
            -map 0:v -map 1:a -c copy -y {temp_output}'
        try:
            subprocess.call(cmd, shell=True)
            # 視訊檔重新命名
            # os.rename(temp_output, os.path.join(fileobj['dir'], fileobj['name']))
            # os.remove(temp_audio)
            # os.remove(temp_video)
            print('視訊和聲音合併完成')
        except:
            print('視訊和聲音合併失敗')
    def empty_folder(self,saveFolder):
        import shutil   
        self.saveFolder = saveFolder
        shutil.rmtree(self.saveFolder)
    async def download_youtube_dl_mkv(self,urls):
        '''
        使用youtube_dl下載影片:mkv format
        '''
        ydl_opts = {'keepvideo':True,
        "outtmpl": "./YouTubeDownload/%(title)s.%(ext)s"}
        # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        filename_collector = FilenameCollectorPP()
        ydl.add_post_processor(filename_collector)
        ydl.download(urls)
        return filename_collector.filenames[0]
    async def download_youtube_dl_mp4(self,urls):
        '''
        使用youtube_dl下載影片:mp4 format
        '''
        return await self.download_youtube_dl(urls,'m4a')
    async def download_youtube_dl(self,urls,format):
        '''
        使用youtube_dl下載mp3
        '''
        # ydl_opts = {'keepvideo':True}
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': '192',
            }],
            "outtmpl": "./YouTubeDownload/%(title)s.%(ext)s"
        }
        # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        filename_collector = FilenameCollectorPP()
        ydl.add_post_processor(filename_collector)
        ydl.download(urls)
        return filename_collector.filenames[0]
    def download_audio(url):
        options = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": "%(title)s.%(ext)s",
        }

        ydl = youtube_dl.YoutubeDL(options)
        filename_collector = FilenameCollectorPP()
        ydl.add_post_processor(filename_collector)
        ydl.download([url])

        return filename_collector.filenames[0]

async def main():
    # 儲存路徑
    saveFolder = './videos/'
    # 使用youtube_dl下載影片
    youTube = YouTubeDownload(saveFolder)
    URL2 = ['https://youtu.be/9nnd8hCXUBg'] # 鄧紫棋  喜歡你
    urls = ['https://www.youtube.com/watch?v=K5rjNK_De-I']# 人質
    await youTube.download_youtube_dl(urls,'mp4')
    # await youTube.download_youtube_dl_mp4(URL2)
    # # # 戴愛玲 - 人質
    # # url = 'https://www.youtube.com/watch?v=Z4VgJ36T-OE'
    # # 張惠妹 - 人質(歌詞版)
    # url = 'https://www.youtube.com/watch?v=K5rjNK_De-I'
    # youTube.downloadVideo(url)
    # youTube.mp4ToMp3()
  
    # # youTube.merge_audio_video()

if __name__ == "__main__":
   asyncio.run(main())