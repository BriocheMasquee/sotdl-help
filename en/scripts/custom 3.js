/* Pages de module SotDL : mêmes retouches que views/partials/base.html du système */
(function () {
  function fix() {
    var main = document.querySelector('body > main') || document.querySelector('main');
    if (!main) { return; }
    /* Les formules sans dé (« +2 », plages « 1-2 ») ne sont pas des jets : on garde le texte, on retire le lien */
    Array.prototype.slice.call(main.querySelectorAll('a[href^="/roll/"]')).forEach(function (link) {
      var formula = decodeURIComponent(link.getAttribute('href').slice('/roll/'.length));
      if (!/d/i.test(formula)) { link.parentNode.replaceChild(document.createTextNode(link.textContent), link); }
    });
    /* Gras en tête de paragraphe ou de puce : rouge (classe .lead) */
    Array.prototype.slice.call(main.querySelectorAll('p > strong, li > strong')).forEach(function (el) {
      var node = el.previousSibling;
      while (node && node.nodeType === 3 && !node.nodeValue.trim()) { node = node.previousSibling; }
      if (!node) { el.classList.add('lead'); }
    });
  }
  fix();
  document.addEventListener('DOMContentLoaded', fix);
  window.addEventListener('load', fix);
})();
