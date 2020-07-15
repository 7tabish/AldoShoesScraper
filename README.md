# AldoShoesScraper
AldoshoesScraper to scrap information of all the products of men, women and kids from https://www.aldoshoes.com/us/en_US
## Extracted data format
{<br />
product_name:  ["Low top sneaker", "Hermond"],<br />
original_price: $70,<br />
reduced_price: $34.97,<br />
color: Black Synthetic Smooth,<br />
size: ["7.5", "9", "9.5", "11"],<br />
style_note: 'Blur the lines between casual and sporty and step into this comfortable sneaker/derby shoe mashup. Finished manmade materials, piped seams and rubber soles, it's a smart style for the guy on-the-go.',<br />
details: ["Low top sneaker", "Round toe", "Laces closure"],<br />
materials: ["Upper: Synthetic", "Sole: Leather"],<br />
measurements: None,<br />
url: 'https://www.aldoshoes.com/us/en_US/hermond-black-synthetic-smooth/p/12648163'<br />
}<br />


## How to run crawler
1. cd aldoshoes
2. scrapy crawl aldoshoes -o outputFilename.json
