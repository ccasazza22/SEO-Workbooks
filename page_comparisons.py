import streamlit as st
from newspaper import Article, Config
import openai
import nltk
nltk.download('punkt')
from bs4 import BeautifulSoup
import requests
from transformers import GPT2Tokenizer

openai.api_key = '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'

# Initialize the GPT2 tokenizer
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

def getContent(url):
    config = Config()
    config.MAX_TEXT = 1000000
    article = Article(url, config=config)
    article.download()
    article.parse()
    article.nlp()
    text = article.text
    return text

def getContentBS(url):
    content = requests.get(url)
    soup = BeautifulSoup(content.text, 'html.parser')
    text = ""
    for p_tag in soup.find_all('p'):
        text += p_tag.get_text()
    return text

def compareURL(articles,site1,site2):
    prompt_start = (
            "You are an AI assistant highlighting the information differences between two articles. You are to help highlight what information is present in one article and not present in the other. Do not make up an answer if there are no significant differences")
    query = "What information does the " + site2 + " page have that the " + site1 +" page does not? Return the information in a bulleted list stating the main information gaps between the two pages."
    prompt =  [
                {"role": "system", "content": prompt_start},
                {"role": "assistant", "content": articles },
                {"role": "user", "content": query},
            ]
    response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-16k-0613',
            messages=prompt,
            temperature=0,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
    answers = response["choices"][0]["message"]["content"]
    return(answers)

# Streamlit Interface
st.title('Article Comparer')

url1 = st.text_input('Enter URL of first article:')
url2 = st.text_input('Enter URL of second article:')
site1 = st.text_input('Enter the name of site 1:')
site2 = st.text_input('Enter the name of site 2:')

if st.button('Compare'):
    if url1 and url2 and site1 and site2:
        # Scrape articles
        article1 = getContent(url1)
        article2 = getContent(url2)

        articles_dict = {
            site1: article1,
            site2: article2
          }

        truncated_articles = {}
        for title, content in articles_dict.items():
            tokens = tokenizer.encode(content, max_length=6000, truncation=True)
            truncated_content = tokenizer.decode(tokens)
            truncated_articles[title] = truncated_content

        articles = "\n\n".join([f"{title}: {content}" for title, content in truncated_articles.items()])

        # Use OpenAI API to compare 
        comparison_result = compareURL(articles, site1, site2)

        # Display comparison result
        st.write(comparison_result)
    else:
        st.write('Please enter both URLs and site names')
