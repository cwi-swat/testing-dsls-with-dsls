from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from more_itertools import collapse
import random   
import string

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


def derive_actionable_elements(driver, filter_elements):
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
    
    # Compute the list of elements that should be filtered
    filtered_elements = list(collapse([f(driver) for f in filter_elements]))
    
    # Derive only those that are displayed and enabled and should not be filtered
    visible_actionable_elements = [
    element for element in actionable_elements
    if element.is_displayed() and element.is_enabled() and not (element in filtered_elements)
    ]

    return visible_actionable_elements

def derive_actions(driver, filter_elements):
    """
    Derives all possible actions on a a set of actionable elements
    """
    visible_actionable_elements = derive_actionable_elements(driver, filter_elements)
    
    actions = []
    
    for element in visible_actionable_elements:
        
        element_type = element.get_attribute("type").lower()
                    
        if element_type == "checkbox" or element_type == "radio":
            actions.append(lambda el=element: (log("click", el), el.click()))
        elif element_type == "text":
            # For text, email, and password inputs: clear the textbox, send some random text, or both
            random_text = generate_random_text()
            random_number = generate_random_number()

            actions.append(lambda el=element: (log("clear+keys", el, random_text), el.clear(), el.send_keys(random_text)))
            actions.append(lambda el=element: (log("clear", el), el.clear()))
            actions.append(lambda el=element: (log("keys", el, random_text), el.send_keys(random_text)))
            actions.append(lambda el=element: (log("keys", el, random_number), el.send_keys(random_number)))
        elif element_type == "number":
            # For number inputs, send a random number, clear the box, or use the spinners with ARROW_UP or ARROW_DOWN
            random_text = generate_random_text()
            random_number = generate_random_number()
            
            actions.append(lambda el=element: (log("clear", el), el.clear()))
            actions.append(lambda el=element: (log("keys", el, random_number), el.send_keys(random_number)))
            actions.append(lambda el=element: (log("keys", el, random_text), el.send_keys(random_text)))
            actions.append(lambda el=element: (log("keys", el, "arrow UP"), el.send_keys(Keys.ARROW_UP)))
            actions.append(lambda el=element: (log("keys", el, "arrow DOWN"), el.send_keys(Keys.ARROW_DOWN)))
            actions.append(lambda el=element: (log("clear+keys", el, "arrow UP"), el.clear(), el.send_keys(Keys.ARROW_UP)))
        else:
            actions.append(lambda el=element: (log("click", el), el.click()))

    return actions

def log(action, element, *args):
    tag_name = element.tag_name
    element_id = element.get_attribute("id")
    element_class = element.get_attribute("class")
    element_type = element.get_attribute("type")
    info = f"Tag: {tag_name}, ID: {element_id}, Class: {element_class}, Type: {element_type}'"
   
    if (len(args)>0):
        print(action, " on ", info, " with", args)
    else:
        print(action, " on ", info)

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
    action()
    
def testar(url, num_runs, length_sequence, filter_elements, preparations, oracles):
    """
    Automated scriptless testing of a web application by executing sequences of actions on the System Under Test (SUT).

    Parameters:
    - url (str): The URL of the web application to be tested.
    - num_runs (int): The number of test runs to be executed. Each run is independent and represents a complete test session.
    - length_sequence (int): The length of the test sequence in each test run. This defines how many actions will be executed in a single run.
    - filter_elements (list of functions): A list of functions that take the driver as input and return an element that should not be considered when deriving act
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
            possible_actions = derive_actions(driver, filter_elements)
            
            #select actionable widgets
            selected_action = select_action(possible_actions)
            
            #execute action
            execute_action(selected_action)
            
            #check oracles
            for oracle in oracles:
                oracle(driver)
                
        # Close the SUT and browser
        driver.quit()
    
