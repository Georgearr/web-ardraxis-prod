with open('templates/about_us.html', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = """      <div class="sekbid-image-card">
          <div class="image-carousel-container">
              <img
                  src="${staticBase}img/fotokabinet/${ardraxisCabinet[sekbid].sekbid_image[0]}"
                  alt="${ardraxisCabinet[sekbid].sekbid}"
                  class="image-carousel-image"
                  loading="lazy"
                  decoding="async"
              />
          </div>
      </div>"""

repl1 = """      <div class="sekbid-image-card">
          <img
              src="${staticBase}img/fotokabinet/${ardraxisCabinet[sekbid].sekbid_image[0]}"
              alt="${ardraxisCabinet[sekbid].sekbid}"
              class="sekbid-image"
              loading="lazy"
              decoding="async"
          />
      </div>"""

target2 = """                    <div class="sekbid-card-photo-wrapper">
                        <div class="carousel-container">
                            <img
                                src="${staticBase}img/fotokabinet/${member.images[0]}"
                                alt="${member.name}"
                                class="sekbid-card-photo carousel-image"
                                loading="lazy"
                                decoding="async"
                            />
                        </div>
                    </div>"""

repl2 = """                    <div class="sekbid-card-photo-wrapper">
                        <img
                            src="${staticBase}img/fotokabinet/${member.images[0]}"
                            alt="${member.name}"
                            class="sekbid-card-photo"
                            loading="lazy"
                            decoding="async"
                        />
                    </div>"""

assert target1 in text, "target1 not found"
assert target2 in text, "target2 not found"

text = text.replace(target1, repl1)
text = text.replace(target2, repl2)

with open('templates/about_us.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated templates/about_us.html successfully")
