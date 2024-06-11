
import requests
from fastapi import FastAPI, HTTPException
from PIL import Image
from io import BytesIO
import os
import base64

app = FastAPI()

@app.get('/')
def opening():
    return {'message': 'Stage 1 complete'}


token = '<Token>'
repo_name = '<Repository name>'
github_api_url = "https://api.github.com"

@app.get('/fetch_img')
def fetch_img():
    try:
        #featching images
        repo_url = f"{github_api_url}/repos/{repo_name}/contents"
        autho_tokn = {'Authorization': f'token {token}'}
        response = requests.get(repo_url, headers=autho_tokn)
        response.raise_for_status()
        files = response.json()
        img_urls = [i['download_url'] for i in files if i['name'].endswith(('png', 'jpg', 'jpeg'))]
        

        #webP conversion
        converted_images = []
        for i in img_urls:
            response = requests.get(i)
            img = Image.open(BytesIO(response.content))

            webp_img = BytesIO()
            img.save(webp_img, format="WEBP")
            webp_img.seek(0)
            img_name = os.path.splitext(os.path.basename(i))[0] + '.webp'

            #Uploading img to repository
            upload_url = f"{github_api_url}/repos/{repo_name}/contents/{img_name}"
            data = {
                'message': 'Add converted WebP image',
                'content': base64.b64encode(webp_img.getvalue()).decode('utf-8'),
                'branch': 'main'
            }
            response = requests.put(upload_url, headers=autho_tokn, json=data)
            response.raise_for_status()
            converted_images.append(img_name)

        return {'converted_images': converted_images}

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except Exception as e:
        print(f"An error occurred: {e}")  
        raise HTTPException(status_code=500, detail=str(e))