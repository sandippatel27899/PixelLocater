import os
import pickle
import base64
import traceback
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.preprocessing.image import ImageDataGenerator


base_model = VGG16(weights='imagenet', include_top=False)


def search_similar_images(user_name, input_image_path, top_k: int = 200):
    result_images = []
    
    try:
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
        
        for record in sorted_images:
            try:
                file_name = record[0]
                similarity = float(record[1])   #TODO: use later in UI
                image_path = f"/media/images/user_{user_name}/{file_name}"
                result_images.append(tuple((image_path, file_name)))
            except Exception as e:
                print("failed for ..", record, e)
    except Exception as e:
        print("Failure for ", user_name)
        print(traceback.format_exc())

    return result_images

def add_features(user_name, image_path, filename):
        
    datagen = ImageDataGenerator(rotation_range=20, zoom_range=0.2, preprocessing_function=preprocess_input)

    
    img = image.load_img(image_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    # Apply data augmentation (rotation and zoom)
    augmented_images = []
    for batch in datagen.flow(x, batch_size=1):
        augmented_images.append(batch.reshape(224, 224, 3))
        if len(augmented_images) == 7:
            break

    # Extract features from each augmented image
    aggregated_features = np.zeros((1, 7, 7, 512))
    for augmented_img in augmented_images:
        features = base_model.predict(np.expand_dims(augmented_img, axis=0))
        aggregated_features += features

    aggregated_features /= len(augmented_images)
    
    with open(f"features/{user_name}/features.pkl", 'rb') as f: 
        features_dict = pickle.load(f)    
    features_dict[filename] = aggregated_features.flatten()
    
    with open(f"features/{user_name}/features.pkl", 'wb') as f: 
        pickle.dump(features_dict, f)


