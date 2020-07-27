#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''# -*- coding: latin-1 -*-'''

'''
GRCN is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
#
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
#
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''

import os
import sys
import time
import ipaddress

__author__ = 'Beiriz'
__version__= 3.001
__datebegin__= "27/07/2020"
__com1__ = "add rule ip nat"

#-----------------------------------------------------------------------
fazer_regras_in = False #Este valor deve ser alterado para True caso haja interesse de gerar também as regras de CGNAT no sentido IN: 'fazer_regras_in = True'. OBS: CGNAT do tipo OUT sempre serão geradas.
indice = 0
txt_publico = ""
txt_privado = ""
masc_subrede_privada = 0 #mascara da subrede de IPs privados que serão atendidos por 1 IP público
qt_ips_publicos = 0 #Quantidade de IPs públicos na rede informada
qt_ips_privados = 0 #Quantidade de IPs privados na rede informada
qt_ips_privados_por_ip_publico = 0 #Quantos IPs privados vão sair por um único IP público ( A relação PRI/PUB)
qt_portas_por_ip = 0 #quantidade de portas que serão reservadas por IP privado.
#As 2 confs abaixo trabalham em conjunto para ajustar o range total de portas de cada IP público
numero_porta_incial = 1 #É a menor porta do IP público que será dividido entre seus IPs privados
numero_porta_final = 65535 #É a maior porta do IP público que será dividido entre seus IPs privados
mascaras = {8192: 19, 4096: 20, 2048: 21, 1024: 22, 512: 23, 256: 24, 128: 25, 64: 26, 32: 27, 16: 28, 8: 29, 4: 30,
            2: 31, 1: 32} #dicionário que retorna a máscara para uma quantidade de IPs
#-------------------------------------------------

os.system('cls' if os.name == 'nt' else 'clear')
titulo = "GRCN - Gerador de Regras CGNAT em nftables - %s - v%s - %s" % (__author__, __version__,__datebegin__)
print("#"*100)
print("    %s" %(titulo))
print("#"*100)

#------------------------------------------------- Parâmetros informados / manual:

try:
  #Indice:
  indice = int(sys.argv[1])
  #Blocos:
  txt_publico = sys.argv[2]
  txt_privado = sys.argv[3]
  #range de portas:
  if len(sys.argv) > 5:
    if sys.argv[4] > 0 and sys.argv[5] > 0:
      numero_porta_incial = int(sys.argv[4])
      numero_porta_final = int(sys.argv[5])
  if len(sys.argv) > 6 and sys.argv[6] > 0:
    qt_portas_por_ip = int(sys.argv[6])
except:
  print("\nErro! Informe pelo menos os parâmetros obrigatórios deste script.\n")
  print("## Manual de Instruções:")
  print("\n###### Exemplo básico:\n")
  print("```")
  print("%spython %s <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO>" %(' '*6, sys.argv[0]))
  print("%spython %s 0 192.0.2.0/27 100.69.0.0/22" %(' '*6, sys.argv[0]))
  print("```")
  print("\n###### Exemplo avançado:\n")
  print("```")
  print("%s python %s <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO> <PORTA_PUBLICA_INICIAL>(OPCIONAL) <PORTA_PUBLICA_FINAL>(OPCIONAL> <QUANTIDADE_PORTAS_POR_IP_PRIVADO>(OPCIONAL)" %(' '*6, sys.argv[0]))
  print("%s python %s 0 192.0.2.0/27 100.69.0.0/22 1025 65535 1000" %(' '*6, sys.argv[0]))
  print("```")
  print("\n###### Parâmetros:\n")
  print("* INDICE: Inteiro >=0 que vai ser o sufixo do nome das regras únicas. Exemplo *CGNATOUT_XXX*;\n")
  print("* BLOCO_PUBLICO: É o bloco de IPs públicos por onde o bloco CGNAT vai sair para a internet. Exemplo: *192.0.2.0/27*\n")
  print("* BLOCO_PRIVADO: É o bloco de IPs privados que serão entregues ao assinante. Exemplo: *100.69.0.0/22*\n")
  print("* PORTA_PUBLICA_INICIAL: É a 1ª porta de cada IP público. Opcionalmente informada, pois seu valor padrão é *1*.\n")
  print("* PORTA_PUBLICA_FINAL: É a última porta de cada IP público. Opcionalmente informada, pois seu valor padrão é *65535*.\n")
  print("* QUANTIDADE_PORTAS_POR_IP_PRIVADO: Opcionalmente informado, pois é automaticamente calculado pela relação de IP privado x público. É a quantidade de portas que será destinada para cada IP privado.\n")
  print("\n####### Observações:\n")
  print("* O range de portas públicas deve ser preferencialmente deixado como padrão, para que cada IP privado receba o maior número possível de portas.\n")
  print("* Respeite a ordem dos parâmetros opcionais: Se quiser preencher apenas <QUANTIDADE_PORTAS_POR_IP_PRIVADO>, que está no final, sem alterar o range de portas, informe *1 65535 <QUANTIDADE_PORTAS_POR_IP_PRIVADO>*.\n")
  print("* Este script vai dividir o <BLOCO_PRIVADO> em N sub-redes privadas. Cada sub-rede privada sai por um único IP público e dela, cada IP privado sai com uma fração das portas de seu IP público.\n")
  print("* Se <BLOCO_PUBLICO> for um /27 e <BLOCO_PRIVADO> um /22, serão colocados exatamente 32 IPs privados (assinantes) atrás de um IP público. Cada IP privado vai sair com 2047 portas de seu IP público (65535/32=2047,96). O famoso *1:32*. A partir da v2.0, podemos calcular outras relações de CGNAT: 1:16, 1:8, etc.\n")
  print("\n")
  print("\nATENÇÃO! Por boas práticas, o script PAROU de gerar as regras CGNAT do tipo IN. Caso queira continuar gerando-as, edite o cgnat-nft.py, alterando o valor *fazer_regras_in* de *False* para *True*;")
  print("\nFIM deste manual!\n")
  exit(0)

#------------------------------------------------- trata os parâmetros informados:

try:
  #Indice:
  nome_arquivo_destino = ("cgnat-%i.conf" % (indice))
  #Blocos:
  if sys.version_info >= (3,0):
    rede_publica = ipaddress.ip_network(str(txt_publico), strict=False)
    rede_privada = ipaddress.ip_network(str(txt_privado), strict=False)
  else:
    rede_publica = ipaddress.ip_network(unicode(txt_publico), strict=False)
    rede_privada = ipaddress.ip_network(unicode(txt_privado), strict=False)
  qt_ips_publicos = int(rede_publica.num_addresses)
  qt_ips_privados = int(rede_privada.num_addresses)
  qt_ips_privados_por_ip_publico = int( qt_ips_privados / qt_ips_publicos )
  #qt_portas
  ###qt_total_portas = (numero_porta_final+1-numero_porta_incial)
  qt_total_portas = (numero_porta_final-(numero_porta_incial-1))
  if qt_portas_por_ip == 0:
    print("Calculando a quantidade de portas / IP privado...")
    qt_portas_por_ip = int( qt_total_portas * qt_ips_publicos / qt_ips_privados )
  # calcula a máscara das subnets privadas baseado na relação PRI/PUB:
  masc_subrede_privada = mascaras[qt_ips_privados_por_ip_publico]
  subnets_privadas = list(rede_privada.subnets(new_prefix=masc_subrede_privada))
except:
  print("\nErro! Informe parâmetros válidos para este script:\n\nRespeite a relação de IP público x IP privado: 1:32, 1:16, 1:8, etc\n\nEncerrando!\n")
  exit(0)

print(" - Indice das regras: %i;" % (indice))
print(" - Rede pública: %s (%i IPs);" % (txt_publico,qt_ips_publicos))
print(" - Rede privada: %s (%i IPs);" % (txt_privado,qt_ips_privados))
print(" - Quantidade de IPs privados por IP público: %i (%i sub-redes /%s);" % (qt_ips_privados_por_ip_publico, qt_ips_publicos, masc_subrede_privada))
print(" - Total de portas públicas: %i (%i a %i);" % (qt_total_portas, numero_porta_incial, numero_porta_final))
print(" - Portas por IP privado: %i;" % (qt_portas_por_ip))
print(" - Arquivo de destino (conf): '%s';" % (nome_arquivo_destino))
print("\n")

if fazer_regras_in:
  print("\nATENÇÃO!\n  Variável fazer_regras_in=True\n  Mesmo não sendo boas práticas, SERÃO geradas regras de CGNAT do tipo IN!\n")


#Checa se o tamanho das redes permite relação de CGNAT
if qt_portas_por_ip == 0 or qt_ips_privados_por_ip_publico < 1:
  print("Erro! Tamanho das redes público, privadas ou quantidade de portas por IP privado que não permite a divisão de CGNAT.\n%i %i %i "%(qt_portas_por_ip,qt_portas_por_ip,qt_ips_privados))
  exit(0)

#------------------------------------------------- Abre o arquivo onde as regras serão armazenadas (destino):
try:
  caminho_deste_script = os.path.dirname(os.path.realpath(__file__))+'/'
  arquivo_destino = open(caminho_deste_script+nome_arquivo_destino, "w")
except (OSError, IOError) as e:
  print ("\nErro!\nFalha ao abrir a escrita do arquivo onde as regras serão armazenadas (destino)")
  sys.exit(1)

arquivo_destino.write("# %s\n" %(titulo))
arquivo_destino.write("# - blocos %s -> %s;\n# - /%i de IPs privados / IP público;\n# - %i portas / IP privado;\n" %(
  txt_privado,
  txt_publico,
  masc_subrede_privada,
  qt_portas_por_ip
))

#-------------------------------------------------------------------------- principal

if sys.version_info >= (3,0):
  input("Tecle [ENTER]...")
else:
  raw_input("Tecle [ENTER]...")
momento_incial = time.time()

#exit(0)

print("\n")
indice_subnet_privada = 0
for ip_publico in rede_publica:
  arquivo_destino.write("# %s #INDICE %i / IP PUBLICO %s\n" % ('-' * 40, indice, str(ip_publico)))
  arquivo_destino.write("add chain ip nat CGNATOUT_%i\n" % (indice))
  if fazer_regras_in:
    arquivo_destino.write("add chain ip nat CGNATIN_%i\n" % (indice))
  arquivo_destino.write("flush chain ip nat CGNATOUT_%i\n" % (indice))
  if fazer_regras_in:
    arquivo_destino.write("flush chain ip nat CGNATIN_%i\n" % (indice))
  #print(subnets_privadas)
  subnet = subnets_privadas[indice_subnet_privada]
  # Zera o range de portas para o prox IP publico
  porta_ini = numero_porta_incial
  ###porta_fim = qt_portas_por_ip
  porta_fim = (numero_porta_incial + (qt_portas_por_ip -1))
  print("%s INDICE=%i - IP_PUBLICO=%s -> SUBNET_PRIVADA=%s" % ("=" * 40, indice, str(ip_publico), str(subnet)))
  for ip_privado in ipaddress.ip_network(subnet):
    #trp = "1-2048"
    trp = "%i-%i" % (porta_ini,porta_fim)
    print("%s IP PRIVADO %s:%s" %("-"*60,str(ip_privado),trp))
    #Regras para cada IP privado
    arquivo_destino.write("%s CGNATOUT_%i ip protocol tcp ip saddr %s counter snat to %s:%s\n" % (
      __com1__,
      indice,
      str(ip_privado),
      str(ip_publico),
      trp
    ))
    arquivo_destino.write("%s CGNATOUT_%i ip protocol udp ip saddr %s counter snat to %s:%s\n" % (
      __com1__,
      indice,
      str(ip_privado),
      str(ip_publico),
      trp
    ))

    if fazer_regras_in:
      arquivo_destino.write("%s CGNATIN_%i ip daddr %s tcp dport %s counter dnat to %s\n" % (
        __com1__,
        indice,
        str(ip_publico),
        trp,
        str(ip_privado)
      ))
      arquivo_destino.write("%s CGNATIN_%i ip daddr %s udp dport %s counter dnat to %s\n" % (
        __com1__,
        indice,
        str(ip_publico),
        trp,
        str(ip_privado)
      ))

    #incrementa o range de portas para o próximo IP privado
    porta_ini += qt_portas_por_ip
    porta_fim += qt_portas_por_ip
    if porta_fim > numero_porta_final:
      porta_fim = numero_porta_final
  #regras finais para a subrede x IP público
  #arquivo_destino.write("\n")
  arquivo_destino.write("%s CGNATOUT_%i counter snat to %s\n" % (
    __com1__,
    indice,
    str(ip_publico)
  ))
  arquivo_destino.write("%s CGNATOUT ip saddr %s counter jump CGNATOUT_%i\n" % (
    __com1__,
    str(subnet),
    indice
  ))
  if fazer_regras_in:
    arquivo_destino.write("%s CGNATIN ip daddr %s/32 counter jump CGNATIN_%i\n" % (
      __com1__,
      str(ip_publico),
      indice
    ))
  #for ip_privado in subnet.subnets(new_prefix=32):
  #  print("    %s" % (str(ip_privado)))
  #arquivo_destino.write("\n")
  indice+=1
  indice_subnet_privada+=1

#-------------------------------------------------------------------------- final

#Fecha o arquivo onde as regras serão armazenadas (destino):
try:
  arquivo_destino.close()
except (OSError, IOError) as e:
  print ("\nErro!\nFalha ao salvar o arquivo onde as regras serão armazenadas (destino)")
  sys.exit(1)

print("\nFIM!\n\nAs regras foram geradas no arquivo:\n%s\n\nDuração: %.3f segundos" %(
  caminho_deste_script + nome_arquivo_destino,
  (time.time()-momento_incial)
))
