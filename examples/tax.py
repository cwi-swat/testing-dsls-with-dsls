from selenium.webdriver.common.by import By
def tax_myql_oracle(driver):
    state = driver.execute_script('return $state;');
    
    assert not True or driver.find_elements(By.ID, 'hasBoughtHouse_div_31')[0].is_displayed(), 'true evaluated to true, however hasBoughtHouse_div_31 was not displayed'
    assert not True or driver.find_elements(By.ID, 'hasMaintLoan_div_95')[0].is_displayed(), 'true evaluated to true, however hasMaintLoan_div_95 was not displayed'
    assert not True or driver.find_elements(By.ID, 'hasSoldHouse_div_152')[0].is_displayed(), 'true evaluated to true, however hasSoldHouse_div_152 was not displayed'
    assert not (True and state['hasSoldHouse']) or driver.find_elements(By.ID, 'sellingPrice_div_244')[0].is_displayed(), 'true && hasSoldHouse evaluated to true, however sellingPrice_div_244 was not displayed'
    assert not (True and state['hasSoldHouse']) or driver.find_elements(By.ID, 'privateDebt_div_306')[0].is_displayed(), 'true && hasSoldHouse evaluated to true, however privateDebt_div_306 was not displayed'
    assert not (True and state['hasSoldHouse']) or driver.find_elements(By.ID, 'valueResidue_div_373')[0].is_displayed(), 'true && hasSoldHouse evaluated to true, however valueResidue_div_373 was not displayed'
    assert state['valueResidue'] == (state['sellingPrice'] - state['privateDebt']), ' valueResidue was not the same as sellingPrice - privateDebt'
