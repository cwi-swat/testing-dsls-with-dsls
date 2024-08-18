from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import random   
import string
import os

def start_SUT_and_get_driver(website_url,preparations):
    """
    Starts up the System Under Test (SUT) by starting a Chrome WebDriver instance and
    performing any necessary preparation steps.

    Parameters:
    - website_url (str): The URL of the web application to be tested. This is where the WebDriver will navigate after starting.
    - preparations (list of functions): A list of preparation steps (functions) to be executed once the WebDriver is
      initialized and navigated to the target URL. These steps might include actions like logging in or setting up the
      initial application state. Each function in the list should accept the WebDriver instance as an argument.

    Returns:
    - WebDriver instance (driver) that can be used for further interactions within the SUT.
    """
    
    # Create ChromeOptions instance
    chrome_options = Options()
    
    # Add the desired argument
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    
    # Initialize the WebDriver with the specified options
    driver = webdriver.Chrome(options=chrome_options)
    
    # Navigate to the URL of the application to be tested
    driver.get(website_url)
    
    # Execute the necesary preparations (i.e. login, etc.) if any.
    for prepare in preparations:
        prepare(driver)
    
    return driver


def derive_actions(driver):
    """
    Derives a list of actionable elements (widgets) from the current state of the web application.
    
    """
     
    # Define the selectors for actionable elements
    selectors = [
        "a",               # Links
        "button",          # Buttons
        "input",           # Input fields (text, checkbox, radio, etc.)
        "select",          # Dropdowns
        "[onclick]",       # Elements with onclick attributes (custom clickable elements)
        "[role='button']"  # Elements with a role attribute as buttons (often used in modern UIs)
    ]

    # Combine all the selectors into a single CSS selector
    all_selectors = ", ".join(selectors)

    # Find all actionable elements
    actionable_elements = driver.find_elements(By.CSS_SELECTOR, all_selectors)
    
    # Derive only those that are displayed and enabled
    visible_actionable_elements = [
    element for element in actionable_elements
    if element.is_displayed() and element.is_enabled()
    ]

    return visible_actionable_elements


def generate_random_text(length=10):
    """
    Function to generate random text string
    """
    
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def generate_random_number(min_value=1, max_value=100):
    """
    Function to generate random number
    """
    return str(random.randint(min_value, max_value))
       
def select_action(possible_actions):
    """
    Returns a randomly selected element from a list 

    """
    selected_action_id = int(random.randint(0, len(possible_actions)-1))
    return possible_actions[selected_action_id]


def execute_action(action):
    """
    Executes an action on a given WebElement based on its type (e.g., click, input text, select a checkbox).

    """
    
    element_type = action.get_attribute("type").lower()
    
    if element_type == "checkbox" or element_type == "radio":
        # For checkbox and radio buttons, simply click them
        action.click()
    elif element_type == "text":
        # For text, email, and password inputs, send some random text
        random_text = generate_random_text()
        action.clear()  # Clear existing text (if any)
        action.send_keys(random_text)
    elif element_type == "number":
        # For number inputs, send a random number
        random_number = generate_random_number()
        action.clear()  # Clear existing value (if any)
        action.send_keys(random_number)
    else:
        action.click()
    
def testar(url, num_runs, length_sequence, preparations, oracles):
    """
    Automated scriptless testing of a web application by executing sequences of actions on the System Under Test (SUT).

    Parameters:
    - url (str): The URL of the web application to be tested.
    - num_runs (int): The number of test runs to be executed. Each run is independent and represents a complete test session.
    - length_sequence (int): The length of the test sequence in each test run. This defines how many actions will be executed in a single run.
    - preparations (list of functions): A list of preparation steps to be performed before starting each test run. These could include steps like logging in or setting up the initial state.
    - oracles (list of functions): A list of oracle functions used to check the correctness or expected outcomes after actions are performed. These functions should take the driver as input and perform assertions or checks.

    The inner loop of the function automates the TESTAR loop:
    1. Derive all actionable elements in the current state
    2. Select one
    3. Execute the corresponding action
    4. Check the state with the oracles
    """
    
    # Outer loop, that iterates through the number of test runs specified
    for i in range(0, num_runs):
        # Start the SUT and get the driver
        driver = start_SUT_and_get_driver(url, preparations)
        
        # Inner loop that executes the test sequence with the specified number of actions (length_sequence)
        for j in range(0, length_sequence):
            #derive the actionable widgets in the current state
            possible_actions = derive_actions(driver)
            
            #select actionable widgets
            selected_action = select_action(possible_actions)
            
            #execute action
            execute_action(selected_action)
            
            #check oracles
            for oracle in oracles:
                oracle(driver)
                
        # Close the SUT and browser
        driver.quit()
    
