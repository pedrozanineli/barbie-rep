import time
import numpy as np

def mps_creation(qnt_mps = 1000,tamanho_limite_mp = 100,tamanho_rede=1000):

    inicio = time.time()
    mps_dic = {}

    # gerar microplasticos

    for mp in range(qnt_mps):

        while True:

            tamanho_mp = np.random.randint(5,tamanho_limite_mp)
            posicao_mp_x,posicao_mp_y = np.random.randint(tamanho_rede),np.random.randint(tamanho_rede)
            
            while posicao_mp_x+tamanho_mp > tamanho_rede or posicao_mp_y+tamanho_mp > tamanho_rede:
                    posicao_mp_x,posicao_mp_y = np.random.randint(tamanho_rede),np.random.randint(tamanho_rede)

            if len(mps_dic) == 0: break

            for mp_k,mp_v in mps_dic.items():

                tamanho_mp_comp,posicao_mp_comp = mp_v

                # Calculando o overlap de dois microplasticos como quadrados

                x1_min, x1_max = posicao_mp_x, posicao_mp_x + tamanho_mp
                y1_min, y1_max = posicao_mp_y, posicao_mp_y + tamanho_mp
                
                x2_min, x2_max = posicao_mp_comp[0], posicao_mp_comp[0] + tamanho_mp_comp
                y2_min, y2_max = posicao_mp_comp[1], posicao_mp_comp[1] + tamanho_mp_comp
                
                overlap_x = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
                overlap_y = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
                
                overlap_area = overlap_x * overlap_y

                if overlap_area > 0: break
            
            if overlap_area == 0: break

        mps_dic.update({mp:[tamanho_mp,[posicao_mp_x,posicao_mp_y]]})

    fim = time.time()
    print(f'MPs criados, {round(fim-inicio,2)}')
    
    return mps_dic