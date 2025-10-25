# render.py
from skimage.filters import gaussian
from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx
import os
import config

def blur(image):
    # Strong blur; preserve original range to avoid brightness shifts
    return gaussian(image, sigma=25, preserve_range=True)

def render(directory, clip_name, output_name, resolution):
    """
    Resize/center with optional blurred background.
    Returns 1 if pass-through, 0 if rendered.
    """
    src = os.path.join(directory, clip_name)
    dst = os.path.join(directory, output_name)

    if resolution is None:
        print("Resolution None: passing through.")
        if os.path.exists(dst):
            os.remove(dst)
        os.replace(src, dst)
        return 1

    main = VideoFileClip(src)
    exact_ratio = main.size[0] / main.size[1]
    target_ratio = resolution[0] / resolution[1]

    if target_ratio * 0.95 < exact_ratio < target_ratio * 1.05:
        print(f"Aspect close to target (exact={exact_ratio:.4f}, target={target_ratio:.4f}). Pass-through.")
        main.close()
        if os.path.exists(dst):
            os.remove(dst)
        os.replace(src, dst)
        return 1

    bg = VideoFileClip(src).resize(resolution).fx(vfx.colorx, 0.1)
    if config.VIDEO["blur"]:
        bg = bg.fl_image(blur)

    fg = main.resize(width=resolution[0])
    video = CompositeVideoClip([bg, fg.set_position("center")], size=resolution)

    try:
        video.write_videofile(dst, audio_codec="aac")  # ffmpeg handles codec defaults
    finally:
        main.close()
        bg.close()
        fg.close()
        video.close()

    return 0
