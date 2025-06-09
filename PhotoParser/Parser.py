from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import sys
import os
import requests
import bs4
import traceback
import logging
from bs4 import BeautifulSoup



class Parser():
    
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
            logger.setLevel(logging.DEBUG)
        return logger   
        
    
    #Рандомная задержка действий как человек
    def _random_sleep(self) -> None:
        time.sleep(random.randint(2,5) * 0.5)
        
        
    #Прокрутка страницы несколько раз 
    def _full_scroll(self, driver, repeate :int) -> None:
        last_height = driver.execute_script("return document.body.scrollHeight")
        self.logger.info("Листаем картинки")
        for _rep in range(0, repeate):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._random_sleep()
            new_height = driver.execute_script("return document.body.scrollHeight")
            if repeate // 2 == _rep:
                self.logger.info("Уже пол пути пролистали")
            if repeate-1 == _rep:
                self.logger.info("Долистали!")
                
            if new_height == last_height:
                break
            last_height = new_height
            try:
                button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'FetchListButton-Button') and .//span[text()='Показать ещё']]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                driver.execute_script("arguments[0].click();", button)
            except Exception:
                continue

            
            
    #Получаем страницу        
    def GetPageSoup(self, page_url :str = None, scroll_range:int = 1) -> bs4.BeautifulSoup:
        if page_url is not None:
            try:
                self.logger.info(f"Searching => {page_url}")
                self._driver.get(page_url)
                WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                self._full_scroll(self._driver, scroll_range)
                return BeautifulSoup(self._driver.page_source, 'html.parser')
            
            except Exception:
                self.logger.info("Ошибка парсинга страницы.")


    #Получаем ключевые слова
    def GetPhotos(self, soup :bs4.BeautifulSoup = None, num:int = 10) -> list:
        params = None
        if soup is not None:
            images = None
            try:
                images = soup.find_all('img', {'class': 'ImagesContentImage-Image ImagesContentImage-Image_clickable'})
            except Exception:
                self.logger.info("Картинки не найдены")
                
            try:
                os.makedirs("images", exist_ok=True)   
            except Exception:
                self.logger.info("Ошибка создания папки images")
                

            if images:
                os.system(f"explorer {os.path.abspath(os.path.normpath('./images'))}")
                self.logger.info("Пиздим картинки!")
                for i, img in enumerate(images[:num]):
                    try:
                        img_url = img["src"].replace("//","http://")
                        if img_url and img_url.startswith("http"):
                            response = requests.get(img_url)
                            with open(f"images/image_{i+1}.jpg", "wb") as f:
                                f.write(response.content)
                    except Exception as e:
                        self.logger.info(f"Ошибка спизжевния картинки \n {i+1} - {img} \n \n {traceback.format_exc()}")
        
        
    #Закрытие драйвера при остановке
    def stop(self):
        try:
            self._driver.quit()
        except Exception:
            self.logger.warning("Ошибка при закрытии драйвера.")
        
        
    #основная функция запуска
    def run(self, target: str, count: int):
        try:
            self.busy = True
            results = None
            url = f"https://yandex.ru/images/search?from=tabbar&text={target}"
            soup = self.GetPageSoup(url, scroll_range = (count//10))

            if soup is not None:
                self.GetPhotos(soup, count)
            else:
                self.busy = False
                self.logger.info("Не удалось получить страницу товара")
        except Exception as e:
            self.logger.warning(traceback.format_exc())        
        
        finally:
            self.stop()

        
    
    
if __name__ == "__main__":
    try:
        debug = True if "--debug" in sys.argv else False
        obj = Parser(show_window=debug, debug=debug)
        logger = obj.logger
        target = str(input("\n Что ищем? >> ")).replace(" ", "+")
        num = int(input("\n Сколько фоток? >> "))
        result = obj.run(target, num)
        
    except KeyboardInterrupt:
        logger.info("\n НЕ ДРОЧИ КЛАВУ а то процесс зависнет.")

    finally:
        logger.info("\n Корректное завершение всех процессов")
        obj.stop()
        quit()
    