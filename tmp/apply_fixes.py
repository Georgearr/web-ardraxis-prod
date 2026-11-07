# 1. Update static/css/magazine.css
with open('static/css/magazine.css', 'r', encoding='utf-8') as f:
    mag_css = f.read()

# Replace padding-top on .magazine-hero to standard clamp(24px, 4vw, 48px) clamp(16px, 3vw, 32px);
# without the extra calc(70px + ...), calc(55px + ...), etc.
old_hero = """/* =========================================================
   HERO SECTION
   ========================================================= */
.magazine-hero {
  position: relative;
  background: linear-gradient(135deg, #0d292b 0%, #16484c 50%, #1d696e 100%);
  color: #ffffff;
  padding: clamp(24px, 4vw, 48px) clamp(16px, 3vw, 32px);
  /* Offset matches the fixed navbar so the hero sits flush under it. */
  padding-top: calc(70px + clamp(24px, 4vw, 48px));
  margin-bottom: clamp(20px, 3vw, 32px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}"""

new_hero = """/* =========================================================
   HERO SECTION
   ========================================================= */
.magazine-hero {
  position: relative;
  background: linear-gradient(135deg, #0d292b 0%, #16484c 50%, #1d696e 100%);
  color: #ffffff;
  padding: clamp(24px, 4vw, 48px) clamp(16px, 3vw, 32px);
  margin-bottom: clamp(20px, 3vw, 32px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}"""

assert old_hero in mag_css, "old_hero not found in magazine.css"
mag_css = mag_css.replace(old_hero, new_hero)

# Restore .magazine-page padding-top: 86px (and 76px on small mobile)
old_page = """.magazine-page {
  width: 100%;
  min-height: 100vh;
  background: var(--mag-bg);
  padding-top: 0;
  padding-bottom: 40px;
  color: var(--mag-text-main);
  position: relative;
  overflow-x: hidden;
}"""

new_page = """.magazine-page {
  width: 100%;
  min-height: 100vh;
  background: var(--mag-bg);
  padding-top: 86px; /* navbar spacing */
  padding-bottom: 40px;
  color: var(--mag-text-main);
  position: relative;
  overflow-x: hidden;
}"""

assert old_page in mag_css, "old_page not found in magazine.css"
mag_css = mag_css.replace(old_page, new_page)

# Remove the media query overrides for .magazine-hero padding-top
old_mq992 = """@media (max-width: 992px) {
  .magazine-hero {
    padding-top: calc(55px + clamp(24px, 4vw, 48px));
  }
}"""

if old_mq992 in mag_css:
    mag_css = mag_css.replace(old_mq992, "")

old_mq768 = """@media (max-width: 768px) {
  .magazine-hero {
    padding-top: calc(46px + clamp(24px, 4vw, 48px));
  }
}"""

if old_mq768 in mag_css:
    mag_css = mag_css.replace(old_mq768, "")

old_mq540 = """@media (max-width: 540px) {
  .magazine-hero {
    padding-top: calc(44px + clamp(24px, 4vw, 48px));
  }"""

new_mq540 = """@media (max-width: 540px) {
  .magazine-page {
    padding-top: 76px;
  }"""

if old_mq540 in mag_css:
    mag_css = mag_css.replace(old_mq540, new_mq540)

with open('static/css/magazine.css', 'w', encoding='utf-8') as f:
    f.write(mag_css)
print("Updated static/css/magazine.css")

# 2. Update static/css/about.css
with open('static/css/about.css', 'r', encoding='utf-8') as f:
    about_css = f.read()

# Add .sekbid-image and update .sekbid-card-photo
# First replace the image-carousel block with .sekbid-image
old_carousel_block = """.image-carousel-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 500px;
}

.image-carousel-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
  transform: translateX(100%);
  opacity: 0;
  animation: image-carousel-slide 15s infinite;
  will-change: transform, opacity;
  z-index: 1;
}

.image-carousel-image:nth-child(1) {
  animation-delay: 0s;
  transform: translateX(0);
  opacity: 1;
}

.image-carousel-image:nth-child(2) {
  animation-delay: 5s;
}

.image-carousel-image:nth-child(3) {
  animation-delay: 10s;
}

@keyframes image-carousel-slide {
  0% {
    transform: translateX(100%);
    opacity: 0;
  }
  3% {
    transform: translateX(0);
    opacity: 1;
  }
  30% {
    transform: translateX(0);
    opacity: 1;
  }
  33.33% {
    transform: translateX(-100%);
    opacity: 0;
  }
  100% {
    transform: translateX(-100%);
    opacity: 0;
  }
}"""

new_sekbid_image_block = """.sekbid-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
  display: block;
}"""

assert old_carousel_block in about_css, "old_carousel_block not found in about.css"
about_css = about_css.replace(old_carousel_block, new_sekbid_image_block)

# Replace member carousel block
old_member_carousel_block = """.carousel-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.sekbid-card-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
  display: block;
}

.carousel-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transform: translateX(100%) scale(1.2);
  opacity: 0;
  animation: carousel-slide 15s infinite;
  will-change: transform, opacity;
}

.carousel-image:nth-child(1) {
  animation-delay: 0s;
  transform: translateX(0) scale(1.1);
  opacity: 1;
}

.carousel-image:nth-child(2) {
  animation-delay: 5s;
}

.carousel-image:nth-child(3) {
  animation-delay: 10s;
}

@keyframes carousel-slide {
  0% {
    transform: translateX(100%) scale(1.2);
    opacity: 0;
  }
  3% {
    transform: translateX(0) scale(1.2);
    opacity: 1;
  }
  10% {
    transform: translateX(0) scale(1.15);
  }
  20% {
    transform: translateX(0) scale(1.1);
  }
  30% {
    transform: translateX(0) scale(1.05);
    opacity: 1;
  }
  31% {
    transform: translateX(0) scale(1);
  }
  33.33% {
    transform: translateX(-100%) scale(0.9);
    opacity: 0;
  }
  100% {
    transform: translateX(-100%) scale(0.9);
    opacity: 0;
  }
}"""

new_member_photo_block = """.sekbid-card-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
  display: block;
}"""

assert old_member_carousel_block in about_css, "old_member_carousel_block not found in about.css"
about_css = about_css.replace(old_member_carousel_block, new_member_photo_block)

# Also update media query in about.css
old_mq_about = """  .image-carousel-container {
    height: auto;
    min-height: 0;
    aspect-ratio: 16 / 9;
  }

  .image-carousel-image {
    height: 100%;
    width: 100%;
    object-fit: cover;
  }"""

new_mq_about = """  .sekbid-image {
    height: 100%;
    width: 100%;
    object-fit: cover;
    object-position: center top;
  }"""

if old_mq_about in about_css:
    about_css = about_css.replace(old_mq_about, new_mq_about)

with open('static/css/about.css', 'w', encoding='utf-8') as f:
    f.write(about_css)
print("Updated static/css/about.css")
