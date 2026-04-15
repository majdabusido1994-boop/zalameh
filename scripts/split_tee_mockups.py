"""Split Higgsfield tee mockups into 4 individual variants for the website."""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

FRONTS_PAIR = "tshirt/hf_20260415_034827_cb3411e3-3e02-4518-a68c-6a491801e3d2.png"
BACKS_PAIR  = "tshirt/hf_20260415_034912_a1576c8b-6849-41ef-8e5a-efdf5fbf67a1.png"

# FRONTS: stacked (black top, cream bottom)
im = Image.open(FRONTS_PAIR).convert("RGB")
W, H = im.size
black_front = im.crop((0, 0, W, H // 2))
cream_front = im.crop((0, H // 2, W, H))
black_front.save("website/images/tee-black-front.jpg", "JPEG", quality=92)
cream_front.save("website/images/tee-cream-front.jpg", "JPEG", quality=92)

# BACKS: side by side (black left, cream right)
im2 = Image.open(BACKS_PAIR).convert("RGB")
W2, H2 = im2.size
black_back = im2.crop((0, 0, W2 // 2, H2))
cream_back = im2.crop((W2 // 2, 0, W2, H2))
black_back.save("website/images/tee-black-back.jpg", "JPEG", quality=92)
cream_back.save("website/images/tee-cream-back.jpg", "JPEG", quality=92)

# Also save the nicest pair shot as hero image
im3 = Image.open("tshirt/hf_20260415_034827_e052cd04-ac03-48ed-a9f2-b7a1e4101309.png").convert("RGB")
im3.save("website/images/tee-hero.jpg", "JPEG", quality=92)

print("saved 5 tee images")
