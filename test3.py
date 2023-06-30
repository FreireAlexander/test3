"""
Create a program that collects articles from the https://www.bbc.com/news website. We are only interested in the sections "/business" (Business - without the "Features & Analysis", "Watch/Listen" and "Special reports" subsections) and "/technology" (Tech - without the Watch/Listen and Features & Analysis subsections).

A. The script should save every article to a separate JSON file, keeping only the article content (TITLE and BODY). All non-relevant content (external links, links to categories, CSS, scripts, multimedia content, etc.) should be removed.

B. Make sure to keep track of the downloaded content. If run again, the script should only collect articles we have not downloaded already.

C. (bonus) Containerize your Python application. Outputs should be outside the container.

The program should be written in Python and could use the Selenium framework.
In order to keep formatting, please encode your script in Base64 and paste it bellow or you can put a link to your code (https://pastebin.com/ for example or a link to GitHub, GitLab, etc.)
The scripts which are not working wouldn't be evaluated. Any comments are also welcome.
Writing a code following PEP 8 is highly recommended.
"""
import os
import json
import requests
from bs4 import BeautifulSoup

def collect_articles(url, downloaded_articles):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    business_tab = soup.find("a", href="/news/business")
    tech_tab = soup.find("a", href="/news/technology")

    if business_tab:
        business_url = "https://www.bbc.com" + business_tab["href"]
        business_articles = collect_articles_from_section(business_url, downloaded_articles)
    else:
        business_articles = []

    if tech_tab:
        tech_url = "https://www.bbc.com" + tech_tab["href"]
        tech_articles = collect_articles_from_section(tech_url, downloaded_articles)
    else:
        tech_articles = []

    collected_articles = business_articles + tech_articles
    return collected_articles


def collect_articles_from_section(url, downloaded_articles):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    article_div = soup.find("div", id="topos-component")
    curated_topic_div = soup.find("div", class_="nw-c-5-slice gel-layout gel-layout--equal b-pw-1280")

    if article_div:
        article_links = article_div.select("a[href^='/news/']")
    else:
        article_links = []

    if curated_topic_div:
        curated_topic_links = curated_topic_div.select("a[href^='/news/']")
        article_links.extend(curated_topic_links)

    collected_articles = []

    for link in article_links:
        article_url = "https://www.bbc.com" + link["href"]

        # Verificar si el artículo ya ha sido descargado
        if article_url in downloaded_articles:
            continue
        
        # Verificar si el enlace termina en "#comp-comments-button"
        if article_url.endswith("#comp-comments-button"):
            continue

        article_response = requests.get(article_url)
        article_response.raise_for_status()
        article_soup = BeautifulSoup(article_response.content, "html.parser")

        title_element = article_soup.find("h1", id="main-heading")
        body_elements = article_soup.find_all(attrs={"data-component": "text-block"})

        if title_element and body_elements:
            title = title_element.text.strip()
            body = " ".join([element.text.strip() for element in body_elements])

            article_data = {
                "title": title,
                "body": body
            }

            collected_articles.append(article_data)

            # Agregar el artículo a la lista de descargados
            downloaded_articles.append(article_url)

    return collected_articles








def load_downloaded_articles(log_file):
    downloaded_articles = []

    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            downloaded_articles = [line.strip() for line in file.readlines()]

    return downloaded_articles

def save_downloaded_articles(downloaded_articles, log_file):
    with open(log_file, "w") as file:
        for article_url in downloaded_articles:
            file.write(article_url + "\n")

def save_articles(articles, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for index, article in enumerate(articles, start=1):
        file_name = f"article_{index}.json"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, "w") as file:
            json.dump(article, file, indent=4)

def main():
    url = "https://www.bbc.com/news"
    output_dir = "articles"
    log_file = "downloaded_articles.txt"

    # Cargar los artículos ya descargados
    downloaded_articles = load_downloaded_articles(log_file)

    # Recopilar los artículos nuevos
    articles = collect_articles(url, downloaded_articles)

    # Guardar los artículos nuevos
    save_articles(articles, output_dir)

    # Guardar la lista actualizada de artículos descargados
    save_downloaded_articles(downloaded_articles, log_file)

if __name__ == "__main__":
    main()

