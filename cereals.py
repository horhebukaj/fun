import time
import random
import pandas as pd
from datetime import date
from seleniumbase import SB

# Global lists for storing scraped data
product_names = []
prices = []
categories = []

def get_text_safe(element, retries=3):
    """Attempt to extract text from an element with retries."""
    for _ in range(retries):
        try:
            text = element.text.strip()
            if text:
                return text
        except Exception:  # Handling all exceptions, not just StaleElementReferenceException
            time.sleep(0.5)  # Brief pause before retrying
    return ""

def loading_data(sb):
    # Short random sleep to mimic human behavior and allow page updates
    time.sleep(random.randint(1, 3))
    
    # Wait for key product and price elements to appear using the exact same XPaths
    try:
        sb.wait_for_element('//a[contains(@class, "h-12") and contains(@class, "text-black") and contains(@class, "line-clamp-2")]', timeout=30)
        sb.wait_for_element('//span[contains(@class, "text-base") and contains(@class, "leading-[1.5]") and contains(@class, "-tracking-[0.48px]")]', timeout=30)
        sb.wait_for_element('//a[contains(@class, "h-12") and contains(@class, "text-black") and contains(@class, "line-clamp-2")]', timeout=30)
    except:
        sb.refresh()
        time.sleep(10)
        sb.wait_for_element('//a[contains(@class, "h-12") and contains(@class, "text-black") and contains(@class, "line-clamp-2")]', timeout=30)
        sb.wait_for_element('//span[contains(@class, "text-base") and contains(@class, "leading-[1.5]") and contains(@class, "-tracking-[0.48px]")]', timeout=30)
    
    # Using the exact same category selector that worked before
    try:
        # Important: Using find_element to get direct DOM element, NOT get_text
        category = sb.execute_script("return document.querySelector('.text-lg.font-bold.text-black').textContent.trim();")
    except:
        category = "unknown"
    print(category)

    # Extract product and price elements using the same XPaths
    product_elements = sb.find_elements('//a[contains(@class, "h-12") and contains(@class, "text-black") and contains(@class, "mb-2")]')
    price_elements = sb.find_elements('//span[contains(@class, "text-base") and contains(@class, "leading-[1.5]") and contains(@class, "-tracking-[0.48px]")]')

    product_texts = []
    for product in product_elements:
        text = get_text_safe(product)
        if text:
            product_texts.append(text)
            print(text)

    price_texts = []
    for price in price_elements:
        text = get_text_safe(price)
        if text:
            price_texts.append(text)

    # Append the extracted texts to the global lists
    for text in product_texts:
        product_names.append(text)
        categories.append(category)
    for text in price_texts:
        prices.append(text)

def getting_data(sb, url):
    # Load the URL using SeleniumBase's functions
    sb.open(url)
    sb.maximize_window()
    sb.execute_script("return document.body.scrollHeight")
    loading_data(sb)

    # Loop through pagination
    while True:
        # Get all pagination tabs using the same XPath
        tabs = sb.find_elements('//a[contains(@class, "cursor-pointer") and contains(@class, "px-2") and contains(@class, "text-xs")]')
        
        if tabs:
            # Get the text content of the last tab using JavaScript
            last_tab_text = sb.execute_script("return arguments[0].textContent.trim()", tabs[-1])
            
            # Check if it contains the ">" character
            if ">" in last_tab_text:
                # Store a reference element for staleness check
                old_product = sb.find_element('//a[contains(@class, "h-12") and contains(@class, "text-black") and contains(@class, "mb-2")]')
                
                # Click the next tab
                tabs[-1].click()
                
                # Wait for the page to change
                sb.wait_for_staleness(old_product, timeout=30)
                
                # Load data from the new page
                loading_data(sb)
                time.sleep(2)
            else:
                break
        else:
            break

# Main execution
with SB(uc=True, headless=True) as sb:
    # Configure window size
    sb.driver.set_window_size(1920, 1200)
    
    # The base URL
    url = "https://www.luluhypermarket.com/en-ae"
    sb.open(url)
    sb.maximize_window()
    
    # Process list of URLs
    ids_to_extract = ["https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-breakfast-spreads-oats-bars/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-breakfast-spreads-cereals/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-breakfast-spreads-jams-spreads/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-breakfast-spreads-honey/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-canned-foods-canned-vegetables/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-canned-foods-canned-beans/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-canned-foods-canned-meat/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-canned-foods-canned-fish/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-rice-pasta-noodles-rice/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-rice-pasta-noodles-pasta-noodles/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-rice-pasta-noodles-soups/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-beverage-water/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-beverage-tea/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-beverage-coffee/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-beverage-softdrinks-juices/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-home-baking-sweeteners-home-baking/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-home-baking-sweeteners-sugar-other-sweeteners/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-biscuits-confectionery-biscuits/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-biscuits-confectionery-chocolates/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-biscuits-confectionery-candy/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-biscuits-confectionery-gums-mints/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-world-foods-arabic-food/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-world-foods-filipino-food/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-world-foods-indian-food/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-world-foods-korean-food/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-dressings-table-sauces-sides-salad-dressing-table-sauces/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-dressings-table-sauces-sides-bottled-olives-pickles/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-chips-snacks-chips/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-chips-snacks-snacks/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-chips-snacks-popcorn/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-chips-snacks-nuts-dates/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-frozen-food-ice-cream/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-frozen-food-ready-meals-snacks/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-frozen-food-burgers/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-frozen-food-pastry-sheets-dough/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-cooking-ingredients-cooking-sauces-cream/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-cooking-ingredients-oils-ghee/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-cooking-ingredients-salt-pepper/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-cooking-ingredients-pulses/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-speciality-food-speciality-food-organic/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-speciality-food-speciality-food-gluten-free/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-speciality-food-speciality-food-sugar-free/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-speciality-food-speciality-food-vegan/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-dairy-eggs-cheese-fresh-milk/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-beverage-long-life-milk/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-dairy-eggs-cheese-laban-flavoured-milk/",
    "https://gcc.luluhypermarket.com/en-ae/grocery-food-cupboard-beverage-dairy-alternatives/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-dairy-eggs-cheese-yoghurt-chilled-desserts/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-dairy-eggs-cheese-fresh-cream/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-dairy-eggs-cheese-cheese/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-dairy-eggs-cheese-butter-margarine/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-dairy-eggs-cheese-eggs/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-bakery-bread-basket/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-bakery-cake-house/",
    "https://gcc.luluhypermarket.com/en-ae/fresh-food-bakery-arabic-bakery/"]
    block_2= ["https://gcc.luluhypermarket.com/en-ae/fresh-food-bakery-asian-bakery/","https://gcc.luluhypermarket.com/en-ae/fresh-food-bakery-croissant-and-savories-corner/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-bakery-healthy-bake-shop/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-delicatessen-cold-cuts-prepacked-cooked-meats/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-delicatessen-olives-pickles/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-delicatessen-indian-ready-mix/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-delicatessen-oriental-food/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-delicatessen-hummus-labneh-other-prepacked-deli/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fruits-vegetables-fruits/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fruits-vegetables-vegetables/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fruits-vegetables-salad-vegetables/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fruits-vegetables-fruit-cuts/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-meat-poultry-fresh-beef-veal/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-meat-poultry-fresh-lamb/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-meat-poultry-fresh-chicken/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-meat-poultry-other-fresh-meat/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-fish-seafoods-fresh-fish/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-fish-seafoods-shellfish-speciality-seafoods/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-fish-seafoods-smoked-fish-dried-fish/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-on-the-go-meals-desserts-sweets-chilled-meals/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-juice-salads-salads-pizzas/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-juice-salads-sandwiches-burgers/",
        "https://gcc.luluhypermarket.com/en-ae/fresh-food-fresh-juice-salads-fresh-juice/",
        "https://gcc.luluhypermarket.com/en-ae/Pantry-Essentials/c/CPUAE0182",
        "https://gcc.luluhypermarket.com/en-ae/Frozen-Foods/c/CPUAE0180"]
    ids_to_extract = ids_to_extract + block_2
    
    for povezava in ids_to_extract:
        getting_data(sb, povezava)
    
    # Now you can work with the extracted data
    print(product_names)
    print(prices)
    print(categories)
    
    # Create and save dataframe
    dataframe = pd.DataFrame({
        "product_names": product_names,
        "prices": prices,
        "category": categories
    })
    dataframe = dataframe.set_index("product_names")
    
    today = date.today()
    filename = f"data_new_{today.day}{today.month}{today.year}.csv"
    dataframe.to_csv(filename)  # Changed path for GitHub Actions environment
