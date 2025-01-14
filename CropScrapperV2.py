from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from time import sleep

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280,720")

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.agrolink.com.br/cotacoes')
sleep(2)

ignore_this_cultures = ['Todos', 'Álcool', 'Aves', 'Bovinos', 'Caprinos', 'Madeira e subprodutos', 'Ovinos', 'Bubalinos']

select_culture = driver.find_element(By.XPATH, "//select[@id='FiltroCotacoesEspecie']")
sleep(2)
select = Select(select_culture)

options = select.options

def encontrar_select_produto():
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            select_produto = driver.find_element(By.XPATH, "//select[@id='FiltroCotacoesProduto']")
            select = Select(select_produto)

            opcoes = select.options

            if len(opcoes) >= 2:
                return select
            else:
                driver.refresh()
                sleep(2)

        except Exception as e:
            driver.refresh()
            sleep(2)

    raise Exception("Elemento select_produto não encontrado com 2 ou mais opções após várias tentativas.")

for index in range(len(options)):
    sleep(3)
    option_text = options[index].text

    if option_text in ignore_this_cultures:
        continue

    select.select_by_index(index)
    sleep(4)

    cultura_selecionada = option_text

    consultar_button = driver.find_element(By.XPATH, "//span[@class='btn-centraliza']")
    consultar_button.click()
    sleep(7)
    
    select_prod = encontrar_select_produto()

    produto_options = select_prod.options

    for prod_index in range(len(produto_options)):
        produto_text = produto_options[prod_index].text

        if produto_text == "Todos":
            continue

        sleep(3)

        select_prod.select_by_index(prod_index)
        sleep(3)
        
        consultar_button = driver.find_element(By.XPATH, "//span[@class='btn-centraliza']")
        consultar_button.click()
        sleep(3)

        table_title = driver.find_element(By.XPATH, "//td[@class='table-title-custom']")
        
        grafico_link = driver.find_element(By.XPATH, "//a[@title='Gráfico']")
        
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", grafico_link)
        sleep(2)

        actions = ActionChains(driver)
        actions.move_to_element(grafico_link).perform()
        sleep(2)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Gráfico']")))
        
        grafico_link.click()
        sleep(3)

        grafico_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table[@class='table table-main orange']"))
        )
        tbody = grafico_table.find_element(By.XPATH, ".//tbody")

        rows = tbody.find_elements(By.XPATH, ".//tr")[:12]

        for row in rows:
            try:
                mes_ano = row.find_element(By.XPATH, ".//th[1]").text
                valor_nacional = row.find_element(By.XPATH, ".//td[2]").text
                print(f"Cultura: {cultura_selecionada} Produto: {produto_text} Mês/Ano: {mes_ano}, Valor Nacional: {valor_nacional}")
            except Exception as e:
                print(f"Erro ao processar linha: {e}")

        driver.back()
        sleep(2)

        select_produto = driver.find_element(By.XPATH, "//select[@id='FiltroCotacoesProduto']")
        select_prod = Select(select_produto)
        produto_options = select_prod.options

    driver.get('https://www.agrolink.com.br/cotacoes')
    sleep(2)

    select_culture = driver.find_element(By.XPATH, "//select[@id='FiltroCotacoesEspecie']")
    select = Select(select_culture)
    options = select.options

driver.quit()
