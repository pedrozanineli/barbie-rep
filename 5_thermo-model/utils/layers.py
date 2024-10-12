import time
import random
import numpy as np
import matplotlib.pyplot as plt


from matplotlib.colors import ListedColormap, BoundaryNorm

# colors = ['#EFB475', '#477081', '#AEC5FB', '#F77B7F']
# colors = ['#EFB475', '#F0F3FC', '#477081', '#F77B7F']

colors = ['#7DA6B7', '#EFB475', '#BCCAF2', '#F77B7F']

cmap = ListedColormap(colors)
bounds = [-1.5, -0.5, 0.5, 1.5, 2.5]
norm = BoundaryNorm(bounds, cmap.N, clip=True)

def layer_creation(dim, porosidade, diametro_max):

    matriz = np.zeros((dim, dim), dtype=int)    
    num_fibras = max(0, int((1 - porosidade) * dim))
    # num_fibras = max(0, int(porosidade * dim))
    count = 0

    if porosidade == 0: return -1*np.ones((dim, dim), dtype=int) 
    
    def adicionar_fibra(diametro):
        x, y = random.randint(0, dim-1), random.randint(0, dim-1)
        direcao = random.choice(['N', 'S', 'L', 'O'])
        
        for _ in range(random.randint(3*dim/4, dim)):
            for dx in range(-diametro//2, diametro//2 + 1):
                for dy in range(-diametro//2, diametro//2 + 1):
                    if 0 <= x + dx < dim and 0 <= y + dy < dim:
                        matriz[x + dx, y + dy] = -1
            
            if direcao == 'N':
                x = max(0, x - 1)
            elif direcao == 'S':
                x = min(dim-1, x + 1)
            elif direcao == 'L':
                y = min(dim-1, y + 1)
            elif direcao == 'O':
                y = max(0, y - 1)
            
            if random.random() < 0.1:
                direcao = random.choice(['N', 'S', 'L', 'O'])

    for i in range(1,num_fibras+1):
        # if count/(i*dim**2) <= porosidade:
        if list(matriz.flatten()).count(1)/(dim**2) < porosidade:
            diametro = random.randint(diametro_max//2, diametro_max)
            adicionar_fibra(diametro)
        else:
            break
    
    return matriz

def filter_creation(tamanho_rede, porosidade, camadas, diametro_fibra, concentracao_cbm, tamanho_cbm, CBM=True, display=False, B1=True):

    inicio = time.time()

    filtro = []
    for camada in range(camadas):

        rede = layer_creation(tamanho_rede,porosidade,diametro_fibra)

        if CBM:
            
            if B1: pbp=2
            else: pbp=3

            espaco_fibra = list(rede.flatten()).count(-1)
            proteinas = round(concentracao_cbm * espaco_fibra)

            for proteina in range(proteinas):
                
                while True:

                    posicao_prot_x,posicao_prot_y = np.random.randint(tamanho_rede),np.random.randint(tamanho_rede)

                    # Nao estamos considerando o possivel overlap de proteinas
                    # Adicionar isso no codigo

                    if rede[posicao_prot_x,posicao_prot_y] != 0 and int(posicao_prot_x+tamanho_cbm) < tamanho_rede and int(posicao_prot_y+tamanho_cbm) < tamanho_rede:

                        rede[posicao_prot_x:int(posicao_prot_x+tamanho_cbm),posicao_prot_y:int(posicao_prot_y+tamanho_cbm)] = pbp
                        break
    
        filtro.append(rede)

        if display:

            # if camada == 0:

            cax = plt.imshow(rede, cmap=cmap, norm=norm)
            plt.title(f'Layer {camada+1}',fontsize=16)
            cbar = plt.colorbar(cax, ticks=[-1,0,1,2])
            cbar.set_ticklabels(['Fiber', 'Pore', 'Microplastic', 'BARBIE1'])            

            plt.xticks([]),plt.yticks([])
            plt.tight_layout()

            # plt.savefig(f'results/filter/{porosidade}_filter_{camada+1}.png',transparent=True,dpi=500)

            plt.show()

    fim = time.time()
    print(f'Filtro criado, {round(fim-inicio,2)}')
    
    return filtro
