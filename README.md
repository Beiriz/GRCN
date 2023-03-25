# GRCN - Gerador de Regras CGNAT em nftables

Beiriz 27/julho/2020

_Testado em Python v2.7.16 e v3.7.7_


## ATENÇÃO! Novidades nesta Versão 4.000:

Os parâmetros mudaram: Agora informe apenas o ÍNDICE, o BLOCO_PUBLICO, o BLOCO_PRIVADO e, opcionalmente, a RELAÇÃO_IP_PUBLICO_X_CLIENTE (1/4, 1/8, 1/16, 1/32, 1/64, 1/125, 1/256)

Não informar mais a máscara do BLOCO_PRIVADO. A máscara dele sempre vai ser um /16. Não necessariamente será usado todo o /16.

Atenção! Não recomendado pelas boas práticas o uso das relações IP/CLIENTES 1/64, 1/128 e 1/256. É muito pouca porta por assinante, gerando problemas.

Exemplos:
```
python3 cgnat-nft.py 0 192.1.2.0/26 100.64.0.0 1/32
python3 cgnat-nft.py 0 192.1.2.0/26 100.64.0.0 1/16
```

## ATENÇÃO! Novidades na Versão 3.000:

Por boas práticas, o script PAROU de gerar as regras CGNAT do tipo IN. Caso queira continuar gerando-as, edite o script cgnat-nft.py:

Alterando a linha:
```
fazer_regras_in = False
```
Para:
```
fazer_regras_in = True
```

Novidades na Versão 2.0: O script passou a fazer o cálculo da quantidade de portas para cada IP privado. Exemplo:

```
 - Indice das regras: 0;
 - Rede pública: 192.0.2.0/27 (32 IPs);
 - Rede privada: 100.64.0.0/22 (1024 IPs);
 - Quantidade de IPs privados por IP público: 32 (32 sub-redes /27);
 - Total de portas públicas: 65535 (1-65535);
 - Portas por IP privado: 2047;
```


------------------------------------------------------------------------

## Pré requisito: "ipaddress" do Python.

Executar como root para instalar:

```
apt install python-pip
pip install ipaddress
```

------------------------------------------------------------------------
## Manual de Instruções:

###### Exemplo básico:

```
      python ./cgnat-nft.py <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO>
      python ./cgnat-nft.py 0 192.0.2.0/27 100.69.0.0/22
```

###### Exemplo avançado:

```
       python ./cgnat-nft.py <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO> <PORTA_PUBLICA_INICIAL>(OPCIONAL) <PORTA_PUBLICA_FINAL>(OPCIONAL> <QUANTIDADE_PORTAS_POR_IP_PRIVADO>(OPCIONAL)
       python ./cgnat-nft.py 0 192.0.2.0/27 100.69.0.0/22 1025 65535 1000
```

###### Parâmetros:

*  INDICE: Inteiro >=0 que vai ser o sufixo do nome das regras únicas. Exemplo *CGNATIN_XXX*;

* BLOCO_PUBLICO: É o bloco de IPs públicos por onde o bloco CGNAT vai sair para a internet. Exemplo: *192.0.2.0/27*

* BLOCO_PRIVADO: É o bloco de IPs privados que serão entregues ao assinante. Exemplo: *100.69.0.0/22*

* PORTA_PUBLICA_INICIAL: É a 1ª porta de cada IP público. Opcionalmente informada, pois seu valor padrão é *1*.

* PORTA_PUBLICA_FINAL: É a última porta de cada IP público. Opcionalmente informada, pois seu valor padrão é *65535*.

* QUANTIDADE_PORTAS_POR_IP_PRIVADO: Opcionalmente informado, pois é automaticamente calculado pela relação de IP privado x público. É a quantidade de portas que será destinada para cada IP privado.


###### Observações:

* O range de portas públicas deve ser preferencialmente deixado como padrão, para que cada IP privado receba o maior número possível de portas.

* Respeite a ordem dos parâmetros opcionais: Se quiser preencher apenas <QUANTIDADE_PORTAS_POR_IP_PRIVADO>, que está no final, sem alterar o range de portas, informe *1 65535 <QUANTIDADE_PORTAS_POR_IP_PRIVADO>*.

* Este script vai dividir o <BLOCO_PRIVADO> em N sub-redes privadas. Cada sub-rede privada sai por um único IP público e dela, cada IP privado sai com uma fração das portas de seu IP público.

* Se <BLOCO_PUBLICO> for um /27 e <BLOCO_PRIVADO> um /22, serão colocados exatamente 32 IPs privados (assinantes) atrás de um IP público. Cada IP privado vai sair com 2047 portas de seu IP público (65535/32=2047,96). O famoso *1:32*. A partir da v2.0, podemos calcular outras relações de CGNAT: 1:16, 1:8, etc.

------------------------------------------------------------------------

Link da live do Marcelo Gondim no "FiqueEmCasaUseDebian #23 - CGNAT com NFTables": https://www.youtube.com/watch?v=5uOFtkplDts

------------------------------------------------------------------------
## LICENÇA

GRCN is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
