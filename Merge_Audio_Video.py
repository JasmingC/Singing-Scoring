from avel import *
import moviepy.editor as mpe

class Merge_Audio_Video:
    def __init__(self):
        a = 0
    async def combine_audio_in_video_async(self,vidname, audname, outname, fps=25):
        '''
        將音訊檔加入影片中
        '''
        my_clip = mpe.VideoFileClip(vidname)
        audio_background = mpe.AudioFileClip(audname)
        final_clip = my_clip.set_audio(audio_background)
        final_clip.write_videofile(outname,fps=fps)
    def combine_audio_in_video(self,vidname, audname, outname, fps=25):
        '''
        將音訊檔加入影片中
        '''
        my_clip = mpe.VideoFileClip(vidname)
        audio_background = mpe.AudioFileClip(audname)
        final_clip = my_clip.set_audio(audio_background)
        final_clip.write_videofile(outname,fps=fps)
    def merge_two_audio(self,audio1, audio2, output):
        '''
        合成兩音訊檔，output:輸出檔名，vol:各別音訊音量大小
        '''
        # audio1 = './videos/vocals.wav'
        # audio2 = './videos/accompaniment.wav'
        # 輸出檔名
        # output = "./output/merge_output.mp3"
        merge_audio(audio1, audio2, output , vol1=1.0, vol2=1.0)
        # 讀取音檔
    def remove_audio(self,video,out):
        '''
        移除音訊檔
        '''
        videoclip = VideoFileClip(video)
        new_clip = videoclip.without_audio()
        new_clip.write_videofile(out)

if __name__ == "__main__":
    merge = Merge_Audio_Video()

    # video = './tempVideo.mp4'
    video = 'converted_ffmpeg.webm'
    audio = './output/temp/accompaniment.wav'
    output = './output/temp/mergeResult.mp4'
    merge.combine_audio_in_video(video,audio,output)


