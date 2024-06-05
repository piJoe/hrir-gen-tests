import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

def generate_hrir(angle, signal, head_size, dampening, sample_rate=48000, sound_speed=343):
    # Calculate ITD
    sin_angle = np.sin(np.radians(angle))
    ITD = np.abs((head_size / sound_speed) * sin_angle)
    ILD = np.abs((head_size * dampening) * sin_angle)
    
    # Convert ITD to sample delay
    sample_delay = int(np.round(ITD * sample_rate))
    
    # Generate impulse responses
    impulse_length = 512  # HeSuVi typically uses 512-sample HRIRs
    h_L = np.zeros(impulse_length)
    h_R = np.zeros(impulse_length)

    signal_calc = min(signal - ILD, signal)
    
    # Ensure we don't exceed the impulse length
    if sample_delay < impulse_length:
        if sin_angle < 0:
            h_R[0] = signal  # Delta function for left ear (no delay)
            h_L[sample_delay] = signal_calc  # Delta function for right ear (with delay)
        else:
            h_L[0] = signal  # Delta function for left ear (no delay)
            h_R[sample_delay] = signal_calc  # Delta function for right ear (with delay)
    else:
        print("Sample delay exceeds impulse length, adjust parameters.")
        return None, None
    
    return h_L, h_R

def save_hrir_as_wav(h_L, h_R, filename, sample_rate=48000):
    # Combine into stereo format
    hrir_stereo = np.vstack((h_L, h_R)).T
    
    # Save as WAV file
    write(filename, sample_rate, hrir_stereo.astype(np.float32))

def combine_hrirs(hrirs):
    return np.column_stack(hrirs)

def save_hrirs_as_wav(hrirs, filename, sample_rate=48000):
    write(filename, sample_rate, hrirs.astype(np.float32))

# Parameters
signal = 0.85     # signal value for the impulse (normally 1, experiment with less)
angle = [-30,30]  # Angle in degrees
head_size = 0.15  # head size in meters (distance between ears)
dampening = 2     # pseudo value for dampening sound between left and right ear (4 seems to be a good starting point)

hrirs = []
for a in angle:
    # Generate HRIRs
    h_L, h_R = generate_hrir(a, signal, head_size, dampening)
    if h_L is not None and h_R is not None:
        save_hrir_as_wav(h_L, h_R, 'hrir.{0}.{1}.wav'.format(head_size, a))    
        hrirs.append(h_L)
        hrirs.append(h_R)

if hrirs:
    combined_hrirs = combine_hrirs(hrirs)
    save_hrirs_as_wav(combined_hrirs, 'combined.{0}.hrir.wav'.format(head_size))

# # Check if HRIRs are generated correctly
# if h_L is not None and h_R is not None:
#     # Save HRIRs as WAV file
#     save_hrir_as_wav(h_L, h_R, 'hrir_angle_{0}.wav'.format(a))
    
#     # # Plot the HRIRs
#     # plt.figure(figsize=(10, 5))
#     # plt.subplot(2, 1, 1)
#     # plt.stem(h_L)
#     # plt.title('Left Ear HRIR')
#     # plt.subplot(2, 1, 2)
#     # plt.stem(h_R)
#     # plt.title('Right Ear HRIR')
#     # plt.tight_layout()
#     # plt.show()
# else:
#     print("Failed to generate HRIRs.")
