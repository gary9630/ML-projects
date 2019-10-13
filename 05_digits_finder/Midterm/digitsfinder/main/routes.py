from __future__ import division, print_function
# -*- coding: UTF-8 -*-
import sys
import os
import glob
import re
import numpy as np
import cv2

# Flask utils
from flask import Flask, redirect, url_for, render_template, request, Blueprint, jsonify
from digitsfinder.models import Post
from werkzeug.utils import secure_filename

# payments
import paypalrestsdk


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/index")
def index():
    return render_template('index.html', title='Digits Finder')

@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

# Model saved with Keras model.save()
#MODEL_PATH = 'models/your_model.h5'


#import HyperLPRLite as pr
from .. import HyperLPRLite as pr

#model = pr.LPR("model/cascade.xml","model/model12.h5","model/ocr_plate_all_gru.h5")

#print('Model loaded. Check http://127.0.0.1:5000/')


def model_predict(img_path, model):
    preds = []
    scores = []

    image = cv2.imread(img_path)

    for pstr,confidence,rect in model.SimpleRecognizePlateByE2E(image):
        if confidence>0.7:
            preds.append(pstr)
            scores.append(confidence)

    return preds, scores



@main.route('/demo', methods=['GET'])
def demo():
    # demo page
    return render_template('demo.html')


@main.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['image']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)


        model = pr.LPR("model/cascade.xml","model/model12.h5","model/ocr_plate_all_gru.h5")

        # Make prediction
        preds, scores = model_predict(file_path, model)


        if len(preds) > 0:
            result = preds[0] + '\n Confidence:' + str(round(scores[0],3))
        else:
            result = 'Sorry, Digits Finder fail this time... We are keeping our models improving, stay tuned!'
        return result
    return None





@main.route("/news")
def news():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('news.html', posts=posts)

@main.route("/about")
def about():
    return render_template('about.html', title='About')



paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AcdRTNZT4DBbcdm_livb8UTnvE7z_zTO5en8fxKK99HVseVdK3Kd6YrmdP29ij_YLJk12He7STb7JoWO",
  "client_secret": "EC6656KOKjLVmBXOKcpUMIMot4MMGQlBddGgMGlbmNE19D1JN5uz_yP8NItthP1WXMz8HQyhkvcco02L" })

@main.route('/price')
def price():
    return render_template('price.html')

@main.route('/price/payment', methods=['POST'])
def payment():

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "testitem",
                    "sku": "12345",
                    "price": "10.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "10.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        print('Payment success!')
    else:
        print(payment.error)

    return jsonify({'paymentID' : payment.id})

@main.route('/price/execute', methods=['POST'])
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)

    return jsonify({'success' : success})
