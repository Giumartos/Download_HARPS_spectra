import eso_down
from eso_down.search import ESOquery
eq = ESOquery()
import numpy as np
import os
from timeit import default_timer as timer

def calcula_SNR_nspec(files):
    '''
    Calcula o SNR total atingido e o número de espectros necessários
    para atingir esse valor. Caso atinja SNR = 1000 (objetivo), para 
    a execução.

    files: tabela Astropy com os espectros e seus dados 
    '''

    # counts = SNR²
    counts, nspec = 0, 0

    # soma SNR² até atingir counts = 10⁶ , que é SNR = 10³
    while counts < 10**6:
        counts += files['SNR (spectra)'][nspec]**2 
        nspec += 1 # numero de espectros considerados para atingir o SNR
        
        if nspec == len(files): # se rodou todos espectros e não atingiu 1000
            break
            
    SNR_total = np.sqrt(counts)

    return SNR_total, nspec


def busca_espectros_before(name_star):

    '''
    Espectros antes do upgrade do HARPS.

    Dado o nome da estrela, busca informações dela no Simbad e depois
    procura os arquivos de espectro dela na Phase 3 da base de dados 
    do ESO. Pode mudar SNRmin e SNRmax, assim como outros dados (ver
    códigos originais na pasta "eso_down").

    Retorna astropy Table com os arquivos dos espectros antes do 
    upgrade do HARPS e suas informações, como data e SNR.

    files_before: astropy table com a lista de arquivos e dados dos espectros
    '''
    # tabela com infos de todos espectros da estrela com SNRmin e SNRmax definidos, antes do upgrade do HARPS
    files_before = eq.searchStarbef(name_star, instrument = 'HARPS', SNRmin = 40, SNRmax = 500)

    # ordenando a tabela pelo SNR, para as datas ficarem misturadas
    files_before.sort('SNR (spectra)', reverse=True)

    return files_before


def busca_espectros_after(name_star):

    '''
    Espectros depois do upgrade do HARPS.
    
    Dado o nome da estrela, busca informações dela no Simbad e depois
    procura os arquivos de espectro dela na Phase 3 da base de dados 
    do ESO. Pode mudar SNRmin e SNRmax, assim como outros dados (ver
    códigos originais na pasta "eso_down").

    Retorna astropy Table com os arquivos dos espectros depois do 
    upgrade do HARPS e suas informações, como data e SNR.

    files_after: astropy table com a lista de arquivos e dados dos espectros
    '''
    # tabela com infos de todos espectros da estrela com SNRmin e SNRmax definidos, antes do upgrade do HARPS
    files_after = eq.searchStaraft(name_star, instrument = 'HARPS', SNRmin = 40, SNRmax = 500)

    # ordenando a tabela pelo SNR, para as datas ficarem misturadas
    files_after.sort('SNR (spectra)', reverse=True)

    return files_after


def download_spectra(files, nspec, path):  
    
    '''
    files: astropy table com todos os arquivos de espectro
    nspec: numero de arquivos para baixar
    path: pasta para baixar os espectros
    '''
    
    eq.ANCILLARYdown(arq = files[:nspec], downloadPath = path)


def get_info (files, nspec):

    '''
    Obtem as datas e o SNR de cada espectro baixado

    files: astropy table com todos os arquivos
    nspec: numero de espectros baixados
    '''

    dates, SNRs = [], []

    for f in files[:nspec]:
        dates.append(f['Date Obs'])
        SNRs.append(f['SNR (spectra)'])

    return np.array(dates), np.array(SNRs)



def write_out_file(out_file_name, SNR_total, nspec, dates, SNRs):

    '''
    Escreve arquivo de saida com SNRtotal, quantidade de espectros baixados, 
    data e SNR de cada espectro
    '''

    # remove o arquivo anterior se já existia
    if os.path.exists(out_file_name):
        os.remove(out_file_name)

    head = "SNRtotal = {:.2f}\n{} spectra downloaded\nDates   SNR".format(SNR_total, nspec)
    np.savetxt(out_file_name, np.array([dates, SNRs]).T, header = head, delimiter='   ', fmt = '%s')


def baixar_antes(parent_path, star, SNR_before, nspec_before, files_before):

    '''
    Baixa apenas os espectros antes do upgrade do HARPS

    parent_path: pasta raiz para baixar os espectros
    star: nome da estrela
    '''

    # cria pasta para colocar espectros antes do upgrade do HARPS
    path_before = os.path.join(parent_path, star, "Before")
    os.makedirs(path_before, exist_ok=True) 

    print("SNR atingido: {:.2f}\nNúmero de espectros: {}".format(SNR_before, nspec_before))

    print("\nIniciando download dos espectros ANTES")
    download_spectra(files_before, nspec_before, path_before)

    # obtendo SNRs e datas dos espectros baixados
    dates_before, SNRs_before = get_info(files_before, nspec_before)
    
    # salvando data e SNR de cada espectro baixado

    # nome dos arquivos 
    out_file_before = path_before + '/info_spectra.txt'

    # salvando
    write_out_file(out_file_before, SNR_before, nspec_before, dates_before, SNRs_before)



def baixar_depois(parent_path, star, SNR_after, nspec_after, files_after):

    '''
    Baixa apenas os espectros depois do upgrade do HARPS

    parent_path: pasta raiz para baixar os espectros
    star: nome da estrela
    '''

    # cria pasta para colocar espectros antes do upgrade do HARPS
    path_after = os.path.join(parent_path, star, "After")
    os.makedirs(path_after, exist_ok=True) 

    print("SNR atingido: {:.2f}\nNúmero de espectros: {}".format(SNR_after, nspec_after))

    print("\nIniciando download dos espectros DEPOIS")
    download_spectra(files_after, nspec_after, path_after)

    # obtendo SNRs e datas dos espectros baixados
    dates_after, SNRs_after = get_info(files_after, nspec_after)
    
    # salvando data e SNR de cada espectro baixado

    # nome dos arquivos 
    out_file_after = path_after + '/info_spectra.txt'

    # salvando
    write_out_file(out_file_after, SNR_after, nspec_after, dates_after, SNRs_after)


def main():

    stars_problems = ['HIP3311', 'HIP96160']

    star_names = []

    amostra = np.loadtxt("amostra_Giulia.csv", delimiter=',',dtype="str", unpack=True, skiprows=1)

    for s in amostra[0][79:]:
        s = "HIP" + s
        star_names.append(s) # 91 estrelas

    # raiz da pasta para salvar os espectros das estrelas
    parent_path = '/home/giumartos/Desktop/Espectros'

    for star in star_names:

        print("\n*** {} ***\n".format(star))

        # buscando espectros antes e depois do upgrade do HARPS
        files_before = busca_espectros_before(star)
        files_after = busca_espectros_after(star)

        # se nao tiver espectros ANTES, baixo apenas os DEPOIS, e vice-versa

        if len(files_after) == 0:

            # calculando SNR e numero de espectros a baixar
            SNR_before, nspec_before = calcula_SNR_nspec(files_before)
            print("\nBaixando apenas espectros ANTES do upgrade\n")
            baixar_antes(parent_path, star, SNR_before, nspec_before, files_before)

        elif len(files_before) == 0:

            # calculando SNR e numero de espectros a baixar
            SNR_after, nspec_after = calcula_SNR_nspec(files_after)
            print("\nBaixando apenas espectros DEPOIS do upgrade\n")
            baixar_depois(parent_path, star, SNR_after, nspec_after, files_after)


        # se tiver espectros ANTES E DEPOIS, verifico se tem SNR > 400 em ambos os casos
        # se ambos forem SNR < 400, baixo ANTES E DEPOIS
        # se algum for SNR > 400, baixo apenas ele

        else:
            # calculando SNR e numero de espectros a baixar
            SNR_before, nspec_before = calcula_SNR_nspec(files_before)
            SNR_after, nspec_after = calcula_SNR_nspec(files_after)

            # se espectros ANTES ou DEPOIS atingiram SNR = 400, baixo so eles. Se não, baixo antes E depois
            if SNR_before >= 400:
                # baixo o que tiver SNR maior
                if SNR_before > SNR_after:
                    print("\nBaixando apenas espectros ANTES do upgrade\n")
                    baixar_antes(parent_path, star, SNR_before, nspec_before, files_before)
                else:
                    print("\nBaixando apenas espectros DEPOIS do upgrade\n")
                    baixar_depois(parent_path, star, SNR_after, nspec_after, files_after)
             
            elif SNR_after >= 400:
                print("\nBaixando apenas espectros DEPOIS do upgrade\n")
                baixar_depois(parent_path, star, SNR_after, nspec_after, files_after)

            else:
                print("Baixando espectros ANTES e DEPOIS do upgrade")
                baixar_antes(parent_path, star, SNR_before, nspec_before, files_before)
                baixar_depois(parent_path, star, SNR_after, nspec_after, files_after)

        # para apitar quando acabar cada estrela
        duration = 0.4 #sec
        freq = 600 #Hz
        os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))

    print("FINALIZADA")


main()