'''
projekt_3.py: druhý projekt do Engeto Online Python Akademie
author: Lukáš Smejkal
email: smejklukas@gmail.com
discord: Razee #6106
'''
import typing
import csv
import sys
import requests
from bs4 import BeautifulSoup

class Main_page:
    def __init__(self, url: str) -> None:
        """
        Initialize Main_page object.

        Args:
            url (str): The URL of the main page.

        Returns:
            None
        """
        self.url = url
        self.soup = BeautifulSoup(self.read_page(), "html.parser")
        table_url = self.find_table()
        self.data = []
        for number, turl in table_url.items():
            print(f"Download location with code {number}")
            data_page = Data_page(turl, number)
            self.data.append(data_page.return_data())

    def find_table(self) -> typing.Dict[str, str]:
        """
        Find table URLs from the main page.

        Returns:
            Dict[str, str]: A dictionary containing table numbers as keys and their URLs as values.
        """
        tables = self.soup.select("table.table")
        href: typing.Dict[str, str] = {}
        for table in tables:
            urls = table.find_all("td", class_="cislo")
            for urll in urls:
                url_url = urll.find_all("a")
                href[url_url[0].text] = url_url[0]["href"]
        return href
    
    def read_page(self) -> str:
        """
        Read the content of the web page.

        Returns:
            str: The content of the web page.
        """
        res = requests.get(self.url)
        htmlData = res.content
        return htmlData
    
    def save_file(self, name_of_file: str) -> str:
        """
        Save data to a CSV file.

        Args:
            name_of_file (str): The name of the CSV file to save the data to.

        Returns:
            str: The name of the saved file.
        """
        with open(name_of_file, "w", encoding="utf-8") as file:
            print("Saving file")
            writer = csv.DictWriter(file, fieldnames=self.fields(), lineterminator='\n')
            writer.writeheader()
            writer.writerows(self.data)
        return name_of_file
    
    def fields(self) -> typing.List[str]:
        """
        Get the list of field names for the CSV file.

        Returns:
            List[str]: The list of field names.
        """
        fields = ['code', 'location', 'registred', 'envelopes', 'valid']
        for line in self.data:
            keys = line.keys()
            for key in keys:
                if key not in fields:
                    fields.append(key)
        return fields


class Data_page(Main_page):
    def __init__(self, url: str, number: str) -> None:
        """
        Initialize Data_page object.

        Args:
            url (str): The URL of the data page.
            number (str): The code number.

        Returns:
            None
        """
        self.url = "https://volby.cz/pls/ps2017nss/" + url
        self.soup = BeautifulSoup(self.read_page(), "html.parser")
        self.data = {
            "code": number,
            "location": self.read_location()
        }
        self.read_votes()
        self.read_political_parties()
    
    def read_location(self) -> str:
        """
        Read the location.

        Returns:
            str: The location.
        """
        h3 = self.soup.find_all("h3")
        town = ""
        for heading in h3:
            if "Obec:" in heading.text:
                town = heading.text.replace("Obec: ", "")
                town = town.replace("\n", "")
                break
        return town

    def read_votes(self) -> bool:
        """
        Read the number of valid votes and registred.

        Returns:
            bool: True if the votes are successfully read, False otherwise.
        """
        table = self.soup.select("#ps311_t1")
        registred = table[0].find_all("td", headers="sa2")
        envelopes = table[0].find_all("td", headers="sa5")
        valid = table[0].find_all("td", headers="sa6")
        self.data["registred"] = registred[0].text
        self.data["envelopes"] = envelopes[0].text
        self.data["valid"] = valid[0].text
        return True

    def read_political_parties(self) -> bool:
        """
        Read the all political parties.

        Returns:
            bool: True if the political parties are successfully read, False otherwise.
        """
        tables = self.soup.select(".t2_470 table")
        for table in tables:
            lines = table.find_all("tr")
            for line in lines:
                name = line.find_all("td", class_="overflow_name")
                if len(name) == 0:
                    continue
                name = name[0].text
                votes = line.find_all("td", class_="cislo")
                votes = votes[1].text
                self.data[name] = votes
        return True
    
    def return_data(self) -> dict:
        """
        Return the collected data.

        Returns:
            dict: The collected data.
        """
        return self.data
    
def main() -> None:
    """
    Main function to run the program.

    Returns:
        None
    """
    if len(sys.argv) < 3:
        print("You wrote the wrong argument")
        return False
    url: str = str(sys.argv[1])
    name_of_file: str = str(sys.argv[2])
    if "https://volby.cz/pls/ps2017nss/ps3" in url and "csv" in name_of_file[-3:]:
        redpage = Main_page(url)
        redpage.save_file(name_of_file)

if __name__ == "__main__":
    main()
