from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import sys
import bs4
import logging
from bs4 import BeautifulSoup



class WBParser():
    
    def __init__(self, show_window:bool=False, debug:bool=False) -> None:

        self.driver_options = Options()
        if not show_window:
            self.driver_options.add_argument("--headless")

        self._driver = webdriver.Firefox(options=self.driver_options)

        self.logger = self._get_logging(debug)
        
        self.busy = False
        
    
    def is_busy(self) -> bool: 
        return bool(self.busy)
    
    #настройка логов
    def _get_logging(self, debug :bool) -> logging.getLoggerClass:
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler) 
        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)
        return logger   
        
    
    #Рандомная задержка действий как человек
    def _random_sleep(self) -> None:
        time.sleep(random.randint(2,5) * 0.5)
        
        
    #Прокрутка страницы несколько раз 
    def _full_scroll(self, driver, repeate :int) -> None:
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(0, repeate):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._random_sleep()
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
            
    #Получаем страницу        
    def GetPageSoup(self, page_url :str = None, scroll_range:int = 1) -> bs4.BeautifulSoup:
        if page_url is not None:
            try:
                self._driver.get(page_url)
                WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                self._random_sleep()
                self._full_scroll(self._driver, scroll_range)
                self._random_sleep()
                return BeautifulSoup(self._driver.page_source, 'html.parser')
            
            except Exception:
                self.logger.info("Ошибка парсинга страницы.")


    #Получаем ключевые слова
    def GetKeywords(self, soup :bs4.BeautifulSoup = None) -> list:
        params = None
        if soup is not None:
            try:
                params = soup.find_all('td', {'class': 'product-params__cell'})
                
            except Exception:
                self.logger.info("Характеристики не найдены")
                
            try:
                title  = soup.find('h1', {'class': 'product-page__title'})
                params.append(title)
                
            except Exception:
                self.logger.info("Название не найдено")
        
        if params:
            keywords = []
            try:
                for data in params:
                    if data is not None:
                        clear_keys = str(data.text).strip().split(" ")
                        for key in clear_keys:
                            key = key.replace(";","").replace(":","").replace("-","")
                            try:
                                key = int(key)
                                
                            except ValueError:
                                if 20 >= len(key) >= 3 and key not in keywords:
                                    keywords.append(key.lower())
            except Exception:
                self.logger.info("Ошибка получения кличевых слов.")
                
            return keywords
                    

    #Получаем позицию товара в поиске по ключевому слову 
    def GetPosition(self, key :str, product_url :str) -> int:
        self.logger.info(f"SEARCHING for {key}")
        
        search_url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={key}"
        soup = self.GetPageSoup(search_url, scroll_range=20)
        products = soup.find_all('a', {'class': 'product-card__link j-card-link j-open-full-product-card'})
        products_links = [item["href"] for item in products]
        try:
            position = products_links.index(product_url)+1
            if position == len(products_links):
                position = None
            else:
                self.logger.debug(f"{key} - {position} = {len(products_links)}")
                
            return [key, position ]
        except ValueError:
            self.logger.debug(f"{key} - NONE")
            return [key, None]
        
    #Закрытие драйвера при остановке
    def stop(self):
        try:
            self._driver.quit
        except Exception:
            self.logger.warning("Ошибка при закрытии драйвера.")
        
        
    #основная функция запуска
    def run(self, url: str):
        try:
            self.busy = True
            results = None
            soup = self.GetPageSoup(url)

            if soup is not None:
                keywords = self.GetKeywords(soup)
                print(f"\n Ключевые слова: {", ".join(keywords)} \n")
                results = [] 
                for key in keywords:
                    data = self.GetPosition(key, url)
                    results.append(data)
                self.busy = False
                return results
            
            else:
                self.busy = False
                self.logger.info("Не удалось получить страницу товара")
        finally:
            self.stop()

        
    
    
# if __name__ == "__main__":

#     debug = True if "--debug" in sys.argv else False
    
#     #show_window включает показ окна selenium 
#     Parser = WBParser(show_window=debug, debug=debug)
    
#     url = str(input("Ссылка Товар >> "))
#     result = Parser.run(url)
    
#     for key_data in result:
#         print("{:20} \t\t {:5}".format(key_data[0], key_data[1] if key_data[1] is not None else 'Нет' ))

    