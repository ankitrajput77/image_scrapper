from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests , os
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo 

logging.basicConfig(filename="log_file.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/result", methods= ['POST','GET'])
def index():
    if request.method == 'POST': 
        try:
            search = request.form['content'].replace(" ","")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"} # to avoid blockage  
            search_link = requests.get(f"https://www.google.com/search?q={search}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")
            search_content = search_link.content

            images_dir = "scrapped_image/"
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            
            search_html = bs(search_content , 'html.parser')
            images_link_list = search_html.find_all("img")

            # delete the header link
            del images_link_list[0]

            img_list =[]

            for index,image_tag in enumerate(images_link_list):
                image_url = image_tag['src']
                image_data = requests.get(image_url).content
                mydict={"Index":index,"Image":image_data}
                img_list.append(mydict)
                with open(os.path.join(images_dir, f"{search}_{images_link_list.index(image_tag)}.jpg"), "wb") as fp:
                    fp.write(image_data)
            
            # mongodb insert
            client = pymongo.MongoClient("mongodb+srv://rajput89207:rajput89207@cluster0.q4cidjn.mongodb.net/?retryWrites=true&w=majority")
            db = client['scap_img']
            review_col = db['images']
            review_col.insert_many(img_list)

            return "Success"
        except Exception as ep:
            logging.info(ep)
            return "error, try again"
    
    else:
        return render_template('index.html')
    



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)