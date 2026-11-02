(function () {
  var galleries = document.querySelectorAll(".gallery");
  var lightbox = null;

  for (var g = 0; g < galleries.length; g++) {
    setup(galleries[g]);
  }

  // Turn one server-rendered gallery into a slideshow. Returns a controller
  // the lightbox drives, so the gallery itself never has to know it exists.
  function setup(gallery) {
    var slides = gallery.querySelectorAll(".gallery-slide");
    var thumbs = gallery.querySelectorAll(".gallery-thumb-btn");
    var prev = gallery.querySelector(".gallery-prev");
    var next = gallery.querySelector(".gallery-next");
    var slidesBox = gallery.querySelector(".gallery-slides");
    var count = slides.length;
    var current = -1;

    if (count === 0) return;

    var control = {
      element: gallery,
      slide: function () { return slides[current]; },
      step: function (delta) { return show(current + delta) ? slides[current] : null; },
      atStart: function () { return current === 0; },
      atEnd: function () { return current === count - 1; },
    };

    // Focus returns here when the lightbox closes, so arrow keys keep working.
    gallery.setAttribute("tabindex", "-1");
    fitFrame();

    function show(index) {
      if (index < 0 || index >= count || index === current) return false;
      current = index;

      for (var i = 0; i < count; i++) {
        slides[i].classList.toggle("is-active", i === index);
        thumbs[i].classList.toggle("is-active", i === index);
      }

      prev.disabled = index === 0;
      next.disabled = index === count - 1;

      // Hidden slides are lazy-loaded, so fetch the neighbours ahead of time.
      eager(index - 1);
      eager(index + 1);

      var t = thumbs[index];
      var strip = t.parentNode;
      var left = t.offsetLeft - (strip.clientWidth - t.offsetWidth) / 2;
      strip.scrollTo({ left: left, behavior: "smooth" });
      return true;
    }

    // Size the frame to the tallest image's aspect so that image fills it,
    // within limits: no taller than 3:4 and no wider than 16:9. Galleries
    // whose images all share an aspect ratio get a frame that fits exactly.
    function fitFrame() {
      var aspect = Infinity;
      for (var i = 0; i < count; i++) {
        var img = slides[i].querySelector("img");
        var w = img && img.getAttribute("width");
        var h = img && img.getAttribute("height");
        if (w > 0 && h > 0) aspect = Math.min(aspect, w / h);
      }
      if (aspect === Infinity) return;
      aspect = Math.max(0.75, Math.min(16 / 9, aspect));
      slidesBox.style.aspectRatio = String(aspect);
    }

    function eager(i) {
      if (i < 0 || i >= count) return;
      var img = slides[i].querySelector("img");
      if (img) img.loading = "eager";
    }

    prev.addEventListener("click", function () { show(current - 1); });
    next.addEventListener("click", function () { show(current + 1); });

    for (var i = 0; i < thumbs.length; i++) {
      (function (idx) {
        thumbs[idx].addEventListener("click", function () { show(idx); });
      })(i);
    }

    gallery.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { show(current - 1); e.preventDefault(); }
      if (e.key === "ArrowRight") { show(current + 1); e.preventDefault(); }
    });

    var endedSwipe = swipeable(slidesBox, function (delta) { show(current + delta); });

    // Click the main image to enlarge it.
    slidesBox.addEventListener("click", function (e) {
      if (endedSwipe()) return;
      if (e.target.tagName !== "IMG") return;
      getLightbox(gallery).open(control);
    });

    gallery.classList.add("is-ready");
    show(0);
  }

  // One overlay shared by every gallery on the page. It shows the largest
  // generated copy of the current slide, fit to the viewport. Any click or
  // key closes it, except Left/Right, which step to the neighbouring slide.
  // The arrows show while the pointer moves and fade once it rests.
  function getLightbox(gallery) {
    if (lightbox) return lightbox;

    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.hidden = true;

    var closeBtn = button("lightbox-close", "Close");
    closeBtn.innerHTML =
      '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">' +
      '<path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" ' +
      'stroke-width="2.2" stroke-linecap="round"/></svg>';

    // Reuse the gallery's own chevrons rather than redraw them here.
    var prevBtn = button("lightbox-prev", "Previous image");
    var nextBtn = button("lightbox-next", "Next image");
    prevBtn.appendChild(chevron(gallery.querySelector(".gallery-prev svg")));
    nextBtn.appendChild(chevron(gallery.querySelector(".gallery-next svg")));

    var img = document.createElement("img");
    var cap = document.createElement("div");
    cap.className = "lightbox-caption";

    box.appendChild(closeBtn);
    box.appendChild(prevBtn);
    box.appendChild(nextBtn);
    box.appendChild(img);
    box.appendChild(cap);
    document.body.appendChild(box);

    var owner = null;
    var idleTimer = null;

    function open(control) {
      owner = control;
      refresh();
      box.hidden = false;
      document.body.classList.add("lightbox-open");
      document.addEventListener("keydown", onKey);
      closeBtn.focus();
      wake();
    }

    function refresh() {
      var slide = owner.slide();
      var src = slide.querySelector("img");
      var fig = slide.querySelector("figcaption");
      img.src = largestSource(src);
      img.alt = src.alt || "";
      cap.textContent = fig ? fig.textContent : "";
      cap.hidden = !cap.textContent;
      prevBtn.disabled = owner.atStart();
      nextBtn.disabled = owner.atEnd();
    }

    function step(delta) {
      if (owner.step(delta)) refresh();
    }

    function close() {
      box.hidden = true;
      document.body.classList.remove("lightbox-open");
      document.removeEventListener("keydown", onKey);
      clearTimeout(idleTimer);
      img.removeAttribute("src");
      owner.element.focus();
      owner = null;
    }

    function onKey(e) {
      // A bare modifier, or a browser shortcut like Cmd+R, is not a dismissal.
      if (e.key === "Shift" || e.key === "Control" || e.key === "Alt" || e.key === "Meta") return;
      if (e.metaKey || e.ctrlKey) return;
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        e.preventDefault();
        step(e.key === "ArrowLeft" ? -1 : 1);
        return;
      }
      if (e.key === "Escape") e.preventDefault();
      close();
    }

    function wake() {
      box.classList.remove("is-idle");
      clearTimeout(idleTimer);
      idleTimer = setTimeout(function () { box.classList.add("is-idle"); }, 2000);
    }

    box.addEventListener("mousemove", wake);
    box.addEventListener("touchstart", wake, { passive: true });

    prevBtn.addEventListener("click", function (e) { e.stopPropagation(); step(-1); });
    nextBtn.addEventListener("click", function (e) { e.stopPropagation(); step(1); });

    var endedSwipe = swipeable(box, step);
    box.addEventListener("click", function () {
      if (!endedSwipe()) close();
    });

    lightbox = { open: open };
    return lightbox;
  }

  function button(cls, label) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = cls;
    b.setAttribute("aria-label", label);
    return b;
  }

  function chevron(svg) {
    var copy = svg.cloneNode(true);
    copy.setAttribute("width", "36");
    copy.setAttribute("height", "36");
    return copy;
  }

  // Step on a horizontal swipe. A swipe still ends in a click on touch
  // browsers, so the returned function tells a click handler whether the
  // click it just received was only the tail of a swipe.
  function swipeable(el, onStep) {
    var startX = null;
    var swiped = false;

    el.addEventListener("touchstart", function (e) {
      startX = e.touches[0].clientX;
      swiped = false;
    }, { passive: true });

    el.addEventListener("touchend", function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      startX = null;
      swiped = Math.abs(dx) > 10;
      if (dx < -40) onStep(1);
      if (dx > 40) onStep(-1);
    });

    return function endedSwipe() {
      var was = swiped;
      swiped = false;
      return was;
    };
  }

  // The build writes a srcset of ascending widths; the last entry is the
  // largest copy that exists for this image.
  function largestSource(img) {
    var srcset = img.getAttribute("srcset");
    if (!srcset) return img.currentSrc || img.src;
    var parts = srcset.split(",");
    var last = parts[parts.length - 1].trim().split(/\s+/)[0];
    return last || img.src;
  }
})();
