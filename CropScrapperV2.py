from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from time import sleep

chrome_options = Options()
# chrome_options.add_argument("--headless") #Descomente para ativar o robô sem abrir uma janela do chrome
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280,720")

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.agrolink.com.br/cotacoes')
sleep(2)

ignore_this_cultures = ['Todos', 'Álcool', 'Aves', 'Bovinos', 'Caprinos', 'Madeira e subprodutos', 'Ovinos', 'Bubalinos', 'Ovos', 'Suínos', 'Mel']

def encontrar_select_cultura():
    tentativas = 5
    for tentativa in range(tentativas):
        try:
            select_culture = driver.find_element(By.XPATH, "//select[@id='FiltroCotacoesEspecie']")
            select = Select(select_culture)
            options = select.options

            if len(options) >= 1:
                print(f"Select de Cultura Encontrado")
                return select, options
            else:
                sleep(7)
                print(f"Select de Cultura não encontrado, tentando novamente... ({tentativa + 1}/{tentativas})")
                driver.refresh()
                sleep(3)

        except Exception as e:
            print(f"Erro ao encontrar select de cultura: {e}")
            driver.refresh()
            sleep(2)

    raise Exception("Elemento select_culture não encontrado após várias tentativas.")

def encontrar_select_produto():
    tentativas = 100
    for tentativa in range(tentativas):
        try:
            select_produto = driver.find_element(By.XPATH, "//select[@id='FiltroCotacoesProduto']")
            select = Select(select_produto)

            opcoes = select.options

            if len(opcoes) >= 2:
                print(f"Select Encontrado")
                return select
            else:
                sleep(7)
                print(f"Select não encontrado, tentando novamente...")
                driver.refresh()
                sleep(4)

        except Exception as e:
            driver.refresh()
            sleep(2)

    raise Exception("Elemento select_produto não encontrado com 2 ou mais opções após várias tentativas.")

select, options = encontrar_select_cultura()

for index in range(len(options)):
    sleep(3)
    try:
        option_text = options[index].text

        if option_text in ignore_this_cultures:
            continue

        select.select_by_index(index)
        sleep(4)

        cultura_selecionada = option_text
        print(f"{option_text} Selecionado(a) e Consultando...")

        consultar_button = driver.find_element(By.XPATH, "//span[@class='btn-centraliza']")
        consultar_button.click()
        sleep(5)
        
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
            print(f"{produto_text} Selecionado(a) e Consultando...")
            consultar_button.click()
            sleep(3)

            try:
                table_title = driver.find_element(By.XPATH, "//td[@class='table-title-custom']")
                print(f"Table Encontrada")            
            except:
                print(f"Table Não Encontrada")
                break

            grafico_link = driver.find_element(By.XPATH, "//a[@title='Gráfico']")
            
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", grafico_link)
            sleep(2)

            actions = ActionChains(driver)
            actions.move_to_element(grafico_link).perform()
            sleep(2)

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Gráfico']")))
            print(f"Gráfico de preços encontrado. Entrando...")
            
            grafico_link.click()
            sleep(3)

            grafico_table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[@class='table table-main orange']"))
            )
            print(f"Coletando valores...")
            tbody = grafico_table.find_element(By.XPATH, ".//tbody")

            rows = tbody.find_elements(By.XPATH, ".//tr")[:12]

            for row in rows:
                try:
                    mes_ano = row.find_element(By.XPATH, ".//th[1]").text
                    valor_nacional = row.find_element(By.XPATH, ".//td[2]").text
                    print(f" Cultura: {cultura_selecionada} Produto: {produto_text} Mês/Ano: {mes_ano}, Valor Nacional: {valor_nacional}")
                    
                except Exception as e:
                    print(f"Erro ao processar linha: {e}")

            driver.back()
            print(f"Próximo Tipo de cultura")
            sleep(2)

            select_produto = driver.find_element(By.XPATH, "//select[@id='FiltroCotacoesProduto']")
            select_prod = Select(select_produto)
            produto_options = select_prod.options

    except IndexError:
        print(f"Erro: Índice fora do intervalo. Tentando recarregar a página...")
        select, options = encontrar_select_cultura()
        continue

    driver.get('https://www.agrolink.com.br/cotacoes')
    print(f"Próxima Cultura")
    sleep(2)

    select_culture = driver.find_element(By.XPATH, "//select[@id='FiltroCotacoesEspecie']")
    select = Select(select_culture)
    options = select.options

driver.quit()
