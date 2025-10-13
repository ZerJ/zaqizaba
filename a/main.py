# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from PIL import Image
import ddddocr
import time
from typing import Union
import os, sys, uvicorn
from fastapi import FastAPI

bocr = ddddocr.DdddOcr()
app = FastAPI()


def t():
    img = Image.open("C:/work/py/pyProject/captcha.png")
    background = Image.new('RGB', img.size, (255, 255, 255))
    mask = img.split()[2]
    background.paste(img, mask)
    img = background

    ocr = ddddocr.DdddOcr()
    res = ocr.classification(img)



    print(res)
    return res


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/getCode/{fileName}")
def read_item(fileName):
    print(fileName)
    # path='c:/work/GolandProjects/melonTicket/'+fileName
    img = Image.open(fileName)
    background = Image.new('RGB', img.size, (255, 255, 255))
    mask = img.split()[3]
    background.paste(img, mask)
    img = background

    ocr = ddddocr.DdddOcr()
    res = ocr.classification(img)

    return {"code": res}


@app.get("/getAutoCode/{fileName}")
def auto(fileName):
    print(fileName)
    # path='c:/work/GolandProjects/melonTicket/'+fileName
    img = Image.open(fileName)
    background = Image.new('RGB', img.size, (255, 255, 255))
    mask = img.split()[2]
    background.paste(img, mask)
    img = background

    ocr = ddddocr.DdddOcr()
    res = ocr.classification(img)

    return {"code": res}


@app.get("/recognize/{fileName}")
def recognize(fileName):
    print(fileName)

    img = open(fileName, "rb").read()

    res = bocr.classification(img, png_fix=True)
    return {"code": res}


if __name__ == "__main__":

    name_app = os.path.basename(__file__)[0:-3]  # Get the name of the script
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)