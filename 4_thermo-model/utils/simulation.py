import time
import numpy as np
import matplotlib.pyplot as plt

# Interaction Energy
# b1_ps = 0.454
# spid_ps = 4.9042

b1_ps = -0.53
spid_ps = -0.44

from matplotlib.colors import ListedColormap, BoundaryNorm

# colors = ['#EFB475', '#477081', '#AEC5FB', '#F77B7F']
# colors = ['#EFB475', '#F0F3FC', '#477081', '#F77B7F']

colors = ['#7DA6B7', '#EFB475', '#BCCAF2', '#F77B7F']

cmap = ListedColormap(colors)
bounds = [-1.5, -0.5, 0.5, 1.5, 2.5]
norm = BoundaryNorm(bounds, cmap.N)
cmap.set_bad(color='#477081')

def filtration_sim(filtro,mps_dic,tamanho_rede,display=True,deslocamento=False,prob=False):

    inicio = time.time()

    mps_retidos,retencao_camada = 0,[]

    if 2 in list(filtro[0].flatten()):
        CBM = True
    else:
        CBM = False

    T = 1
    kB = 1

    energias,probabilidade = [],[]

    for i,rede in enumerate(filtro):

        # energias,probabilidade = [],[]
        
        mps_retidos_camada = 0

        for mp_k in list(mps_dic.keys()):

            mp_tamanho,mp_posicao = mps_dic[mp_k]
            
            regiao_overlap = rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho]
            regiao_overlap_vizinhos = rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho]

            regiao_overlap = regiao_overlap.flatten()

            # fibra = -1 | vazio = 0 | cbm = 2

            fibra_count = list(regiao_overlap).count(-1)
            vazio_count = list(regiao_overlap).count(0)

            kB = 8.617333e-5
            T = 300
            beta = kB*T

            if CBM:
                cbm_count = list(regiao_overlap).count(2)

                energia = (fibra_count*spid_ps + cbm_count*b1_ps)/mp_tamanho
                p_reter = 1/(1 + np.exp(-2.5*(-energia - 2.5)))
                # p_reter = 1/(1 + np.exp(beta*(-energia)))
                
            else:

                energia = (fibra_count*spid_ps)/mp_tamanho
                p_reter = 1/(1 + np.exp(-2.5*(-energia - 2.5)))
                # p_reter = 1/(1 + np.exp(beta*(-energia)))

            if p_reter > np.random.random():
                
                # supondo que nao possa existir sobreposicao de MPs

                if list(rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho].flatten()).count(1) < 1 and list(rede[mp_posicao[1]:mp_posicao[1]+mp_tamanho].flatten()).count(1) < 1:

                    # rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho] = 1
                    rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho] = 1
                    
                    posx = mp_posicao[0]-1
                    posy = mp_posicao[1]-1

                    rede[posx:posx+mp_tamanho,posy] = -2
                    rede[posx+mp_tamanho,posy:posy+mp_tamanho] = -2
                    rede[posx:posx+mp_tamanho,posy+mp_tamanho] = -2
                    rede[posx,posy:posy+mp_tamanho] = -2

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
            cbar = plt.colorbar(cax, ticks=[-1,0,1,2])
            cbar.set_ticklabels(['Fiber', 'Pore', 'Microplastic', 'BARBIE1'])
            
            plt.title(f'Layer {i+1} - retained: {mps_retidos_camada}')

            plt.xticks([])
            plt.yticks([])

            plt.tight_layout()
            # plt.savefig(f'results/simulation/sim_{i+1}.png',transparent=True,dpi=500)
            
            plt.show()

    if prob:
        plt.hist(energias,density=True,color='#477081',bins=20)
        plt.xlabel('Energy (eV)',fontsize=14)
        plt.ylabel('Count',fontsize=14)
        
        plt.grid(),plt.tight_layout()
        
        # plt.savefig('results/energies_dist.png',transparent=True,dpi=500)
        plt.show()

    fim = time.time()
    print(f'Simulação finalizada, {round(fim-inicio,2)}')

    return mps_retidos,retencao_camada