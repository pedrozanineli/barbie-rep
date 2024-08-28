import numpy as np
import matplotlib.pyplot as plt

def layers_creation(tamanho_rede=1000,porosidade=0.3,camadas=6,limite_tamanho_poro=100,CBM=True,concentracao_cbm=0.9,tamanho_cbm=4,display=True):

    filtro = []
    
    for camada in range(camadas):

        # gerar rede

        rede = np.zeros([tamanho_rede,tamanho_rede])

        # definir porosidade

        poros = round(porosidade * tamanho_rede)

        for poro in range(poros):

            # 2 alternativas:
            # 1. gerar tamanho aleatório do poro | colocar os poros na rede
            
            tamanho_poro = np.random.randint(1,limite_tamanho_poro)
            posicao_poro_x,posicao_poro_y = np.random.randint(tamanho_rede),np.random.randint(tamanho_rede)

            for i in range(tamanho_poro):
                for j in range(tamanho_poro):
                    
                    if posicao_poro_x+i < tamanho_rede and posicao_poro_y+j < tamanho_rede:
                        rede[posicao_poro_x+i,posicao_poro_y+j] = -1

            # 2. quantidade de cadeias que vamos colocar

        # insercao das proteínas CBM

        if CBM:
            
            # proteinas = round(concentracao_cbm * tamanho_rede)

            # Ao inves de calcular para a rede inteira
            # pode ser uma boa opcao calcular para os espacos livres

            espaco_fibra = list(rede.flatten()).count(0)
            proteinas = round(concentracao_cbm * espaco_fibra)

            for proteina in range(proteinas):
                
                while True:

                    posicao_prot_x,posicao_prot_y = np.random.randint(tamanho_rede),np.random.randint(tamanho_rede)

                    # Nao estamos considerando o possivel overlap de proteinas
                    # Adicionar isso no codigo

                    if rede[posicao_prot_x,posicao_prot_y] != -1 and int(posicao_prot_x+tamanho_cbm) < tamanho_rede and int(posicao_prot_y+tamanho_cbm) < tamanho_rede:

                        rede[posicao_prot_x:int(posicao_prot_x+tamanho_cbm),posicao_prot_y:int(posicao_prot_y+tamanho_cbm)] = 2
                        break

        # exibir rede

        if display:
            plt.imshow(rede,vmin=-1,vmax=2)
            plt.colorbar()
            plt.show()

        filtro.append(rede)

    return filtro