# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import librosa
import os
import soundfile as sf

class Pitch_Shift:

    async def aug_pitch_shift(self,input_audio,outputFolder,fileName,Keys,samplerate):
        '''
        升降Key
        '''
        dirpath = os.path.dirname(input_audio)
        topath = dirpath.replace('audio', 'aug_audio')
        if not os.path.isdir(topath):   # 判斷目標路徑是否存在，不存在則創建
            os.mkdir(topath)
        # 讀取檔案
        y, sr = librosa.load(input_audio, sr=samplerate)
        y_shift_results = []
        for step in Keys:
            # 升降Key調整
            y_shift = librosa.effects.pitch_shift(y, sr, n_steps=step)   # 使用PS生成新資料
            y_shift_results.append(y_shift)
            # 儲存檔案
            sf.write(outputFolder + fileName + '_' + str(step) +'.wav', y_shift, samplerate, subtype='PCM_24')
            print('完成，儲存位置: ' + outputFolder + fileName + '_' + str(step) +'.wav')
            # # [librosa]0.8版本後不再支持write_wav，改用soundfile
            # librosa.output.write_wav(os.path.join(topath,    # 資料匯出為檔案
            #     os.path.basename(input_audio).replace('.ogg', '_ps{}.ogg'.format(step))), y_shift, sr)
        return y,y_shift_results

    def aug_time_stretch(self,input_audio):
        '''
        音量調整
        '''
        dirpath = os.path.dirname(input_audio)
        topath = dirpath.replace('audio', 'aug_audio')
        if not os.path.isdir(topath):   # 判斷目標路徑是否存在，不存在則創建
            os.mkdir(topath)
        y, sr = librosa.load(input_audio, sr=44100)
        for rate in [0.7, 0.8, 0.9, 1.1, 1.2, 1.3]:
            y_shift = librosa.effects.time_stretch(y, rate=rate)   # 使用TS生成新資料
            data = y_p
            librosa.output.write_wav(os.path.join(topath,    # 資料匯出為檔案
                os.path.basename(input_audio).replace('.ogg', '_ts{}.ogg'.format(rate))), y_shift, sr)

    def pitch_plot(self,y,y_ps,Keys):
        '''
        畫出調整後音高圖
        '''
        plt.subplot(311)
        plt.plot(y)
        plt.title('Original waveform')
        plt.axis([0, 200000, -0.4, 0.4])
        # plt.axis([88000, 94000, -0.4, 0.4])
        id = 312
        for i in range(len(Keys)):
            plt.subplot(id)
            plt.plot(y_shift_results[i])
            plt.title('Pitch Shift Key: ' + str(Keys[i]) +' transformed waveform')
            plt.axis([0, 200000, -0.4, 0.4])
            # plt.axis([88000, 94000, -0.4, 0.4])
            plt.tight_layout()
            id += 1
        plt.show()

    def demo_plot(self):
        audio = './videos/accompaniment.wav'
        y, sr = librosa.load(audio, sr=44100)
        y_ps = librosa.effects.pitch_shift(y, sr, n_steps=16)   # n_steps控制音調變化尺度
        y_ts = librosa.effects.time_stretch(y, rate=1.2)   # rate控制時間維度的變換尺度
        plt.subplot(311)
        plt.plot(y)
        plt.title('Original waveform')
        plt.axis([0, 200000, -0.4, 0.4])
        # plt.axis([88000, 94000, -0.4, 0.4])
        plt.subplot(312)
        plt.plot(y_ts)
        plt.title('Time Stretch transformed waveform')
        plt.axis([0, 200000, -0.4, 0.4])
        plt.subplot(313)
        plt.plot(y_ps)
        plt.title('Pitch Shift transformed waveform')
        plt.axis([0, 200000, -0.4, 0.4])
        # plt.axis([88000, 94000, -0.4, 0.4])
        plt.tight_layout()
        # save wav 
        # [Error]module 'librosa' has no attribute 'output'
        # [librosa]0.8版本後不再支持write_wav，改用soundfile
        # librosa.output.write_wav('pitch_shift.wav', y, y_ps)

        # [soundfile]Write out audio as 24bit PCM WAV
        data = y_ps
        samplerate = 44100
        sf.write('stereo_file.wav', data, samplerate, subtype='PCM_24')

        plt.show()

if __name__ == "__main__":
    # 讀取音檔
    audio = './output/temp/accompaniment.wav'
    # 輸出位置
    outputFolder = './output/temp/'
    PS = Pitch_Shift()
    # 指定升降Key
    keys = [-2,-1,0,1,2]
    # 升降Key調整
    y,y_shift_results = PS.aug_pitch_shift(audio,outputFolder,Keys=keys,samplerate=44100)
    # 畫出升降Key差異圖
    # PS.pitch_plot(y,y_shift_results,keys)