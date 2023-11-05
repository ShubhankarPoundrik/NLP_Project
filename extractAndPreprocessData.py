import json
from time import time

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
        ct = 0
        for img_annotation in annotations_data:
            # if ct == 10:
            #     break
            # ct += 1
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



extractData()
filterToRemoveMultiples()