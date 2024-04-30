import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from io import StringIO
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# A classe service é usada para iniciar uma instância do chrome webdriver
service = Service()

# wevdriver.ChromeOptions é usado para definir a preferência para o browser do Chrome
options = webdriver.ChromeOptions()

# Inicia-se a instância do chrome webdriver com as definicads 'options' e 'service'
driver = webdriver.Chrome(service=service, options=options)

url = 'https://s2gpr.sefaz.ce.gov.br/fornecedor-web/paginas/cadastro_pessoas_compras/AssistenteEmissaoCRC.seam'

driver.get(url)

#tela de site inseguro
avancar = driver.find_element(By.XPATH, "//button[@id='details-button']")
avancar.click()

prosseguir = driver.find_element(By.XPATH, "//a[@id='proceed-link']")
prosseguir.click()
sleep(2)
#inicio de teste no site navegação padrão
pessoaJuridica = driver.find_element(By.XPATH, "//input[@id='formularioDeBusca:j_id111:j_id123:1']")
pessoaJuridica.click()
sleep(2)

cnpj = driver.find_element(By.XPATH, "//input[@id='formularioDeBusca:filtroCnpjDecorate:filtroCnpj']")
for _ in range(18):
    cnpj.send_keys(Keys.LEFT)
cnpj.send_keys('49947755000197')

consultarButton = driver.find_element(By.XPATH, "//input[@id='formularioDeBusca:pesquisar']")
consultarButton.click()
consultarButton.click()
sleep(5)
#processamento
tabelaDocumentacaoComplementar = driver.find_element(By.XPATH, "//*[@id='formularioDeBusca:tableDocComplementarPessoaJuridica']")

htmlContent = tabelaDocumentacaoComplementar.get_attribute("outerHTML")
sleep(1)

soup = BeautifulSoup(htmlContent, "html.parser")
sleep(1)

documentacaoComplementar = soup.find(name="table")
sleep(1)

htmlContentIO = StringIO(str(documentacaoComplementar))

DF = pd.read_html(htmlContentIO)[0]
DFfiltrado = DF[['Status', 'Tipo', 'Validade']]
sleep(1)

DF.to_csv("documentacaoComplementar.csv", encoding="UTF-8", sep=";", index=False)
DFfiltrado.to_csv("documentacaoComplementarFiltrada.csv", encoding="UTF-8", sep=";", index=False)

def enviar_email(destinatario, assunto, corpo):
    remetente = "complementardocumentacao@gmail.com"  # Insira seu endereço de e-mail
    senha = "documentacaoComplementar123"  # Insira sua senha
    sleep(1)

    # Configuração do servidor SMTP do Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(remetente, senha)
    sleep(1)

    # Criação do e-mail
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))
    sleep(1)

    # Envio do e-mail
    server.send_message(msg)
    del msg
    server.quit()

# Carrega o arquivo CSV com os dados da documentação
DFread = pd.read_csv("documentacaoComplementarFiltrada.csv", sep=";")

# Converte a coluna 'Validade' para o formato de data
DFread['Validade'] = pd.to_datetime(DFread['Validade'], format='%d/%m/%Y')
sleep(1)

# Calcula a data atual
data_atual = datetime.now()

# Calcula a data da validade dentro de 10 dias da data atual
data_limite = data_atual + timedelta(days=10)

# Filtra as documentações dentro de 10 dias da validade
documentacoes_vencendo = DFread[DFread['Validade'] <= data_limite]
sleep(1)

# Verifica se há documentações vencendo
if not documentacoes_vencendo.empty:
    # Formata o corpo do e-mail
    corpo_email = "As seguintes documentações estão vencendo em breve:\n\n" + documentacoes_vencendo.to_string(index=False)
    sleep(1)

    # Envia o e-mail
    enviar_email("natannlino@gmail.com", "Documentações Vencendo em Breve", corpo_email)