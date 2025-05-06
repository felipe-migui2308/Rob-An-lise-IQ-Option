# Robô de Análise - IQ Option

Este repositório contém um robô automatizado desenvolvido para realizar operações de **PUT** e **CALL** na plataforma IQ Option, com base em análise de tendências do mercado. O objetivo é automatizar o processo de análise e execução de operações utilizando a biblioteca `iqoptionapi` para interagir com a plataforma IQ Option.

![Demonstração do Robô](https://github.com/felipe-migui2308/Rob-An-lise-IQ-Option/blob/main/Robo-analise.png.png)

## Funcionalidades

- **Conexão automática**: O robô se conecta à plataforma IQ Option utilizando as credenciais fornecidas.
- **Escolha de ativos**: O usuário pode escolher o ativo em que o robô fará as análises e operações (exemplo: EURUSD, EURUSD-OTC).
- **Execução de operações PUT e CALL**: O robô executa operações baseadas na análise de tendências, considerando condições de subida e queda de preços.
- **Registro de resultados**: O robô registra o histórico de operações realizadas em um arquivo CSV, com data, ativo, tipo de operação, valor investido, preço de entrada, resultado e lucro/prejuízo.
- **Interface gráfica**: Interface simples e intuitiva em Tkinter, permitindo fácil configuração e controle do robô.

## Requisitos

Certifique-se de ter as bibliotecas necessárias instaladas. Você pode instalar as dependências utilizando o seguinte comando:


As bibliotecas necessárias estão listadas no arquivo `requirements.txt`.

## Como usar

1. **Clone o repositório**:

git clone https://github.com/felipe-migui2308/Rob-An-lise-IQ-Option.git


3. **Execute o robô**:

Para rodar o robô, basta executar o script principal:

python robô_analise.py


4. **Configure o login**:

Na interface gráfica, insira seu **email**, **senha** e selecione o tipo de conta (real ou demo). Depois, clique em "Conectar" para estabelecer a conexão com a plataforma.

5. **Escolha o ativo**: 

Selecione o ativo que deseja analisar e operar (exemplo: EURUSD, EURUSD-OTC).

6. **Valor da operação**:

Defina o valor a ser investido nas operações (por padrão, o valor é 2).

7. **Estratégias**:

Ative ou desative as estratégias de **PUT** e **CALL** para que o robô realize as operações conforme a análise de tendências.

8. **Iniciar análise**:

Clique em "▶ Iniciar Análise" para que o robô comece a monitorar o mercado e realizar as operações automaticamente.

9. **Parar análise**:

Para interromper a análise, clique em "⛔ Parar e Fechar".

## Histórico de Operações

O histórico de todas as operações realizadas será registrado em um arquivo CSV chamado `historico_operacoes.csv`. Esse arquivo contém as seguintes colunas:

- **Data e Hora**
- **Ativo**
- **Tipo (PUT ou CALL)**
- **Valor da operação**
- **Preço de entrada**
- **Resultado (WIN, LOSS ou EMPATE)**
- **Lucro/Prejuízo**

## Contribuições

Se você deseja contribuir para este projeto, sinta-se à vontade para fazer um fork e enviar pull requests com melhorias ou correções.

## Licença

Este projeto é de código aberto e pode ser utilizado de acordo com a licença MIT.

