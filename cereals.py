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
    
    # Wait for key product and price elements to appear
    try:
        sb.wait_for_element('//a[contains(@class, "h-12") and contains(@class, "text-black") and contains(@class, "line-clamp-2")]', timeout=30)
        sb.wait_for_element('//span[contains(@class, "text-base") and contains(@class, "leading-[1.5]") and contains(@class, "-tracking-[0.48px]")]', timeout=30)
    except:
        sb.refresh()
        time.sleep(10)
        sb.wait_for_element('//a[contains(@class, "h-12") and contains(@class, "text-black") and contains(@class, "line-clamp-2")]', timeout=30)
        sb.wait_for_element('//span[contains(@class, "text-base") and contains(@class, "leading-[1.5]") and contains(@class, "-tracking-[0.48px]")]', timeout=30)
    
    # IMPROVED: More robust category detection with multiple approaches
    category = "unknown"
    try:
        # Try direct find_element method (more similar to original implementation)
        elements = sb.find_elements(".text-lg.font-bold.text-black")
        if elements and len(elements) > 0:
            category = elements[0].text.strip()
            print(f"Found category using primary selector: {category}")
    except Exception as e:
        print(f"Primary category selector failed: {str(e)}")
        try:
            # Try breadcrumb navigation
            breadcrumbs = sb.find_elements(".breadcrumb-item a")
            if breadcrumbs and len(breadcrumbs) > 1:
                category = breadcrumbs[-2].text.strip()
                print(f"Found category using breadcrumbs: {category}")
        except Exception as e:
            print(f"Breadcrumb selector failed: {str(e)}")
            try:
                # Extract from URL as last resort
                url_parts = sb.get_current_url().split('/')
                for part in url_parts:
                    if 'food' in part or 'grocery' in part:
                        category = part.replace('-', ' ').title()
                        break
                print(f"Extracted category from URL: {category}")
            except:
                print("Failed to extract category")
                category = "unknown"
    
    # Rest of the loading_data function remains the same...
    # Extract product names and prices
    product_elements = sb.find_elements('//a[contains(@class, "h-12") and contains(@class, "text-black") and contains(@class, "mb-2")]')
    price_elements = sb.find_elements('//span[contains(@class, "text-base") and contains(@class, "leading-[1.5]") and contains(@class, "-tracking-[0.48px]")]')
    
    # ... existing code for processing products and prices ...

def getting_data(sb, url):
    # Load the URL using UC mode's reconnect capability for better stealth
    sb.uc_open_with_reconnect(url, 4)  # Attempt reconnection up to 4 times if needed
    sb.maximize_window()
    sb.execute_script("return document.body.scrollHeight")
    loading_data(sb)

    # IMPROVED: Loop through pagination using a more reliable approach
    page_num = 1
    while True:
        print(f"Processing page {page_num}")
        # Get all pagination tabs
        tabs = sb.find_elements('//a[contains(@class, "cursor-pointer") and contains(@class, "px-2") and contains(@class, "text-xs")]')
        
        # Use the original approach: Check if the last tab has ">" text
        next_button = None
        if tabs and len(tabs) > 0 and tabs[-1].text == ">":
            next_button = tabs[-1]
            
            # Get a reference product from current page
            try:
                first_product = sb.find_element('//a[contains(@class, "h-12") and contains(@class, "text-black") and contains(@class, "mb-2")]')
                
                # IMPORTANT: Wait for the button to be clickable before clicking
                sb.wait_for_element_to_be_clickable('//a[contains(@class, "cursor-pointer") and contains(@class, "px-2") and contains(@class, "text-xs") and text()=">"]', timeout=10)
                
                # Click and wait for page change
                print("Clicking next button")
                next_button.click()
                
                # Wait for the page to update (similar to waiting for staleness)
                sb.wait_for_staleness(first_product, timeout=15)
                
                # Add a short sleep to ensure page is fully loaded
                time.sleep(2)
                
                # Load data from the new page
                loading_data(sb)
                page_num += 1
            except Exception as e:
                print(f"Error during pagination: {str(e)}")
                break
        else:
            print("No more pages or next button not found")
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
