import os
import cv2

# ---- Directory Options ----
# Folder path
path = "./renders/render_1/masks"  # "./Data/Source_Images/Training_Images/vott-csv-export"

# ---- Export Options ----
# This is where it places the CSV. This script substitutes for the vott export, so we can just place it there
# Place the CSV inside the training folder
# output = "./Data/Source_Images/Training_Images/vott-csv-export"
# Place the CSV inside the images folder
output = "./renders/render_1/images"

# ---- Input Options ----
# Image format EX: "Training Scene_1.0001.jpg"
prefix = ""
# Length of number, ex: 0052.png is numberPadding = 4
number_padding = 0
# Set an offset. If a section of frames is rendered ex: 50-100, specify an offset of 50
number_offset = 0
# Type of image export
suffix = ".jpg"

# --- Output Options ----
# Show generated files. This is very beneficial to seeing how it handles input
show_generated = True
# Write CSV
write_csv = False


# Convert a number like 52 to 0052 so it can be used to grab the filename
def pad_number(number):
    added_padding = ""
    for i in range(number_padding - len(str(number))):
        added_padding = added_padding + "0"
    return added_padding + str(number)


print("Initializing first file as " + prefix + pad_number(number_offset) + suffix)
print("At location: " + path + "/" + prefix + str(pad_number(0 + number_offset)) + suffix)
# Output CSV setup
if write_csv:
    try:
        output = open(output + "/Annotations-export.csv", "x")
        print("Creating file...")
    except:
        output = open(output + "/Annotations-export.csv", "w")
        print("Output file already exsits...")
    output.write("\"image\",\"xmin\",\"ymin\",\"xmax\",\"ymax\",\"label\"\n")

for i in range(len(os.listdir(path)) - 1):
    # Open image
    im = cv2.imread(path + "/" + prefix + pad_number(i + number_offset) + suffix)
    # Run threshold
    imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 40, 30, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(im, contours, -1, (0, 255, 0), 3)

    cv2.imshow('image', im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    MINIMUM_WIDTH = 40
    MINIMUM_HEIGHT = 40

    rectangles = []
    corners = []
    for c in contours:
        # Find the rectangle from the bounding box
        rect = cv2.boundingRect(c)
        x, y, w, h = rect
        # Create an initial filter to pull out the small rectangles
        if w < MINIMUM_WIDTH:
            continue
        if h < MINIMUM_HEIGHT:
            continue

        rectangles.append((x, y, w, h))

    for c in rectangles:
        # Compare every detection against every other to determine if they're valid
        valid = True
        test_box_corners = ((c[0], c[1]), (c[0] + c[2], c[1] + c[3]))
        for j in rectangles:
            inner_test_box = ((j[0], j[1]), (j[0] + j[2], j[1] + j[3]))
            # This just checks to make sure they aren't the same box
            if test_box_corners[0] != inner_test_box[0] and test_box_corners[1] != inner_test_box[1]:

                # If the x of the test box is inside of the corners box and the y is also inside the corners box
                if test_box_corners[0][0] > inner_test_box[0][0] and test_box_corners[0][1] > inner_test_box[0][1]:
                    if test_box_corners[1][0] < inner_test_box[1][0] and test_box_corners[1][1] < inner_test_box[1][1]:
                        valid = False
                        break
                else:
                    # Both have to be false to fail
                    continue
            else:
                # This is just the same box so just ignore it
                continue
        if valid:
            detected_box = ("\"" + prefix + pad_number(i + number_offset) + suffix + "\"" + "," + str(c[0]) + "," + str(c[1]) + "," + str(c[0]+c[2]) + "," + str(c[1]+c[3]) + "," + "\"" + "chair" + "\"" + "\n")
            corners.append(detected_box)
            # Write it to the image if show_generated is enabled
            if show_generated:
                cv2.rectangle(im, (c[0], c[1]), (c[0] + c[2], c[1] + c[3]), (0, 255, 0), 2)
                cv2.putText(im, 'Corner', (c[0] + c[2] + 10, c[1] + c[3]), 0, 0.3, (0, 255, 0))

    if write_csv:
        for j in corners:
            output.write(j)

    # Show image
    if show_generated:
        cv2.imshow('image', im)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if i % 20 == 0:
        print("Labeled image {}.".format(i))

output.close()
