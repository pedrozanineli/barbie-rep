import numpy as np
import matplotlib.pyplot as plt

# Interaction Energy
# b1_ps = 0.454
# spid_ps = 4.9042

b1_ps = -24.05
spid_ps = -0.05

def filtration_sim(filtro,mps_dic,tamanho_rede,display=True,deslocamento=False,prob=False):

    mps_retidos,retencao_camada = 0,[]

    if 2 in list(filtro[0].flatten()):
        CBM = True
    else:
        CBM = False

    T = 1
    kB = 1

    energias,probabilidade = [],[]

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
                p_reter = 1/(1 + np.exp(-0.1*(-energia - 10)))
                
            else:
                # p_reter = (spid_ps*fibra_count - vazio_count)/mp_tamanho

                energia = fibra_count*spid_ps
                p_reter = 1/(1 + np.exp(-0.1*(-energia - 10)))

            # if p_reter > vazio_count*np.random.random():
            if p_reter > np.random.random():
                
                rede[mp_posicao[0]:mp_posicao[0]+mp_tamanho,mp_posicao[1]:mp_posicao[1]+mp_tamanho] = 1
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
                probabilidade.append(probabilidade)

        if i != 0:
            retencao_camada.append(retencao_camada[i-1]+mps_retidos_camada)
        else:
            retencao_camada.append(mps_retidos_camada)

        if prob: plt.scatter(energia,probabilidade,color='royalblue') ; plt.show()

        if display:
            plt.imshow(rede,vmin=-1,vmax=2)
            plt.title(f'Camada {i+1} - retidos: {mps_retidos_camada}, passaram: {len(mps_dic)}')
            plt.colorbar()
            plt.show()

    return mps_retidos,retencao_camada