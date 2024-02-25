import os
import pickle
import base64
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from sklearn.metrics.pairwise import cosine_similarity


base_model = VGG16(weights='imagenet', include_top=False)


def search_similar_images(user_name, input_image_path, top_k: int = 200):
    with open(f"features/{user_name}/features.pkl", 'rb') as f: 
        features_dict = pickle.load(f)
    
    query_img = image.load_img(input_image_path, target_size=(224, 224))
    query_img_array = image.img_to_array(query_img)
    query_img_array = np.expand_dims(query_img_array, axis=0)
    query_img_array = preprocess_input(query_img_array)

    query_features = base_model.predict(query_img_array).flatten()

    similarities = {}
    for filename, features in features_dict.items():
        similarities[filename] = cosine_similarity([query_features], [features])[0][0]

    sorted_images = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    result_images = []
    for record in sorted_images:
        try:
            file_name = record[0]
            similarity = float(record[1])   #TODO: use later in UI
            image_path = f"/media/images/user_{user_name}/{file_name}"
            result_images.append(tuple((image_path, file_name)))
        except Exception as e:
            print("failed for ..", record, e)

    return result_images


