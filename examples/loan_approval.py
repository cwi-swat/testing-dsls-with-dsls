def loan_approval_myql_oracle(driver):
    state = driver.execute_script('return $state;');
    
    assert not True or driver.find_elements(By.ID, 'fullName_div_25')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'age_div_70')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'hasLicense_div_104')[0].is_displayed
    assert not (True and (state['age'] < 18)) or driver.find_elements(By.ID, 'inSchool_div_183')[0].is_displayed
    assert not ((True and (state['age'] < 18)) and state['inSchool']) or driver.find_elements(By.ID, 'grade_div_258')[0].is_displayed
    assert not ((True and not (((state['age'] < 18)))) and ((state['age'] >= 18) and (state['age'] <= 65))) or driver.find_elements(By.ID, 'employed_div_360')[0].is_displayed
    assert not (((True and not (((state['age'] < 18)))) and ((state['age'] >= 18) and (state['age'] <= 65))) and state['employed']) or driver.find_elements(By.ID, 'jobTitle_div_445')[0].is_displayed
    assert not (((True and not (((state['age'] < 18)))) and ((state['age'] >= 18) and (state['age'] <= 65))) and state['employed']) or driver.find_elements(By.ID, 'yearsInJob_div_496')[0].is_displayed
    assert not (((True and not (((state['age'] < 18)))) and ((state['age'] >= 18) and (state['age'] <= 65))) and state['employed']) or driver.find_elements(By.ID, 'monthlySalary_div_578')[0].is_displayed
    assert not (((True and not (((state['age'] < 18)))) and ((state['age'] >= 18) and (state['age'] <= 65))) and state['employed']) or driver.find_elements(By.ID, 'monthlyExpenses_div_640')[0].is_displayed
    assert not (((True and not (((state['age'] < 18)))) and ((state['age'] >= 18) and (state['age'] <= 65))) and state['employed']) or driver.find_elements(By.ID, 'annualSavings_div_713')[0].is_displayed
    assert state['annualSavings'] == (((state['monthlySalary'] - state['monthlyExpenses'])) * 12)
    assert not (((True and not (((state['age'] < 18)))) and ((state['age'] >= 18) and (state['age'] <= 65))) and not ((state['employed']))) or driver.find_elements(By.ID, 'lookingForJob_div_822')[0].is_displayed
    assert not ((True and not (((state['age'] < 18)))) and not ((((state['age'] >= 18) and (state['age'] <= 65))))) or driver.find_elements(By.ID, 'retired_div_910')[0].is_displayed
    assert not (((True and not (((state['age'] < 18)))) and not ((((state['age'] >= 18) and (state['age'] <= 65))))) and state['retired']) or driver.find_elements(By.ID, 'yearsRetired_div_975')[0].is_displayed
    assert not (((True and not (((state['age'] < 18)))) and not ((((state['age'] >= 18) and (state['age'] <= 65))))) and state['retired']) or driver.find_elements(By.ID, 'annualPension_div_1039')[0].is_displayed
    assert not (((True and not (((state['age'] < 18)))) and not ((((state['age'] >= 18) and (state['age'] <= 65))))) and state['retired']) or driver.find_elements(By.ID, 'healthcareExpenses_div_1101')[0].is_displayed
    assert not (((True and not (((state['age'] < 18)))) and not ((((state['age'] >= 18) and (state['age'] <= 65))))) and state['retired']) or driver.find_elements(By.ID, 'netPension_div_1180')[0].is_displayed
    assert state['netPension'] == (state['annualPension'] - state['healthcareExpenses'])
    assert not True or driver.find_elements(By.ID, 'seniorDiscount_div_1296')[0].is_displayed
    assert state['seniorDiscount'] == ((state['age'] >= 65) and state['retired'])
    assert not True or driver.find_elements(By.ID, 'income_div_1398')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'monthlyDebts_div_1446')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'hasCoSigner_div_1501')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'loanAmount_div_1564')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'interestRate_div_1608')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'loanTerm_div_1666')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'totalInterest_div_1709')[0].is_displayed
    assert state['totalInterest'] == (lambda div: ((((state['loanAmount'] * state['interestRate']) * state['loanTerm'])) / div) if div != 0 else 0)(100)
    assert not True or driver.find_elements(By.ID, 'totalRepayment_div_1809')[0].is_displayed
    assert state['totalRepayment'] == (state['loanAmount'] + state['totalInterest'])
    assert not True or driver.find_elements(By.ID, 'monthlyPayment_div_1892')[0].is_displayed
    assert state['monthlyPayment'] == (lambda div: (state['totalRepayment'] / div) if div != 0 else 0)(((state['loanTerm'] * 12)))
    assert not True or driver.find_elements(By.ID, 'loanApproved_div_1984')[0].is_displayed
    assert state['loanApproved'] == ((((state['income'] > 50000) and (state['monthlyDebts'] < 10000))) or state['hasCoSigner'])
    assert not (True and state['loanApproved']) or driver.find_elements(By.ID, 'approvalMessage_div_2114')[0].is_displayed
    assert state['approvalMessage'] == 'Approved'
    assert not (True and not ((state['loanApproved']))) or driver.find_elements(By.ID, 'not_approvalMessage_div_2214')[0].is_displayed
    assert state['not_approvalMessage'] == 'Not Approved'
