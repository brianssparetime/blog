(function () {
  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  var posts = [];
  var timer = null;

  fetch("/search-index.json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      posts = data;
      render(posts);
    });

  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      var query = input.value.trim().toLowerCase();
      if (!query) {
        render(posts);
        return;
      }
      var matched = posts.filter(function (p) {
        if (p.title.toLowerCase().indexOf(query) !== -1) return true;
        if (p.description && p.description.toLowerCase().indexOf(query) !== -1) return true;
        for (var i = 0; i < p.tags.length; i++) {
          if (p.tags[i].toLowerCase().indexOf(query) !== -1) return true;
        }
        return false;
      });
      render(matched);
    }, 200);
  });

  function render(list) {
    if (list.length === 0) {
      results.innerHTML = '<p class="search-message">No posts found.</p>';
      return;
    }
    var html = '<div class="post-grid">';
    for (var i = 0; i < list.length; i++) {
      var p = list[i];
      html += '<div class="post-card">';
      if (p.image) {
        html += '<div class="post-card-img">';
        html += '<a href="' + esc(p.url) + '"><img src="' + esc(p.image) + '" alt="' + esc(p.title) + '" loading="lazy"></a>';
        html += "</div>";
      }
      html += '<div class="post-card-body">';
      html += '<a href="' + esc(p.url) + '">';
      html += '<h3 class="heading">' + esc(p.title) + "</h3></a>";
      html += "<p><i>" + esc(p.date) + "</i></p>";
      if (p.description) {
        html += "<p>" + esc(p.description) + "</p>";
      }
      if (p.tags.length) {
        html += '<p class="tags">';
        for (var j = 0; j < p.tags.length; j++) {
          html += '<span class="tag"><a href="/tags/' + esc(p.tags[j]) + '/">' + esc(p.tags[j]) + "</a></span>";
        }
        html += "</p>";
      }
      html += "</div></div>";
    }
    html += "</div>";
    results.innerHTML = html;
  }

  function esc(s) {
    var el = document.createElement("span");
    el.textContent = s;
    return el.innerHTML;
  }
})();
