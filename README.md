------------------------------------------------------------------------
Beiriz 01/jun/2020
------------------------------------------------------------------------

Pré requisito: "ipaddress" do Python.

Executar como root para instalar: pip install ipaddress

------------------------------------------------------------------------
Exemplo de uso do script:
------------------------------------------------------------------------

Exemplo básico:
python cgnat-nft.py <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO>
python cgnat-nft.py 0 xxx.xxx.xxx.xxx/27 100.69.0.0/22


Exemplo avançado:
python cgnat-nft.py <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO> <QUANTIDADE_PORTAS_POR_IP_PRIVADO>(OPCIONAL)
python cgnat-nft.py 0 xxx.xxx.xxx.xxx/27 100.69.0.0/22 2000


- <INDICE>: Inteiro >=0 que vai ser o sufixo do nome das regras únicas. Exemplo CGNATIN_XXX;
- <BLOCO_PUBLICO>: É o bloco de IPs públicos por onde o bloco CGNAT vai sair para a internet. Exemplo: X.X.X.X/27
- <BLOCO_PRIVADO>: É o bloco de IPs privados que serão entregues ao assinante. Exemplo: 100.69.0.0/22
- <QUANTIDADE_PORTAS_POR_IP_PRIVADO>: Opcionalmente informado, pois seu valor Default é '2000'. Cada IP privado vai conseguir sair por 2000 portas do IP público.

OBS: Esse script vai dividir o <BLOCO_PRIVADO> em /27s. Se <BLOCO_PUBLICO> for um /27, serão colocados exatamente 32 IPs privados (assinantes) atrás de um IP público. O famoso "1:32".

Ele também pode ser executado no bash com o comando "./cgnat-nft.sh", ao invés do "python cgnat-nft.py".

Link da live do Marcelo Gondim no "FiqueEmCasaUseDebian #23 - CGNAT com NFTables": https://www.youtube.com/watch?v=5uOFtkplDts

------------------------------------------------------------------------
LICENÇA
------------------------------------------------------------------------

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