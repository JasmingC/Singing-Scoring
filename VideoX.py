from moviepy.editor import *
import pygame
import cv2
import playsound
import threading
import multiprocessing as mp
# from moviepy import *

class VideoX:
    def __init__(self):
        self.fileName = ''
    def playMp3(self,filePath):
        '''
        播放mp3
        '''
        playsound.playsound(filePath)
    def playMp4_v3(self,filePath):
        '''
        使用moviepy播放mp4
        '''
        video = VideoFileClip(filePath)
        # 設置窗口標題
        pygame.display.set_caption("myVideo")
        # 設置窗口大小
        # video.size = (640, 480)
        # surface = pygame.display.set_mode(video.size)
        # 全螢幕
        video.preview()
    def playMp4_v2(self,filePath):
        '''
        使用OpenCV播放mp4
        '''
        cap = cv2.VideoCapture(filePath)

        #check if the video capture is open
        if(cap.isOpened() == False):
            print("Error Opening Video Stream Or File")

        if(cap.isOpened()):
            ret, frame =cap.read()

            if ret == True:
                frame = cv2.resize(frame, (960, 480)) 
                cv2.imshow('frame', frame)
                
                # if cv2.waitKey(25)  == ord('q'):
                #     break

            # else:
            #     break
        
    def playMp4(self,filePath):
        '''
        播放mp4
        '''
        cap = cv2.VideoCapture(filePath)

        #check if the video capture is open
        if(cap.isOpened() == False):
            print("Error Opening Video Stream Or File")

        while(cap.isOpened()):
            ret, frame =cap.read()

            if ret == True:
                frame = cv2.resize(frame, (960, 480)) 
                cv2.imshow('frame', frame)
                
                if cv2.waitKey(25)  == ord('q'):
                    break

            else:
                break
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":

    # from moviepy.editor import VideoFileClip
 
    # clip1 = VideoFileClip("./videos/張惠妹 - 人質(歌詞版).mp3")
    # audioclip1 = clip1.audio
    # clip2 = VideoFileClip("./videos/張惠妹 - 人質(歌詞版).mp4")
    
    # new_video = clip2.set_audio(audioclip1)
    # # audioclip1.write_audiofile("twice_jelly_jelly.mp3")  # 如果想要輸出 mp3
    # new_video.write_videofile("./videos/new_audio.mp4")
    
   
    videoX = VideoX()
    videoX.playMp3('./videos/張惠妹 - 人質(歌詞版).mp3')
    # videoX.playMp4('./videos/張惠妹 - 人質(歌詞版).mp4')
    # videoX.playMp4_v3('./videos/張惠妹 - 人質(歌詞版).mp4')

    # mp3 = mp.Process(target=videoX.playMp3('./videos/張惠妹 - 人質(歌詞版).mp3'), args=('website',))
    # mp4 = mp.Process(target=videoX.playMp4_v2('./videos/張惠妹 - 人質(歌詞版).mp4'), args=('website',))
    
    # 開始加速執行
    # mp4.start()
    # mp3.start()
    
    # 結束多進程
    # mp3.join()
    # mp4.join()

    # sound_trd = threading.Thread (target = videoX.playMp3('./videos/張惠妹 - 人質(歌詞版).mp3'))
    # # sound_trd.start ()
    # video_trd = threading.Thread (target = videoX.playMp4_v2('./videos/張惠妹 - 人質(歌詞版).mp4'))
    # video_trd.start ()
