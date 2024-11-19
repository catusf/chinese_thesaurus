import requests

# URL of the webpage
url = "https://jyc.kxue.com/m/list/list/a.html"

# Fetch the content
response = requests.get(url)
response.encoding = 'gbk'  # Set encoding to GBK

# Save the HTML content as UTF-8
# with open("output.html", "w", encoding="utf-8") as file:
#     file.write(response.text)

print("HTML file has been saved in UTF-8 encoding as 'output.html'.")
with open("output.html", "r", encoding="utf-8") as file:
    text= file.read()
    print(text.find('ao.html'))
    

