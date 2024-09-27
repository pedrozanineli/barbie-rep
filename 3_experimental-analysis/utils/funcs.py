import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit
from matplotlib import gridspec

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
    
    count = 0
    for i in range(1,7):
        
        if os.path.isfile(f'{caminho}/{index}_converted_{i}.txt'):
            df = pd.read_csv(f'{caminho}/{index}_converted_{i}.txt',names=['WL','CD Abs'],sep=' ')
            count+=1
        
        if i == 1: cd_abs_actual = df['CD Abs']
        else: cd_abs_actual = np.add(np.array(df['CD Abs']),cd_abs_actual)
    
    cd_abs_actual = [x/count for x in cd_abs_actual]
    cd_abs_actual = np.array(cd_abs_actual)

    if water:

        wl_water, abs_water, se_water = cdproc(3,'CD_data/water_data')

        if len(list((df['WL']))) > len(wl_water):
            cd_abs_actual = cd_abs_actual[list(df['WL']).index(251):list(df['WL']).index(190)]

        cd_abs_actual = np.subtract(cd_abs_actual,abs_water)

    avg = cd_abs_actual.mean()
    std = cd_abs_actual.std()
    normalized = (cd_abs_actual - avg) / std
    standard_error = std / np.sqrt(len(cd_abs_actual))

    cd_abs_actual = normalized.copy()
    cd_abs_actual = smooth(cd_abs_actual)

    # return np.array(df['WL']), cd_abs_actual, standard_error

    if water:
        return list(range(190,251))[::-1], cd_abs_actual, standard_error
    else:
        return np.array(df['WL']), cd_abs_actual, standard_error

# cd_plot(water)

def cdplot(wls,ramp_plot,l,c):

    plt.plot(wls,ramp_plot,label=l,color=c)

    plt.xlabel('Wavelength (nm)',fontsize=14),plt.ylabel('CD Absorbance (millidegrees)',fontsize=14)
    plt.legend(fontsize=12)    

def rampproc(caminho,temp_min,arqinicio,arqfim,water=False,index=1,cold=False):
    
    actual_temp = temp_min
    wls,ramp_plot,temp,error = [],[],[],[]
    count=0

    for i in range(arqinicio,arqfim):
        
        df = pd.read_csv(f'{caminho}/{index}_converted_{i}.txt',names=['WL','CD Abs'],sep=' ')
        count+=1

        if i % 6 == 0 and i != arqinicio:
            
            cd_abs_actual = [x/count for x in cd_abs_actual]
            cd_abs_actual = cd_abs_actual[list(df['WL']).index(250):list(df['WL']).index(200)]
            cd_abs_actual = np.array(cd_abs_actual)

            if water:
                # Read Water Before!
                cd_abs_actual = np.subtract(cd_abs_actual,cd_abs_w[30:])

            avg = cd_abs_actual.mean()
            std = cd_abs_actual.std()
            normalized = (cd_abs_actual - avg) / std
            standard_error = std / np.sqrt(len(cd_abs_actual))

            # Descomentar para normalizar
            # cd_abs_actual = smooth(normalized)
            cd_abs_actual = smooth(cd_abs_actual)

            wls.append(list(df['WL']))
            temp.append(actual_temp)
            ramp_plot.append(cd_abs_actual)
            error.append(standard_error)

            if cold: actual_temp -= 5
            else: actual_temp += 5

        if i % 6 == 0 or i == arqinicio: cd_abs_actual = list(df['CD Abs'])
        else: cd_abs_actual = np.add(np.array(df['CD Abs']),cd_abs_actual)

    return wls[0], temp, np.array(ramp_plot), error

def boltzmann(x, A1, A2, x0, dx):
    return A2 + (A1 - A2) / (1 + np.exp((x - x0) / dx))

def wlspectra(wl,wls,temperaturas,cd_abs,error,TM=False,c='#E0218A'):

    index = wls.index(wl)
    wl_cd = []

    for i in range(len(cd_abs)):
        wl_cd.append(cd_abs[i][index])

    plt.errorbar(temperaturas,wl_cd,yerr=error,capsize=3,fmt="r--o",color=c,ecolor = "black")
    plt.xlabel('Temperature ºC'),plt.ylabel('CD Abs')

    if TM:
        popt, pcov = curve_fit(boltzmann, temperaturas, wl_cd, p0=[0, 10, 30, 10])
        plt.plot(range(20,100), boltzmann(range(20,100), *popt), color='gray', linestyle='--', label=f'TM = {round(popt[2],2)}ºC')
        plt.legend()
        print(popt)

def rampplot(wls,temp,ramp_plot):

    from scipy import interpolate

    min_temp,max_temp = min(temp),max(temp)
    wls = wls[wls.index(250):wls.index(200)]
    # wls = wls[wls.index(250):wls.index(190)]

    X_b1, Y_b1 = np.meshgrid(wls, temp)
    Z_b1 = np.array([ramp_plot[i] for i in range(len(temp))])

    Q1 = np.percentile(Z_b1, 25, axis=None)
    Q3 = np.percentile(Z_b1, 75, axis=None)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers_mask = (Z_b1 < lower_bound) | (Z_b1 > upper_bound)

    Z_b1_cleaned = Z_b1.copy()
    Z_b1_cleaned[outliers_mask] = np.nan

    X_valid = X_b1[~outliers_mask]
    Y_valid = Y_b1[~outliers_mask]
    Z_valid = Z_b1_cleaned[~outliers_mask]

    interp_func = interpolate.griddata((X_valid, Y_valid), Z_valid, (X_b1, Y_b1), method='linear')

    Z_b1 = np.where(outliers_mask, interp_func, Z_b1)

    fig = plt.figure(figsize=(15,10))
    ax = fig.add_subplot(111, projection='3d')

    im = ax.plot_surface(X_b1, Y_b1, Z_b1, cmap='viridis')

    ax.set_xlabel('\nWavelength (nm)\n',fontsize=18)
    ax.set_ylabel('Temperature (ºC)',fontsize=18)
    # ax.set_zlabel('CD Absorbance (millidegrees)',fontsize=14)

    # ax.set_xlim(min(X_b1),max(X_b1))
    ax.set_ylim(min_temp,max_temp)

    cbar = fig.colorbar(im,shrink=0.5,pad=0.01,orientation='horizontal')
    cbar.set_label('CD Absorbance (millidegrees)', fontsize=18)
    cbar.ax.tick_params(labelsize=12)

    plt.tight_layout()

    return ax

def rampplot2D(wls,temp,ramp_plot):

    wls = wls[wls.index(250):wls.index(200)]

    X_b1, Y_b1 = np.meshgrid(wls, temp)
    
    min_value = np.min(ramp_plot)
    max_value = np.max(ramp_plot)
    ramp_plot = (ramp_plot - min_value) / (max_value - min_value)

    sc = plt.pcolormesh(X_b1,Y_b1,ramp_plot,cmap='viridis',shading='auto')
    
    plt.xlabel('Wavelength (nm)',fontsize=14)
    plt.ylabel('Temperature (ºC)',fontsize=14)

    # cb = plt.colorbar(sc)
    # cb.set_label('CD Absorbance (millidegrees)', fontsize=14)

    return sc

def pontualspectra(caminho,l,c):

    df = pd.read_csv(f'{caminho}',sep='\t',names=['Temperature','CD Absorbance'])

    temp, cdabs = df['Temperature'],df['CD Absorbance']

    # cdabs = (cdabs - min(cdabs)) / (max(cdabs) - min(cdabs))
    # cdabs = smooth(cdabs)

    plt.plot(temp, cdabs,'-o',label=l,color=c,markersize=4)

def ramp2d(cd_abs_1,cd_abs_2,wls_1,wls_2,temp_1,temp_2,min_temp=25,max_temp=60):

    def proc(wls, temp, ramp_plot, min_val, max_val):
        # Garantir que wls e temp tenham o mesmo comprimento
        wls = wls[wls.index(250):wls.index(200)]  # Exemplo de filtragem, ajuste conforme necessário
        X, Y = np.meshgrid(wls, temp)
        
        # Normalização usando os valores globais
        # ramp_plot = (ramp_plot - min_val) / (max_val - min_val)

        return X, Y, ramp_plot

    combined_data = np.concatenate((cd_abs_1.flatten(),cd_abs_2.flatten()))

    min_value = np.min(combined_data)
    max_value = np.max(combined_data)

    fig = plt.figure(figsize=(10, 5))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 0.05])

    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])
    cax = plt.subplot(gs[2])

    xb1, yb1, zb1 = proc(wls_1, temp_1, cd_abs_1, min_value, max_value)
    xcbm, ycbm, zcbm = proc(wls_2, temp_2, cd_abs_2, min_value, max_value)

    vmin = min(zcbm.min(), zb1.min())
    vmax = max(zcbm.max(), zb1.max())

    sc1 = ax1.pcolormesh(yb1, xb1, zb1, cmap='viridis', shading='auto', vmin=vmin, vmax=vmax)
    ax1.set_title('Heating Ramp',fontsize=16,loc='left')
    ax2.set_xlim(min_temp,max_temp)
    ax1.set_ylabel('Wavelength (nm)', fontsize=14)
    ax1.set_xlabel('Temperature (ºC)', fontsize=14)

    sc2 = ax2.pcolormesh(ycbm, xcbm[::-1], zcbm[::-1], cmap='viridis', shading='auto', vmin=vmin, vmax=vmax)
    ax2.set_title('Cooling Ramp',fontsize=16,loc='left')
    ax2.set_xlim(max_temp,min_temp)
    ax2.set_xlabel('Temperature ºC', fontsize=14)
    ax2.set_yticks([])

    cb = fig.colorbar(sc1, cax=cax, orientation='vertical')
    cb.set_label('\nCD Absorbance (millidegrees)', fontsize=14)
