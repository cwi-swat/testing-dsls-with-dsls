from miniTESTAR import testar
from selenium.webdriver.common.by import By
import os

def test_lambda():
    
    testar('https://lambdatest.github.io/sample-todo-app/', 3, 100, [], [])


def test_tax():
    
    # oracle
    def visibility_conditional_questions(driver):
        current_state = driver.execute_script("return $state;")
        assert not (current_state["hasSoldHouse"]) or all([(e.is_displayed() and e.is_enabled()) for id in ["sellingPrice_div_242", "privateDebt_div_304", "valueResidue_div_371"] for e in driver.find_elements(By.ID, id)])
    
    testar('file://' + os.getcwd() + '/../../examples/tax.html', 1, 500, [], [visibility_conditional_questions])


def test_binary():
    
    testar('file://' + os.getcwd() + '/../../examples/binary.html', 3, 100, [], [])


def test_cyclic():
    
    testar('file://' + os.getcwd() + '/../../examples/cyclic.html', 3, 100, [], [])


def test_demo():
    
    testar('file://' + os.getcwd() + '/../../examples/demo.html', 3, 100, [], [])


