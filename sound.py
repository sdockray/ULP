import os
import librosa
import numpy as np
import scipy





def describe_freq(freqs):
    mean = np.mean(freqs)
    std = np.std(freqs) 
    maxv = np.amax(freqs) 
    minv = np.amin(freqs) 
    median = np.median(freqs)
    skew = scipy.stats.skew(freqs)
    kurt = scipy.stats.kurtosis(freqs)
    q1 = np.quantile(freqs, 0.25)
    q3 = np.quantile(freqs, 0.75)
    mode = scipy.stats.mode(freqs)[0][0]
    iqr = scipy.stats.iqr(freqs)
    
    return [mean, std, maxv, minv, median, skew, kurt, q1, q3, mode, iqr]


def sound_file_stats(fn, sr=16000):
    y, _ = librosa.load(fn, sr=sr) # load first seconds
    cent = librosa.feature.spectral_centroid(y=y, sr=sr, center=False)
    avg_cent = np.mean(cent)

    rms_window = 1.0 # in seconds 
    rms = librosa.feature.rms(y=y, hop_length=int(sr*rms_window))
    rms_db = librosa.core.amplitude_to_db(rms, ref=0.0)
    avg_rms = np.mean(rms_db[0])

    return {
        'file': fn,
        'avg_freq': avg_cent,
        'avg_rms': avg_rms 
    }

if __name__=="__main__":
    # test_file = os.path.join("cache", "audio", "31166f35aa", "44.78.mp4")
    test_file = os.path.join("cache", "audio", "31166f35aa", "3.64.mp4")
    print(sound_file_stats(test_file))
    test_file = os.path.join("cache", "audio", "31166f35aa", "44.78.mp4")
    print(sound_file_stats(test_file))
    test_file = os.path.join("cache", "audio", "01effe63e9", "30.62.mp4")
    print(sound_file_stats(test_file))
    
