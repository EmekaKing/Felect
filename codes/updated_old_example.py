# import packages
import numpy as np
import os
from os.path import isfile, join, exists, basename, splitext
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image


# import utilities
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


# Any model exported using the `export_inference_graph.py` tool can be loaded here simply by changing `PATH_TO_CKPT` to point to a new .pb file.
# Name of the directory containing the object detction module being used
MODEL_NAME = 'm_ssdres101_0.09'


# Path to frozen detection graph. This is the actual model that is used for the object detection.
direc = "C:/Users/emeka/models/research/object_detection"
PATH_TO_CKPT = direc + '/' + MODEL_NAME + '/frozen_inference_graph.pb'


# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(direc, 'datafaults', 'label_map.pbtxt')
#number of classes the object detector can identify
NUM_CLASSES = 4


detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef() #tf.compat.v1.GraphDef
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:    #tf.io.gfile.GFile
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')


# Loading label map
# Label maps map indices to category names, so that when the convolution network predicts a number, it can map it to its correspondsing classname.  Here internal utility functions is used. Also using anything that returns a dictionary mapping integers to appropriate string labels is sufficient.
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
PATH_TO_TEST_IMAGES_DIR = 'images_600x600'

#TEST_IMAGE_PATHS = [ os.path.join(mmm, PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 3) ]  # change this value if you want to add image limits
TEST_IMAGE_PATHS = os.path.join(direc, PATH_TO_TEST_IMAGES_DIR, 'valid') #val,test
TIP = []
for subdir, dirs, files in os.walk(TEST_IMAGE_PATHS):
    for file in files:
        if (file.endswith('.jpg')):
            img_path = os.path.join(subdir, file)
            TIP.append(img_path)

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 12)


with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        i = 0   # add variable for a janky fix
        for image_path in TIP:
            bname = basename(image_path)
            b_name = bname.split('.')[0]
            image = Image.open(image_path)
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            image_np = load_image_into_numpy_array(image)
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')
            # Actual detection.
            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})
            # Visualization of the results of a detection.
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=3)

            plt.figure(figsize=IMAGE_SIZE)
            plt.imshow(image_np)
            plt.axis('off')
            # plt.show()
            # when running on local PC, matplotlib is not set for graphical display so instead the outputs is saved to a folder.
            plt.savefig(direc+"/"+"val/"+"val101_09/{}.png".format(b_name), bbox_inches='tight', pad_inches = 0) #dpi 924size == 12inches
            i = i+1
