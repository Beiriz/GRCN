#!/usr/bin/env python3
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
__version__= 1.200
__datebegin__= "01/06/2020"
__com1__ = "add rule ip nat"
#-----------------------------------------------------------------------

momento_incial = time.time()

indice = 0
txt_publico = ""
txt_privada = ""
masc_subrede_privada = int(27) #32 IPs cgnat para 1 IP público
qt_portas = int(2000) #quantidade de portas que serão reservadas por IP privado.

#--------------------------------------------------------------------------

os.system('cls' if os.name == 'nt' else 'clear')
titulo = "GRCN - Gerador de Regras CGNAT em nftables - %s - v%s - %s" % (__author__, __version__,__datebegin__)
print("#"*100)
print("    %s" %(titulo))
print("#"*100)

try:
  indice = sys.argv[1]
  indice = int(indice)
  txt_publico = sys.argv[2]
  txt_privada = sys.argv[3]
  if len(sys.argv) > 4 and sys.argv[4] > 0:
    qt_portas = int(sys.argv[4])
except:
  print("\nErro! Informe os parâmetros para este script:")
  print("\n")
  print("Exemplo básico:")
  print("python %s <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO>" %(sys.argv[0]))
  print("python %s 0 xxx.xxx.xxx.xxx/27 100.69.0.0/22" %(sys.argv[0]))
  print("\n")
  print("Exemplo avançado:")
  print("python %s <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO> <QUANTIDADE_PORTAS_POR_IP_PRIVADO>(OPCIONAL)" %(sys.argv[0]))
  print("python %s 0 xxx.xxx.xxx.xxx/27 100.69.0.0/22 %i" %(sys.argv[0], qt_portas))
  print("\n")
  print("- <INDICE>: Inteiro >=0 que vai ser o sufixo do nome das regras únicas. Exemplo CGNATIN_XXX;")
  print("- <BLOCO_PUBLICO>: É o bloco de IPs públicos por onde o bloco CGNAT vai sair para a internet. Exemplo: X.X.X.X/27")
  print("- <BLOCO_PRIVADO>: É o bloco de IPs privados que serão entregues ao assinante. Exemplo: 100.69.0.0/22")
  print("- <QUANTIDADE_PORTAS_POR_IP_PRIVADO>: Opcionalmente informado, pois seu valor Default é '%i'. Cada IP privado vai conseguir sair por 2000 portas do IP público." % qt_portas)
  print("\nOBS: Esse script vai dividir o <BLOCO_PRIVADO> em /%is. Se <BLOCO_PUBLICO> for um /27, São colocados exatamente 32 IPs privados (assinantes) atrás de um IP público.\n" % masc_subrede_privada)
  print("\n")
  exit(0)

#-------------------------------------------------------------------------- ajustes dos inputs

nome_arquivo_destino = ("cgnat-%i.conf" % (indice))
rede_publica = ipaddress.ip_network(unicode(txt_publico), strict=False)
rede_privada = ipaddress.ip_network(unicode(txt_privada), strict=False)

print(" - Indice: %i;" % (indice))
print(" - Rede pública: %s;" % (txt_publico))
print(" - Rede privada: %s;" % (txt_privada))
print(" - Máscara da subrede privada: %i;" % (masc_subrede_privada))
print(" - Portas por IP privado: %i;" % (qt_portas))
print(" - Arquivo de destino (conf): '%s';" % (nome_arquivo_destino))
print("\n INICIO - %s..." % (time.ctime(momento_incial)))

#Abre o arquivo onde as regras serão armazenadas (destino):
try:
  caminho_deste_script = os.path.dirname(os.path.realpath(__file__))+'/'
  arquivo_destino = open(caminho_deste_script+nome_arquivo_destino, "w")
except (OSError, IOError) as e:
  print "\nErro!\nFalha ao abrir a escrita do arquivo onde as regras serão armazenadas (destino): %s" % (nome_arquivo_destino)
  sys.exit(1)

arquivo_destino.write("# %s\n" %(titulo))
arquivo_destino.write("# - blocos %s -> %s;\n# - /%i de IPs privados / IP público;\n# - %i portas / IP privado;\n" %(
  txt_privada,
  txt_publico,
  masc_subrede_privada,
  qt_portas
))

#-------------------------------------------------------------------------- principal

# Divide o /22 privado em vários /27 (32 IPs privados por IP público)
subnets_privadas = list(rede_privada.subnets(new_prefix=masc_subrede_privada))
#subnets_privadas = rede_privada.subnets(new_prefix=masc_subrede_privada)

for ip_publico in rede_publica:
  if len(subnets_privadas) <= indice:
    print('Erro de indexação para o IP %s! Infome uma máscara para a subrede compatível com a quantidade de IPs públicos.' % str(ip_publico))
  else:
    arquivo_destino.write("# %s #INDICE %i / IP PUBLICO %s\n" % ('-' * 40, indice, str(ip_publico)))
    arquivo_destino.write("add chain ip nat CGNATOUT_%i\n" % (indice))
    arquivo_destino.write("add chain ip nat CGNATIN_%i\n" % (indice))
    arquivo_destino.write("flush chain ip nat CGNATOUT_%i\n" % (indice))
    arquivo_destino.write("flush chain ip nat CGNATIN_%i\n" % (indice))
    subnet = subnets_privadas[indice]
    # Zera o range de portas para o prox IP publico
    porta_ini = 1
    porta_fim = qt_portas
    print("%s INDICE=%i - IP_PUBLICO=%s -> SUBNET_PRIVADA=%s" % ("=" * 40, indice, str(ip_publico),str(subnet)))
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
      #incrementa o range de portas para o próximo IP privado do /27
      porta_ini+=qt_portas
      porta_fim += qt_portas
      if porta_fim > 65535:
        porta_fim = 65535
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
    arquivo_destino.write("%s CGNATIN ip daddr %s/32 counter jump CGNATIN_%i\n" % (
      __com1__,
      str(ip_publico),
      indice
    ))
    #for ip_privado in subnet.subnets(new_prefix=32):
    #  print("    %s" % (str(ip_privado)))
    #arquivo_destino.write("\n")
    indice+=1

#-------------------------------------------------------------------------- final

#Fecha o arquivo onde as regras serão armazenadas (destino):
try:
  arquivo_destino.close()
except (OSError, IOError) as e:
  print "\nErro!\nFalha ao salvar o arquivo onde as regras serão armazenadas (destino): %s" % (nome_arquivo_destino)
  sys.exit(1)

print("\nFIM! %.3f segundos" %(
  (time.time()-momento_incial)
))