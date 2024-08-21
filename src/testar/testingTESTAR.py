from miniTESTAR import testar, start_SUT_and_get_driver
from selenium.webdriver.common.by import By
import os


def test_lambda():
    
    testar('https://lambdatest.github.io/sample-todo-app/', 3, 100, [], [], [], 20)


def test_saucer():
  
    def test_Sauce_login(driver):
       
        # Localizar username y escibir uno
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        
        # Localizar password y escibir uno
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        
        # Localizar el botón y hacer click
        driver.find_element(By.ID, "login-button").click()
        
    def filter_burger(driver):
        return driver.find_element(By.ID, "react-burger-menu-btn")
    
    def filter_external_links(driver):
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        # Filter the links to Twitter, Facebook and LinkedIn
        social_links = [ link for link in all_links if link.get_attribute("href") and any(social in link.get_attribute("href") for social in ["twitter.com", "facebook.com", "linkedin.com"])]
        
        return social_links
    
    testar("https://www.saucedemo.com/", 1, 100, [filter_burger, filter_external_links], [test_Sauce_login], [], 20)
     
    
def test_parabank():
    
    def filter_external_links(driver):
        # Find all anchors
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        # Filter the links to parasoft.com
        unwanted = ["parasoft.com","?_wadl&_type=xml","?wsdl"]
        external_links = [ link for link in all_links if link.get_attribute("href") and any(href in link.get_attribute("href") for href in unwanted)]
        
        return external_links
    
    def filter_zero_sized_elements(driver):
        # Find all elements on the page
        all_elements = driver.find_elements(By.XPATH, "//*")
        
        # Filter elements that have size {'height': 0, 'width': 0}
        zero_sized_elements = [element for element in all_elements if element.size['height'] == 0 and element.size['width'] == 0]
        
        return zero_sized_elements
        
    def parabank_login(driver):
       
        # Localizar username y escibir uno
        driver.find_element(By.NAME, "username").send_keys("john")
        
        # Localizar password y escibir uno
        driver.find_element(By.NAME, "password").send_keys("demo")
        
        # Localizar el botón y hacer click
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Log In']").click()

    
    testar("https://para.testar.org/", 1, 40, [filter_external_links, filter_zero_sized_elements], [parabank_login], [], 180)

