import time
import numpy as np
import matplotlib.pyplot as plt

vazao = 1e-8 # m^3/s

densidade = 15 # kg/m^3 # considerando isopor
potencial_quimico = 2.6e20 # eV/m^3 # 2.6e-7 eV/nm^3

b1_ps = -0.58 # eV
cbm_ps = -0.44 # eV
spid_ps = -0.46/2 # eV

# area de contato em meV/Ang^2
# b1_ps = -0.71
# spid_ps = -1,1

kB = 8.617333e-5
T = 297.15
beta = kB*T

from matplotlib.colors import ListedColormap, BoundaryNorm

colors = ['#7DA6B7', '#EFB475', '#BCCAF2', '#F77B7F']

cmap = ListedColormap(colors)
bounds = [-1.5, -0.5, 0.5, 1.5, 2.5]
norm = BoundaryNorm(bounds, cmap.N)
cmap.set_bad(color='#acbdef')

def pot_quimico_mp(mp_tamanho,tamanho_rede):
    
    mp_volume = mp_tamanho**3*1e-27
    mp_pot_quimico = potencial_quimico*mp_volume # eV

    area = (tamanho_rede**2)*10e-18
    velocidade = vazao/area
    massa = densidade*mp_volume

    e_cin = (massa*velocidade)/2

    return mp_pot_quimico + (e_cin/1.602e-19)

def filtration_sim(filtro,mps_dic,tamanho_rede,display=True,deslocamento=False,prob=False):

    inicio = time.time()

    mps_retidos,retencao_camada = 0,[]
    b1=True

    if 2 in list(filtro[0].flatten()):
        CBM = True
    else:
        if 3 in list(filtro[0].flatten()): b1=False
        else: CBM = False

    energias,probabilidade = [],[]

    for i,rede in enumerate(filtro):

        # energias,probabilidade = [],[]
        
        mps_retidos_camada = 0

        for mp_k in list(mps_dic.keys()):

            mp_tamanho,mp_posicao = mps_dic[mp_k]
            
            e_free = pot_quimico_mp(100,1000)
            
            regiao_overlap = rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho]
            regiao_overlap_vizinhos = rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho]

            regiao_overlap = regiao_overlap.flatten()

            # fibra = -1 | vazio = 0 | cbm = 2

            fibra_count = list(regiao_overlap).count(-1)
            vazio_count = list(regiao_overlap).count(0)

            if CBM:

                if b1: cbm_count = list(regiao_overlap).count(2)
                else: cbm_count = list(regiao_overlap).count(3)

                if not b1: energia = (fibra_count*spid_ps + cbm_count*cbm_ps)
                else: energia = (fibra_count*spid_ps + cbm_count*b1_ps)
                                
            else:

                energia = (fibra_count*spid_ps)
            
            # p_reter = 1/(1 + np.exp(-2.5*(-energia - 2.5)))
            p_reter = 1/(1 + np.exp(-beta*(-e_free - energia)))
            rv = np.random.random()

            if p_reter > rv and energia != 0:

                overlap_max = (mp_tamanho**2)*0.1
                
                if list(regiao_overlap.flatten()).count(1) < overlap_max:

                    rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho] = 1
                    
                    posx = mp_posicao[0]
                    posy = mp_posicao[1]

                    rede[posx:posx+mp_tamanho-1,posy] = -2
                    rede[posx+mp_tamanho-1,posy:posy+mp_tamanho] = -2
                    rede[posx:posx+mp_tamanho-1,posy+mp_tamanho-1] = -2
                    rede[posx,posy:posy+mp_tamanho-1] = -2

                    mps_retidos += 1
                    mps_retidos_camada += 1
                    del mps_dic[mp_k]

            else:
                if deslocamento:

                    mp_posicao_x,mp_posicao_y = mp_posicao

                    while True:

                        deslocamento_x = T*np.random.random()
                        deslocamento_y = T*np.random.random()

                        if mp_posicao_x+deslocamento_x+mp_tamanho <= tamanho_rede or mp_posicao_y+deslocamento_y+mp_tamanho <= tamanho_rede:
                            mps_dic[mp_k] = [mp_tamanho,[mp_posicao_x+deslocamento_x,mp_posicao_y+deslocamento_y]]
                            break

            if prob:
                # energias.append(energia)
                energias.append(energia)
                probabilidade.append(p_reter)

        if i != 0:
            retencao_camada.append(retencao_camada[i-1]+mps_retidos_camada)
        else:
            retencao_camada.append(mps_retidos_camada)

        if display:

            # plt.imshow(rede,cmap='plasma')
            # plt.title(f'Camada {i+1} - retidos: {mps_retidos_camada}, passaram: {len(mps_dic)}')
            
            rede = np.where(rede == -2, np.nan, rede)

            cax = plt.imshow(rede, cmap=cmap, norm=norm)
            # cbar = plt.colorbar(cax, ticks=[-1,0,1,2])
            # cbar.set_ticklabels(['Fiber', 'Pore', 'Microplastic', 'BARBIE1'])
            
            # plt.title(f'Layer {i+1} - retained: {mps_retidos_camada}')

            plt.xticks([])
            plt.yticks([])

            plt.tight_layout()
            # plt.savefig(f'results/simulation/por_sim_{i}.png',transparent=True,dpi=700)
            
            plt.show()

    if prob:

        plt.figure(figsize=(7,4))
        
        plt.subplot(121)
        plt.hist(energias,density=True,color='#477081',bins=20)
        plt.xlabel('Energy (eV)',fontsize=14)
        plt.ylabel('Count',fontsize=14)        
        # plt.grid()
        
        plt.subplot(122)
        plt.scatter(energias,probabilidade,color='#477081')
        plt.xlabel('Energy (eV)',fontsize=14)
        plt.ylabel('Retention Probability',fontsize=14)
        
        plt.xlim(min(energias),max(energias))
        plt.tight_layout()
        # plt.savefig('results/energies_dist.svg',transparent=True,dpi=700)
        plt.show()

    fim = time.time()
    print(f'Simulação finalizada, {round(fim-inicio,2)}')

    return mps_retidos,retencao_camada