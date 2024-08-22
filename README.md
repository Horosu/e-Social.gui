# Automação de Extração de Dados do e-Social

Este projeto realiza a automação do processo de extração de dados do sistema do governo e-Social para cada trabalhador. Ele copia o HTML e o CSS da página e transforma essas informações em um arquivo PDF para registro.

## Índice

- [Descrição](#descrição)
- [Instalação](#instalação)
- [Uso](#uso)
- [Funcionalidades](#funcionalidades)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Contato](#contato)

## Descrição

Este projeto é uma solução automatizada para extração de dados de cada trabalhador no sistema do e-Social, facilitando o processo de geração de registros. A automação navega pelo sistema, extrai os dados desejados, copia o HTML e o CSS da página, e transforma tudo em um PDF pronto para armazenamento e consulta.

## Instalação

1. Clone o repositório:
   ```terminal´´´´
   git clone https://github.com/Horosu/e-social.pdf/

2. Navegue até o diretório do projeto:
    ```terminal´´´´
    cd nome-do-projeto

4. Instalando um ambiente virtual:
    ```terminal´´´
    python -m venv nome_do_ambiente

5. Ativando o ambiente virtual:
    ```terminal´´´
    nome_do_ambiente\Scripts\activate

6. Instale as dependências no ambiente virtual:
    ```terminal´´´´
    pip install -r requirements.txt    

7. Configure as variáveis de ambiente conforme necessário.

## Uso

1. Atualize a planilha "dados.xlsx" adicionando os dados de informação de cada usuário que deseja fazer a captura.

2. Na linha 118 do código, atualize a data que é informada em "periodo_apuracao = "00/0000""

3. Após atualizar a data de apuração, capture o curl (bash) da primeira requisição do e-Social. 

## Requisitos

- Python 3.x
- Bibliotecas necessárias (listadas em `requirements.txt`)
- Ambiente virtual (se necessário)

## Funcionalidades

 - Extração automática de dados do e-Social
 - Conversão de HTML e CSS para PDF
 - Armazenamento organizado por trabalhador

## Contribuição

 - Faça um fork do projeto
 - Crie uma branch para sua feature (git checkout -b feature/nova-feature)
 - Commit suas mudanças (git commit -m 'Adicionei uma nova feature')
 - Envie para o branch (git push origin feature/nova-feature)
 - Abra um Pull Request
 - Licença
 - Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.


## Contato
- Desenvolvido por Horosu - Entre em contato para mais informações.

