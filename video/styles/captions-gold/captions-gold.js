/* captions-gold: builds word-highlight captions from window.CAPTION_WORDS
   ([{text, start, end}], made by tools/script_timings.py or hyperframes transcribe)
   and adds their animation to the host timeline:

     CaptionsGold.attach(tl, "#captions");

   Words are grouped up to MAX_WORDS per screen, breaking after sentence ends.
   The active word gets a gold pill with dark text. */
(function () {
  var MAX_WORDS = 3;
  var HOLD = 0.35; // seconds a group lingers after its last word when there is room

  function groups(words) {
    var out = [], cur = [];
    words.forEach(function (w) {
      cur.push(w);
      if (cur.length === MAX_WORDS || /[.!?]$/.test(w.text)) { out.push(cur); cur = []; }
    });
    if (cur.length) out.push(cur);
    return out;
  }

  function attach(tl, selector, words) {
    words = words || window.CAPTION_WORDS || [];
    var root = document.querySelector(selector);
    var gs = groups(words);
    gs.forEach(function (g, gi) {
      var start = g[0].start;
      var next = gi + 1 < gs.length ? gs[gi + 1][0].start : Infinity;
      var end = Math.min(g[g.length - 1].end + HOLD, next - 0.04);

      var el = document.createElement("div");
      el.className = "cg-group";
      g.forEach(function (w) {
        var word = document.createElement("span");
        word.className = "cg-word";
        var bg = document.createElement("span");
        bg.className = "cg-bg";
        word.appendChild(bg);
        word.appendChild(document.createTextNode(w.text.replace(/[.,!?]+$/, "")));
        el.appendChild(word);
        w._el = word;
        w._bg = bg;
      });
      root.appendChild(el);

      tl.set(el, { visibility: "visible" }, start)
        .fromTo(el, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.14, ease: "power2.out" }, start);
      g.forEach(function (w) {
        tl.to(w._bg, { opacity: 1, scaleX: 1, duration: 0.1, ease: "power2.out" }, w.start)
          .set(w._el, { color: "#07080a", textShadow: "none" }, w.start + 0.1) // once the pill fully covers the word
          .to(w._bg, { opacity: 0, duration: 0.08 }, w.end)
          .set(w._el, { color: "#f6efe2", textShadow: "0 6px 18px rgba(0, 0, 0, 0.55)" }, w.end);
      });
      tl.to(el, { opacity: 0, duration: 0.08 }, end - 0.08).set(el, { visibility: "hidden" }, end);
    });
  }

  window.CaptionsGold = { attach: attach };
})();
