# Sistema-POS

Esta aplicação é um sistema de Ponto de Venda (POS) com controle de estoque e gerenciamento de colaboradores, desenvolvida em Python utilizando Flask para a autenticação, Kivy para a interface gráfica e SQLAlchemy para o gerenciamento do banco de dados.

## Requisitos

Antes de começar, certifique-se de que você tem as seguintes ferramentas instaladas em sua máquina:

- **Python 3.7 ou superior**
- **Git** (opcional, para clonar o repositório)
- **Virtualenv** (opcional, mas recomendado)

## Instalação

### 1. Clone o repositório (opcional)

Se você estiver usando Git, pode clonar o repositório:

```bash
git clone https://github.com/Caeeles/sistema-POS.git
```

Se preferir, você também pode simplesmente baixar o código como um arquivo zip e descompactá-lo.

### 2. Crie e ative um ambiente virtual (opcional, mas recomendado)
É altamente recomendável usar um ambiente virtual para evitar conflitos de dependências.

```bash
python -m venv venv
```
Para ativar o ambiente virtual:

Windows:

```bash
venv\Scripts\activate
```
Linux/MacOS:

```bash
source venv/bin/activate
```

### 3. Instale as dependências
Com o ambiente virtual ativado (se aplicável), instale as dependências necessárias:
```bash
pip install -r requirements.txt
```

### 4. Configuração do Banco de Dados
A aplicação usa SQLAlchemy e Alembic para o gerenciamento do banco de dados.

Se houver migrações a serem aplicadas, execute:
```bash
alembic upgrade head
```

### 5. Executando a Aplicação
5.1 Executando com o script
Você pode executar a aplicação com o script start.py que executa sequencialmente o servidor de autenticação e a interface gráfica:
```bash
python start.py
```
ou se preferir, pode executar separadamente. 

5.2.1 Executando o Backend (Flask)
Primeiro, você deve iniciar o servidor Flask:

```bash
cd api
python app.py
```

5.2.2 Executando a Interface Gráfica (Kivy)
Com o backend rodando, em outro terminal ou aba, execute a interface gráfica da aplicação:

```bash
cd ..
python main.py
```

### 6. Utilização
Após executar os passos acima, a aplicação estará rodando. Siga as instruções na interface para fazer login e começar a usar o sistema de Ponto de Venda.

## Dependências
Este projeto depende das seguintes bibliotecas Python:

Kivy - Biblioteca para a interface gráfica
Flask - Framework web para a API de autenticação
SQLAlchemy - ORM para banco de dados
Alembic - Ferramenta de migração de banco de dados
E outras listadas no arquivo requirements.txt.

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests no repositório.