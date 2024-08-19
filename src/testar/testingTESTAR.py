from miniTESTAR import testar
from selenium.webdriver.common.by import By
import os


def test_lambda():
    
    testar('https://lambdatest.github.io/sample-todo-app/', 3, 100, [], [], [])


def test_tax():
      
    testar('file://' + os.getcwd() + '/../../examples/tax.html', 1, 500, [], [], [])

def test_binary():
    
    testar('file://' + os.getcwd() + '/../../examples/binary.html', 3, 100, [], [], [])


def test_cyclic():
    
    testar('file://' + os.getcwd() + '/../../examples/cyclic.html', 3, 100, [], [], [])


def test_demo():
    
    testar('file://' + os.getcwd() + '/../../examples/demo.html', 3, 100, [], [], [])
    
def test_loan_approval():
    
    testar('file://' + os.getcwd() + '/../../examples/loan_approval.html', 3, 100, [], [], [])

  
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
    
    testar("https://www.saucedemo.com/", 1, 100, [filter_burger, filter_external_links], [test_Sauce_login], [])
     
    
    