from tkinter import Y
import numpy as np
import time as t
import librosa
import librosa.display
import matplotlib.pyplot as plt
import hparam_score as hp


user_audio_path = "./output/rec_temp/vocals.wav"
standard_audio_path = "./output/temp/vocals_0.wav"

# 音訊讀取
print('0 音訊讀取...')
'''
y, sr = librosa.load('./output/temp/vocals_0.wav')
fig, ax = plt.subplots()
M = librosa.feature.melspectrogram(y=y, sr=sr)
M_db = librosa.power_to_db(M, ref=np.max)
img = librosa.display.specshow(M_db, y_axis='mel', x_axis='time', ax=ax)
ax.set(title='Mel spectrogram display')
fig.colorbar(img, ax=ax, format="%+2.f dB")
'''
#######################################################

standard, sr = librosa.load('./output/temp/vocals_0.wav')
user1, sr = librosa.load('./output/rec_temp/85.wav')
# user2, sr = librosa.load('./output/rec_temp/vocals.wav')

fig, ax = plt.subplots(2,1,figsize=(12,6))
mel_spec_stan = librosa.feature.melspectrogram(standard, sr=sr)
stan_db = librosa.power_to_db(mel_spec_stan, ref=np.max)
img1 = librosa.display.specshow(stan_db, y_axis='mel', x_axis='time', ax=ax[0])
ax[0].set(title='Standard Mel spectrogram display')
plt.colorbar(img1, ax=ax[0], format='%+2.0f dB')


mel_spec_user1 = librosa.feature.melspectrogram(user1, sr=sr)
user1_db = librosa.power_to_db(mel_spec_user1, ref=np.max)
img2 = librosa.display.specshow(user1_db, y_axis='mel', x_axis='time', ax=ax[1])
ax[1].set(title='USER1 Mel spectrogram display')
plt.colorbar(img2, ax=ax[1], format='%+2.0f dB')
plt.tight_layout()
'''
subplot4 = fig2.add_subplot(3,1,2)
mel_spec_user1 = librosa.feature.melspectrogram(user1)
mel_spec_user1 = librosa.power_to_db(mel_spec_user1, ref=np.max)
librosa.display.specshow(mel_spec_user1, sr=sr ,x_axis='time', y_axis='hz')
plt.title('good')
plt.colorbar(format='%+2.0f dB')

subplot5 = fig2.add_subplot(3,1,3)
mel_spec_user2 = librosa.feature.melspectrogram(user2)
mel_spec_user2 = librosa.power_to_db(mel_spec_user2, ref=np.max)
librosa.display.specshow(mel_spec_user2, sr=sr, x_axis='time', y_axis='hz')
plt.title('bad')
plt.colorbar(format='%+2.0f dB')

plt.tight_layout()
'''
plt.tight_layout()
plt.show()


'''
# fig1: 波形圖
fig1 = plt.figure()

subplot1 = fig1.add_subplot(2,1,1)
librosa.display.waveplot(standard, sr=sr)
plt.title('Standard waveform')
plt.ylabel("Amplitude")

subplot2 = fig1.add_subplot(2,1,2)
librosa.display.waveplot(user, sr=sr)
plt.title('User waveform')
plt.ylabel("Amplitude")

plt.tight_layout()
plt.show()
'''

'''
# fig2: Mel 頻譜圖
fig2 = plt.figure(figsize=(12, 12))

subplot3 = fig2.add_subplot(3,1,1)
mel_spec_stan = librosa.feature.melspectrogram(standard)
mel_spec_stan = librosa.amplitude_to_db(mel_spec_stan, ref=np.max)
librosa.display.specshow(mel_spec_stan, sr=sr, x_axis='time', y_axis='hz')
plt.title('Standard')
plt.colorbar(format='%+2.0f dB')

subplot4 = fig2.add_subplot(3,1,2)
mel_spec_user1 = librosa.feature.melspectrogram(user1)
mel_spec_user1 = librosa.power_to_db(mel_spec_user1, ref=np.max)
librosa.display.specshow(mel_spec_user1, sr=sr ,x_axis='time', y_axis='hz')
plt.title('good')
plt.colorbar(format='%+2.0f dB')

subplot5 = fig2.add_subplot(3,1,3)
mel_spec_user2 = librosa.feature.melspectrogram(user2)
mel_spec_user2 = librosa.power_to_db(mel_spec_user2, ref=np.max)
librosa.display.specshow(mel_spec_user2, sr=sr, x_axis='time', y_axis='hz')
plt.title('bad')
plt.colorbar(format='%+2.0f dB')

plt.tight_layout()
plt.show()

'''

'''
y, sr = librosa.load('./output/temp/vocals_0.wav')
fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)
D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
img = librosa.display.specshow(D, y_axis='linear', x_axis='time',
                               sr=sr, ax=ax[0])
ax[0].set(title='Linear-frequency power spectrogram')
ax[0].label_outer()

hop_length = 1024
D = librosa.amplitude_to_db(np.abs(librosa.stft(y, hop_length=hop_length)),
                            ref=np.max)
librosa.display.specshow(D, y_axis='hz', sr=sr, hop_length=hop_length,
                         x_axis='time', ax=ax[1])
ax[1].set(title='Log-frequency power spectrogram')
ax[1].label_outer()
fig.colorbar(img, ax=ax, format="%+2.f dB")

plt.show()
'''

'''
# 1.計算梅爾倒頻譜係數MFCC 
print('1 計算MFCC...')
user_mfccs = librosa.feature.mfcc(y=user_wav, sr=hp.sample_rate, n_mfcc=13)
standard_mfccs = librosa.feature.mfcc(y=standard_wav, sr=hp.sample_rate, n_mfcc=13)
        
# 2.產生MFCC頻譜圖
print('2 產生MFCC圖...')
fig1 = plt.figure(figsize=(12, 6))
assert np.shape(user_mfccs)[0] == np.shape(standard_mfccs)[0]

# 子圖1:標準 MFCC 頻譜圖
subplot1 = fig1.add_subplot(2,1,1)
img1 = librosa.display.specshow(standard_mfccs, sr=sr, x_axis='time')
plt.title('Standard MFCC ')
plt.ylabel("Frequency(Hz)") # y label
fig1.colorbar(img1, ax=subplot1) 

# 子圖2:User MFCC 頻譜圖
subplot2 = fig1.add_subplot(2,1,2)
img2 = librosa.display.specshow(user_mfccs, sr=sr, x_axis='time')
plt.title('User MFCC ')
plt.ylabel("Frequency(Hz)") # y label
fig1.colorbar(img2, ax=subplot2) 

plt.tight_layout() # 自動調整圖形之間間距
'''    
'''
# 2.產生Mel頻譜圖
print('2/5 產生Mel頻譜圖...')
        
fig3 = plt.figure(figsize=(12, 6))
# 子圖3:標準Mel頻譜圖
subplot5 = fig3.add_subplot(2,1,1)
stan_mel_sp = librosa.feature.melspectrogram(standard_mfccs, sr=sr, n_fft=2048, hop_length=1024)
stan_mel_sp_db = librosa.power_to_db(stan_mel_sp)
img5 = librosa.display.specshow(stan_mel_sp_db, sr=sr, x_axis='time', y_axis='hz')
plt.title('Standard Mel ')
plt.ylabel("Frequency(Hz)") # y label
fig3.colorbar(img5, ax=subplot5) 

# 子圖4:User Mel頻譜圖
subplot6 = fig3.add_subplot(2,1,2)
user_mel_sp = librosa.feature.melspectrogram(user_mfccs, sr=sr, n_fft=2048, hop_length=1024)
user_mel_sp_db = librosa.power_to_db(user_mel_sp)
img6 = librosa.display.specshow(user_mel_sp_db, sr=sr, x_axis='time', y_axis='hz')
plt.title('User Mel ')      
plt.ylabel("Frequency(Hz)") # y label
fig3.colorbar(img6, ax=subplot6) 
plt.tight_layout() # 自動調整圖形之間間距
'''