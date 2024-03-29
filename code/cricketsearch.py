import requests
import spacy
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_sm")

def scrape_winners(self, url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        winnersData = {}
        tables = soup.find_all("table", {"class": "wikitable"})

        for table in tables:
            rows = table.find_all("tr")
            header = rows[0].find_all(["th", "td"])
            year_index, winner_index = None, None

            for i, col in enumerate(header):
                if "Year" in col.text:
                    year_index = i
                elif "Winner" in col.text:
                    winner_index = i

            if year_index is not None and winner_index is not None:
                for row in rows[1:]:
                    columns = row.find_all(["td", "th"])
                    year = columns[year_index].text.strip()
                    winner = columns[winner_index].text.strip()

                    if year.isdigit():
                        winnersData[int(year)] = winner

        return winnersData
    else:
        print(
            f"Failed to retrieve data from {url}. Check the URL and try again.")
        return None


def answer_question(self, command, winnersData, t20_world_cup_url):

    doc = nlp(command)

    years = [ent.text for ent in doc.ents if ent.label_ == "DATE"]

    relevant_entities = [
        ent.text for ent in doc.ents if ent.label_ in ["ORG", "EVENT"]]

    if years and relevant_entities:
        year = int(years[0])
        cricket_winner = winnersData.get(year)
        t20winnersData = self.scrape_winners(t20_world_cup_url)
        t20_winner = t20winnersData.get(year)
        if cricket_winner is not None:
            answer = f"The ICC worldcup in {year} was won by {cricket_winner}."
        elif t20_winner is not None:
            answer = f"The ICC T20 Worldcup in {year} was won by {t20_winner}."
        else:
            answer = f"I don't have information about {relevant_entities[0]} winner in {year}."
    else:
        answer = "I couldn't identify the year or relevant entities in your question. Please provide a valid question."

    return answer
