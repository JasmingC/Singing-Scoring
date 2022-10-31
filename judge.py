# 唱歌音高、節奏評分
import os
import numpy as np
import librosa
import librosa.display
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt
import utils_score as utils
import hparam_score as hp
import time
import json
from beat_track_v5 import Beat

class Judge:
    def __init__(self):
        a = 0
    def load_JSON(self,jsonPATH,jsonKEY):
        '''
        讀取JSON檔
        '''
        try:
            with open(jsonPATH) as json_file:
                data = json.load(json_file)
                for p in data[jsonKEY]:
                    for key, value in p.items():
                        tempStr = key + ':' + str(value)              
                        # print (tempStr)
                result = json.dumps(data, indent=4)
                print (result)
                # return result
                return data[jsonKEY][0]
        except ValueError as error:
            errorMsg = 'Load JSON Error!'
            print (error)
            return errorMsg

    def judge(self,standard_audio_path,user_audio_path ):
        '''
        音準評分計算
        '''
        start = time.time()
        # #　get_samplerate
        # standard_samplerate = librosa.get_samplerate(standard_audio_path)
        # print('standard_samplerate:',standard_samplerate)
        # user_samplerate = librosa.get_samplerate(user_audio_path)
        # print('user_samplerate:',user_samplerate)
        print('1/5 計算梅爾倒頻譜係數MFCC...')
        # # 使用者音訊
        # user_wav = utils.load_wav(user_audio_path)
        # # 找出音訊結束點
        # user_wav = user_wav[0:utils.find_endpoint(user_wav)]
        # 使用者音訊讀取
        user_wav, sr = librosa.load(user_audio_path, sr=hp.sample_rate)
        # 標準音訊
        standard_wav, sr = librosa.load(standard_audio_path, sr=hp.sample_rate)
        # print('sample_rate:',sr)
        # 設定圖形大小
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
        user_mfccs = librosa.feature.mfcc(y=user_wav, sr=hp.sample_rate, n_mfcc=24)
        standard_mfccs = librosa.feature.mfcc(y=standard_wav, sr=sr, n_mfcc=24)
        # print ('user_mfccs shape:',user_mfccs.shape)
        # print ('standard_mfccs shape:',standard_mfccs.shape)
        print('2/5 產生MFCC 頻譜圖...')
        assert np.shape(user_mfccs)[0] == np.shape(standard_mfccs)[0]
        
        fig2 = plt.figure(figsize=(12, 6))
        # 子圖3:標準 MFCC 頻譜圖
        subplot3 = fig2.add_subplot(2,1,1)
        img3 = librosa.display.specshow(standard_mfccs, sr=sr, x_axis='time')
        plt.title('Standard MFCC ')
        plt.ylabel("Frequency(Hz)") # y label
        fig2.colorbar(img3, ax=subplot3) 

        # 子圖4:User MFCC 頻譜圖
        subplot4 = fig2.add_subplot(2,1,2)
        img4 = librosa.display.specshow(user_mfccs, sr=sr, x_axis='time')
        plt.title('User MFCC ')
        plt.ylabel("Frequency(Hz)") # y label
        fig2.colorbar(img4, ax=subplot4) 

        plt.tight_layout() # 自動調整圖形之間間距
        # plt.show()

        # # Visualize the MFCC series
        # fig, ax = plt.subplots(nrows=2, sharex=True)
        # img = librosa.display.specshow(librosa.power_to_db(S, ref=np.max),
        #                             x_axis='time', y_axis='mel', fmax=8000,
        #                             ax=ax[0])
        # fig.colorbar(img, ax=[ax[0]])
        # ax[0].set(title='Mel spectrogram')
        # ax[0].label_outer()
        # img = librosa.display.specshow(standard_mfccs, x_axis='time', ax=ax[1])
        # fig.colorbar(img, ax=[ax[1]])
        # ax[1].set(title='MFCC')

        scores = np.array(list())
        print('3/5 fastdtw比較標準音訊與使用者音訊...')
        # 2.fastdtw比較標準音訊與使用者音訊
        for i in range(np.shape(user_mfccs)[0]):
            out = fastdtw(user_mfccs[i], standard_mfccs[i], dist=euclidean)
            scores = np.append(scores, out[0])

        zeros = np.zeros([24, np.shape(user_mfccs)[1]])
        scores_stan = np.array(list())
        print('4/5 fastdtw比較標準音訊與zeros...')
        # 3.fastdtw比較標準音訊與zeros
        for i in range(np.shape(user_mfccs)[0]):
            out = fastdtw(zeros[i], standard_mfccs[i], dist=euclidean)
            scores_stan = np.append(scores_stan, out[0])
        
        # 計算得分
        # print('scores_stan:',scores_stan,'scores_stan.mean():',scores_stan.mean())
        # print('scores:',scores,'scores.mean():',scores.mean())
        print('5/5 計算得分完成!')
        score = 1 - (scores.mean()-200) / scores_stan.mean()
        # print('score1:',round(score,2),'分')
        score = score * 100
        # print('score2:',round(score,2),'分')
        # score = score + 22
        # 線性調整分數
        if (score < 70):
            diff = 70 - score
            score = score - (diff * 15)

        # 分數上下限設定
        if (score > 95):
            score = 95
        if (score < 20):
            score = 20  
    
        end = time.time()
        print('5/5 計算得分完成!')
        print('花費時間:',round((end-start),2),'秒')
        print('使用者音準分數:',round(score,2),'分')
        
        return score
    def main(self):
        '''
        主程式
        '''
        # 使用者唱歌音訊檔
        # user_audio_path = "./audio/vocals_音準95_節奏95.wav"
        # user_audio_path = "./audio/vocals_音準70_節奏60.wav"
        user_audio_path = "./audio/vocals_音準50_節奏70.wav"
        # user_audio_path = "./audio/vocals_音準20_節奏60.wav"
        # user_audio_path = "./audio/amateur1_hostage_vocals (mp3cut.net).wav"

        # 標準唱歌音訊檔
        standard_audio_path = "./audio/vocals_音準95_節奏95.wav"
        # standard_audio_path = "./audio/aMEI_hostage_vocals (mp3cut.net).wav"

        print ('user_audio_path:',user_audio_path)
        print ('standard_audio_path:',standard_audio_path)
        
        # 唱歌評分
        self.judge(standard_audio_path,user_audio_path)

        beat = Beat()
        # 計算節奏分數
        beat.score(standard_audio_path,user_audio_path)

if __name__ == "__main__":
    a = Judge()
    a.main()