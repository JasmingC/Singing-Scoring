# ————————————————
# 版权声明：本文为CSDN博主「一粒马豆」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/MAILLIBIN/article/details/89764853

import matplotlib.pyplot as plt
import librosa
import librosa.display
import librosa.util
import numpy as np
import pandas as pd
 
# 標準唱歌音訊檔
standard_audio_path = "./audio/aMEI_hostage_vocals (mp3cut.net).wav"

#要转换的输入wav音频文件
input_wav=standard_audio_path
 
y,sr=librosa.load(input_wav,sr=None,duration=None)
chroma=librosa.feature.chroma_cqt(y=y, sr=sr) 
 
c=pd.DataFrame(chroma)
c0=(c==1)
c1=c0.astype(int)
labels=np.array(range(1,13))
note_values=labels.dot(c1)
 
plt.figure(figsize=(20,10))
plt.subplots_adjust(wspace=1, hspace=0.2)
 
plt.subplot(211)
plt.xlabel('second')
plt.ylabel('amplitude')
librosa.display.waveshow(y, sr=sr,color="#ff9999")
 
plt.subplot(212)
plt.xlabel('time')
plt.ylabel('Pitch')
plt.grid(linewidth=0.5,alpha=0.3)
plt.xticks(range(0,1000,50))
plt.yticks(range(1,13),["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"])
plt.plot(note_values,color="#008080",linewidth=0.8)
plt.hlines(note_values, range(len(note_values)),np.array(range(len(note_values)))+1 ,color="red", linewidth=10)
plt.show()
