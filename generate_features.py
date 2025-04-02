import os
import pickle
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import gc
from tqdm import tqdm
from PIL import Image


Image.MAX_IMAGE_PIXELS = None

# Load the pre-trained ResNet50 model (for example)
base_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def create_features(user_name, image_paths):
    # Create a new features dictionary to store features
    features_dict = {}
    
    # Initialize the data generator (for data augmentation if needed)
    datagen = ImageDataGenerator(rotation_range=20, zoom_range=0.2, preprocessing_function=preprocess_input)
    
    # Iterate over all image paths
    for image_path in tqdm(image_paths):
        # Load and preprocess the image
        img = image.load_img(image_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        
        # Apply data augmentation (if necessary)
        augmented_images = []
        for batch in datagen.flow(x, batch_size=1):
            augmented_images.append(batch.reshape(224, 224, 3))
            if len(augmented_images) == 7:  # Generate 7 augmented images
                break
        
        # Extract features from each augmented image
        aggregated_features = np.zeros((1, 7, 7, 512))
        for augmented_img in augmented_images:
            features = base_model.predict(np.expand_dims(augmented_img, axis=0))
            aggregated_features += features

        # Average the aggregated features
        aggregated_features /= len(augmented_images)
        
        # Flatten the features and add to the dictionary
        features_dict[os.path.basename(image_path)] = aggregated_features.flatten()
    
    # Create a directory to store the features file if it doesn't exist
    os.makedirs(f"features/{user_name}", exist_ok=True)

    # Save the features dictionary to a new features.pkl file
    with open(f"features/{user_name}/features.pkl", 'wb') as f:
        pickle.dump(features_dict, f)

    print(f"Features file saved at: features/{user_name}/features.pkl")
    
    # Optionally, release resources after saving
    try:
        del features_dict
        gc.collect()
    except:
        print("Error while releasing resources.")
        pass


def get_image_paths(image_dir):
    # Define a list of acceptable image file extensions
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    
    # Get all files from the directory
    image_paths = []
    
    # Loop through the files in the directory
    for filename in os.listdir(image_dir):
        # Get the full path of the file
        file_path = os.path.join(image_dir, filename)
        
        # Check if it's a file and has a valid image extension
        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in valid_extensions):
            image_paths.append(file_path)
    
    return image_paths

user_name = "hiren"
image_dir_path = "/Users/sandippatel/SPINFO/PixelLocater/Hiren"

image_paths = get_image_paths(image_dir_path)

create_features(user_name, image_paths)
