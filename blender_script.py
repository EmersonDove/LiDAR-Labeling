import bpy
import mathutils
import random
import os
import time
import threading

# ---- Render Settings ----
# Get all files in files directory
Working_Directory = "/Users/emerson/PycharmProjects/LiDAR-Labeling"  # <-- Change this one

output_directory_images = os.path.join(Working_Directory, "renders/render_1/images")
output_directory_masks = os.path.join(Working_Directory, "renders/render_1/masks")

Frame_Count = 0

print("Output Directory Images >  " + output_directory_images)
print("Output Directory Masks >  " + output_directory_masks)

# Create a counter to set filenames
rendered_frames = 0

# Set how many frames of this to render
frames_needed = 100

# Set quality to .JPEG. You can also use .PNG for higher quality but .JPEG is significantly smaller
bpy.context.scene.render.image_settings.file_format = 'JPEG'

# ---- Target Settings ----
# Limits (Based on transforms of constraint planes)
plus_x = bpy.data.objects["+X"].location[0]
minus_x = bpy.data.objects["-X"].location[0]
plus_y = bpy.data.objects["+Y"].location[1]
minus_y = bpy.data.objects["-Y"].location[1]
plus_z = bpy.data.objects["+Z"].location[2]
minus_z = bpy.data.objects["-Z"].location[2]

# Get the camera to move
camera = bpy.data.objects["render_camera"]

# Get the scene object to hide
scene = bpy.data.objects["house"]

# Get the chairs
obj = bpy.data.objects["chairs"]

# Reset Location - this is a bit irrelevant but it does help see that everything is working
camera.location = mathutils.Vector((0, 0, 0))

# ---- Enables/Disables ----
# Enable/disable the rendering
run_render = True


# Function to randomize target motion
def move_camera(obj):
    # Store the current location
    loc = obj.location
    # Randomize value
    (x, y, z) = (random.random() - .5, random.random() - .5, random.random() - .5)
    # Adding adjustment values to the property
    loc = loc + mathutils.Vector((x, y, z))

    # Too far in the X direction
    if loc[0] > plus_x:
        loc[0] = plus_x

    if loc[0] < minus_x:
        loc[0] = minus_x

    # Too far in a Y direction
    if loc[1] > plus_y:
        loc[1] = plus_y

    if loc[1] < minus_y:
        loc[1] = minus_y

    # Too far in a Z direction
    if loc[2] > plus_z:
        loc[2] = plus_z

    if loc[2] < minus_z:
        loc[2] = minus_z

    # Set location to new location
    obj.location = loc
    # Generate a random rotation
    obj.rotation_euler = mathutils.Vector(
        ((random.random() - .5) * 10, (random.random() - .5) * 10, (random.random() - .5) * 10))


# Append the above function to the frame change event
# Uncommenting allows move_target to run every frame change
# bpy.app.handlers.frame_change_pre.append(move_target)
def render_clip(rendered_frames, camera, run_render, frames_needed, scene, obj):
    # Set the project end to the length
    bpy.context.scene.frame_end = frames_needed

    # Render through each frame
    for i in range(frames_needed):
        # Skip frame zero

        # Move the camera to a new place
        move_camera(camera)

        # First run the scene render, this means we have to turn off the object
        obj.hide_render = True
        if run_render:
            bpy.context.scene.render.filepath = output_directory_images + "/" + str(rendered_frames)
            # Run the render
            bpy.ops.render.render(write_still=True)
        else:
            time.sleep(.15)
        obj.hide_render = False

        # For the mask render we need to hide the body
        scene.hide_render = True
        if run_render:
            # Set it to the mask directory
            bpy.context.scene.render.filepath = output_directory_masks + "/" + str(rendered_frames)
            # Perform render
            bpy.ops.render.render(write_still=True)
        else:
            time.sleep(.15)
        # Reset it back to original settings
        scene.hide_render = False

        # Increment counter
        rendered_frames += 1


if __name__ == "__main__":
    # thread = threading.Thread(target=render_clip, args=(rendered_frames, obj, run_render, frames_needed, scene, ))
    # thread.start()
    render_clip(rendered_frames, camera, run_render, frames_needed, scene, obj)


# Print total frames rendered at program end
print("Rendered: " + str(rendered_frames))
