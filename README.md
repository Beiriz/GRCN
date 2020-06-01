#Beiriz 01/jun/2020

#Pré requisito: ipaddress
Executar como root para instalar:
pip install ipaddress

#Exemplo de uso do script:

Exemplo básico:
python cgnat-nft.py <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO>
python cgnat-nft.py 0 xxx.xxx.xxx.xxx/27 100.69.0.0/22


Exemplo avançado:
python cgnat-nft.py <INDICE> <BLOCO_PUBLICO> <BLOCO_PRIVADO> <MASC_SUB_PRIVADO>(OPCIONAL) <QUANTIDADE_PORTAS_POR_IP_PRIVADO>(OPCIONAL)
python cgnat-nft.py 0 xxx.xxx.xxx.xxx/27 100.69.0.0/22 0 0


- <INDICE>: Inteiro >=0 que vai ser o sufixo do nome das regras únicas. Exemplo CGNATIN_XXX;
- <BLOCO_PUBLICO>: É o bloco de IPs públicos por onde o bloco CGNAT vai sair para a internet. Exemplo: X.X.X.X/27
- <BLOCO_PRIVADO>: É o bloco de IPs privados que serão entregues ao assinante. Exemplo: 100.69.0.0/22
- <MASC_SUB_PRIVADO>: Opcionalmente informado, pois seu valor Default é '0'. Inteiro que representa a máscara da subrede do bloco privado que vai ser associado à um IP público;
- <QUANTIDADE_PORTAS_POR_IP_PRIVADO>: Opcionalmente informado, pois seu valor Default é '0'. Cada IP privado vai conseguir sair por 2000 portas do IP público.
