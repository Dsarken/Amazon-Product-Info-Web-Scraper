import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


def scrape_urls(root, file_path):
    # Open the csv file and read the urls
    urls = pd.read_csv(file_path, header=None)[0]
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument('--log-level=3')
    options.add_argument("headless")
    with webdriver.Edge(options=options) as driver:
        results = []
        progress_bar = tqdm(urls, desc="Scraping Progress", colour="green")
        # Looping through each url
        for url in progress_bar:
            driver.get(url)
            progress_bar = tqdm(urls)
            # Wait for the important elements to load
            wait = WebDriverWait(driver, 2)
            try:
                product_title = driver.find_element(
                    By.CSS_SELECTOR, '#productTitle').text
            except TimeoutException:
                product_title = 'No Title'  # Assign no title if the title is not found

            try:
                # Try to find the price using the class names
                product_price_symbol = driver.find_element(
                    By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[1]/span[2]/span[1]').text
                product_price_whole = driver.find_element(
                    By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[1]/span[2]/span[2]').text
                product_price_fraction = driver.find_element(
                    By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[1]/span[2]/span[3]').text
                product_price = f'{product_price_symbol}{product_price_whole}.{product_price_fraction}'
            except NoSuchElementException:
                # If the class names are not found, try to find the price using an alternate XPATH
                try:
                    product_price = driver.find_element(
                        By.XPATH, '//*[@id="corePrice_desktop"]/div/table/tbody/tr/td[2]/span[1]/span[2]').text

                except NoSuchElementException:
                    try:  # If the product isn't available it will replace the price
                        product_price = driver.find_element(
                            By.XPATH, '//*[@id="price"]').text
                    except NoSuchElementException:
                        try:  # Try method for books, automatically retrieves price of paperback
                            product_price = driver.find_element(
                                By.XPATH, '//*[@id="a-autoid-4-announce"]/span[2]/span').text
                            if product_price == ' $0.00 ':
                                product_price = 'Free' + ' Kindle Edition'
                            else:
                                product_price = product_price + ' Kindle Edition'
                        except NoSuchElementException:
                            try:  # Try method if product is unavailable
                                product_price = driver.find_element(
                                    By.XPATH, '//*[@id="availability"]/span').text
                            except NoSuchElementException:
                                product_price = 'Not Available'
            try:
                product_rating = driver.find_element(
                    By.CSS_SELECTOR, '#acrCustomerReviewText').text
            except NoSuchElementException:
                # If rating is not found, print a warning message
                print(f'Number of Reviews not found for {url}')
                product_rating = ''

            try:
                product_num_stars = driver.find_element(
                    By.XPATH, '//*[@id="reviewsMedley"]/div/div[1]/span[1]/span/div[2]/div/div[2]/div/span/span').text
            except NoSuchElementException:
                # If number of stars is not found, print a warning message
                print(f'Number of Stars not found for {url}')
                product_num_stars = ''

            # Append the product info to the results list
            results.append({
                'Product Title': product_title,
                'Product Price': product_price,
                'Number of Ratings': product_rating,
                'Number of Stars': product_num_stars
            })
            progress_bar.update(1)
        progress_bar.close()

        # Convert the results list to a DataFrame and write it to a CSV file
        df = pd.DataFrame(results)
        try:
            df.to_csv('product_data.csv', index=False)
        except Exception as e:
            print(f'Error writing to CSV file: {e}')
        popup = tk.Toplevel(root)
        popup.title("Pop up")
        popup.geometry("400x200")
        popup_label = tk.Label(
            popup, text="Scraping Finished! Check product_data.csv")
        popup_label.pack(pady=20)
        popup_button = ttk.Button(popup, text="OK", command=popup.destroy)
        popup_button.pack(pady=10)


def select_file(root):
    # Use the askopenfilename function to show the file dialog
    file_path = fd.askopenfilename(title="Select a file", initialdir="/",
                                   filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
    # Check if a file is selected
    if file_path:
        # Print the file path
        print(file_path)
        scrape_urls(root, file_path)
    else:
        # Print a message if no file is selected
        print("No file selected")


def main():
    # Creating the GUI
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("vista")
    root.title("Amazon Product Scraper")
    root.geometry('300x200')

    # Creating a label and entry for the url input
    instructions_text = ttk.Label(
        root, text="This application scrapes product pages on Amazon\nPlease select a csv file to begin scraping:", font=("Arial", 12))
    # Starting the GUI event loop
    instructions_text.pack()

    # Creating a button to start the scraping process
    select_file_button = ttk.Button(
        text="Choose CSV file", command=lambda: select_file(root))
    select_file_button.pack()

    # Main loop for window
    root.mainloop()


if __name__ == "__main__":
    main()
