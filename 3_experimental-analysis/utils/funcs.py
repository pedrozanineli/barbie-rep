import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

from matplotlib import font_manager

font_path = '../Ruda/Ruda-VariableFont_wght.ttf'
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = prop.get_name()

def smooth(y):
    
    window_size = 11  # Tamanho da janela (deve ser um número ímpar)
    poly_order = 3    # Ordem do polinômio
    y_smooth = savgol_filter(y, window_size, poly_order)
    
    return y_smooth

def cdproc(index,caminho,water=False):
    
    for i in range(1,7):
        
        df = pd.read_csv(f'{caminho}/{index}_converted_{i}.txt',names=['WL','CD Abs'],sep=' ')

        if i == 1: cd_abs_actual = df['CD Abs']
        else: cd_abs_actual = np.add(np.array(df['CD Abs']),cd_abs_actual)
    
    cd_abs_actual = [x/6 for x in cd_abs_actual]
    cd_abs_actual = np.array(cd_abs_actual)

    if water:
        # Read Water Before!
        cd_abs_actual = np.subtract(cd_abs_actual,cd_abs_w[30:])

    avg = cd_abs_actual.mean()
    std = cd_abs_actual.std()
    normalized = (cd_abs_actual - avg) / std
    standard_error = std / np.sqrt(len(cd_abs_actual))

    # cd_abs_actual = normalized.copy()
    cd_abs_actual = smooth(cd_abs_actual)

    return np.array(df['WL']), cd_abs_actual, standard_error

# cd_plot(water)

def cdplot(wls,ramp_plot,l,c):

    plt.plot(wls,ramp_plot,label=l,color=c)

    plt.xlabel('Wavelength (nm)',fontsize=12),plt.ylabel('CD Absorbance (millidegrees)',fontsize=12)
    plt.legend(fontsize=12)    

def wlspectra(wl,wls,temperaturas,cd_abs,error):

    index = wls.index(wl)
    wl_cd = []

    for i in range(len(cd_abs)):
        wl_cd.append(cd_abs[i][index])

    plt.errorbar(temperaturas,wl_cd,yerr=error,capsize=3,fmt="r--o",color="#E0218A",ecolor = "black")
    plt.xlabel('Temperature ºC'),plt.ylabel('CD Abs')

def rampproc(caminho,temp_min,arqinicio,arqfim,water=False):
    
    actual_temp = temp_min
    wls,ramp_plot,temp,error = [],[],[],[]

    for i in range(arqinicio,arqfim):
        
        df = pd.read_csv(f'{caminho}/1_converted_{i}.txt',names=['WL','CD Abs'],sep=' ')

        if i % 6 == 0 and i != 1:
                        
            cd_abs_actual = [x/6 for x in cd_abs_actual]
            cd_abs_actual = np.array(cd_abs_actual)

            if water:
                # Read Water Before!
                cd_abs_actual = np.subtract(cd_abs_actual,cd_abs_w[30:])

            avg = cd_abs_actual.mean()
            std = cd_abs_actual.std()
            normalized = (cd_abs_actual - avg) / std
            standard_error = std / np.sqrt(len(cd_abs_actual))

            # cd_abs_actual = smooth(cd_abs_actual)
            # Descomentar para normalizar
            # cd_abs_actual = smooth(normalized)

            wls.append(list(df['WL']))
            temp.append(actual_temp)
            ramp_plot.append(cd_abs_actual)
            error.append(standard_error)

            actual_temp += 5

        if i % 6 == 0 or i == 1: cd_abs_actual = list(df['CD Abs'])
        else: cd_abs_actual = np.add(np.array(df['CD Abs']),cd_abs_actual)

    return wls[0], temp, np.array(ramp_plot), error

def rampplot(wls,temp,ramp_plot):

    X_b1, Y_b1 = np.meshgrid(wls, temp)
    Z_b1 = np.array([ramp_plot[i] for i in range(len(temp))])

    fig = plt.figure(figsize=(15,5))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(X_b1, Y_b1, Z_b1, cmap='viridis')

    ax.set_ylabel('Temp')

    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Temperature (ºC)')
    ax.set_zlabel('CD Absorbance (millidegrees)')

    ax.view_init(10,-30)

    plt.tight_layout()

    return ax

def pontualspectra(caminho,l,c):

    df = pd.read_csv(f'{caminho}',sep='\t',names=['Temperature','CD Absorbance'])
    plt.plot(df['Temperature'],df['CD Absorbance'],'-o',label=l,color=c)
