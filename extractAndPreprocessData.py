import json
from time import time
import csv

def extractData():
    start_time = time()
    file_path = "annotations/instances_val2017.json"
    data = None
    extracted_data = []
    try:
        with open(file_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found.")
        return
    
    if "annotations" in data:
        annotations_data = data["annotations"]
        for img_annotation in annotations_data:
            extracted_data.append({"image_id":img_annotation["image_id"], "bbox":img_annotation["bbox"], "category_id":img_annotation["category_id"]})

    else:
        print("No 'annotations' key found in the JSON file.")

    if extracted_data:
        print(extracted_data[:10])
    else:
        return
    
    extracted_data = {"annotations":extracted_data}

    print("Time taken: ", (time() - start_time)/60, " minutes.")
    
    with open("extracted_data.json", "w") as f:
        json.dump(extracted_data, f)

    print(f"Written {len(extracted_data['annotations'])} annotations to file")
    print("Done. Time taken: ", (time() - start_time)/60, " minutes.")



def filterToRemoveMultiples():
    # filter out annotations with multiple objects of same class in the image

    # Read data from the file
    start_time = time()
    file_path = "extracted_data.json"
    with open(file_path, "r") as file:
        data = json.load(file)

    # Create a dictionary to store unique instances of category_id for each image_id
    filtered_data = {}
    for annotation in data["annotations"]:
        image_id = annotation["image_id"]
        category_id = annotation["category_id"]
        bbox = annotation["bbox"]
        if (image_id, category_id) not in filtered_data:
            filtered_data[(image_id, category_id)] = {"bbox": bbox, "error": False}
        else:
            filtered_data[(image_id, category_id)]["error"] = True

    ans_list = []
    # dictionary without items with error = True in value
    for key, value in filtered_data.items():
        if not value["error"]:
            ans_list.append({"image_id": key[0], "bbox": value["bbox"], "category_id": key[1]})

    ans_json = {"annotations": ans_list}
    # write to file
    with open("filtered_data.json", "w") as file:
        json.dump(ans_json, file)

    print(f"Written {len(ans_json['annotations'])} annotations to file")
    print("Done. Time taken: ", (time() - start_time)/60, " minutes.")


def getCategoryNames():
    # Read data from the file
    start_time = time()
    file_path = "annotations/instances_val2017.json"
    with open(file_path, "r") as file:
        data = json.load(file)
    # Create a dictionary to store unique instances of category_id for each image_id
    categoryNames = {}
    for category in data["categories"]:
        categoryNames[category["id"]] = [category["name"], category["supercategory"]]
    print("Done. Time taken: ", (time() - start_time)/60, " minutes.")
    return categoryNames

def determinePositionAndMakeCsvFile():
    positionMap = {0: "topLeft", 1: "topCenter", 2: "topRight", 3: "middleLeft", 4: "middleCenter", 5: "middleRight", 6: "bottomLeft", 7: "bottomCenter", 8: "bottomRight"}
    start_time = time()
    file_path = "annotations/instances_val2017.json"
    dimensionsDictionary = {}
    data = None
    try:
        with open(file_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found.")
        return
    
    if "images" in data:
        images_data = data["images"]
        for img in images_data:
            dimensionsDictionary[img["id"]] = {"width": img["width"], "height": img["height"]}
    else:
        print("No 'images' key found in the JSON file.")
        return
    # read data from filtered_data.json
    file_path = "filtered_data.json"
    with open(file_path, "r") as file:
        filteredData = json.load(file)
    # create a dictionary to store the final data
    finalData = []
    ct = 0
    categoryMap = getCategoryNames()
    for annotation in filteredData["annotations"]:
        image_id = annotation["image_id"]
        bbox = annotation["bbox"]
        category_id = annotation["category_id"]
        height = dimensionsDictionary[image_id]["height"]
        width = dimensionsDictionary[image_id]["width"]
        bboxCenter = [bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2]
        # if the image is divided into 3 parts vertically and 3 parts horizontally, which part is the bboxCenter in?
        # 0, 1, 2
        # 3, 4, 5
        # 6, 7, 8
        if bboxCenter[0] < width/3:
            if bboxCenter[1] < height/3:
                position = 0
            elif bboxCenter[1] < 2*height/3:
                position = 3
            else:
                position = 6
        elif bboxCenter[0] < 2*width/3:
            if bboxCenter[1] < height/3:
                position = 1
            elif bboxCenter[1] < 2*height/3:
                position = 4
            else:
                position = 7
        else:
            if bboxCenter[1] < height/3:
                position = 2
            elif bboxCenter[1] < 2*height/3:
                position = 5
            else:
                position = 8
        categoryMapping = categoryMap[category_id]
        finalData.append([ct, image_id, bbox, category_id, height, width, position, positionMap[position], categoryMapping[0], categoryMapping[1]])
        ct += 1
    # write to csv file with headers
    with open("filteredDataWithPosition.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(["row_id", "image_id", "bbox", "category_id", "height", "width", "position", "positionName", "categoryName", "superCategoryName"])
        writer.writerows(finalData)
    print("Done. Time taken: ", (time() - start_time)/60, " minutes.")
    


# extractData()
# filterToRemoveMultiples()
determinePositionAndMakeCsvFile()
