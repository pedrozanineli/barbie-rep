import numpy as np
import matplotlib.pyplot as plt

# Interaction Energy
# b1_ps = 0.454
# spid_ps = 4.9042

b1_ps = 20
spid_ps = 1

def filtration_sim(filtro,mps_dic,display=True):

    mps_retidos,retencao_camada = 0,[]

    if 2 in list(filtro[0].flatten()):
        CBM = True
    else:
        CBM = False

    for i,rede in enumerate(filtro):
        
        mps_retidos_camada = 0

        for mp_k in list(mps_dic.keys()):

            mp_tamanho,mp_posicao = mps_dic[mp_k]
            
            # se o mp estiver em cima de cbm, calcular overlap
            # se nao, P = 0

            regiao_overlap = rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho]
            regiao_overlap_vizinhos = rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho]

            regiao_overlap = regiao_overlap.flatten()

            # fibra = -1 | vazio = 0 | cbm = 2

            fibra_count = list(regiao_overlap).count(0)
            vazio_count = list(regiao_overlap).count(-1)

            # calculo da propriedade por meio da energia de interacao e distancia
            # considerar energia on-site + 1os vizinhos
            
            # B1-PS # 0.454 eV - Coulomb # -6.7572 eV - LJ
            # CBM-Spid # -40.6812 eV - Coulomb # -11.6706 eV - LJ
            # Spid-PS # 4.9042 eV - Coulomb # -0.8546 eV - LJ
            
            if CBM:
                cbm_count = list(regiao_overlap).count(2)
                energia = fibra_count*spid_ps + cbm_count*b1_ps
                
                # p_reter = ((spid_ps*fibra_count+b1_ps*cbm_count) - vazio_count)/mp_tamanho
                
                T = 1
                kB = 1

                beta = 1/kB*T
                p_reter = 1 - abs(np.exp(-beta*(spid_ps*fibra_count+cbm_count*b1_ps)/mp_tamanho))

            else:
                # p_reter = (spid_ps*fibra_count - vazio_count)/mp_tamanho

                T = 1
                kB = 1

                beta = 1/kB*T
                p_reter = 1 - abs(np.exp(-beta*(spid_ps*fibra_count)/mp_tamanho))

            if p_reter > (vazio_count/mp_tamanho)*np.random.random():
                
                rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho] = 1
                mps_retidos += 1
                mps_retidos_camada += 1
                del mps_dic[mp_k]

        retencao_camada.append(mps_retidos_camada)

        if display:
            plt.imshow(rede,vmin=-1,vmax=2)
            plt.title(f'Camada {i+1} - retidos: {mps_retidos_camada}, passaram: {len(mps_dic)}')
            plt.colorbar()
            plt.show()

    return mps_retidos,retencao_camada