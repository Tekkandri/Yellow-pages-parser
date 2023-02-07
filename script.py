from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import csv
import re

url = "http://ryp.us//index.php?GroupID=1000"
start_of_url = "http://ryp.us//"

opt = webdriver.ChromeOptions()
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.124 YaBrowser/22.9.4.863 Yowser/2.5 Safari/537.36'
opt.add_argument(f"user-agent={ua}")

driver = webdriver.Chrome("C:\\Users\\pc\\PycharmProjects\\AvitoToCSV\\chromedriver.exe")

lst = {}

sep = ";"

def get_line(records):
    for record in records:
        Record = {
            'name': "",
            'tel': [],
            'cel': [],
            'web': "",
            'email': "",
            'address': [],
            'town': [],
            'state': [],
            'zip': [],
        }

        str = record.get_text(sep)
        str_list = str.split(sep)
        str_list.remove(str_list[0])
        str_list.remove(str_list[0])
        str_list.remove(str_list[1])

        for substring in str_list:
            regexp = re.compile('[A-Z]{2} $\d{5}')
            regexp2 = re.compile(', [A-Z]{2}')
            Record["name"] = str_list[0]
            if substring.find("Tel:") != -1 or substring.find("T+F:") != -1:
                if len(Record["tel"]) == 0:
                    Record["tel"].append(substring.split()[1])
                elif len(Record["address"]) == len(Record["tel"]):
                    Record["tel"][len(Record["address"]) - 1] += substring.split()[1] + sep
                else:
                    Record["tel"][len(Record["address"])] += sep+substring.split()[1]
            elif substring.find("Cell:") != -1:
                if len(Record["cel"]) == 0:
                    Record["cel"].append(substring.split()[1])
                elif len(Record["address"]) == len(Record["cel"]):
                    Record["cel"][len(Record["address"]) - 1] += substring.split()[1] + sep
                else:
                    Record["cel"][len(Record["address"])] += sep + substring.split()[1]
            elif substring.find("@") != -1:
                Record["email"] = substring
            elif substring.find("www.") != -1 or substring.find(".com") != -1 or substring.find("WWW.") != -1 or substring.find(".net") != -1 or substring.find(".org") != -1 or substring.find(".edu") != -1or substring.find(".tv") != -1:
                Record["web"] = substring
            elif regexp.findall(substring):
                Record["town"].append(substring.split(",")[0])
                Record["state"].append(substring.split(",")[1].split()[0])
                Record["zip"].append(substring.split(",")[1].split()[1])
            elif regexp2.findall(substring):
                Record["town"].append(substring.split(",")[0])
                Record["state"].append(substring.split(",")[1])
                Record["zip"].append("")
            elif substring != str_list[0] and substring != " " and substring.find("Fax:") == -1 and substring.find("Home:") == -1:
                Record["address"].append(substring)
                Record["tel"].append("")
                Record["cel"].append("")

        if len(Record["address"]) != 0:
            for i in range(len(Record["address"])):
                cel_prime = ""
                cel_second = ""
                tel_prime = ""
                tel_second = ""
                if len(Record["cel"]) != 0:
                    if Record["cel"][i].find(sep) != -1:
                        cel_prime = Record["cel"][i].split(";")[0]
                        cel_second = Record["cel"][i].split(";")[1]
                    else:
                        cel_prime = Record["cel"][i]

                if len(Record["tel"]) != 0:
                    if Record["tel"][i].find(sep) != -1:
                        tel_prime = Record["tel"][i].split(";")[0]
                        tel_second = Record["tel"][i].split(";")[1]
                    else:
                        tel_prime = Record["tel"][i]

                line = [key, Record["name"], tel_prime, cel_prime, Record["web"],
                    Record["email"], Record["address"][i], Record["town"][i], Record["state"][i], Record["zip"][i],
                    tel_second, cel_second, start_of_url+lst[key]]
                file_writer.writerow(line)
        else:
            cel_prime = ""
            cel_second = ""
            tel_prime = ""
            tel_second = ""
            if len(Record["cel"]) != 0:
                if Record["cel"][0].find(sep) != -1:
                    cel_prime = Record["cel"][0].split(";")[0]
                    cel_second = Record["cel"][0].split(";")[1]
                else:
                    cel_prime = Record["cel"][0]

            if len(Record["tel"]) != 0:
                if Record["tel"][0].find(sep) != -1:
                    tel_prime = Record["tel"][0].split(";")[0]
                    tel_second = Record["tel"][0].split(";")[1]
                else:
                    tel_prime = Record["tel"][0]

            line = [key, Record["name"], tel_prime, cel_prime, Record["web"],
                    Record["email"], Record["address"], Record["town"], Record["state"], Record["zip"],
                    tel_second, cel_second, start_of_url+lst[key]]
            file_writer.writerow(line)


try:
    driver.get(url)
    sleep(3)

    soup = BeautifulSoup(driver.page_source, "lxml")
    items = soup.findAll("a", {"class": "CategoryLink"})
    for item in items:
        lst[item.text] = item["href"]
    key_lst = list(lst.keys())

    for i in range(len(key_lst)):
        if key_lst[i] != " Real Estate Agencies":
            lst.pop(key_lst[i])

    with open("categories_real_estate.csv", mode="w", encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter=";", lineterminator="\r")
        file_writer.writerow(
                ["Category", "Name", "Tel-prime", "Cel-prime", "web", "e-mail", "Address", "Town/City", "State", "Zip",
                 "Tel-second", "Cel-second","Link"])

        for key in lst:
            driver.get(start_of_url+lst[key])
            sleep(3)
            soup = BeautifulSoup(driver.page_source, "lxml")
            records = soup.findAll("div", {"class": "Record"})
            get_line(records)
            if soup.find("div", {"RightListInner"}).find("div", {"id": "pagingControls"}):
                pages = soup.find("div", {"id": "pagingControls"}).findAll("a", {"class": "PageLink"})
                for i in range(len(pages)):
                    driver.get(start_of_url + pages[i]["href"])
                    sleep(3)
                    soup = BeautifulSoup(driver.page_source, "lxml")
                    records = soup.findAll("div", {"class": "Record"})
                    get_line(records)

except Exception as e:
    print(e)

finally:

    driver.close()
    driver.quit()