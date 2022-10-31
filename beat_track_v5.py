# https://librosa.org/doc/0.9.1/generated/librosa.beat.beat_track.html#librosa.beat.beat_track
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np
# 標準唱歌音訊檔
standard_audio_path = "./audio/aMEI_hostage_vocals (mp3cut.net).wav"
# 使用者唱歌音訊檔
user_audio_path = "./audio/amateur1_hostage_vocals (mp3cut.net).wav"

class Beat:
    def __init__(self):
        self.test = 0
    def score(self,standard_audio_path,user_audio_path):
        '''
        計算節奏分數
        '''
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

        score_tempo = 100 - abs(Standard_BPM - User_BPM)*4
        if (score_tempo > 95): score_tempo = 95
        if (score_tempo < 60): score_tempo = 60
        # score_tempo = int(score_tempo)
        score_tempo = round(score_tempo,2)
        print('使用者節奏分數:',score_tempo,'分')
        plt.tight_layout() # 自動調整圖形之間間距
        plt.show()

if __name__ == "__main__":
    beat = Beat()
    # 計算節奏分數
    beat.score(standard_audio_path,user_audio_path)